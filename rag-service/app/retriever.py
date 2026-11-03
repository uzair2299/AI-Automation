"""Retrieval coordinator marrying embedding generation with vector search."""
from typing import List, Optional
from app.embeddings import EmbeddingService
from app.models import DocumentSearchResult
from app.vector_store import VectorStoreClient


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
        query_embedding = await self.embedding_service.get_embedding(query)
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            category=category,
        )
        return results

