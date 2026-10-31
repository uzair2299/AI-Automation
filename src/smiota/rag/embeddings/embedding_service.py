"""Concrete embedding implementations including Vertex AI and Deterministic Mock."""
import asyncio
import hashlib
import math
import re
from typing import Any

from smiota.core.logging import logger
from smiota.llm.provider import GeminiProvider
from smiota.rag.config import RAGConfig
from smiota.rag.embeddings.base import BaseEmbeddingService


class DeterministicEmbeddingService(BaseEmbeddingService):
    """Produces reproducible, normalized vector embeddings without network calls.

    Ideal for fast, isolated, deterministic unit testing and local development.
    """

    def __init__(self, dimension: int = 768):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def _generate_vector(self, text: str) -> list[float]:
        """Produce a normalized float vector deterministically based on input text tokens."""
        clean = text.lower().strip()
        tokens = re.findall(r"\w+", clean) or ["empty"]
        vector = [0.0] * self._dimension

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for i in range(min(len(digest), self._dimension)):
                idx = (int(digest[i]) * (i + 1)) % self._dimension
                val = (digest[i] - 128.0) / 128.0
                vector[idx] += val

        # L2 Normalize vector
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        else:
            vector[0] = 1.0

        return vector

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._generate_vector(t) for t in texts]

    async def embed_query(self, query: str) -> list[float]:
        return self._generate_vector(query)


class VertexEmbeddingService(BaseEmbeddingService):
    """Generates embeddings using Google Cloud Vertex AI text-embedding-004."""

    def __init__(self, config: RAGConfig | None = None, provider: GeminiProvider | None = None):
        self.config = config or RAGConfig()
        self.provider = provider or GeminiProvider()
        self._dimension = self.config.embedding_dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    async def _embed_single_with_retry(self, text: str) -> list[float]:
        """Fetch embedding for a single text chunk with exponential backoff retry."""
        attempt = 0
        backoff = self.config.retry_backoff_seconds

        while attempt < self.config.max_retries:
            try:
                emb = await self.provider.generate_embedding(text)
                if emb and any(v != 0.0 for v in emb):
                    return emb
                # If provider returned simulated zeros, check if retry is needed
                return emb or ([0.0] * self._dimension)
            except Exception as exc:
                attempt += 1
                if attempt >= self.config.max_retries:
                    logger.error(f"Vertex embedding exhausted {self.config.max_retries} attempts: {exc}")
                    raise
                logger.warning(f"Vertex embedding attempt {attempt} failed: {exc}. Retrying in {backoff:.2f}s...")
                await asyncio.sleep(backoff)
                backoff *= 2.0

        return [0.0] * self._dimension

    async def _embed_batch_with_retry(self, texts: list[str]) -> list[list[float]]:
        """Fetch embeddings for a batch of text chunks in a single API call with retry."""
        if not texts:
            return []

        # If provider supports native batching, send the entire batch in 1 request
        if hasattr(self.provider, "generate_embeddings_batch"):
            attempt = 0
            backoff = self.config.retry_backoff_seconds
            while attempt < self.config.max_retries:
                try:
                    embeddings = await self.provider.generate_embeddings_batch(texts)
                    if embeddings and len(embeddings) == len(texts):
                        return embeddings
                    break
                except Exception as exc:
                    attempt += 1
                    if attempt >= self.config.max_retries:
                        logger.warning(
                            f"Vertex batch embedding exhausted retries: {exc}. Falling back to single-chunk embedding."
                        )
                        break
                    await asyncio.sleep(backoff)
                    backoff *= 2.0

        # Graceful fallback to single-chunk concurrent embedding
        return await asyncio.gather(*(self._embed_single_with_retry(t) for t in texts))

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Batch embedding generation respecting configured batch size."""
        results: list[list[float]] = []
        batch_size = self.config.embedding_batch_size

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_results = await self._embed_batch_with_retry(batch)
            results.extend(batch_results)

        return results

    async def embed_query(self, query: str) -> list[float]:
        return await self._embed_single_with_retry(query)


class EmbeddingService(BaseEmbeddingService):
    """Unified embedding service facade preserving backward compatibility."""

    def __init__(
        self,
        config: RAGConfig | None = None,
        provider: Any | None = None,
        use_deterministic: bool = False,
    ):
        self.config = config or RAGConfig()
        if use_deterministic or self.config.embedding_provider == "deterministic":
            self._backend: BaseEmbeddingService = DeterministicEmbeddingService(
                dimension=self.config.embedding_dimension
            )
        else:
            self._backend = VertexEmbeddingService(
                config=self.config,
                provider=provider if isinstance(provider, GeminiProvider) else None,
            )

    @property
    def dimension(self) -> int:
        return self._backend.dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return await self._backend.embed_texts(texts)

    async def embed_query(self, query: str) -> list[float]:
        return await self._backend.embed_query(query)

    # Backward compatibility helpers
    async def get_embedding(self, text: str) -> list[float]:
        return await self.embed_query(text)

    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        return await self.embed_texts(texts)
