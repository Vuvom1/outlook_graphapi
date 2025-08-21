"""
Common schemas used across the Outlook service API.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class StatusEnum(str, Enum):
    """API response status enumeration."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class BaseResponse(BaseModel):
    """Base response model for all API responses."""

    status: StatusEnum = StatusEnum.SUCCESS
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    message: Any | None = None


class ErrorResponse(BaseResponse):
    """Error response model."""

    status: StatusEnum = StatusEnum.ERROR
    error_code: str | None = None
    error_details: dict[str, Any] | None = None


class PaginationRequest(BaseModel):
    """Request model for pagination parameters."""

    limit: int = Field(default=20, ge=1, le=100, description="Number of items to retrieve (1-100)")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class PaginationResponse(BaseModel):
    """Response model for paginated results."""

    total_count: int = Field(description="Total number of items")
    has_more: bool = Field(description="Whether there are more items available")
    limit: int = Field(description="Number of items requested")
    offset: int = Field(description="Number of items skipped")


class HealthResponse(BaseModel):
    """Health check response model."""

    service: str
    status: str
    timestamp: str
    version: str
    components: dict[str, str]
    configuration: dict[str, Any] | None = None
    endpoints: dict[str, str] | None = None
