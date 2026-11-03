"""Unit tests for standalone RAG Service."""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app, seed_initial_documents


@pytest.fixture(autouse=True)
async def ensure_seeded():
    """Ensure database has initial seed documents."""
    await seed_initial_documents()


@pytest.mark.asyncio
async def test_rag_service_health():
    """Verify RAG service health endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "smiota-rag-service"
        assert data["indexed_chunks"] >= 3


@pytest.mark.asyncio
async def test_rag_service_search():
    """Verify semantic search endpoint."""
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


@pytest.mark.asyncio
async def test_rag_service_ingest():
    """Verify document ingestion endpoint."""
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
