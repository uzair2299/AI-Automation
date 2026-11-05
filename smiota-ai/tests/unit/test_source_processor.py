"""Unit tests for SourceProcessor, RAG source deduplication, URL validation, and schema compatibility."""
import pytest
from services.source_processor import SourceProcessor, get_source_processor
from rag_client.models import DocumentChunk, ScoredChunk
from schemas.chat import SourceReference, ChatMessageResponse


def test_source_processor_defaults():
    """Verify default configurations of SourceProcessor."""
    processor = SourceProcessor()
    assert processor.max_displayed_sources == 5
    assert processor.enabled is True
    assert "smiota.com" in processor.allowed_domains


def test_safe_url_validation():
    """Verify that only safe HTTP/HTTPS URLs pass validation and unsafe protocols are rejected."""
    processor = SourceProcessor(allowed_domains=["smiota.com", "dev.smiota.com"])

    # Safe URLs
    assert processor.is_valid_url("https://smiota.com/resources/lockers") is True
    assert processor.is_valid_url("http://smiota.com/about") is True
    assert processor.is_valid_url("https://dev.smiota.com/status") is True

    # Disallowed domains
    assert processor.is_valid_url("https://malicious-site.com/exploit") is False

    # Blocked dangerous schemes (XSS prevention)
    assert processor.is_valid_url("javascript:alert(1)") is False
    assert processor.is_valid_url("data:text/html,<script>alert(1)</script>") is False
    assert processor.is_valid_url("file:///etc/passwd") is False
    assert processor.is_valid_url("vbscript:MsgBox(1)") is False

    # Blocked localhost / internal private IPs (SSRF & internal leakage prevention)
    assert processor.is_valid_url("http://localhost:8000/admin") is False
    assert processor.is_valid_url("http://127.0.0.1:5432") is False
    assert processor.is_valid_url("http://192.168.1.1/router") is False
    assert processor.is_valid_url("http://10.0.0.5/internal") is False


def test_source_type_inference():
    """Verify accurate classification of source types (website, pdf, runbook, internal_docs)."""
    processor = SourceProcessor()

    # PDF detection
    assert processor.infer_source_type("https://smiota.com/specs.pdf", "Specs") == "pdf"
    assert processor.infer_source_type("https://smiota.com/manual", "User Manual", category="pdf") == "pdf"

    # Runbook detection
    assert processor.infer_source_type("https://smiota.com/runbooks/install", "Installation Runbook") == "runbook"
    assert processor.infer_source_type("https://smiota.com/doc", "Hardware SOP", category="runbook") == "runbook"

    # Internal docs
    assert processor.infer_source_type("https://smiota.com/internal", "Internal Spec", category="internal") == "internal_docs"

    # Standard website
    assert processor.infer_source_type("https://smiota.com/smart-lockers", "Smart Lockers") == "website"


def test_title_sanitization_and_fallbacks():
    """Verify that multi-part suffixes are stripped and missing titles are derived from URL or document ID."""
    processor = SourceProcessor()

    # Stripping part suffixes
    assert processor.clean_title("Smart Locker Guide (Part 1)") == "Smart Locker Guide"
    assert processor.clean_title("Smart Locker Guide - Part 2") == "Smart Locker Guide"
    assert processor.clean_title("Smart Locker Guide [Part 3]") == "Smart Locker Guide"

    # Fallback to URL slug when title is empty
    fallback_title = processor.clean_title("", url="https://smiota.com/resources/what-are-smart-lockers")
    assert fallback_title == "What Are Smart Lockers"

    # Fallback to document ID when URL is missing or has no slug
    fallback_doc = processor.clean_title("", document_id="doc_refrigerated_lockers_spec")
    assert fallback_doc == "Doc Refrigerated Lockers Spec"


def test_source_deduplication_and_part_merging():
    """Verify that multi-part chunks from the same document/URL are deduplicated and retain highest score."""
    processor = SourceProcessor()

    chunks = [
        ScoredChunk(
            chunk=DocumentChunk(
                chunk_id="chk-1",
                document_id="doc-guide",
                title="Smart Locker Complete Guide (Part 1)",
                category="website",
                text="Introduction to smart lockers.",
                chunk_index=0,
                token_count=10,
                content_hash="h1",
                metadata={"canonical_url": "https://smiota.com/resources/smart-lockers/"},
            ),
            score=0.85,
        ),
        ScoredChunk(
            chunk=DocumentChunk(
                chunk_id="chk-2",
                document_id="doc-guide",
                title="Smart Locker Complete Guide (Part 2)",
                category="website",
                text="Advanced locker hardware details.",
                chunk_index=1,
                token_count=15,
                content_hash="h2",
                metadata={"canonical_url": "https://smiota.com/resources/smart-lockers/"},
            ),
            score=0.92,  # Higher score
        ),
        ScoredChunk(
            chunk=DocumentChunk(
                chunk_id="chk-3",
                document_id="doc-refrigerated",
                title="Refrigerated Lockers Spec",
                category="hardware",
                text="Cold storage temperatures.",
                chunk_index=0,
                token_count=12,
                content_hash="h3",
                metadata={"canonical_url": "https://smiota.com/hardware/cold-storage"},
            ),
            score=0.88,
        ),
    ]

    sources = processor.process_sources(chunks)

    # Should deduplicate 3 chunks into 2 unique sources
    assert len(sources) == 2

    # First source should have cleaned title and highest score
    smart_locker_src = next(s for s in sources if s.document_id == "doc-guide")
    assert smart_locker_src.title == "Smart Locker Complete Guide"
    assert smart_locker_src.relevance_score == 0.92
    assert smart_locker_src.domain == "smiota.com"
    assert smart_locker_src.source_type == "website"


def test_max_displayed_sources_enforcement():
    """Verify that returned sources do not exceed max_displayed_sources."""
    processor = SourceProcessor(max_displayed_sources=2)

    chunks = []
    for i in range(10):
        chunks.append(
            ScoredChunk(
                chunk=DocumentChunk(
                    chunk_id=f"chk-{i}",
                    document_id=f"doc-{i}",
                    title=f"Article {i}",
                    category="website",
                    text=f"Content {i}",
                    chunk_index=0,
                    token_count=5,
                    content_hash=f"h{i}",
                    metadata={"canonical_url": f"https://smiota.com/article-{i}"},
                ),
                score=0.90 - (i * 0.05),
            )
        )

    sources = processor.process_sources(chunks)
    assert len(sources) == 2
    assert sources[0].document_id == "doc-0"
    assert sources[1].document_id == "doc-1"


def test_sources_disabled_returns_empty():
    """Verify that when disabled, processor returns an empty list."""
    processor = SourceProcessor(enabled=False)

    chunk = ScoredChunk(
        chunk=DocumentChunk(
            chunk_id="chk-1",
            document_id="doc-1",
            title="Article",
            category="website",
            text="Content",
            chunk_index=0,
            token_count=5,
            content_hash="h",
            metadata={"canonical_url": "https://smiota.com/article"},
        ),
        score=0.9,
    )

    assert processor.process_sources([chunk]) == []


def test_empty_retrieval_returns_empty():
    """Verify empty input returns empty list."""
    processor = SourceProcessor()
    assert processor.process_sources([]) == []


def test_dict_chunk_handling():
    """Verify processor handles raw dict chunks from RAG service as well as ScoredChunk models."""
    processor = SourceProcessor()

    dict_chunks = [
        {
            "id": "dict-1",
            "title": "Raw Dict Article",
            "canonical_url": "https://smiota.com/raw-dict",
            "score": 0.89,
            "category": "website",
        }
    ]

    sources = processor.process_sources(dict_chunks)
    assert len(sources) == 1
    assert sources[0].title == "Raw Dict Article"
    assert sources[0].url == "https://smiota.com/raw-dict"
    assert sources[0].relevance_score == 0.89


def test_chat_message_response_backward_compatibility():
    """Verify ChatMessageResponse synchronizes answer and response bidirectionally."""
    # Case 1: Initialized with legacy 'response' only
    legacy_resp = ChatMessageResponse(
        session_id="sess-1",
        response="This is legacy text.",
        agent_used="knowledge",
    )
    assert legacy_resp.response == "This is legacy text."
    assert legacy_resp.answer == "This is legacy text."
    assert legacy_resp.sources == []

    # Case 2: Initialized with modern 'answer' and 'sources'
    modern_resp = ChatMessageResponse(
        session_id="sess-2",
        answer="This is modern answer.",
        agent_used="knowledge",
        sources=[
            SourceReference(
                title="Smiota Docs",
                url="https://smiota.com/docs",
                source_type="website",
                domain="smiota.com",
            )
        ],
    )
    assert modern_resp.answer == "This is modern answer."
    assert modern_resp.response == "This is modern answer."
    assert len(modern_resp.sources) == 1
    assert modern_resp.sources[0].title == "Smiota Docs"
