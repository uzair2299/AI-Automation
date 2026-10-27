"""RAG (Retrieval Augmented Generation) knowledge engine.

Provides modular streaming ingestion, token-aware chunking, provider-independent
vector storage, and multi-stage hybrid retrieval.
"""
from smiota.rag.chunking import ChunkingService, DocumentChunker
from smiota.rag.config import RAGConfig
from smiota.rag.embeddings import (
    BaseEmbeddingService,
    DeterministicEmbeddingService,
    EmbeddingService,
    VertexEmbeddingService,
)
from smiota.rag.ingestion import IngestionService, RecordNormalizer, read_jsonl_stream
from smiota.rag.models import (
    DocumentChunk,
    IngestionStats,
    RawRecord,
    RetrievalQuery,
    ScoredChunk,
)
from smiota.rag.prompts import (
    SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT,
    build_rag_prompt,
    format_retrieved_chunks,
)
from smiota.rag.retrieval import (
    BaseReranker,
    KnowledgeRetriever,
    NoOpReranker,
    RetrievalService,
    cosine_similarity,
    dot_product,
    maximal_marginal_relevance,
    reciprocal_rank_fusion,
)
from smiota.rag.vector_store import (
    BaseVectorStore,
    InMemoryVectorStore,
    VectorStoreClient,
    VectorStoreFactory,
)

__all__ = [
    "SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT",
    "BaseEmbeddingService",
    "BaseReranker",
    "BaseVectorStore",
    "ChunkingService",
    "DeterministicEmbeddingService",
    "DocumentChunk",
    "DocumentChunker",
    "EmbeddingService",
    "InMemoryVectorStore",
    "IngestionService",
    "IngestionStats",
    "KnowledgeRetriever",
    "NoOpReranker",
    "RAGConfig",
    "RawRecord",
    "RecordNormalizer",
    "RetrievalQuery",
    "RetrievalService",
    "ScoredChunk",
    "VectorStoreClient",
    "VectorStoreFactory",
    "VertexEmbeddingService",
    "build_rag_prompt",
    "cosine_similarity",
    "dot_product",
    "format_retrieved_chunks",
    "maximal_marginal_relevance",
    "read_jsonl_stream",
    "reciprocal_rank_fusion",
]
