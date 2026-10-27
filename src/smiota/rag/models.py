"""Pydantic data models for the RAG ingestion and retrieval subsystem."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RawRecord:
    """Normalized source record extracted from raw input formats like JSONL."""

    source_id: str
    title: str
    category: str
    extracted_text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentChunk:
    """Text chunk ready for embedding and vector storage."""

    chunk_id: str
    document_id: str
    title: str
    category: str
    text: str
    chunk_index: int
    token_count: int
    content_hash: str
    embedding: list[float] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoredChunk:
    """Document chunk enriched with similarity and ranking scores."""

    chunk: DocumentChunk
    score: float
    dense_score: float = 0.0
    sparse_score: float = 0.0
    rerank_score: float | None = None
    rank: int = 1


@dataclass
class RetrievalQuery:
    """Parameters defining a semantic or hybrid retrieval query."""

    text: str
    top_k: int = 5
    candidate_count: int = 20
    category: str | None = None
    filters: dict[str, Any] = field(default_factory=dict)
    similarity_threshold: float | None = None
    enable_mmr: bool = False
    mmr_lambda: float = 0.5


@dataclass
class IngestionStats:
    """Execution telemetry and diagnostics for an ingestion run."""

    total_records_read: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    chunks_created: int = 0
    chunks_embedded: int = 0
    chunks_upserted: int = 0
    duplicate_chunks_skipped: int = 0
    duration_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
