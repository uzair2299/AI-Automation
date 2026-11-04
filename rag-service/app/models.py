"""Data contracts and schemas for RAG REST Service."""
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from smiota_common.models import APIResponse


class DocumentMetadata(BaseModel):
    title: str
    category: str = "general"
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class DocumentChunkRecord(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    category: str
    content: str
    chunk_index: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentSearchResult(BaseModel):
    document_id: str
    similarity_score: float
    document: DocumentMetadata


class VectorSearchRequest(BaseModel):
    query: str = Field(..., description="User question or technical query")
    top_k: int = Field(default=5, ge=1, le=50)
    category: Optional[str] = Field(default=None, description="Optional filtering category")


class VectorSearchResponse(BaseModel):
    query: str
    results: List[DocumentSearchResult]
    total_found: int


class DocumentIngestionRequest(BaseModel):
    title: str
    content: str
    category: str = "runbook"
    tags: List[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentIngestionResponse(BaseModel):
    document_id: str
    chunks_created: int
    status: str = "indexed"


__all__ = [
    "APIResponse",
    "DocumentChunkRecord",
    "DocumentIngestionRequest",
    "DocumentIngestionResponse",
    "DocumentMetadata",
    "DocumentSearchResult",
    "VectorSearchRequest",
    "VectorSearchResponse",
]
