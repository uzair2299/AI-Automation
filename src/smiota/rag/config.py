"""Configuration settings for the RAG ingestion and retrieval subsystem."""
from dataclasses import dataclass, field
from typing import Any

from smiota.core.config import get_settings


@dataclass
class RAGConfig:
    """Configuration settings for the provider-independent RAG subsystem.

    Coordinates parameter limits and operational defaults across text chunking,
    embedding generation, vector database backends, and multi-stage retrieval.

    All token estimates assume the standard heuristic of ~4 characters per token.
    Instances can be initialized directly with keyword overrides or constructed
    from application environment variables via `RAGConfig.from_settings()`.
    """

    # --------------------------------------------------------------------------
    # 1. Chunking Boundaries & Structural Splitting
    # --------------------------------------------------------------------------
    # Target chunk size in tokens (~1600 characters). Primary splitting boundary.
    target_chunk_size: int = 400

    # Overlap between consecutive chunks in tokens to preserve transitional context.
    chunk_overlap: int = 50

    # Minimum token threshold. Chunks smaller than this are merged with adjacent
    # blocks or kept intact if the entire parent document is short.
    min_chunk_size: int = 50

    # Hard upper bound in tokens. Prevents oversized chunks from exceeding model
    # context limits when paragraphs or code blocks lack natural breaks.
    max_chunk_size: int = 500

    # --------------------------------------------------------------------------
    # 2. Ingestion & Embedding Batching
    # --------------------------------------------------------------------------
    # Number of chunks grouped into each batch API request to the embedding provider.
    # Balances network throughput against provider payload size limits.
    embedding_batch_size: int = 32

    # Maximum number of retry attempts for transient embedding API or network failures.
    max_retries: int = 3

    # Base delay in seconds for exponential backoff during retry attempts.
    retry_backoff_seconds: float = 1.0

    # --------------------------------------------------------------------------
    # 3. Vector Store Backend & Distance Metric
    # --------------------------------------------------------------------------
    # Underlying storage and index adapter. Supported options:
    # - 'memory': In-memory vector store with BM25 keyword index and content hashing.
    # - 'pgvector': PostgreSQL pgvector extension adapter (future pluggable backend).
    vector_store_backend: str = "memory"

    # Distance function for vector similarity searches:
    # - 'cosine': Normalized cosine similarity [-1.0, 1.0], typical for text embeddings.
    # - 'dot_product': Inner product; identical to cosine when embeddings are unit-normalized.
    similarity_metric: str = "cosine"

    # --------------------------------------------------------------------------
    # 4. Retrieval & Ranking Parameters
    # --------------------------------------------------------------------------
    # Candidate pool size retrieved from the initial vector/keyword search before
    # applying hybrid fusion, MMR diversity filtering, or cross-encoder reranking.
    retrieval_candidate_count: int = 20

    # Final number of top-scoring chunks returned to the caller or orchestrating agent.
    final_result_count: int = 5

    # Optional minimum cosine similarity threshold [0.0, 1.0]. Results with scores
    # below this cutoff are discarded during pure dense retrieval. Set to None to disable.
    similarity_threshold: float | None = None

    # --------------------------------------------------------------------------
    # 5. Hybrid Search & Diversity (RRF & MMR)
    # --------------------------------------------------------------------------
    # When True, executes both dense vector search and sparse BM25 keyword search,
    # combining their rankings via Reciprocal Rank Fusion (RRF).
    enable_hybrid_search: bool = True

    # Weight multiplier for dense vector candidate rankings in RRF score accumulation.
    hybrid_dense_weight: float = 0.5

    # Weight multiplier for sparse BM25 candidate rankings in RRF score accumulation.
    hybrid_bm25_weight: float = 0.5

    # Smoothing constant k used in Reciprocal Rank Fusion: score = weight / (k + rank).
    # Standard literature recommendation is 60.
    rrf_k: int = 60

    # When True, applies Maximal Marginal Relevance (MMR) to balance query relevance
    # against intra-result diversity, penalizing redundant or repetitive chunks.
    enable_mmr: bool = False

    # Trade-off parameter lambda for MMR in the range [0.0, 1.0].
    # - 1.0: Pure relevance (no diversity penalty).
    # - 0.0: Pure diversity (maximizes distance from already selected chunks).
    # - 0.5: Balanced trade-off between relevance and diversity.
    mmr_lambda: float = 0.5

    # --------------------------------------------------------------------------
    # 6. Text Extraction & Schema Normalization
    # --------------------------------------------------------------------------
    # Priority list of JSON keys inspected when extracting text content from
    # variable-schema raw JSONL records. The first matching, non-empty key is used.
    text_fields: list[str] = field(
        default_factory=lambda: [
            "content_markdown",
            "content",
            "text",
            "body",
            "description",
            "details",
            "runbook",
            "message",
        ]
    )

    # Primary key field name in raw records used to derive document IDs.
    id_field: str = "id"

    # Field name in raw records used to extract human-readable titles.
    title_field: str = "title"

    # Field name in raw records used for categorical routing and filtered retrieval.
    category_field: str = "category"

    # Fallback category tag assigned when the record lacks a valid category field.
    default_category: str = "general"

    # --------------------------------------------------------------------------
    # 7. Embedding Model & Provider
    # --------------------------------------------------------------------------
    # Embedding generation provider:
    # - 'vertex': Google Cloud Vertex AI / Gemini text-embedding-004 API.
    # - 'deterministic': Deterministic pseudo-embeddings for fast local unit testing (zero cost).
    embedding_provider: str = "vertex"

    # Name of the upstream model deployed or requested from the embedding provider.
    embedding_model: str = "text-embedding-004"

    # Dimension size of the embedding vectors produced by the model (768 for text-embedding-004).
    embedding_dimension: int = 768

    # --------------------------------------------------------------------------
    # 8. Storage & Knowledge Base Ingestion Paths
    # --------------------------------------------------------------------------
    # Root directory path containing knowledge documents (.jsonl, .json, .txt, .md).
    # Defaults to the public knowledge partition for unauthenticated visitors.
    knowledge_dir: str = "data/knowledge/public"
    public_knowledge_dir: str = "data/knowledge/public"
    internal_knowledge_dir: str = "data/knowledge/internal"
    auto_index_on_startup: bool = True

    # Supported file extensions when scanning the knowledge directory.
    supported_extensions: list[str] = field(
        default_factory=lambda: [".jsonl", ".json", ".txt", ".md"]
    )

    # Backward-compatible file path for single JSONL ingestion workflows.
    default_jsonl_path: str = "data/knowledge/public/website_content.jsonl"

    @classmethod
    def from_settings(cls, **overrides: Any) -> "RAGConfig":
        """Construct a RAGConfig instance using application settings with optional overrides.

        Reads system defaults such as VECTOR_STORE_BACKEND and RAG_KNOWLEDGE_DIR
        from the centralized application configuration while allowing callers to
        override specific parameters.

        Args:
            **overrides: Explicit keyword arguments that supersede environment defaults.

        Returns:
            RAGConfig: Fully configured configuration dataclass instance.
        """
        settings = get_settings()
        backend = overrides.get(
            "vector_store_backend",
            getattr(settings, "VECTOR_STORE_BACKEND", "memory"),
        )
        knowledge_dir = overrides.get(
            "knowledge_dir",
            getattr(settings, "RAG_KNOWLEDGE_DIR", "data/knowledge/public"),
        )
        embedding_provider = overrides.get(
            "embedding_provider",
            getattr(settings, "RAG_EMBEDDING_PROVIDER", "vertex"),
        )
        auto_index_on_startup = overrides.get(
            "auto_index_on_startup",
            getattr(settings, "RAG_AUTO_INDEX_ON_STARTUP", True),
        )
        return cls(
            vector_store_backend=backend,
            knowledge_dir=knowledge_dir,
            embedding_provider=embedding_provider,
            auto_index_on_startup=auto_index_on_startup,
            **overrides,
        )
