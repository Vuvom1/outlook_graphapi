"""
Email operations router for Outlook service.
Provides endpoints for reading, sending, and managing emails through Microsoft Graph API.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request

from schemas.common_schemas import BaseResponse
from schemas.email_schemas import (
    AttachmentRequest,
    AttachmentResponse,
    CreateDraftRequest,
    CreateDraftResponse,
    EmailResponse,
    ListEmailsResponse,
    PrioritizeEmailRequest,
    SendEmailRequest,
    SendEmailResponse,
    UpdateEmailRequest,
    UpdateEmailResponse,
)
from services.email_service import EmailService
from auth.dependencies import require_oauth_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router and service
email_router = APIRouter(prefix="/emails", tags=["Email Operations"])
email_service = EmailService()


# Dependency to extract and validate access token
async def get_access_token(authorization: str = Header(..., alias="Authorization")):
    """Extract and validate access token from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format. Use 'Bearer <token>'")

    token = authorization.replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Access token is required")

    return token


@email_router.get("/list", summary="List Emails")
async def list_emails(
    request: Request,
    limit: int = Query(10, ge=1, le=100, description="Number of emails to retrieve (1-100)"),
    offset: int = Query(0, ge=0, description="Number of emails to skip"),
    folder: str = Query("inbox", description="Email folder to read from"),
    search: str | None = Query(None, description="Search query for filtering emails"),
    include_body: bool = Query(False, description="Whether to include email body in the response"),
    access_token: str = Depends(require_oauth_token),
) -> ListEmailsResponse:
    """
    List emails from Outlook using Microsoft Graph API.
    """
    try:
        result = await email_service.list_emails(
            access_token=access_token,
            limit=limit,
            offset=offset,
            folder=folder,
            search=search,
            include_body=include_body,
        )

        return ListEmailsResponse(message="Emails retrieved successfully", emails=result)

    except Exception as e:
        logger.error(f"Error listing emails: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list emails: {str(e)}")


@email_router.get("/{message_id}", summary="Get Email by ID")
async def get_email_by_id(message_id: str, access_token: str = Depends(get_access_token)) -> EmailResponse:
    """
    Get a specific email by its ID.
    """
    try:
        result = await email_service.get_email_by_id(access_token, message_id)

        return EmailResponse(message="Email retrieved successfully", email=result)

    except Exception as e:
        logger.error(f"Error getting email {message_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get email: {str(e)}")


@email_router.post("/send", summary="Send Email")
async def send_email(request: SendEmailRequest, access_token: str = Depends(get_access_token)) -> SendEmailResponse:
    """
    Send an email through Outlook using Microsoft Graph API.
    """
    try:
        result = await email_service.send_email(access_token, request)

        return SendEmailResponse(
            message="Email sent successfully", sent_at=result["sent_at"], recipients=result["recipients"]
        )

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@email_router.post("/drafts", summary="Create Draft Email")
async def create_draft_email(
    request: CreateDraftRequest, access_token: str = Depends(get_access_token)
) -> CreateDraftResponse:
    """
    Create a draft email in Outlook.
    """
    try:
        result = await email_service.create_draft(access_token, request)

        return CreateDraftResponse(
            message="Draft created successfully", draft_id=result["result"], created_at=result["created_at"]
        )

    except Exception as e:
        logger.error(f"Error creating draft: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create draft: {str(e)}")


@email_router.patch("/{email_id}", summary="Update Email")
async def update_email(
    email_id: str, request: UpdateEmailRequest, access_token: str = Depends(get_access_token)
) -> UpdateEmailResponse:
    """
    Update an existing email's subject and/or body.
    """
    try:
        result = await email_service.update_email(access_token, email_id, request)

        return UpdateEmailResponse(
            message=result["result"],
            updated_at=result["updated_at"],
        )

    except Exception as e:
        logger.error(f"Error updating email {email_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update email: {str(e)}")


@email_router.post("/drafts/{draft_id}/attachments", summary="Add Attachment to Draft")
async def add_attachment_to_draft(
    draft_id: str, request: AttachmentRequest, access_token: str = Depends(get_access_token)
) -> AttachmentResponse:
    """
    Add attachments to an existing draft email.
    """
    try:
        result = await email_service.add_attachment_to_draft(access_token, draft_id, request)

        return AttachmentResponse(
            message="Attachment added successfully",
            attachment_name=result["attachment_name"],
            operation=result["operation"],
        )

    except Exception as e:
        logger.error(f"Error adding attachment to draft {draft_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add attachment: {str(e)}")


@email_router.post("/drafts/{draft_id}/send", summary="Send Draft Email")
async def send_draft_email(draft_id: str, access_token: str = Depends(get_access_token)) -> BaseResponse:
    """
    Send a draft email through Outlook.
    """
    try:
        await email_service.send_draft(access_token, draft_id)

        return BaseResponse(message="Draft sent successfully")

    except Exception as e:
        logger.error(f"Error sending draft {draft_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send draft: {str(e)}")


@email_router.patch("/{email_id}/priority", summary="Set Email Priority")
async def prioritize_email(
    email_id: str, request: PrioritizeEmailRequest, access_token: str = Depends(get_access_token)
) -> BaseResponse:
    """
    Set the priority/importance level of an email.
    """
    try:
        await email_service.prioritize_email(access_token, email_id, request.priority_level)

        return BaseResponse(message=f"Email priority set to {request.priority_level.value}")

    except Exception as e:
        logger.error(f"Error prioritizing email {email_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to prioritize email: {str(e)}")


@email_router.patch("/{email_id}/read", summary="Mark Email as Read/Unread")
async def mark_email_read(
    email_id: str,
    is_read: bool = Query(True, description="Mark as read (true) or unread (false)"),
    access_token: str = Depends(get_access_token),
) -> BaseResponse:
    """
    Mark an email as read or unread.
    """
    try:
        await email_service.mark_email_read(access_token, email_id, is_read)

        status = "read" if is_read else "unread"
        return BaseResponse(message=f"Email marked as {status}")

    except Exception as e:
        logger.error(f"Error marking email {email_id} as read: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update email read status: {str(e)}")


@email_router.delete("/{email_id}", summary="Delete Email")
async def delete_email(email_id: str, access_token: str = Depends(get_access_token)) -> BaseResponse:
    """
    Delete an email (move to Deleted Items folder).
    """
    try:
        result = await email_service.delete_email(access_token, email_id)

        return BaseResponse(
            message=result["result"],
            timestamp=result["deleted_at"],
        )

    except Exception as e:
        logger.error(f"Error deleting email {email_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete email: {str(e)}")


@email_router.get("/folders/list", summary="List Mail Folders")
async def list_folders(access_token: str = Depends(get_access_token)) -> BaseResponse:
    """
    Get list of all mail folders.
    """
    try:
        result = await email_service.list_folders(access_token)

        return BaseResponse(message="Folders retrieved successfully", **result)

    except Exception as e:
        logger.error(f"Error listing folders: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list folders: {str(e)}")


# Legacy endpoints for backward compatibility (deprecated)
@email_router.get("/list-message", summary="Read Emails (Legacy)", deprecated=True)
async def list_emails_legacy(
    limit: int = Query(10, ge=1, le=100, description="Number of emails to retrieve (1-100)"),
    offset: int = Query(0, ge=0, description="Number of emails to skip"),
    folder: str = Query("inbox", description="Email folder to read from"),
    search: str | None = Query(None, description="Search query for filtering emails"),
    include_body: bool = Query(False, description="Whether to include email body in the response"),
    access_token: str = Header(..., description="OAuth access token for Microsoft Graph API"),
) -> dict:
    """Legacy endpoint for listing emails. Use /emails/list instead."""
    try:
        result = await email_service.list_emails(access_token, limit, offset, folder, search, include_body)

        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "emails": result.get("emails", []),
        }

    except Exception as e:
        logger.error(f"Error listing emails (legacy): {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list emails: {str(e)}")


@email_router.get("/get-message", summary="Get Email by ID (Legacy)", deprecated=True)
async def get_email_by_id_legacy(
    message_id: str = Query(..., description="ID of the email to retrieve"),
    access_token: str = Header(..., description="OAuth access token for Microsoft Graph API"),
) -> dict:
    """Legacy endpoint for getting email by ID. Use /emails/{message_id} instead."""
    try:
        result = await email_service.get_email_by_id(access_token, message_id)

        return {"status": "success", "timestamp": datetime.utcnow().isoformat() + "Z", "email": result}

    except Exception as e:
        logger.error(f"Error getting email (legacy): {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get email: {str(e)}")


@email_router.post("/send-message", summary="Send Email (Legacy)", deprecated=True)
async def send_email_legacy(
    to: str = Query(..., description="Comma-separated list of recipient email addresses"),
    subject: str = Query(..., description="Subject of the email"),
    message: str = Query(..., description="Content of the email message"),
    access_token: str = Header(..., description="OAuth access token for Microsoft Graph API"),
) -> dict:
    """Legacy endpoint for sending email. Use /emails/send instead."""
    try:
        request = SendEmailRequest(to=to.split(","), subject=subject, body=message)

        result = await email_service.send_email(access_token, request)

        return {"status": "success", "timestamp": datetime.utcnow().isoformat() + "Z", "result": result}

    except Exception as e:
        logger.error(f"Error sending email (legacy): {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
