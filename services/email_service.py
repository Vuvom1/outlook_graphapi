"""
Email service for handling Microsoft Graph API operations.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from schemas.email_schemas import (
    SendEmailRequest, CreateDraftRequest,
    UpdateEmailRequest, AttachmentRequest, ImportanceLevel
)

logger = logging.getLogger(__name__)


class EmailService:
    """Service class for email operations using Microsoft Graph API."""
    
    def __init__(self):
        self.base_url = "https://graph.microsoft.com/v1.0"
    
    async def list_emails(self, access_token: str, limit: int, offset: int, folder: str, search: Optional[str], include_body: bool) -> Dict[str, Any]:
        """List emails from the specified folder with filtering."""
        try:
            # Import here to avoid circular imports
            from tools.list_message import list_message_tool
            
            # Convert request to tool parameters
            tool_parameters = {
                "limit": limit,
                "offset": offset,
                "folder": folder,
                "search": search,
                "include_body": include_body,
                "access_token": access_token
            }
            
            # Call the existing tool
            result = list_message_tool.invoke(tool_parameters=tool_parameters)

            logger.info(f"Listed emails from folder: {folder}")

            return result
            
        except Exception as e:
            logger.error(f"Failed to list emails: {e}")
            raise
    
    async def get_email_by_id(self, access_token: str, message_id: str) -> Dict[str, Any]:
        """Get a specific email by its ID."""
        try:
            from tools.get_message import get_message_tool
            
            tool_parameters = {
                "message_id": message_id,
                "access_token": access_token
            }
            
            result = get_message_tool.invoke(tool_parameters=tool_parameters)
            
            logger.info(f"Retrieved email with ID: {message_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get email {message_id}: {e}")
            raise
    
    async def send_email(self, access_token: str, request: SendEmailRequest) -> Dict[str, Any]:
        """Send an email."""
        try:
            from tools.send_message import send_message_tool
            
            # Convert recipients list to comma-separated string
            to_recipients = ",".join(request.to)
            
            tool_parameters = {
                "to": to_recipients,
                "subject": request.subject,
                "message": request.body,
                "access_token": access_token
            }
            
            result = send_message_tool.invoke(tool_parameters=tool_parameters)
            
            logger.info(f"Sent email to {len(request.to)} recipients")
            return result

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise
    
    async def create_draft(self, access_token: str, request: CreateDraftRequest) -> Dict[str, Any]:
        """Create a draft email."""
        try:
            from tools.draft_message import draft_email_tool

            tool_parameters = {
                "subject": request.subject,
                "body": request.body,
                "to_recipients": request.to,
                "cc_recipients": request.cc,
                "bcc_recipients": request.bcc,
                "importance": request.importance.value,
                "access_token": access_token
            }

            result = draft_email_tool.invoke(tool_parameters=tool_parameters)

            return {
                "result": result,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as e:
            logger.error(f"Failed to create draft: {e}")
            raise
    
    async def update_email(self, access_token: str, email_id: str, request: UpdateEmailRequest) -> Dict[str, Any]:
        """Update an existing email."""
        try:
            from tools.update_message import update_message_tool
            
            tool_parameters = {
                "email_id": email_id,
                "subject": request.subject,
                "body_content": request.body_content,
                "body_type": request.body_type.value,
                "access_token": access_token
            }
            
            result = update_message_tool.invoke(tool_parameters=tool_parameters)
            
            # Track updated fields
            updated_fields = []
            if request.subject is not None:
                updated_fields.append("subject")
            if request.body_content is not None:
                updated_fields.append("body")
            if request.importance is not None:
                updated_fields.append("importance")
            
            logger.info(f"Updated email {email_id}")
            return {
                "result": result,
                "updated_fields": updated_fields,
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as e:
            logger.error(f"Failed to update email {email_id}: {e}")
            raise
    
    async def add_attachment_to_draft(self, access_token: str, draft_id: str, request: AttachmentRequest) -> Dict[str, Any]:
        """Add attachment to a draft email."""
        try:
            from tools.add_attachment_to_draft import add_attachment_to_draft_tool
            
            tool_parameters = {
                "draft_id": draft_id,
                "file_to_attach": [request.file_content],
                "attachment_name": request.file_name,
                "access_token": access_token
            }
            
            result = add_attachment_to_draft_tool.invoke(tool_parameters=tool_parameters)
            
            logger.info(f"Added attachment to draft {draft_id}")
            return {
                "result": result,
                "attachment_name": request.file_name,
                "operation": "added"
            }
            
        except Exception as e:
            logger.error(f"Failed to add attachment to draft {draft_id}: {e}")
            raise
    
    async def send_draft(self, access_token: str, draft_id: str) -> Dict[str, Any]:
        """Send a draft email."""
        try:
            from tools.send_draft import send_draft_tool
            
            tool_parameters = {
                "draft_id": draft_id,
                "access_token": access_token
            }
            
            result = send_draft_tool.invoke(tool_parameters=tool_parameters)
            
            logger.info(f"Sent draft email {draft_id}")
            return {
                "result": result,
                "sent_at": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as e:
            logger.error(f"Failed to send draft {draft_id}: {e}")
            raise
    
    async def prioritize_email(self, access_token: str, email_id: str, priority_level: ImportanceLevel) -> Dict[str, Any]:
        """Set the priority/importance level of an email."""
        try:
            from tools.prioritize_message_tool import prioritize_email_tool
            
            tool_parameters = {
                "email_id": email_id,
                "priority_level": priority_level.value,
                "access_token": access_token
            }
            
            result = prioritize_email_tool.invoke(tool_parameters=tool_parameters)
            
            logger.info(f"Set priority for email {email_id} to {priority_level.value}")
            return {
                "result": result,
                "priority_level": priority_level.value,
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as e:
            logger.error(f"Failed to prioritize email {email_id}: {e}")
            raise

    async def delete_email(self, access_token: str, message_id: str) -> Dict[str, Any]:
        """Delete an email by its ID."""
        try:
            from tools.delete_message import delete_message_tool
            
            tool_parameters = {
                "message_id": message_id,
                "access_token": access_token
            }
            
            result = delete_message_tool.invoke(tool_parameters=tool_parameters)
            
            logger.info(f"Deleted email with ID: {message_id}")
            return {
                "result": result,
                "deleted_at": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete email {message_id}: {e}")
            raise

email_service = EmailService()  