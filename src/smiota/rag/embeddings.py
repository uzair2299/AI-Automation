"""Text embedding generation service."""
from smiota.llm.provider import GeminiProvider
from smiota.core.logging import logger


class EmbeddingService:
    """Generates normalized vector embeddings for indexing and search."""

    def __init__(self, provider: GeminiProvider | None = None):
        self.provider = provider or GeminiProvider()

    async def get_embedding(self, text: str) -> list[float]:
        """Generate embedding vector."""
        return await self.provider.generate_embedding(text)

    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embedding generation."""
        return [await self.provider.generate_embedding(t) for t in texts]
