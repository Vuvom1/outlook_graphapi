"""
Email-related schemas for the Outlook service API.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from .common_schemas import BaseResponse, PaginationResponse


class ImportanceLevel(str, Enum):
    """Email importance/priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class BodyType(str, Enum):
    """Email body content types."""

    TEXT = "text"
    HTML = "html"


class EmailRecipient(BaseModel):
    """Email recipient model."""

    name: str | None = None
    email: EmailStr


class EmailBody(BaseModel):
    """Email body content model."""

    content: str
    content_type: BodyType = BodyType.TEXT


class EmailAttachment(BaseModel):
    """Email attachment model."""

    name: str
    content_type: str | None = None
    size: int | None = None
    content: str | None = None  # Base64 encoded content


class ListEmailsResponse(BaseResponse):
    """Response model for listing emails."""

    emails: list[Any] = Field(..., description="List of emails")


class SendEmailRequest(BaseModel):
    """Request model for sending emails."""

    to: str = Field(..., description="Comma-separated list of recipient email addresses")
    cc: str | None | None = Field(None, description="Comma-separated list of CC recipient email addresses")
    bcc: str | None | None = Field(None, description="Comma-separated list of BCC recipient email addresses")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Content of the email message")
    body_type: BodyType = Field(BodyType.TEXT, description="Content type of the body")
    importance: ImportanceLevel = Field(ImportanceLevel.NORMAL, description="Importance level of the email")


class GetEmailResponse(BaseResponse):
    """Response model for getting a single email."""

    email: Any = Field(..., description="Email details")


class CreateDraftRequest(SendEmailRequest):
    """Request model for creating draft emails."""

    pass


class UpdateEmailRequest(BaseModel):
    """Request model for updating emails."""

    subject: str | None = Field(None, description="New subject for the email")
    body_content: str | None = Field(None, description="New body content for the email")
    body_type: BodyType = Field(BodyType.TEXT, description="Content type of the body")
    importance: ImportanceLevel | None = Field(None, description="Importance level of the email")


class AttachmentRequest(BaseModel):
    """Request model for adding attachments."""

    file_name: str = Field(..., description="Name of the attachment file")
    file_content: str = Field(..., description="Base64 encoded file content")
    content_type: str | None = Field(None, description="MIME type of the file")


class PrioritizeEmailRequest(BaseModel):
    """Request model for prioritizing emails."""

    priority_level: ImportanceLevel = Field(ImportanceLevel.NORMAL, description="Priority level")


# Response Models
class EmailDetail(BaseModel):
    """Detailed email model."""

    id: str
    subject: str | None = None
    sender: EmailRecipient | None = None
    to_recipients: list[EmailRecipient] = []
    cc_recipients: list[EmailRecipient] = []
    bcc_recipients: list[EmailRecipient] = []
    received_datetime: str | None = None
    sent_datetime: str | None = None
    body_preview: str | None = None
    body: EmailBody | None = None
    is_read: bool = False
    has_attachments: bool = False
    importance: ImportanceLevel = ImportanceLevel.NORMAL
    conversation_id: str | None = None
    attachments: list[EmailAttachment] = []


class EmailListResponse(BaseResponse):
    """Response model for email list."""

    emails: list[EmailDetail]
    pagination: PaginationResponse
    folder: str


class EmailResponse(BaseResponse):
    """Response model for single email."""

    email: Any = Field(..., description="Email details")


class SendEmailResponse(BaseResponse):
    """Response model for send email operation."""

    sent_at: str = Field(..., description="Timestamp when email was sent")
    recipients: dict = Field(..., description="Recipients information")


class CreateDraftResponse(BaseResponse):
    """Response model for create draft operation."""

    draft_id: str = Field(..., description="ID of the created draft")
    created_at: str = Field(..., description="Timestamp when draft was created")


class UpdateEmailResponse(BaseResponse):
    """Response model for update email operation."""

    message: str
    updated_at: str


class AttachmentResponse(BaseResponse):
    """Response model for attachment operations."""

    attachment_id: str | None = None
    attachment_name: str
    operation: str  # 'added', 'removed', 'updated'


class FolderInfo(BaseModel):
    """Mail folder information model."""

    id: str
    display_name: str
    total_item_count: int
    unread_item_count: int
    child_folder_count: int


class FoldersResponse(BaseResponse):
    """Response model for folders list."""

    folders: list[FolderInfo]
    count: int
