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

    STANDARD_ATTRS = {
        "args", "asctime", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelname", "levelno", "lineno", "module", "msecs",
        "message", "msg", "name", "pathname", "process", "processName",
        "relativeCreated", "stack_info", "thread", "threadName",
    }

    def format(self, record: logging.LogRecord) -> str:
        settings = get_settings()
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "severity": record.levelname,
            "service": "smiota-ai",
            "environment": getattr(settings, "ENVIRONMENT", "development"),
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "-"),
        }
        if hasattr(record, "event"):
            payload["event"] = record.event
        if hasattr(record, "duration_ms"):
            payload["duration_ms"] = record.duration_ms
        if hasattr(record, "error_type"):
            payload["error_type"] = record.error_type

        # Extract allowlisted structured extras
        for key, value in record.__dict__.items():
            if key not in self.STANDARD_ATTRS and key not in payload and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
            if "error_type" not in payload and record.exc_info[0]:
                payload["error_type"] = record.exc_info[0].__name__
        return json.dumps(payload)


def setup_logging() -> logging.Logger:
    """Configures structured logging for cloud-native GCP / Kubernetes environment."""
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO if not settings.DEBUG else logging.DEBUG)

    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

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

    # Mute noisy low-level third-party network & transport loggers
    for noisy in ("httpcore", "httpx", "urllib3", "google.auth", "google.api_core"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # File handler: write all application logs to logs/smiota.log
    try:
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        logs_dir = os.path.join(base_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(logs_dir, "smiota.log"), encoding="utf-8")
        file_handler.addFilter(CorrelationFilter())
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] [%(correlation_id)s] %(message)s")
        )
        root_logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"Warning: could not initialize file logger: {e}\n")

    logger = logging.getLogger("smiota")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()

