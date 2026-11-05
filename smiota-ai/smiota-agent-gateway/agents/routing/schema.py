"""Data schemas for intent classification and agent routing."""
from typing import Any, Optional
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    """Normalized routing decision produced by an intent classifier."""

    agent_name: str = Field(
        ...,
        description="Target agent name (e.g. 'customer', 'aiops', 'security', 'developer', 'qa')",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 (0% to 100% certainty)",
    )
    matched_intent: str = Field(
        default="unknown",
        description="Categorical intent name (e.g. 'locker_pickup', 'incident_investigation')",
    )
    routing_method: str = Field(
        default="rule_pattern",
        description="Method used: 'rule_pattern', 'context_continuity', 'gemini_semantic', 'channel_default', or 'fallback'",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Human or LLM rationale for selecting this agent",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context, timing, or debug diagnostics",
    )
