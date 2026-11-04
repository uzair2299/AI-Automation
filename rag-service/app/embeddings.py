"""Embedding generation service supporting Gemini Vertex and Token-based Deterministic Fallback."""
import hashlib
import logging
import math
import re
from typing import List

try:
    from app.config import settings
except ImportError:
    from .config import settings

logger = logging.getLogger("rag-service.embeddings")


class EmbeddingService:
    """Generates normalized dense vector embeddings."""

    def __init__(self, dimension: int = 768):
        self.dimension = dimension

    def _deterministic_embedding(self, text: str) -> List[float]:
        """Produce a normalized float vector deterministically based on input text tokens."""
        clean = text.lower().strip()
        tokens = (re.findall(r"\w+", clean) or ["empty"])[:250]
        vector = [0.0] * self.dimension

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for i in range(min(len(digest), self.dimension)):
                idx = (int(digest[i]) * (i + 1)) % self.dimension
                val = (digest[i] - 128.0) / 128.0
                vector[idx] += val

        # L2 Normalize vector
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            return [v / norm for v in vector]
        vector[0] = 1.0
        return vector

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for input text."""
        logger.debug("Entering get_embedding")
        try:
            if settings.EMBEDDING_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
                try:
                    import httpx
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={settings.GEMINI_API_KEY}"
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.post(url, json={"content": {"parts": [{"text": text}]}})
                        if resp.status_code == 200:
                            values = resp.json().get("embedding", {}).get("values", [])
                            if values:
                                logger.debug("Exiting get_embedding (gemini)")
                                return values
                        else:
                            logger.warning(
                                "Gemini embedding API returned non-200 status code: %d", resp.status_code
                            )
                except Exception as exc:
                    logger.error(
                        "Gemini embedding API call failed, falling back to deterministic embedding: %s",
                        exc,
                        exc_info=True,
                    )

            result = self._deterministic_embedding(text)
            logger.debug("Exiting get_embedding (deterministic)")
            return result
        except Exception as exc:
            logger.error("Failed to generate embedding: %s", exc, exc_info=True)
            raise
