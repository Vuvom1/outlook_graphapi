"""
Email-related schemas for the Outlook service API.
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Any, Dict
from enum import Enum
from .common_schemas import BaseResponse, PaginationRequest, PaginationResponse


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
    name: Optional[str] = None
    email: EmailStr


class EmailBody(BaseModel):
    """Email body content model."""
    content: str
    content_type: BodyType = BodyType.TEXT


class EmailAttachment(BaseModel):
    """Email attachment model."""
    name: str
    content_type: Optional[str] = None
    size: Optional[int] = None
    content: Optional[str] = None  # Base64 encoded content

class ListEmailsResponse(BaseResponse):
    """Response model for listing emails."""
    emails: List[Any] = Field(..., description="List of emails")

class SendEmailRequest(BaseModel):
    """Request model for sending emails."""
    to: List[EmailStr] = Field(..., description="List of recipient email addresses")
    cc: Optional[List[EmailStr]] = Field(None, description="List of CC recipient email addresses")
    bcc: Optional[List[EmailStr]] = Field(None, description="List of BCC recipient email addresses")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Content of the email message")
    body_type: BodyType = Field(BodyType.TEXT, description="Content type of the body")
    importance: ImportanceLevel = Field(ImportanceLevel.NORMAL, description="Importance level of the email")

    @validator('to', 'cc', 'bcc')
    def validate_recipients(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v

class GetEmailResponse(BaseResponse):
    """Response model for getting a single email."""
    email: Any = Field(..., description="Email details")


class CreateDraftRequest(SendEmailRequest):
    """Request model for creating draft emails."""
    pass


class UpdateEmailRequest(BaseModel):
    """Request model for updating emails."""
    subject: Optional[str] = Field(None, description="New subject for the email")
    body_content: Optional[str] = Field(None, description="New body content for the email")
    body_type: BodyType = Field(BodyType.TEXT, description="Content type of the body")
    importance: Optional[ImportanceLevel] = Field(None, description="Importance level of the email")


class AttachmentRequest(BaseModel):
    """Request model for adding attachments."""
    file_name: str = Field(..., description="Name of the attachment file")
    file_content: str = Field(..., description="Base64 encoded file content")
    content_type: Optional[str] = Field(None, description="MIME type of the file")


class PrioritizeEmailRequest(BaseModel):
    """Request model for prioritizing emails."""
    priority_level: ImportanceLevel = Field(ImportanceLevel.NORMAL, description="Priority level")


# Response Models
class EmailDetail(BaseModel):
    """Detailed email model."""
    id: str
    subject: Optional[str] = None
    sender: Optional[EmailRecipient] = None
    to_recipients: List[EmailRecipient] = []
    cc_recipients: List[EmailRecipient] = []
    bcc_recipients: List[EmailRecipient] = []
    received_datetime: Optional[str] = None
    sent_datetime: Optional[str] = None
    body_preview: Optional[str] = None
    body: Optional[EmailBody] = None
    is_read: bool = False
    has_attachments: bool = False
    importance: ImportanceLevel = ImportanceLevel.NORMAL
    conversation_id: Optional[str] = None
    attachments: List[EmailAttachment] = []


class EmailListResponse(BaseResponse):
    """Response model for email list."""
    emails: List[EmailDetail]
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
    email_id: str
    updated_at: str
    updated_fields: List[str]


class AttachmentResponse(BaseResponse):
    """Response model for attachment operations."""
    attachment_id: Optional[str] = None
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
    folders: List[FolderInfo]
    count: int
