"""Smiota Common Foundation Library."""

from smiota_common.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    SmiotaException,
)
from smiota_common.logging import (
    CloudJSONFormatter,
    CorrelationFilter,
    correlation_id_ctx,
    setup_logging,
)
from smiota_common.middleware import CorrelationIdMiddleware
from smiota_common.models import APIResponse, ErrorDetail

__all__ = [
    "APIResponse",
    "AuthenticationError",
    "AuthorizationError",
    "CloudJSONFormatter",
    "CorrelationFilter",
    "CorrelationIdMiddleware",
    "ErrorDetail",
    "ResourceNotFoundError",
    "ServiceUnavailableError",
    "SmiotaException",
    "correlation_id_ctx",
    "setup_logging",
]
