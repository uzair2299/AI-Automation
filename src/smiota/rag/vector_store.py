"""Vector store bridge."""
from smiota.rag.vector_store.base import BaseVectorStore
from smiota.rag.vector_store.factory import VectorStoreFactory
from smiota.rag.vector_store.in_memory_store import InMemoryVectorStore, VectorStoreClient

__all__ = [
    "BaseVectorStore",
    "InMemoryVectorStore",
    "VectorStoreClient",
    "VectorStoreFactory",
]
