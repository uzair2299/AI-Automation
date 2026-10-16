"""SQLAlchemy entity for Human-in-the-Loop (HITL) remediation approvals."""
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, Text, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from smiota.models.base import Base, UUIDMixin, TimestampMixin


class RemediationApproval(Base, UUIDMixin, TimestampMixin):
    """Tracks required human approvals for high-impact infrastructure remediation."""
    __tablename__ = "remediation_approvals"

    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    requested_by_user_id: Mapped[str] = mapped_column(String(64), nullable=False)

    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(32), default="pending", index=True, nullable=False)
    decision_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_by_user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    execution_result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_approvals_tenant_status", "tenant_id", "status"),
    )
