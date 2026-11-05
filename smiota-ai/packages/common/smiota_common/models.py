"""Standardized API response models and contracts for Smiota AI microservices."""
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Detailed error object for structured API failure responses."""
    code: str = Field(default="INTERNAL_ERROR", description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    field: Optional[str] = Field(default=None, description="Request field that caused the error, if applicable")


class APIResponse(BaseModel, Generic[T]):
    """Standardized API Response Envelope used across all Smiota microservices."""
    data: Optional[T] = Field(default=None, description="Payload data returned by the endpoint")
    message: Optional[str] = Field(default=None, description="Informational message or operation summary")
    status: str = Field(default="success", description="'success' or 'error'")
    errors: Optional[List[ErrorDetail]] = Field(default=None, description="Optional list of error details")

