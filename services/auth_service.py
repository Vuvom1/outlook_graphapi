"""
Authentication service for handling OAuth operations.
"""
import logging
from typing import Dict, Any
from providers.outlook import OutlookProvider
from config import SYSTEM_CREDENTIALS, REDIRECT_URI

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication operations."""
    
    def __init__(self):
        self.outlook_provider = OutlookProvider()
    
    async def get_authorization_url(self) -> Dict[str, Any]:
        """Generate OAuth authorization URL."""
        try:
            auth_url = self.outlook_provider._oauth_get_authorization_url(
                redirect_uri=REDIRECT_URI,
                system_credentials=SYSTEM_CREDENTIALS
            )
            
            logger.info("Generated OAuth authorization URL")
            return {
                "authorization_url": auth_url,
                "redirect_uri": REDIRECT_URI
            }
            
        except Exception as e:
            logger.error(f"Failed to generate authorization URL: {e}")
            raise
    
    async def exchange_code_for_tokens(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens."""
        try:
            request_data = {
                "args": {
                    "code": code,
                    "state": state
                }
            }
            
            oauth_credentials = self.outlook_provider._oauth_get_credentials(
                redirect_uri=REDIRECT_URI,
                system_credentials=SYSTEM_CREDENTIALS,
                request=request_data
            )
            
            logger.info("Successfully exchanged authorization code for access token")
            return {
                "access_token": oauth_credentials.credentials.get("access_token"),
                "refresh_token": oauth_credentials.credentials.get("refresh_token"),
                "expires_at": oauth_credentials.expires_at,
                "token_type": "Bearer"
            }
            
        except Exception as e:
            logger.error(f"OAuth callback failed: {e}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token."""
        try:
            credentials = {"refresh_token": refresh_token}
            
            new_credentials = self.outlook_provider.oauth_refresh_credentials(
                redirect_uri=REDIRECT_URI,
                system_credentials=SYSTEM_CREDENTIALS,
                credentials=credentials
            )
            
            logger.info("Successfully refreshed access token")
            return {
                "access_token": new_credentials.credentials.get("access_token"),
                "refresh_token": new_credentials.credentials.get("refresh_token"),
                "expires_at": new_credentials.expires_at,
                "token_type": "Bearer"
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise
    
    async def validate_access_token(self, access_token: str) -> Dict[str, bool]:
        """Validate an access token."""
        try:
            credentials = {"access_token": access_token}
            self.outlook_provider._validate_credentials(credentials)
            
            logger.info("Access token validation successful")
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return {"valid": False}
