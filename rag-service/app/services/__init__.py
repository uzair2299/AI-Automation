"""Domain services for document chunking, embedding generation, loading, and retrieval."""
from typing import Any
from app.core.config import settings
from app.services.chunking import DocumentChunker
from app.services.embeddings import EmbeddingService
from app.services.loader import find_knowledge_file, infer_category, load_real_knowledge_base
from app.services.retriever import KnowledgeRetriever
from app.storage import get_vector_store

_embedding_service_instance: Any = None
_chunker_instance: Any = None
_retriever_instance: Any = None


def get_embedding_service() -> EmbeddingService:
    """Retrieve or initialize embedding service singleton."""
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService(dimension=settings.EMBEDDING_DIMENSION)
    return _embedding_service_instance


def get_chunker() -> DocumentChunker:
    """Retrieve or initialize document chunker singleton."""
    global _chunker_instance
    if _chunker_instance is None:
        _chunker_instance = DocumentChunker(
            target_chunk_size=settings.TARGET_CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP,
        )
    return _chunker_instance


def get_retriever() -> KnowledgeRetriever:
    """Retrieve or initialize knowledge retriever singleton."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeRetriever(
            vector_store=get_vector_store(),
            embedding_service=get_embedding_service(),
        )
    return _retriever_instance


def set_retriever(retriever: KnowledgeRetriever):
    """Override active knowledge retriever singleton."""
    global _retriever_instance
    _retriever_instance = retriever


__all__ = [
    "DocumentChunker",
    "EmbeddingService",
    "KnowledgeRetriever",
    "find_knowledge_file",
    "get_chunker",
    "get_embedding_service",
    "get_retriever",
    "infer_category",
    "load_real_knowledge_base",
    "set_retriever",
]
