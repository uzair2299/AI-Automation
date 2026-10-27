"""Abstract Vector Store contract."""
from abc import ABC, abstractmethod
from typing import Any

from smiota.rag.models import DocumentChunk, ScoredChunk


class BaseVectorStore(ABC):
    """Provider-independent vector database interface.

    Allows swapping between in-memory, pgvector, Vertex AI Vector Search, or Qdrant
    purely through configuration and adapter injection.
    """

    @abstractmethod
    async def upsert(self, chunks: list[DocumentChunk]) -> int:
        """Insert or update chunks into the vector store. Returns number of upserted chunks."""
        ...

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        category: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[ScoredChunk]:
        """Perform dense vector similarity search returning ranked candidate chunks."""
        ...

    @abstractmethod
    async def search_bm25(
        self,
        query_text: str,
        top_k: int = 20,
        category: str | None = None,
    ) -> list[ScoredChunk]:
        """Perform sparse keyword/BM25 search across indexed chunk text."""
        ...

    @abstractmethod
    async def delete(self, chunk_ids: list[str]) -> int:
        """Delete chunks by ID. Returns count of removed items."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Return total number of active chunks in storage."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify storage backend availability."""
        ...
