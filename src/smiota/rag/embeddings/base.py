"""Base embedding service abstract interface."""
from abc import ABC, abstractmethod


class BaseEmbeddingService(ABC):
    """Abstract interface defining document and query embedding contracts."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Vector dimensionality."""
        ...

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of text documents."""
        ...

    @abstractmethod
    async def embed_query(self, query: str) -> list[float]:
        """Generate a single embedding vector for a search query."""
        ...
