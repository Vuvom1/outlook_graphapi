"""
Schemas package for the Outlook service.
Contains Pydantic models for request/response validation.
"""

from .common_schemas import (
    BaseResponse,
    ErrorResponse,
)
from .email_schemas import (
    AttachmentRequest,
    CreateDraftRequest,
    EmailListResponse,
    EmailResponse,
    SendEmailRequest,
    UpdateEmailRequest,
)
from .oauth_schemas import (
    OAuthTokenRequest,
    OAuthTokenResponse,
    RefreshTokenRequest,
    ValidateTokenRequest,
    ValidateTokenResponse,
)

__all__ = [
    # Email schemas
    "EmailResponse",
    "EmailListResponse",
    "SendEmailRequest",
    "CreateDraftRequest",
    "UpdateEmailRequest",
    "AttachmentRequest",
    "EmailRecipient",
    "EmailBody",
    "EmailAttachment",
    # OAuth schemas
    "OAuthTokenRequest",
    "OAuthTokenResponse",
    "RefreshTokenRequest",
    "ValidateTokenRequest",
    "ValidateTokenResponse",
    # Common schemas
    "BaseResponse",
    "ErrorResponse",
]
