"""Structured logging and correlation ID tracking for RAG Service."""
from smiota_common.logging import (
    CloudJSONFormatter,
    CorrelationFilter,
    correlation_id_ctx,
    setup_logging as common_setup_logging,
)
from smiota_common.middleware import CorrelationIdMiddleware

from app.core.config import settings


def setup_logging():
    """Configures structured logging for RAG microservice."""
    return common_setup_logging(
        service_name=getattr(settings, "SERVICE_NAME", "smiota-rag-service"),
        log_level=getattr(settings, "LOG_LEVEL", "INFO"),
        environment=getattr(settings, "ENVIRONMENT", "development"),
    )


__all__ = [
    "CloudJSONFormatter",
    "CorrelationFilter",
    "CorrelationIdMiddleware",
    "correlation_id_ctx",
    "setup_logging",
]

