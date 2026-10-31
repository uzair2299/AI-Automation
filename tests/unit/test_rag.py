"""Comprehensive unit tests for provider-independent RAG subsystem."""
import json

import pytest

from smiota.rag.chunking.chunking_service import ChunkingService, DocumentChunker
from smiota.rag.config import RAGConfig
from smiota.rag.embeddings.embedding_service import DeterministicEmbeddingService, EmbeddingService
from smiota.rag.ingestion.ingestion_service import IngestionService
from smiota.rag.ingestion.jsonl_reader import RecordNormalizer, read_jsonl_stream
from smiota.rag.models import DocumentChunk
from smiota.rag.retrieval.retrieval_service import KnowledgeRetriever, RetrievalService
from smiota.rag.retrieval.similarity import (
    cosine_similarity,
    dot_product,
    maximal_marginal_relevance,
    reciprocal_rank_fusion,
)
from smiota.rag.vector_store.factory import VectorStoreFactory
from smiota.rag.vector_store.in_memory_store import InMemoryVectorStore


@pytest.fixture
def rag_config():
    """Default RAGConfig for test isolation."""
    return RAGConfig(
        target_chunk_size=50,
        chunk_overlap=10,
        min_chunk_size=10,
        max_chunk_size=80,
        embedding_batch_size=4,
        retrieval_candidate_count=10,
        final_result_count=5,
        vector_store_backend="memory",
        embedding_provider="deterministic",
        embedding_dimension=32,
    )


@pytest.fixture
def deterministic_embeddings(rag_config):
    return DeterministicEmbeddingService(dimension=rag_config.embedding_dimension)


@pytest.fixture
def memory_store(rag_config):
    return InMemoryVectorStore(config=rag_config)


# ==============================================================================
# 1. Chunking Tests
# ==============================================================================

def test_short_record_kept_intact(rag_config):
    """Short self-contained records should not be arbitrarily split."""
    chunker = ChunkingService(rag_config)
    short_text = "Smart Locker door solenoid is operating within normal resistance thresholds."
    chunks = chunker.split_text(short_text, document_id="doc-short", title="Solenoid Status")

    assert len(chunks) == 1
    assert chunks[0].text == short_text
    assert chunks[0].chunk_index == 0
    assert chunks[0].document_id == "doc-short"
    assert chunks[0].content_hash


def test_oversized_record_chunking_with_overlap(rag_config):
    """Long text should be split along paragraph or sentence boundaries respecting overlap."""
    chunker = ChunkingService(rag_config)
    paragraphs = [
        "First section discusses kubernetes pod memory exhaustion and Prometheus alert rule configuration.",
        "Second section investigates OOMKilled events and container limits under high traffic load.",
        "Third section outlines remediation procedures including rolling restart and memory request increases.",
        "Fourth section covers verification using Grafana dashboards and OpenSearch audit logs.",
    ]
    long_text = "\n\n".join(paragraphs)
    chunks = chunker.split_text(long_text, document_id="doc-runbook", title="K8s Runbook")

    assert len(chunks) > 1
    # Check consecutive chunk indices
    for i, chk in enumerate(chunks):
        assert chk.chunk_index == i
        assert chk.document_id == "doc-runbook"
        assert chk.token_count <= rag_config.max_chunk_size + 20


def test_empty_or_whitespace_text_handling(rag_config):
    """Empty or whitespace text should produce no chunks."""
    chunker = ChunkingService(rag_config)
    assert chunker.split_text("") == []
    assert chunker.split_text("   \n\n  \t ") == []


def test_legacy_document_chunker_compatibility():
    """Existing DocumentChunker interface returning plain strings must remain functional."""
    chunker = DocumentChunker(chunk_size=100)
    text = "# Section 1\nThis is paragraph one.\n\n## Section 2\nThis is paragraph two."
    chunks = chunker.split_text(text)
    assert isinstance(chunks, list)
    assert len(chunks) >= 2
    assert isinstance(chunks[0], str)


# ==============================================================================
# 2. JSONL Reader & Record Normalizer Tests
# ==============================================================================

def test_jsonl_streaming_line_by_line(tmp_path):
    """Verify streaming reader processes lines without loading entire file and handles malformed lines."""
    jsonl_file = tmp_path / "sample.jsonl"
    lines = [
        json.dumps({"id": "doc-1", "title": "Runbook 1", "content": "Valid content one."}),
        "MALFORMED_JSON_LINE_HERE",
        json.dumps({"document_id": "doc-2", "text": "Valid content two from alternate field."}),
        json.dumps({"_id": "doc-3", "body": "Valid content three."}),
    ]
    jsonl_file.write_text("\n".join(lines), encoding="utf-8")

    stream = list(read_jsonl_stream(jsonl_file, skip_invalid=True))
    assert len(stream) == 4

    # Line 1: valid
    assert stream[0][0] == 1
    assert stream[0][1]["id"] == "doc-1"
    assert stream[0][2] is None

    # Line 2: malformed
    assert stream[1][0] == 2
    assert stream[1][1] is None
    assert "Malformed JSON" in stream[1][2]

    # Line 3 & 4: valid
    assert stream[2][1]["document_id"] == "doc-2"
    assert stream[3][1]["_id"] == "doc-3"


def test_record_normalizer_variable_schemas(rag_config):
    """Normalizer extracts text from various candidate fields and preserves extra fields as metadata."""
    normalizer = RecordNormalizer(rag_config)

    # Schema A: standard
    record_a = normalizer.normalize({"id": "A1", "title": "Title A", "content": "Content A", "env": "prod"})
    assert record_a is not None
    assert record_a.source_id == "A1"
    assert record_a.extracted_text == "Content A"
    assert record_a.metadata.get("env") == "prod"

    # Schema B: alternate fields
    record_b = normalizer.normalize({"doc_id": "B1", "name": "Name B", "body": "Body B", "author": "ops"})
    assert record_b is not None
    assert record_b.source_id == "B1"
    assert record_b.title == "Name B"
    assert record_b.extracted_text == "Body B"
    assert record_b.metadata.get("author") == "ops"

    # Schema C: empty text returns None
    record_c = normalizer.normalize({"id": "C1", "title": "No text here", "random": 123})
    assert record_c is None


# ==============================================================================
# 3. Embedding Service Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_deterministic_embedding_service(deterministic_embeddings):
    """Deterministic embedding service returns consistent unit-normalized vectors."""
    text1 = "GKE pod memory alert"
    text2 = "GKE pod memory alert"
    text3 = "Smart Locker door solenoid"

    vec1 = await deterministic_embeddings.embed_query(text1)
    vec2 = await deterministic_embeddings.embed_query(text2)
    vec3 = await deterministic_embeddings.embed_query(text3)

    assert len(vec1) == deterministic_embeddings.dimension
    assert vec1 == vec2  # Exact reproducibility
    assert vec1 != vec3  # Distinct texts produce distinct vectors

    # Vector is normalized (magnitude == 1.0)
    mag = sum(x * x for x in vec1)
    assert pytest.approx(mag, 0.001) == 1.0


@pytest.mark.asyncio
async def test_embedding_batching(rag_config):
    """EmbeddingService generates embeddings in batches respecting configured batch size."""
    emb_service = EmbeddingService(config=rag_config, use_deterministic=True)
    texts = [f"Text chunk number {i}" for i in range(10)]

    results = await emb_service.embed_texts(texts)
    assert len(results) == 10
    for vec in results:
        assert len(vec) == rag_config.embedding_dimension


@pytest.mark.asyncio
async def test_vertex_embedding_service_native_batch_call(rag_config):
    """VertexEmbeddingService utilizes native batch provider call when available."""
    from unittest.mock import AsyncMock, MagicMock
    from smiota.rag.embeddings.embedding_service import VertexEmbeddingService

    mock_provider = MagicMock()
    mock_provider.generate_embeddings_batch = AsyncMock(
        return_value=[[0.1] * rag_config.embedding_dimension, [0.2] * rag_config.embedding_dimension]
    )

    service = VertexEmbeddingService(config=rag_config, provider=mock_provider)
    texts = ["Chunk one", "Chunk two"]
    results = await service.embed_texts(texts)

    assert len(results) == 2
    assert results[0][0] == 0.1
    assert results[1][0] == 0.2
    mock_provider.generate_embeddings_batch.assert_called_once_with(["Chunk one", "Chunk two"])


@pytest.mark.asyncio
async def test_gemini_provider_embed_content_response_parsing():
    """Verify GeminiProvider parses Google GenAI EmbedContentResponse without attribute error."""
    from unittest.mock import MagicMock
    from google.genai import types
    from smiota.llm.provider import GeminiProvider

    provider = GeminiProvider()
    mock_client = MagicMock()
    # Simulate official Google GenAI EmbedContentResponse with .embeddings (plural)
    mock_client.models.embed_content.return_value = types.EmbedContentResponse(
        embeddings=[types.ContentEmbedding(values=[0.42] * 768)]
    )
    provider._client = mock_client

    # Single text embedding
    emb = await provider.generate_embedding("Test prompt")
    assert len(emb) == 768
    assert emb[0] == 0.42

    # Batch embedding
    mock_client.models.embed_content.return_value = types.EmbedContentResponse(
        embeddings=[
            types.ContentEmbedding(values=[0.1] * 768),
            types.ContentEmbedding(values=[0.2] * 768),
        ]
    )
    batch_emb = await provider.generate_embeddings_batch(["A", "B"])
    assert len(batch_emb) == 2
    assert batch_emb[0][0] == 0.1
    assert batch_emb[1][0] == 0.2



# ==============================================================================
# 4. Vector Store & Factory Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_in_memory_vector_store_upsert_and_deduplication(memory_store, deterministic_embeddings):
    """Verify upsert, count, deduplication by content hash, and deletion."""
    text = "Smart Locker door solenoid failure procedure."
    emb = await deterministic_embeddings.embed_query(text)

    chunk1 = DocumentChunk(
        chunk_id="chk-1",
        document_id="doc-1",
        title="Locker Doc",
        category="runbook",
        text=text,
        chunk_index=0,
        token_count=10,
        content_hash="hash-123",
        embedding=emb,
    )

    # First upsert
    upserted = await memory_store.upsert([chunk1])
    assert upserted == 1
    assert await memory_store.count() == 1

    # Idempotent upsert with same content hash under different ID should be skipped
    chunk_duplicate = DocumentChunk(
        chunk_id="chk-duplicate",
        document_id="doc-1",
        title="Locker Doc",
        category="runbook",
        text=text,
        chunk_index=0,
        token_count=10,
        content_hash="hash-123",
        embedding=emb,
    )
    upserted_dupe = await memory_store.upsert([chunk_duplicate])
    assert upserted_dupe == 0
    assert await memory_store.count() == 1

    # Delete
    deleted = await memory_store.delete(["chk-1"])
    assert deleted == 1
    assert await memory_store.count() == 0


def test_vector_store_factory_selection(rag_config):
    """VectorStoreFactory should return InMemoryVectorStore for 'memory' and raise informative error for 'pgvector'."""
    VectorStoreFactory.reset()
    store = VectorStoreFactory.get_vector_store(backend="memory", config=rag_config)
    assert isinstance(store, InMemoryVectorStore)

    # pgvector not installed yet
    with pytest.raises(NotImplementedError) as exc_info:
        VectorStoreFactory.get_vector_store(backend="pgvector", config=rag_config)
    assert "pgvector" in str(exc_info.value)

    # Unknown backend
    with pytest.raises(ValueError) as exc_info:
        VectorStoreFactory.get_vector_store(backend="unknown_backend", config=rag_config)
    assert "Unsupported vector store backend" in str(exc_info.value)


# ==============================================================================
# 5. Similarity, Hybrid Fusion, and MMR Tests
# ==============================================================================

def test_cosine_and_dot_product_similarity():
    """Verify standard cosine and dot product similarity computations."""
    vec_a = [1.0, 0.0, 0.0]
    vec_b = [1.0, 0.0, 0.0]
    vec_c = [0.0, 1.0, 0.0]

    assert cosine_similarity(vec_a, vec_b) == 1.0
    assert cosine_similarity(vec_a, vec_c) == 0.0
    assert dot_product(vec_a, vec_b) == 1.0


def test_reciprocal_rank_fusion():
    """Verify RRF rank aggregation combines dense and sparse candidate lists."""
    from smiota.rag.models import ScoredChunk

    def make_scored(cid: str, score: float):
        chunk = DocumentChunk(
            chunk_id=cid, document_id="doc", title="", category="", text="", chunk_index=0, token_count=1, content_hash=cid
        )
        return ScoredChunk(chunk=chunk, score=score)

    dense = [make_scored("A", 0.9), make_scored("B", 0.8), make_scored("C", 0.7)]
    sparse = [make_scored("B", 10.0), make_scored("A", 5.0), make_scored("D", 3.0)]

    fused = reciprocal_rank_fusion(dense, sparse, k=60)
    assert len(fused) == 4
    # "A" and "B" appeared high in both, so they should lead
    top_ids = [f.chunk.chunk_id for f in fused[:2]]
    assert "A" in top_ids and "B" in top_ids
    assert fused[0].rank == 1
    assert fused[1].rank == 2


def test_maximal_marginal_relevance():
    """Verify MMR balances query relevance with diversity to avoid duplicate chunks."""
    from smiota.rag.models import ScoredChunk

    query_emb = [0.8, 0.6]

    chunk_a = DocumentChunk(
        chunk_id="A", document_id="doc", title="", category="", text="A", chunk_index=0, token_count=1,
        content_hash="A", embedding=[1.0, 0.0]  # Sim(Q, A) = 0.8
    )
    chunk_b = DocumentChunk(
        chunk_id="B", document_id="doc", title="", category="", text="B", chunk_index=1, token_count=1,
        content_hash="B", embedding=[1.0, 0.0]  # Duplicate of A: Sim(A, B) = 1.0, Sim(Q, B) = 0.8
    )
    chunk_c = DocumentChunk(
        chunk_id="C", document_id="doc", title="", category="", text="C", chunk_index=2, token_count=1,
        content_hash="C", embedding=[0.0, 1.0]  # Orthogonal to A: Sim(A, C) = 0.0, Sim(Q, C) = 0.6
    )

    candidates = [
        ScoredChunk(chunk=chunk_a, score=0.8),
        ScoredChunk(chunk=chunk_b, score=0.8),
        ScoredChunk(chunk=chunk_c, score=0.6),
    ]

    selected = maximal_marginal_relevance(query_emb, candidates, top_k=2, lambda_mult=0.5)
    assert len(selected) == 2
    selected_ids = [s.chunk.chunk_id for s in selected]
    # MMR should pick A (highest relevance), then prefer C over redundant B for diversity
    assert "A" in selected_ids
    assert "C" in selected_ids
    assert "B" not in selected_ids


# ==============================================================================
# 6. End-to-End Retrieval & Ingestion Pipeline Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_retrieval_service_top_5(rag_config, memory_store, deterministic_embeddings):
    """Retrieval service retrieves top 5 most relevant chunks for user query."""
    retrieval_service = RetrievalService(
        vector_store=memory_store,
        embedding_service=deterministic_embeddings,
        config=rag_config,
    )

    # Index 8 varied chunks
    topics = [
        ("GKE high memory eviction and OOMKilled troubleshooting", "kubernetes"),
        ("GKE container memory limits and pod resource quotas", "kubernetes"),
        ("Prometheus alerting rules for GKE node memory pressure", "kubernetes"),
        ("Smart locker door solenoid mechanical jam diagnostics", "hardware"),
        ("Smart locker PIN retrieval and customer pickup flow", "customer"),
        ("Wazuh SIEM brute force detection and SSH lockout", "security"),
        ("Playwright regression test flakiness on checkout flow", "qa"),
        ("Terraform plan PR diff review and infrastructure CI/CD", "devops"),
    ]

    chunks = []
    for i, (text, cat) in enumerate(topics):
        emb = await deterministic_embeddings.embed_query(text)
        chunks.append(
            DocumentChunk(
                chunk_id=f"chk-{i}",
                document_id=f"doc-{i}",
                title=f"Doc {i}",
                category=cat,
                text=text,
                chunk_index=0,
                token_count=10,
                content_hash=f"hash-{i}",
                embedding=emb,
            )
        )
    await memory_store.upsert(chunks)

    # Query for Kubernetes memory issues
    results = await retrieval_service.retrieve("How do I investigate GKE memory exhaustion and pod evictions?", top_k=5)
    assert len(results) == 5
    assert results[0].rank == 1
    # The top result should be related to kubernetes memory
    assert "memory" in results[0].chunk.text.lower() or "gke" in results[0].chunk.text.lower()


@pytest.mark.asyncio
async def test_streaming_ingestion_pipeline(tmp_path, rag_config, memory_store, deterministic_embeddings):
    """Full streaming ingestion test verifying batching, stats, and memory efficiency."""
    ingestion_service = IngestionService(
        vector_store=memory_store,
        embedding_service=deterministic_embeddings,
        config=rag_config,
    )

    sample_jsonl = tmp_path / "runbooks.jsonl"
    records = [
        {"id": "doc-1", "title": "GKE Alert", "content": "Investigate high CPU usage and crash loops in pod."},
        {"id": "doc-2", "title": "Smart Locker", "content": "Reset the door lock solenoid sensor calibration."},
        {"id": "doc-3", "title": "SIEM Alert", "content": "Review Wazuh audit events for repeated failed logins."},
        {"INVALID": "NO TEXT HERE"},  # Invalid record
    ]
    sample_jsonl.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

    stats = await ingestion_service.ingest_file(sample_jsonl)

    assert stats.total_records_read == 4
    assert stats.valid_records == 3
    assert stats.invalid_records == 1
    assert stats.chunks_upserted >= 3
    assert stats.duration_seconds >= 0.0
    assert await memory_store.count() >= 3


@pytest.mark.asyncio
async def test_legacy_knowledge_retriever_compatibility():
    """Verify existing KnowledgeRetriever interface returns DocumentSearchResult."""
    retriever = KnowledgeRetriever()
    results = await retriever.retrieve(query="GKE high memory node eviction", category="runbook")
    assert len(results) > 0
    assert hasattr(results[0], "document_id")
    assert hasattr(results[0], "score")
    assert "runbook" in results[0].category


@pytest.mark.asyncio
async def test_directory_ingestion_with_mixed_file_types(tmp_path, rag_config, memory_store, deterministic_embeddings):
    """Verify scanning and ingesting a directory containing .jsonl, .json, and .md files."""
    knowledge_dir = tmp_path / "knowledge_base"
    knowledge_dir.mkdir()

    # 1. JSONL file
    (knowledge_dir / "alerts.jsonl").write_text(
        json.dumps({"id": "alert-1", "title": "Kafka Lag", "content": "Consumer lag exceeds threshold on topic."}) + "\n",
        encoding="utf-8",
    )

    # 2. JSON file (array)
    (knowledge_dir / "hardware.json").write_text(
        json.dumps([{"id": "hw-1", "title": "Battery Low", "content": "Backup battery voltage below 11.2V."}]),
        encoding="utf-8",
    )

    # 3. Markdown file
    (knowledge_dir / "deploy.md").write_text(
        "# Deployment Checklist\n\nEnsure database migrations run before releasing canary traffic.",
        encoding="utf-8",
    )

    ingestion_service = IngestionService(
        vector_store=memory_store,
        embedding_service=deterministic_embeddings,
        config=rag_config,
    )

    stats = await ingestion_service.ingest_directory(knowledge_dir)
    assert stats.valid_records == 3
    assert stats.chunks_upserted >= 3
    assert await memory_store.count() >= 3


def test_dynamic_chunk_context_prompt_injection():
    """Verify build_rag_prompt injects retrieved chunks between system prompt and user query."""
    from smiota.rag.models import DocumentChunk, ScoredChunk
    from smiota.rag.prompts import (
        SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT,
        build_rag_prompt,
    )

    chunk = DocumentChunk(
        chunk_id="chk-koha",
        document_id="doc-koha",
        title="Smiota Library Solutions",
        category="library",
        text="Smiota lockers integrate directly with Koha using standard SIP2 APIs.",
        chunk_index=0,
        token_count=12,
        content_hash="hash-koha",
        metadata={"canonical_url": "https://smiota.com/library/"},
    )
    scored = ScoredChunk(chunk=chunk, score=0.9234)

    user_query = "Can we connect Smiota with Koha ILS?"
    prompt = build_rag_prompt(user_message=user_query, retrieved_chunks=[scored])

    assert SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT in prompt
    assert "[RETRIEVED KNOWLEDGE CONTEXT]:" in prompt
    assert "https://smiota.com/library/" in prompt
    assert "Smiota lockers integrate directly with Koha" in prompt
    assert f"User: {user_query}" in prompt
    assert "RESPONSE FORMATTING & FAST SCANNING GUIDELINES" in SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT
    assert "FORMAT SELECTION" in SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT
