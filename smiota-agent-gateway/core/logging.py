"""Logging infrastructure for Smiota AI Platform."""
import logging
import os
from typing import Optional

from core.config import get_settings
from smiota_common.logging import (
    CloudJSONFormatter,
    CorrelationFilter,
    correlation_id_ctx,
    setup_logging as common_setup_logging,
)


def setup_logging() -> logging.Logger:
    """Configures structured logging for cloud-native GCP / Kubernetes environment."""
    settings = get_settings()
    environment = getattr(settings, "ENVIRONMENT", "development")
    log_level_str = settings.LOG_LEVEL if not settings.DEBUG else "DEBUG"

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    log_file_path = os.path.join(base_dir, "logs", "smiota.log")

    return common_setup_logging(
        service_name="smiota",
        log_level=log_level_str,
        environment=environment,
        log_file_path=log_file_path,
    )


logger = setup_logging()

__all__ = [
    "CloudJSONFormatter",
    "CorrelationFilter",
    "correlation_id_ctx",
    "logger",
    "setup_logging",
]
