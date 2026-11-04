"""Retrieval coordinator marrying embedding generation with vector search."""
import logging
from typing import List, Optional

from app.schemas.document import DocumentSearchResult
from app.services.embeddings import EmbeddingService
from app.storage.memory import VectorStoreClient

logger = logging.getLogger("rag-service.services.retriever")


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
            store_name = type(self.vector_store).__name__
            logger.info(
                "KnowledgeRetriever: Embedding query '%s' (top_k=%d, category=%s)",
                query,
                top_k,
                category or "all",
            )
            query_embedding = await self.embedding_service.get_embedding(query)
            logger.info(
                "KnowledgeRetriever: Query embedded successfully (dim=%d). Querying store: %s",
                len(query_embedding),
                store_name,
            )
            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                category=category,
            )
            logger.info(
                "KnowledgeRetriever: Found %d matching chunks from %s for query '%s'",
                len(results),
                store_name,
                query,
            )
            for idx, r in enumerate(results, start=1):
                preview = (
                    r.document.content[:160].replace("\n", " ").strip()
                    + ("..." if len(r.document.content) > 160 else "")
                )
                logger.info(
                    "  -> Match #%d: score=%.4f | title='%s' | cat=%s | id=%s | snippet=\"%s\"",
                    idx,
                    r.similarity_score,
                    r.document.title,
                    r.document.category,
                    r.document_id[:8],
                    preview,
                )
            logger.info("Exiting KnowledgeRetriever.retrieve")
            return results
        except Exception as exc:
            logger.error("Error occurred in KnowledgeRetriever.retrieve: %s", exc, exc_info=True)
            raise

