"""High-level retrieval service orchestrating embeddings, vector search, hybrid fusion, and ranking."""
from typing import Any

from smiota.core.logging import logger
from smiota.rag.config import RAGConfig
from smiota.rag.embeddings.base import BaseEmbeddingService
from smiota.rag.embeddings.embedding_service import EmbeddingService
from smiota.rag.models import RetrievalQuery, ScoredChunk
from smiota.rag.retrieval.reranker import BaseReranker, NoOpReranker
from smiota.rag.retrieval.similarity import maximal_marginal_relevance, reciprocal_rank_fusion
from smiota.rag.vector_store.base import BaseVectorStore


class RetrievalService:
    """Orchestrates query embedding, multi-stage retrieval, hybrid RRF, MMR, and reranking."""

    def __init__(
        self,
        vector_store: BaseVectorStore | None = None,
        embedding_service: BaseEmbeddingService | None = None,
        reranker: BaseReranker | None = None,
        config: RAGConfig | None = None,
    ):
        self.config = config or RAGConfig()
        if vector_store is None:
            from smiota.rag.vector_store.factory import VectorStoreFactory

            self.vector_store = VectorStoreFactory.get_vector_store(config=self.config)
        else:
            self.vector_store = vector_store
        self.embedding_service = embedding_service or EmbeddingService(config=self.config)
        self.reranker = reranker or NoOpReranker()

    async def retrieve(
        self,
        query: str | RetrievalQuery,
        top_k: int | None = None,
        category: str | None = None,
        filters: dict[str, Any] | None = None,
        enable_mmr: bool | None = None,
        similarity_threshold: float | None = None,
    ) -> list[ScoredChunk]:
        """Execute semantic or hybrid retrieval for user query."""
        if isinstance(query, str):
            effective_query = RetrievalQuery(
                text=query,
                top_k=top_k or self.config.final_result_count,
                candidate_count=self.config.retrieval_candidate_count,
                category=category,
                filters=filters or {},
                similarity_threshold=similarity_threshold or self.config.similarity_threshold,
                enable_mmr=enable_mmr if enable_mmr is not None else self.config.enable_mmr,
                mmr_lambda=self.config.mmr_lambda,
            )
        else:
            effective_query = query
            if top_k is not None:
                effective_query.top_k = top_k
            if category is not None:
                effective_query.category = category

        logger.debug(
            f"Retrieving top {effective_query.top_k} chunks for query: '{effective_query.text[:50]}...'",
            extra={
                "event": "rag.retrieval.started",
                "top_k": effective_query.top_k,
                "category": effective_query.category,
            },
        )

        # 1. Generate query embedding
        query_embedding = await self.embedding_service.embed_query(effective_query.text)

        # 2. Retrieve dense vector candidates
        dense_candidates = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=effective_query.candidate_count,
            category=effective_query.category,
            filters=effective_query.filters,
        )

        candidates: list[ScoredChunk] = dense_candidates

        # 3. Hybrid search: Fuse dense and sparse BM25 results using RRF
        if self.config.enable_hybrid_search:
            sparse_candidates = await self.vector_store.search_bm25(
                query_text=effective_query.text,
                top_k=effective_query.candidate_count,
                category=effective_query.category,
            )
            if sparse_candidates:
                candidates = reciprocal_rank_fusion(
                    dense_results=dense_candidates,
                    sparse_results=sparse_candidates,
                    k=self.config.rrf_k,
                    dense_weight=self.config.hybrid_dense_weight,
                    sparse_weight=self.config.hybrid_bm25_weight,
                )

        # 4. Optional similarity threshold filtering (applies to pure dense cosine similarity)
        threshold = effective_query.similarity_threshold
        if threshold is not None and not self.config.enable_hybrid_search:
            candidates = [c for c in candidates if c.score >= threshold]

        # 5. Optional Maximal Marginal Relevance (MMR) for diversity
        if effective_query.enable_mmr and query_embedding:
            candidates = maximal_marginal_relevance(
                query_embedding=query_embedding,
                candidate_chunks=candidates,
                top_k=effective_query.top_k,
                lambda_mult=effective_query.mmr_lambda,
            )

        # 6. Optional reranker stage
        reranked = await self.reranker.rerank(
            query=effective_query.text,
            candidates=candidates,
            top_k=effective_query.top_k,
        )

        final_results = reranked[: effective_query.top_k]

        logger.debug(
            f"Retrieval returned {len(final_results)} scored chunks",
            extra={
                "event": "rag.retrieval.completed",
                "returned_count": len(final_results),
            },
        )
        return final_results


class KnowledgeRetriever:
    """Backward-compatible retriever facade converting ScoredChunks to DocumentSearchResult."""

    def __init__(
        self,
        vector_store: Any | None = None,
        embedding_service: Any | None = None,
        config: RAGConfig | None = None,
    ):
        self.config = config or RAGConfig()
        if vector_store is not None:
            store: BaseVectorStore = (
                vector_store._store if hasattr(vector_store, "_store") else vector_store
            )
        else:
            from smiota.rag.vector_store.in_memory_store import VectorStoreClient

            store = VectorStoreClient()._store
        emb_service: BaseEmbeddingService = (
            embedding_service
            if isinstance(embedding_service, BaseEmbeddingService)
            else EmbeddingService(config=self.config)
        )
        self._service = RetrievalService(
            vector_store=store,
            embedding_service=emb_service,
            config=self.config,
        )

    async def retrieve(
        self,
        query: str,
        category: str | None = None,
        top_k: int = 5,
    ) -> list[Any]:
        """Perform semantic retrieval returning DocumentSearchResult instances."""
        from smiota.schemas.rag import DocumentSearchResult

        results = await self._service.retrieve(query=query, category=category, top_k=top_k)
        return [
            DocumentSearchResult(
                document_id=r.chunk.document_id,
                title=r.chunk.title,
                content=r.chunk.text,
                score=r.score,
                category=r.chunk.category,
                metadata=r.chunk.metadata,
            )
            for r in results
        ]
