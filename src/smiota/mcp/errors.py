"""Normalized error classes for Smiota MCP tools and API client integration."""
from typing import Any, Optional
from smiota.core.exceptions import SmiotaException


class SmiotaMcpError(SmiotaException):
    """Base error for Smiota MCP tool execution."""
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, details=details)
        self.error_code = error_code


class McpAuthenticationRequiredError(SmiotaMcpError):
    """Raised when an unauthenticated guest attempts to access protected customer data."""
    def __init__(self, message: str = "Authentication required. Please log in to your Smiota account.", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, error_code="AUTHENTICATION_REQUIRED", details=details)


class McpAccessDeniedError(SmiotaMcpError):
    """Raised when caller lacks permission or attempts cross-tenant access."""
    def __init__(self, message: str = "Access denied. Caller is not authorized for the requested tenant or customer record.", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, error_code="ACCESS_DENIED", details=details)


class McpInvalidInputError(SmiotaMcpError):
    """Raised when tool arguments fail validation or are missing."""
    def __init__(self, message: str, missing_fields: Optional[list[str]] = None, details: Optional[dict[str, Any]] = None):
        det = dict(details or {})
        if missing_fields:
            det["missing_fields"] = missing_fields
        super().__init__(message=message, error_code="INVALID_INPUT", details=det)
        self.missing_fields = missing_fields or []


class McpInvalidIdentifierError(SmiotaMcpError):
    """Raised when a package tracking number, UUID, or identifier format is invalid."""
    def __init__(self, message: str = "Invalid identifier format.", identifier: Optional[str] = None):
        details = {"identifier": identifier} if identifier else {}
        super().__init__(message=message, error_code="INVALID_IDENTIFIER", details=details)


class McpUpstreamNotFoundError(SmiotaMcpError):
    """Raised when upstream API returns 404 (package or user not found)."""
    def __init__(self, message: str = "The requested package or record was not found.", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, error_code="NOT_FOUND", details=details)


class McpUpstreamRateLimitedError(SmiotaMcpError):
    """Raised when upstream API returns 429 Too Many Requests."""
    def __init__(self, message: str = "Upstream rate limit exceeded. Please retry shortly.", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message=message, error_code="RATE_LIMITED", details=details)
        self.retry_after = retry_after


class McpUpstreamTimeoutError(SmiotaMcpError):
    """Raised when upstream API times out."""
    def __init__(self, message: str = "Upstream service timed out. Please try again.", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, error_code="UPSTREAM_TIMEOUT", details=details)


class McpUpstreamServiceUnavailableError(SmiotaMcpError):
    """Raised when upstream API returns 502/503/504 or connection fails."""
    def __init__(self, message: str = "Smiota backend service is temporarily unavailable.", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, error_code="SERVICE_UNAVAILABLE", details=details)


class McpUnexpectedResponseError(SmiotaMcpError):
    """Raised when upstream returns non-JSON or unexpected schema."""
    def __init__(self, message: str = "Unexpected response from upstream service.", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, error_code="UNEXPECTED_RESPONSE", details=details)
