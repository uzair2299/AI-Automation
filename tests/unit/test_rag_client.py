"""Unit tests for standalone RAGServiceClient."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from smiota.rag.client import RAGServiceClient
from smiota.rag.models import ScoredChunk


@pytest.mark.asyncio
async def test_rag_client_search_success():
    """Verify RAG client searches remote service and maps into ScoredChunk list."""
    client = RAGServiceClient(service_url="http://localhost:8001")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "success",
        "data": {
            "query": "solenoid voltage",
            "results": [
                {
                    "document_id": "doc-123",
                    "similarity_score": 0.94,
                    "document": {
                        "title": "Hardware Specs",
                        "category": "hardware",
                        "content": "Solenoid operates at 12V DC.",
                        "metadata": {"section": "power"},
                    },
                }
            ],
            "total_found": 1,
        },
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        chunks = await client.search(query="solenoid voltage", top_k=1)
        assert len(chunks) == 1
        assert isinstance(chunks[0], ScoredChunk)
        assert chunks[0].score == 0.94
        assert chunks[0].chunk.title == "Hardware Specs"
        assert chunks[0].chunk.text == "Solenoid operates at 12V DC."
        assert chunks[0].chunk.metadata == {"section": "power"}


@pytest.mark.asyncio
async def test_rag_client_ingest_success():
    """Verify document ingestion through REST client."""
    client = RAGServiceClient(service_url="http://localhost:8001")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "success",
        "data": {
            "document_id": "doc-999",
            "chunks_created": 3,
            "status": "indexed",
        },
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await client.ingest(
            title="Postmortem Jan 2026",
            content="Incident summary...",
            category="postmortem",
            tags=["network", "dns"],
        )
        assert result["data"]["document_id"] == "doc-999"
        assert result["data"]["chunks_created"] == 3


@pytest.mark.asyncio
async def test_rag_client_health():
    """Verify health endpoint querying."""
    client = RAGServiceClient(service_url="http://localhost:8001")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "ok",
        "service": "smiota-rag-service",
        "indexed_chunks": 15,
        "version": "1.0.0",
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        health = await client.health()
        assert health["status"] == "ok"
        assert health["indexed_chunks"] == 15


@pytest.mark.asyncio
async def test_rag_client_fallback_to_local_retriever():
    """Verify client gracefully falls back to local retriever if remote is unavailable."""
    client = RAGServiceClient(service_url="http://localhost:8001", enable_fallback=True)

    mock_retriever = MagicMock()
    mock_retriever.retrieve = AsyncMock(return_value=[])

    client._local_retriever = mock_retriever

    with patch("httpx.AsyncClient.post", side_effect=Exception("Connection refused")):
        chunks = await client.search(query="test query")
        assert chunks == []
        mock_retriever.retrieve.assert_awaited_once_with(query="test query", top_k=5)

