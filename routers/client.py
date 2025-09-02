"""
Client portal router for server-side rendering of OAuth authentication UI.
Provides a web interface for users to authenticate and get credentials.
"""
from datetime import datetime

import httpx
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from auth.dependencies import get_current_user_simple
from models.database import credentials_db
from providers.outlook import outlook_provider
from services.auth_service import AuthService

# Initialize router, templates, and services
client_router = APIRouter(prefix="/client", tags=["Client Portal"])
templates = Jinja2Templates(directory="templates")
auth_service = AuthService()


# Remove the old session management functions since we're using database now
def get_base_url(request: Request) -> str:
    """Get the base URL for API endpoints."""
    return f"{request.url.scheme}://{request.url.netloc}"


@client_router.get("/", response_class=HTMLResponse, summary="Client Portal Homepage")
async def client_portal(request: Request):
    """
    Main client portal page for OAuth authentication.
    """
    try:
        user = get_current_user_simple(request)
        authenticated = user is not None
        access_token = None
        user_info = {}
        token_expires = None

        if authenticated:
            access_token = user.get("access_token")
            user_info = {
                "email": user.get("email"),
                "name": user.get("display_name")
            }
            # Format token expiration
            if user.get("token_expires_at"):
                expires_at = datetime.fromisoformat(user["token_expires_at"])
                token_expires = expires_at.strftime("%Y-%m-%d %H:%M:%S")
        # Get authorization URL for non-authenticated users
        auth_url = None
        if not authenticated:
            try:
                # Use the OAuth endpoint from our API
                auth_url = "/oauth/get_authorization_url"
            except Exception:
                auth_url = "/oauth/get_authorization_url"  # Fallback to API endpoint
        return templates.TemplateResponse("client_portal.html", {
            "request": request,
            "authenticated": authenticated,
            "auth_url": auth_url,
            "access_token": access_token,
            "user_info": user_info,
            "token_expires": token_expires,
            "base_url": get_base_url(request)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading client portal: {str(e)}")


@client_router.get("/get-auth-url", summary="Get OAuth Authorization URL")
async def get_auth_url(request: Request):
    """
    Get the OAuth authorization URL dynamically.
    """
    try:
        # Check if Azure credentials are properly configured
        from config import SYSTEM_CREDENTIALS
        if not SYSTEM_CREDENTIALS.get("client_id") or SYSTEM_CREDENTIALS.get("client_id") == "your-client-id-here":
            return {
                "success": False,
                "error": "Azure credentials not configured. Please set AZURE_CLIENT_ID and AZURE_CLIENT_SECRET environment variables.",
                "fallback_url": "/oauth/get_authorization_url"
            }
        base_url = get_base_url(request)
        redirect_uri = f"{base_url}/client/callback"
        # Use the outlook provider's OAuth method
        auth_url = outlook_provider._oauth_get_authorization_url(redirect_uri)
        return {"success": True, "auth_url": auth_url}
    except Exception as e:
        error_msg = str(e)
        if "client_id" in error_msg.lower() or "client_secret" in error_msg.lower():
            error_msg = "Azure credentials not properly configured. Please check your environment variables."
        return {"success": False, "error": error_msg, "fallback_url": "/oauth/get_authorization_url"}


@client_router.get("/callback", summary="OAuth Callback Page")
async def client_oauth_callback_page(request: Request):
    """
    OAuth callback page that handles authorization code exchange.
    """
    return templates.TemplateResponse("oauth_callback.html", {
        "request": request,
        "base_url": get_base_url(request)
    })


@client_router.get("/callback-handler", summary="OAuth Callback Handler (API)")
async def client_oauth_callback_handler(request: Request, code: str, state: str = None):
    """
    Handle OAuth callback and store user session (API endpoint).
    This is called by the JavaScript on the callback page.
    """
    try:
        # Exchange code for tokens and save to database
        result = await auth_service.exchange_code_for_tokens(code, state)
        # Create response with session token cookie
        response = RedirectResponse(url="/client", status_code=302)
        response.set_cookie(
            "session_token",
            result["session_token"],
            max_age=24*3600,  # 24 hours
            httponly=True,
            secure=False  # Set to True in production with HTTPS
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth callback error: {str(e)}")


@client_router.get("/test-api", response_class=HTMLResponse, summary="API Testing Console")
async def test_api_page(request: Request):
    """
    API testing console page.
    """
    user = get_current_user_simple(request)
    if not user:
        # Redirect to login if not authenticated
        return RedirectResponse(url="/client", status_code=302)
    return templates.TemplateResponse("test_api.html", {
        "request": request,
        "access_token": user["access_token"],
        "base_url": get_base_url(request),
        "user_info": {
            "email": user["email"],
            "name": user["display_name"]
        }
    })


@client_router.post("/test-endpoint", summary="Test API Endpoint")
async def test_endpoint(request: Request, endpoint: str = Form(...), method: str = Form(...)):
    """
    Test an API endpoint and return results.
    """
    user = get_current_user_simple(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        base_url = get_base_url(request)
        headers = {"Authorization": f"Bearer {user['access_token']}"}
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(f"{base_url}{endpoint}", headers=headers)
            elif method.upper() == "POST":
                response = await client.post(f"{base_url}{endpoint}", headers=headers)
            elif method.upper() == "PATCH":
                response = await client.patch(f"{base_url}{endpoint}", headers=headers)
            elif method.upper() == "DELETE":
                response = await client.delete(f"{base_url}{endpoint}", headers=headers)
            else:
                raise HTTPException(status_code=400, detail="Unsupported HTTP method")
        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "data": response.json() if response.content else {},
            "message": f"{method.upper()} {endpoint} - Status: {response.status_code}"
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "data": {"error": str(e)},
            "message": f"Error testing {method.upper()} {endpoint}: {str(e)}"
        }


@client_router.get("/logout", summary="Logout User")
async def logout(request: Request):
    """
    Clear user session and redirect to login.
    """
    session_token = request.cookies.get("session_token")
    if session_token:
        credentials_db.invalidate_session(session_token)
    response = RedirectResponse(url="/client", status_code=302)
    response.delete_cookie("session_token")
    return response


@client_router.get("/status", summary="Get Authentication Status")
async def get_status(request: Request):
    """
    Get current authentication status (API endpoint).
    """
    user = get_current_user_simple(request)
    if not user:
        return {"authenticated": False, "message": "No active session"}
    # Check token expiration
    token_expires_at = datetime.fromisoformat(user["token_expires_at"])
    token_valid = token_expires_at > datetime.utcnow()
    return {
        "authenticated": token_valid,
        "user_info": {
            "email": user["email"],
            "name": user["display_name"]
        },
        "token_expires_at": user["token_expires_at"],
        "token_valid": token_valid
    }


@client_router.get("/simple-test", summary="Simple OAuth Test")
async def simple_oauth_test(request: Request):
    """
    Simple endpoint to test OAuth functionality.
    """
    user = get_current_user_simple(request)
    if not user:
        return {"authenticated": False, "message": "Please authenticate first"}
    return {
        "authenticated": True,
        "access_token": user.get('access_token', 'N/A'),
        "user_info": {
            "email": user.get("email"),
            "name": user.get("display_name")
        },
        "message": "OAuth authentication successful!"
    }
