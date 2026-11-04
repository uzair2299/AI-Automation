"""Structured logging and correlation ID tracking for RAG Service."""
import json
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

try:
    from app.config import settings
except ImportError:
    from .config import settings

# Async context variable for tracking correlation / request IDs across threads & coroutines
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class CorrelationFilter(logging.Filter):
    """Injects the active request/correlation ID into each log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_ctx.get() or "-"
        return True


class CloudJSONFormatter(logging.Formatter):
    """Google Cloud Logging & Datadog compliant structured JSON formatter."""

    STANDARD_ATTRS = {
        "args", "asctime", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelname", "levelno", "lineno", "module", "msecs",
        "message", "msg", "name", "pathname", "process", "processName",
        "relativeCreated", "stack_info", "thread", "threadName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "severity": record.levelname,
            "service": getattr(settings, "SERVICE_NAME", "smiota-rag-service"),
            "environment": getattr(settings, "ENVIRONMENT", "development"),
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
            if record.exc_info[0]:
                payload["error_type"] = record.exc_info[0].__name__
        return json.dumps(payload)


def setup_logging() -> logging.Logger:
    """Configures structured logging for RAG microservice."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO if not settings.DEBUG else logging.DEBUG)

    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(CorrelationFilter())

    # Production uses machine-readable JSON for Cloud Logging; Dev uses readable text
    if getattr(settings, "ENVIRONMENT", "development").lower() in ("prod", "production"):
        handler.setFormatter(CloudJSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] [%(correlation_id)s] %(message)s")
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Mute noisy transport loggers
    for noisy in ("httpcore", "httpx", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    service_logger = logging.getLogger("rag-service")
    service_logger.setLevel(log_level)
    return service_logger


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Ensures every HTTP request has an X-Correlation-ID header for logging and tracing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or f"rag-{uuid.uuid4().hex[:12]}"
        request.state.correlation_id = correlation_id
        token = correlation_id_ctx.set(correlation_id)

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            correlation_id_ctx.reset(token)
