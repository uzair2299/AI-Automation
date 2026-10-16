"""Hybrid search retriever combining embeddings and keyword relevance."""
from typing import Optional, Any
from smiota.rag.vector_store import VectorStoreClient
from smiota.rag.embeddings import EmbeddingService
from smiota.schemas.rag import DocumentSearchResult
from smiota.core.logging import logger


class KnowledgeRetriever:
    """Retrieves relevant runbooks, incident postmortems, and technical docs."""

    def __init__(
        self,
        vector_store: Optional[VectorStoreClient] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        self.vector_store = vector_store or VectorStoreClient()
        self.embedding_service = embedding_service or EmbeddingService()

    async def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 5,
    ) -> list[DocumentSearchResult]:
        """Perform semantic retrieval for user query."""
        logger.info(f"Retrieving knowledge for query: '{query}'")
        query_embedding = await self.embedding_service.get_embedding(query)
        raw_results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            category=category,
        )

        return [
            DocumentSearchResult(
                document_id=r["document_id"],
                title=r["title"],
                content=r["content"],
                score=r.get("score", 0.0),
                category=r.get("category", "runbook"),
                metadata=r.get("metadata", {}),
            )
            for r in raw_results
        ]
