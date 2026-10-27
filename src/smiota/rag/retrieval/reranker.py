"""Reranker interfaces for two-stage retrieval ranking."""
from abc import ABC, abstractmethod

from smiota.rag.models import ScoredChunk


class BaseReranker(ABC):
    """Abstract interface for reranking candidate chunks."""

    @abstractmethod
    async def rerank(
        self,
        query: str,
        candidates: list[ScoredChunk],
        top_k: int = 5,
    ) -> list[ScoredChunk]:
        """Rerank candidates based on cross-encoding or higher-order relevance."""
        ...


class NoOpReranker(BaseReranker):
    """Pass-through reranker maintaining original candidate ordering."""

    async def rerank(
        self,
        query: str,
        candidates: list[ScoredChunk],
        top_k: int = 5,
    ) -> list[ScoredChunk]:
        sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)[:top_k]
        for rank, item in enumerate(sorted_candidates, start=1):
            item.rank = rank
            item.rerank_score = item.score
        return sorted_candidates
