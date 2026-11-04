"""Storage adapters for vector embeddings and document metadata."""
from typing import Any
from app.core.config import settings
from app.storage.memory import VectorStoreClient, cosine_similarity
from app.storage.pgvector import PgVectorStoreClient

_vector_store_instance: Any = None


def get_vector_store():
    """Retrieve or initialize the active vector store singleton."""
    global _vector_store_instance
    if _vector_store_instance is None:
        if settings.is_pgvector:
            _vector_store_instance = PgVectorStoreClient()
        else:
            _vector_store_instance = VectorStoreClient()
    return _vector_store_instance


def set_vector_store(store: Any):
    """Override active vector store (e.g. for fallback or tests)."""
    global _vector_store_instance
    _vector_store_instance = store


__all__ = [
    "PgVectorStoreClient",
    "VectorStoreClient",
    "cosine_similarity",
    "get_vector_store",
    "set_vector_store",
]
