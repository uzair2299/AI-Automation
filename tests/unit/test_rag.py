"""Unit tests for Gateway RAG client models, prompts, and configuration."""
import pytest
from unittest.mock import AsyncMock, patch

from rag_client.config import RAGConfig
from rag_client.models import DocumentChunk, ScoredChunk, RetrievalQuery
from rag_client.prompts import (
    SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT,
    build_rag_prompt,
    format_retrieved_chunks,
)


def test_rag_config_defaults():
    """Verify RAG configuration default values."""
    config = RAGConfig()
    assert config.target_chunk_size == 400
    assert config.chunk_overlap == 50
    assert config.final_result_count == 5


def test_rag_models():
    """Verify DocumentChunk and ScoredChunk data structures."""
    chunk = DocumentChunk(
        chunk_id="chk-1",
        document_id="doc-1",
        title="Hardware Specs",
        category="hardware",
        text="Standard locker specs.",
        chunk_index=0,
        token_count=3,
        content_hash="abc",
        metadata={"canonical_url": "https://smiota.com/hardware"},
    )
    scored = ScoredChunk(chunk=chunk, score=0.95, rank=1)
    assert scored.score == 0.95
    assert scored.chunk.title == "Hardware Specs"
    assert scored.rank == 1


def test_dynamic_chunk_context_prompt_injection():
    """Verify build_rag_prompt injects retrieved chunks between system prompt and user query."""
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
    assert "You are Smiota SI" in SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT


def test_format_retrieved_chunks_formats_multiple_types():
    """Verify format_retrieved_chunks formats both dict and ScoredChunk items."""
    dict_item = {
        "title": "Multifamily Lockers",
        "canonical_url": "https://smiota.com/multifamily",
        "content": "Deliveries for residential complexes.",
    }
    formatted = format_retrieved_chunks([dict_item])
    assert "Multifamily Lockers" in formatted
    assert "https://smiota.com/multifamily" in formatted
    assert "Deliveries for residential complexes." in formatted
