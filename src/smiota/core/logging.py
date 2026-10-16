import json
import logging
import sys
from contextvars import ContextVar
from typing import Optional
from smiota.core.config import get_settings

# Async context variable for tracking correlation / request IDs across threads & coroutines
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class CorrelationFilter(logging.Filter):
    """Injects the active request/correlation ID into each log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_ctx.get() or "-"
        return True


class CloudJSONFormatter(logging.Formatter):
    """Google Cloud Logging & Datadog compliant structured JSON formatter."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging() -> logging.Logger:
    """Configures structured logging for cloud-native GCP / Kubernetes environment."""
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO if not settings.DEBUG else logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(CorrelationFilter())

    # Production uses machine-readable JSON for GCP Cloud Logging; Dev uses readable text
    if settings.ENVIRONMENT.lower() in ("prod", "production"):
        handler.setFormatter(CloudJSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] [%(correlation_id)s] %(message)s")
        )

    # Configure root and smiota loggers
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Remove any default handlers to avoid duplicate log entries
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    logger = logging.getLogger("smiota")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()

