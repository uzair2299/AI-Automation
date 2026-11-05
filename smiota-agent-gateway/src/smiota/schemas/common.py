"""Common API response schemas, envelopes, and pagination models."""
from typing import Generic, TypeVar, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard unified response wrapper for all Smiota API endpoints."""
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ErrorResponse(BaseModel):
    """Standardized error envelope."""
    success: bool = False
    error_code: str
    message: str
    details: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaginationParams(BaseModel):
    """Query parameters for paginated listing."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated collection envelope."""
    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool
