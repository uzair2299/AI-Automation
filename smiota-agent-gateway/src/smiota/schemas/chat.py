"""Schemas for Chat interactions, SSE streams, and channel payloads."""
from typing import Any
from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """Structured RAG source reference."""

    title: str = Field(..., description="Document or page title")
    url: str = Field(..., description="Sanitized, validated public web URL for the source")
    source_type: str = Field(
        "website", description="Type of source: website, runbook, pdf, internal_docs"
    )
    document_id: str | None = Field(None, description="Internal unique identifier for the document")
    domain: str | None = Field(None, description="Extracted domain/hostname of the source URL")
    score: float | None = Field(None, description="Relevance similarity score (if available)")

    @property
    def relevance_score(self) -> float | None:
        """Alias for score for backward-compatible attribute access."""
        return self.score


class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="User query or instruction")
    channel: str = Field("webchat", description="Channel origin: webchat, teams, ide, mobile")
    session_id: str | None = Field(None, description="Conversation session ID")
    target_agent: str | None = Field(
        None, description="Direct to specific agent: aiops, security, developer, qa, customer"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Contextual metadata (e.g. repo, pod, incident ID)"
    )


class ChatMessageResponse(BaseModel):
    session_id: str
    response: str = Field(default="", description="The assistant response text")
    answer: str = Field(default="", description="The assistant generated answer")
    sources: list[SourceReference] = Field(
        default_factory=list,
        description="Structured, validated, and deduplicated RAG source citations",
    )
    agent_used: str
    requires_approval: bool = False
    approval_id: str | None = None
    suggested_actions: list[str] = Field(default_factory=list)
    user: dict[str, Any] | None = Field(
        default=None, description="User necessary information object"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Response metadata")

    def model_post_init(self, __context: Any) -> None:
        """Keep answer and response fields synchronized for backwards compatibility."""
        if not self.answer and self.response:
            self.answer = self.response
        elif not self.response and self.answer:
            self.response = self.answer
