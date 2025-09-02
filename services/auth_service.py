"""
Authentication service for handling OAuth operations and credential storage.
"""

import logging
from typing import Any

import httpx

from config import REDIRECT_URI
from models.database import credentials_db
from providers.outlook import OutlookProvider

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication operations."""

    def __init__(self):
        self.outlook_provider = OutlookProvider()

    async def get_authorization_url(self) -> dict[str, Any]:
        """Generate OAuth authorization URL."""
        try:
            auth_url = self.outlook_provider._oauth_get_authorization_url(
                redirect_uri=REDIRECT_URI
            )

            logger.info("Generated OAuth authorization URL")
            return {"authorization_url": auth_url, "redirect_uri": REDIRECT_URI}

        except Exception as e:
            logger.error(f"Failed to generate authorization URL: {e}")
            raise

    async def exchange_code_for_tokens(self, code: str, state: str = None) -> dict[str, Any]:
        """Exchange authorization code for access tokens and save to database."""
        try:
            # Exchange code for tokens using the OAuth provider
            oauth_credentials = self.outlook_provider._oauth_get_credentials(
                redirect_uri=REDIRECT_URI, code=code
            )
            tokens = {
                "access_token": oauth_credentials.credentials.get("access_token"),
                "refresh_token": oauth_credentials.credentials.get("refresh_token"),
                "expires_in": oauth_credentials.credentials.get("expires_in", 3600),
                "token_type": "Bearer",
            }
            # Get user information from Microsoft Graph API
            user_info = await self.get_user_info(tokens["access_token"])
            # Save credentials to database
            user_id = credentials_db.save_user_credentials(user_info, tokens)
            # Create a session token
            session_token = credentials_db.create_session(user_id)
            logger.info(f"Successfully saved credentials for user: {user_info.get('mail', 'unknown')}")
            return {
                "user_id": user_id,
                "session_token": session_token,
                "user_info": user_info,
                **tokens
            }

        except Exception as e:
            logger.error(f"OAuth callback failed: {e}")
            raise

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
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

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an expired access token."""
        try:
            credentials = {"refresh_token": refresh_token}

            new_credentials = self.outlook_provider.oauth_refresh_credentials(
                redirect_uri=REDIRECT_URI, credentials=credentials
            )

            logger.info("Successfully refreshed access token")
            return {
                "access_token": new_credentials.credentials.get("access_token"),
                "refresh_token": new_credentials.credentials.get("refresh_token"),
                "expires_at": new_credentials.expires_at,
                "token_type": "Bearer",
            }

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise

    async def validate_access_token(self, access_token: str) -> dict[str, bool]:
        """Validate an access token."""
        try:
            credentials = {"access_token": access_token}
            self.outlook_provider._validate_credentials(credentials)

            logger.info("Access token validation successful")
            return {"valid": True}

        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return {"valid": False}
