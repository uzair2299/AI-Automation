"""Observability & Telemetry instrumentation (OpenTelemetry & Prometheus)."""
from fastapi import FastAPI


def setup_telemetry(app: FastAPI) -> None:
    """Instruments the FastAPI application with OpenTelemetry tracing and Prometheus metrics.

    In production, this exports traces to GCP Cloud Trace and exposes /metrics for Prometheus.
    """
    # Placeholder for OpenTelemetry SDK initialization
    pass
