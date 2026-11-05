"""Enterprise exception hierarchy for Smiota AI microservices."""
from typing import Any, Optional


class SmiotaException(Exception):
    """Base exception for all domain errors within Smiota AI microservices."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        self.error_code = error_code


class ServiceUnavailableError(SmiotaException):
    """Raised when an internal upstream service is unreachable or times out."""

    def __init__(self, service_name: str, message: Optional[str] = None):
        msg = message or f"Service '{service_name}' is currently unavailable."
        super().__init__(message=msg, details={"service": service_name}, status_code=503, error_code="SERVICE_UNAVAILABLE")


class ResourceNotFoundError(SmiotaException):
    """Raised when an entity or resource is not found."""

    def __init__(self, resource: str, resource_id: Optional[str] = None):
        msg = f"Resource '{resource}'" + (f" with id '{resource_id}'" if resource_id else "") + " was not found."
        super().__init__(message=msg, details={"resource": resource, "id": resource_id}, status_code=404, error_code="NOT_FOUND")


class AuthenticationError(SmiotaException):
    """Raised on authentication or token failure."""

    def __init__(self, message: str = "Authentication required or invalid credentials."):
        super().__init__(message=message, status_code=401, error_code="UNAUTHENTICATED")


class AuthorizationError(SmiotaException):
    """Raised when user or service lacks permissions."""

    def __init__(self, message: str = "Forbidden: insufficient permissions for this operation."):
        super().__init__(message=message, status_code=403, error_code="PERMISSION_DENIED")

