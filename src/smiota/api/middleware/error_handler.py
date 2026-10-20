"""Global exception handling middleware converting domain errors to JSON responses."""
from fastapi import Request
from fastapi.responses import JSONResponse
from smiota.core.logging import logger
from smiota.core.exceptions import (
    SmiotaException,
    PromptInjectionDetectedError,
    RemediationApprovalRequiredError,
    AgentNotFoundError,
    ResourceNotFoundError,
    AuthorizationError,
    AuthenticationError,
    BackendServiceUnavailableError,
)


async def smiota_exception_handler(request: Request, exc: SmiotaException) -> JSONResponse:
    """Handle custom Smiota exceptions with appropriate HTTP status codes."""
    status_code = 500

    if isinstance(exc, AuthenticationError):
        status_code = 401
        error_code = "AUTHENTICATION_FAILED"
    elif isinstance(exc, BackendServiceUnavailableError):
        status_code = 503
        error_code = "BACKEND_UNAVAILABLE"
    elif isinstance(exc, PromptInjectionDetectedError):
        status_code = 400
        error_code = "SAFETY_GUARDRAIL_VIOLATION"
    elif isinstance(exc, RemediationApprovalRequiredError):
        status_code = 403
        error_code = "APPROVAL_REQUIRED"
    elif isinstance(exc, AgentNotFoundError):
        status_code = 404
        error_code = "AGENT_NOT_FOUND"
    elif isinstance(exc, ResourceNotFoundError):
        status_code = 404
        error_code = "RESOURCE_NOT_FOUND"
    elif isinstance(exc, AuthorizationError):
        status_code = 403
        error_code = "FORBIDDEN"
    else:
        error_code = "INTERNAL_SERVER_ERROR"

    logger.warning(f"Handled {exc.__class__.__name__}: {exc.message} (status: {status_code})")

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error_code": error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )
