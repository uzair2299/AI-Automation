"""SQLAlchemy entities for conversational sessions and multi-turn message history."""
from typing import Optional, Any
from sqlalchemy import String, Text, JSON, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from smiota.models.base import Base, UUIDMixin, TimestampMixin


class ChatSession(Base, UUIDMixin, TimestampMixin):
    """Represents a conversational session originating from Teams, WebChat, or IDE."""
    __tablename__ = "chat_sessions"

    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    current_agent: Mapped[str] = mapped_column(String(64), default="aiops", nullable=False)
    session_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    __table_args__ = (
        Index("ix_chat_sessions_tenant_user", "tenant_id", "user_id"),
    )


class ChatMessage(Base, UUIDMixin, TimestampMixin):
    """Represents an individual message (user, assistant, tool, system) in a session."""
    __tablename__ = "chat_messages"

    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # user, assistant, system, tool
    content: Mapped[str] = mapped_column(Text, nullable=False)
    agent_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    tool_calls: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
