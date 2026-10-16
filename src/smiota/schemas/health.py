"""Schemas for deep system health checks and readiness probes."""
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ComponentHealth(BaseModel):
    status: str  # healthy, degraded, unavailable
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class SystemHealthResponse(BaseModel):
    status: str  # ok, degraded, error
    version: str = "0.1.0"
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    components: dict[str, ComponentHealth] = Field(default_factory=dict)
