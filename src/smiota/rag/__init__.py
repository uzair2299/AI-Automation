"""Smiota RAG subsystem client and prompt context utilities."""
from smiota.rag.client import RAGServiceClient
from smiota.rag.config import RAGConfig
from smiota.rag.models import (
    DocumentChunk,
    RetrievalQuery,
    ScoredChunk,
)
from smiota.rag.prompts import (
    SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT,
    build_rag_prompt,
    format_retrieved_chunks,
)

__all__ = [
    "RAGServiceClient",
    "RAGConfig",
    "DocumentChunk",
    "RetrievalQuery",
    "ScoredChunk",
    "SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT",
    "build_rag_prompt",
    "format_retrieved_chunks",
]
