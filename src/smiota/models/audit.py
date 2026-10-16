"""SQLAlchemy entity for comprehensive agent, tool, and safety audit trails."""
from typing import Optional, Any
from sqlalchemy import String, Text, JSON, Float, Index
from sqlalchemy.orm import Mapped, mapped_column

from smiota.models.base import Base, UUIDMixin, TimestampMixin


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """Stores full audit traces of user interactions, agent thoughts, and tool actions."""
    __tablename__ = "audit_logs"

    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)

    agent_name: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)

    tool_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    tool_params: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tool_output_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    remediation_approved_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_audit_tenant_session", "tenant_id", "session_id"),
    )
