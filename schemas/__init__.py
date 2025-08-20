"""
Schemas package for the Outlook service.
Contains Pydantic models for request/response validation.
"""

from .email_schemas import *
from .oauth_schemas import *
from .common_schemas import *

__all__ = [
    # Email schemas
    "EmailRequest",
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
    "PaginationRequest",
    "PaginationResponse"
]
