"""
OAuth authentication router for Outlook service.
Handles OAuth flow for Microsoft Graph API access.
"""

import logging
import httpx

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from config import REDIRECT_URI, SYSTEM_CREDENTIALS
from providers.outlook import OutlookProvider
from models.database import credentials_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
oauth_router = APIRouter(prefix="/oauth", tags=["OAuth Authentication"])

# Initialize Outlook provider
outlook_provider = OutlookProvider()


@oauth_router.get("/get_authorization_url", summary="Initiate OAuth Authorization")
async def get_authorization_url():
    """
    Generate and return the Microsoft OAuth authorization URL.
    Users should visit this URL to grant permissions.
    """
    try:
        auth_url = outlook_provider._oauth_get_authorization_url(
            redirect_uri=REDIRECT_URI
        )

        logger.info("Generated OAuth authorization URL")

        return {
            "authorization_url": auth_url,
            "redirect_uri": REDIRECT_URI,
            "message": "Visit the authorization_url to grant permissions, then you'll be redirected back to the callback endpoint.",
        }

    except Exception as e:
        logger.error(f"Failed to generate authorization URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate authorization URL: {str(e)}")


@oauth_router.get("/get_credentials", summary="Get OAuth Credentials")
async def get_credentials(code: str = Query(..., description="Authorization code from the redirect")):
    """
    Exchange the authorization code for OAuth credentials and save to database.

    This endpoint is called after the user grants permissions and is redirected back to the application.
    """
    try:
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code is required")

        # Exchange code for credentials
        credentials = outlook_provider._oauth_get_credentials(
            redirect_uri=REDIRECT_URI, code=code
        )

        tokens = {
            "access_token": credentials.credentials.get("access_token"),
            "refresh_token": credentials.credentials.get("refresh_token"),
            "expires_in": credentials.credentials.get("expires_in", 3600),
            "token_type": "Bearer",
        }

        # Get user information from Microsoft Graph API
        user_info = await get_user_info(tokens["access_token"])
        
        # Save credentials to database
        user_id = credentials_db.save_user_credentials(user_info, tokens)
        
        # Create a session token for web interface integration
        session_token = credentials_db.create_session(user_id)

        logger.info(f"Successfully exchanged authorization code for credentials and saved for user: {user_info.get('mail', 'unknown')}")

        return {
            "message": "Credentials obtained and saved successfully",
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": credentials.expires_at,
            "token_type": "Bearer",
            "user_id": user_id,
            "session_token": session_token,
            "user_info": user_info
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get credentials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get credentials: {str(e)}")


async def get_user_info(access_token: str) -> dict:
    """Get user information from Microsoft Graph API."""
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get("https://graph.microsoft.com/v1.0/me", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user info: {response.status_code} {response.text}")
                return {"mail": "unknown@example.com", "displayName": "Unknown User"}
                
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return {"mail": "unknown@example.com", "displayName": "Unknown User"}


@oauth_router.post("/refresh", summary="Refresh Access Token")
async def refresh_token(refresh_token: str):
    """
    Refresh an expired access token using the refresh token.

    Request body should contain:
    {
        "refresh_token": "your_refresh_token_here"
    }
    """
    try:
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token is required")

        # Create credentials object for refresh
        credentials = {"refresh_token": refresh_token}

        # Refresh the credentials
        new_credentials = outlook_provider.oauth_refresh_credentials(
            redirect_uri=REDIRECT_URI, credentials=credentials
        )

        logger.info("Successfully refreshed access token")

        return {
            "message": "Token refreshed successfully",
            "access_token": new_credentials.credentials.get("access_token"),
            "refresh_token": new_credentials.credentials.get("refresh_token"),
            "expires_at": new_credentials.expires_at,
            "token_type": "Bearer",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")


@oauth_router.post("/validate", summary="Validate Access Token")
async def validate_token(access_token: str):
    """
    Validate an access token by making a test call to Microsoft Graph API.

    Request body should contain:
    {
        "access_token": "your_access_token_here"
    }
    """
    try:
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")

        # Validate the credentials
        credentials = {"access_token": access_token}
        outlook_provider._validate_credentials(credentials)

        logger.info("Access token validation successful")

        return {"message": "Access token is valid", "valid": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        return JSONResponse(
            status_code=401, content={"message": "Access token is invalid or expired", "valid": False, "error": str(e)}
        )
