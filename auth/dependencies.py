"""
Simplified authentication for OAuth testing.
"""

from typing import Optional, Dict
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.database import credentials_db
import logging

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


def get_current_user_simple(request: Request) -> Optional[Dict]:
    """Simple user authentication - checks session cookie."""
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    
    user_data = credentials_db.validate_session(session_token)
    return user_data


def get_access_token_simple(request: Request) -> Optional[str]:
    """Simple access token extraction for OAuth testing."""
    user_data = get_current_user_simple(request)
    if user_data:
        return user_data.get('access_token')
    return None


def require_oauth_token(request: Request) -> str:
    """Require OAuth access token for API calls."""
    access_token = get_access_token_simple(request)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OAuth authentication required. Please authenticate first.",
        )
    return access_token
