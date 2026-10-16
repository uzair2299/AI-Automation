"""Schemas for Chat interactions, SSE streams, and channel payloads."""
from typing import Optional, Any
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="User query or instruction")
    channel: str = Field("webchat", description="Channel origin: webchat, teams, ide, mobile")
    session_id: Optional[str] = Field(None, description="Conversation session ID")
    target_agent: Optional[str] = Field(None, description="Direct to specific agent: aiops, security, developer, qa, customer")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Contextual metadata (e.g. repo, pod, incident ID)")


class ChatMessageResponse(BaseModel):
    session_id: str
    response: str
    agent_used: str
    requires_approval: bool = False
    approval_id: Optional[str] = None
    suggested_actions: list[str] = Field(default_factory=list)
