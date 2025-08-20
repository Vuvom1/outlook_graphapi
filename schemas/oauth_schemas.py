"""
OAuth-related schemas for the Outlook service API.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from .common_schemas import BaseResponse


class OAuthTokenRequest(BaseModel):
    """Request model for OAuth token operations."""
    refresh_token: str = Field(..., description="Refresh token for obtaining new access token")


class ValidateTokenRequest(BaseModel):
    """Request model for token validation."""
    access_token: str = Field(..., description="Access token to validate")


class OAuthTokenResponse(BaseResponse):
    """Response model for OAuth token operations."""
    access_token: str = Field(..., description="Access token for API calls")
    refresh_token: str = Field(..., description="Refresh token for token renewal")
    token_type: str = Field(default="Bearer", description="Type of the token")
    expires_at: int = Field(..., description="Token expiration timestamp")
    expires_in: Optional[int] = Field(None, description="Token expiration in seconds")


class RefreshTokenRequest(BaseModel):
    """Request model for refreshing access tokens."""
    refresh_token: str = Field(..., description="Valid refresh token")


class ValidateTokenResponse(BaseResponse):
    """Response model for token validation."""
    valid: bool = Field(..., description="Whether the token is valid")
    expires_at: Optional[int] = Field(None, description="Token expiration timestamp if valid")


class AuthorizationUrlResponse(BaseResponse):
    """Response model for authorization URL generation."""
    authorization_url: str = Field(..., description="OAuth authorization URL")
    redirect_uri: str = Field(..., description="Configured redirect URI")
    state: Optional[str] = Field(None, description="State parameter for security")


class OAuthCallbackRequest(BaseModel):
    """Request model for OAuth callback handling."""
    code: str = Field(..., description="Authorization code from OAuth provider")
    state: Optional[str] = Field(None, description="State parameter from authorization request")
    error: Optional[str] = Field(None, description="Error from OAuth provider")
    error_description: Optional[str] = Field(None, description="Error description from OAuth provider")
