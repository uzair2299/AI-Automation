"""Structured logging engine with correlation ID tracking and cloud JSON formatting."""
from contextvars import ContextVar
import json
import logging
import os
import sys
from typing import Optional, Sequence

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

    def __init__(self, service_name: str = "smiota", environment: str = "development"):
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "severity": record.levelname,
            "service": self.service_name,
            "environment": self.environment,
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


def setup_logging(
    service_name: str = "smiota",
    log_level: str = "INFO",
    environment: str = "development",
    log_file_path: Optional[str] = None,
    mute_loggers: Sequence[str] = ("httpcore", "httpx", "urllib3", "google.auth", "google.api_core"),
) -> logging.Logger:
    """Configures structured logging for cloud-native GCP / Kubernetes environment."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(CorrelationFilter())

    # Production uses machine-readable JSON for GCP/Datadog; Dev uses readable text
    if environment.lower() in ("prod", "production"):
        handler.setFormatter(CloudJSONFormatter(service_name=service_name, environment=environment))
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] [%(correlation_id)s] %(message)s")
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Mute noisy transport loggers
    for noisy in mute_loggers:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Optional file logger
    if log_file_path:
        try:
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.addFilter(CorrelationFilter())
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] [%(correlation_id)s] %(message)s")
            )
            root_logger.addHandler(file_handler)
        except Exception as e:
            sys.stderr.write(f"Warning: could not initialize file logger at {log_file_path}: {e}\n")

    logger = logging.getLogger(service_name)
    logger.setLevel(level)
    return logger

