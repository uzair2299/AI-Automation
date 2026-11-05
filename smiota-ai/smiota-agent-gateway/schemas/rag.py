"""Schemas for RAG (Retrieval Augmented Generation) knowledge management."""
from typing import Any, Optional
from pydantic import BaseModel, Field


class DocumentIngestionRequest(BaseModel):
    title: str = Field(..., description="Document or runbook title")
    content: str = Field(..., description="Full text or markdown content")
    category: str = Field("runbook", description="Category: runbook, postmortem, architecture, faq")
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentIngestionResponse(BaseModel):
    document_id: str
    chunks_created: int
    status: str = "indexed"


class VectorSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class DocumentSearchResult(BaseModel):
    document_id: str
    title: str
    content: str
    score: float
    category: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class VectorSearchResponse(BaseModel):
    query: str
    results: list[DocumentSearchResult]
    total_found: int
