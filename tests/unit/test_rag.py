"""Unit tests for RAG chunker and vector retrieval."""
import pytest
from smiota.rag.chunking import DocumentChunker
from smiota.rag.retriever import KnowledgeRetriever


def test_document_chunker():
    chunker = DocumentChunker(chunk_size=100)
    text = "# Section 1\nThis is paragraph one.\n\n## Section 2\nThis is paragraph two."
    chunks = chunker.split_text(text)
    assert len(chunks) >= 2


@pytest.mark.asyncio
async def test_knowledge_retriever():
    retriever = KnowledgeRetriever()
    results = await retriever.retrieve(query="GKE high memory node eviction", category="runbook")
    assert len(results) > 0
    assert "runbook" in results[0].category
