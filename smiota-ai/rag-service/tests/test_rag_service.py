"""Unit tests for standalone RAG Service."""
import logging
from unittest.mock import patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app, seed_initial_documents


@pytest.fixture(autouse=True)
async def ensure_seeded():
    """Ensure database has initial seed documents."""
    await seed_initial_documents()


@pytest.mark.asyncio
async def test_rag_service_health(caplog):
    """Verify RAG service health endpoint and entry/exit logging."""
    with caplog.at_level(logging.INFO):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["service"] == "smiota-rag-service"
            assert data["indexed_chunks"] >= 3

    log_messages = [record.message for record in caplog.records]
    assert any("Entering health_check endpoint" in m for m in log_messages)
    assert any("Exiting health_check endpoint" in m for m in log_messages)


@pytest.mark.asyncio
async def test_rag_service_search(caplog):
    """Verify semantic search endpoint and entry/exit logging."""
    with caplog.at_level(logging.INFO):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/rag/search",
                json={"query": "refrigerated temperature", "top_k": 2},
            )
            assert response.status_code == 200
            res = response.json()
            assert res["status"] == "success"
            assert len(res["data"]["results"]) > 0
            first_doc = res["data"]["results"][0]["document"]
            assert "refrigerated" in first_doc["title"].lower() or "refrigerated" in first_doc["content"].lower()

    log_messages = [record.message for record in caplog.records]
    assert any("Entering search_knowledge endpoint" in m for m in log_messages)
    assert any("Exiting search_knowledge endpoint" in m for m in log_messages)
    assert any("Entering KnowledgeRetriever.retrieve" in m for m in log_messages)
    assert any("Exiting KnowledgeRetriever.retrieve" in m for m in log_messages)


@pytest.mark.asyncio
async def test_rag_service_ingest(caplog):
    """Verify document ingestion endpoint and entry/exit logging."""
    with caplog.at_level(logging.INFO):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/rag/ingest",
                json={
                    "title": "Battery Backup UPS Guidelines",
                    "content": "All Smiota locker towers include a 1500VA online UPS providing 4 hours of backup power in case of a utility outage.",
                    "category": "hardware",
                    "tags": ["power", "battery"],
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["chunks_created"] >= 1
            assert data["data"]["status"] == "indexed"

    log_messages = [record.message for record in caplog.records]
    assert any("Entering ingest_document endpoint" in m for m in log_messages)
    assert any("Exiting ingest_document endpoint" in m for m in log_messages)


@pytest.mark.asyncio
async def test_rag_service_correlation_id():
    """Verify correlation ID middleware preserves or generates X-Correlation-ID."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Custom correlation ID passed
        res = await ac.get("/health", headers={"X-Correlation-ID": "test-corr-12345"})
        assert res.headers.get("X-Correlation-ID") == "test-corr-12345"

        # 2. Auto-generated correlation ID when not passed
        res2 = await ac.get("/health")
        assert res2.headers.get("X-Correlation-ID") is not None
        assert res2.headers.get("X-Correlation-ID").startswith("rag-")


@pytest.mark.asyncio
async def test_rag_service_validation_error(caplog):
    """Verify validation errors are caught and logged with details."""
    with caplog.at_level(logging.WARNING):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Missing required field 'query'
            response = await ac.post("/api/v1/rag/search", json={"top_k": 5})
            assert response.status_code == 422
            data = response.json()
            assert data["status"] == "error"
            assert "validation" in data["message"].lower()

    log_messages = [record.message for record in caplog.records]
    assert any("Request validation failed" in m for m in log_messages)


@pytest.mark.asyncio
async def test_rag_service_error_handling(caplog):
    """Verify internal server errors are logged with exc_info and return clean 500 response."""
    with caplog.at_level(logging.ERROR):
        with patch("app.main.retriever.retrieve", side_effect=RuntimeError("Simulated database failure")):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post(
                    "/api/v1/rag/search",
                    json={"query": "test query", "top_k": 2},
                )
                assert response.status_code == 500
                data = response.json()
                assert data["status"] == "error"
                # Internal traceback details should not be leaked to the client response
                assert "Simulated database failure" not in data["message"]

    # Verify exception details and traceback were logged on server side
    error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(error_records) > 0
    assert any("Error during search_knowledge endpoint" in r.message for r in error_records)
    assert any(r.exc_info is not None for r in error_records)
