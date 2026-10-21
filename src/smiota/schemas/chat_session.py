"""Schemas for Chat Sessions, Messages, and Conversation History."""
from datetime import UTC, datetime
from typing import Any, Literal
import uuid

from pydantic import BaseModel, Field

MessageType = Literal[
    "text",           # Standard text or markdown message
    "card",           # Structured UI card (e.g., parcel pickup, locker info)
    "approval_gate",  # Security verification gate (e.g., remote door unlock)
    "quick_replies",  # Action suggestions or quick chips
]


class ChatMessage(BaseModel):
    """Normalized chat message representing a single turn in a conversation."""
    id: str = Field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:10]}", description="Unique message ID")
    session_id: str = Field(..., description="Parent session identifier")

    # Identity & Actor Attribution
    role: Literal["user", "assistant", "system"] = Field(
        ..., description="Role: 'user' (human resident), 'assistant' (AI agent), or 'system'"
    )
    sender_name: str | None = Field(
        None, description="Human-friendly name of the sender (e.g. 'Alex Morgan', 'Smiota Concierge')"
    )
    agent_name: str | None = Field(
        None, description="Specialized AI agent that generated the response (e.g. 'Customer', 'Security')"
    )

    # Content & UI Presentation Type
    message_type: MessageType = Field(
        "text", description="Display type: 'text', 'card', 'approval_gate', 'quick_replies'"
    )
    content: str = Field(
        ..., description="Human-readable text/markdown representation for LLM context and fallback display"
    )
    card_payload: dict[str, Any] | None = Field(
        None, description="Structured JSON payload for rendering interactive UI cards"
    )
    suggested_actions: list[str] = Field(
        default_factory=list, description="Follow-up quick reply action chips"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Message creation timestamp"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Custom turn-level metadata"
    )


class ChatSession(BaseModel):
    """Session-level conversation envelope managing multi-tenant isolation and history."""
    session_id: str = Field(..., description="Unique conversation session ID")
    user_id: str = Field(..., description="Verified primary user identifier")
    tenant_id: str = Field(..., description="Tenant identifier for strict data isolation")
    channel: str = Field("webchat", description="Communication channel (e.g., 'webchat', 'teams', 'slack')")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Session creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last activity timestamp"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Session-level metadata (building, unit, location)"
    )
    messages: list[ChatMessage] = Field(
        default_factory=list, description="Ordered conversation history turns"
    )


class ChatHistoryResponse(BaseModel):
    """Response returned when fetching chat session history."""
    session_id: str
    user_id: str
    tenant_id: str
    channel: str
    total_messages: int
    messages: list[ChatMessage]
