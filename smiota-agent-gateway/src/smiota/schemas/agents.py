"""Schemas for agent registration, metadata, routing diagnostics, and capabilities."""
from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentCapability(BaseModel):
    name: str
    description: str
    access_level: str = "read_only"


class AgentMetadataResponse(BaseModel):
    name: str
    domain: str
    description: str
    capabilities: list[AgentCapability] = Field(default_factory=list)
    active: bool = True
    tools_count: int = 0


class IntentClassificationDiagnostic(BaseModel):
    query: str
    classified_agent: str
    confidence: float
    reasoning: Optional[str] = None
    extracted_entities: dict[str, Any] = Field(default_factory=dict)
