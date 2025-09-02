"""
Simplified authentication for OAuth testing.
"""

import logging
from datetime import datetime, timedelta

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer

from models.database import credentials_db
from services import AuthService

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)

def get_access_token_simple(request: Request) -> str | None:
    """Simple access token extraction for OAuth testing."""
    user_data = get_current_user(request)
    if user_data:
        return user_data.get('access_token')
    return None


async def require_oauth_token(request: Request) -> str:
    """Require OAuth access token for API calls."""
    access_token = await get_access_token_with_refresh(request)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OAuth authentication required. Please authenticate first.",
        )
    return access_token


def get_current_user(request: Request) -> dict | None:
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    user_data = credentials_db.validate_session(session_token)
    return user_data

async def get_access_token_with_refresh(request: Request) -> str | None:
    """
    Get access token for the current user, refresh if expired or near expiry.
    """
    user_data = get_current_user(request)
    if not user_data:
        return None
    access_token = user_data.get('access_token')
    refresh_token = user_data.get('refresh_token')
    token_expires_at = user_data.get('token_expires_at')
    user_id = user_data.get('user_id')
    if not access_token or not refresh_token or not token_expires_at or not user_id:
        return None
    # Check if token is expired or will expire in next 5 minutes
    try:
        expires_at = datetime.fromisoformat(token_expires_at)
    except Exception:
        logger.error("Invalid token_expires_at format")
        return None
    now = datetime.utcnow()
    if expires_at - now < timedelta(minutes=5):
        # Token expired or about to expire, refresh
        auth_service = AuthService()
        try:
            new_tokens = await auth_service.refresh_access_token(refresh_token)
            credentials_db.update_tokens(
                user_id=user_id,
                access_token=new_tokens["access_token"],
                refresh_token=new_tokens.get("refresh_token", refresh_token),
                expires_in=3600  # or parse from new_tokens if available
            )
            return new_tokens["access_token"]
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OAuth token expired and refresh failed. Please re-authenticate."
            )
    return access_token
