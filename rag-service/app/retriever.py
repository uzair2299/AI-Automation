"""Retrieval coordinator marrying embedding generation with vector search."""
import logging
from typing import List, Optional

try:
    from app.embeddings import EmbeddingService
    from app.models import DocumentSearchResult
    from app.vector_store import VectorStoreClient
except ImportError:
    from .embeddings import EmbeddingService
    from .models import DocumentSearchResult
    from .vector_store import VectorStoreClient

logger = logging.getLogger("rag-service.retriever")


class KnowledgeRetriever:
    """Coordinates query embedding and vector search."""

    def __init__(self, vector_store: VectorStoreClient, embedding_service: EmbeddingService):
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    async def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 5,
    ) -> List[DocumentSearchResult]:
        """Embed user query and retrieve top matching document chunks."""
        logger.info("Entering KnowledgeRetriever.retrieve")
        try:
            query_embedding = await self.embedding_service.get_embedding(query)
            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                category=category,
            )
            logger.info("Exiting KnowledgeRetriever.retrieve")
            return results
        except Exception as exc:
            logger.error("Error occurred in KnowledgeRetriever.retrieve: %s", exc, exc_info=True)
            raise
