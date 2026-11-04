"""API schemas and data contracts for RAG Service."""
from app.schemas.document import (
    APIResponse,
    DocumentChunkRecord,
    DocumentIngestionRequest,
    DocumentIngestionResponse,
    DocumentMetadata,
    DocumentSearchResult,
    VectorSearchRequest,
    VectorSearchResponse,
)

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

