"""REST Client for the decoupled standalone RAG Knowledge Service (Port 8001)."""
from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from smiota.core.config import get_settings
from smiota.core.logging import logger
from smiota.rag.models import DocumentChunk, ScoredChunk


class RAGServiceClient:
    """Asynchronous HTTP REST client to query and ingest into the standalone RAG Service."""

    def __init__(
        self,
        service_url: Optional[str] = None,
        timeout: float = 10.0,
        enable_fallback: bool = True,
    ):
        settings = get_settings()
        self.service_url = (service_url or getattr(settings, "RAG_SERVICE_URL", "http://localhost:8001")).rstrip("/")
        self.timeout = timeout
        self.enable_fallback = enable_fallback
        self._local_retriever = None

    def _get_local_retriever(self):
        """Offline fallback retriever hook (if injected)."""
        return self._local_retriever

    async def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> list[ScoredChunk]:
        """Perform semantic search against the standalone RAG service with local fallback."""
        url = f"{self.service_url}/api/v1/rag/search"
        payload = {
            "query": query,
            "top_k": top_k,
            "category": category,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    results_raw = data.get("data", {}).get("results", [])
                    if not results_raw and "results" in data:
                        results_raw = data["results"]

                    chunks: list[ScoredChunk] = []
                    for idx, item in enumerate(results_raw):
                        doc = item.get("document", item)
                        chunk_obj = DocumentChunk(
                            chunk_id=item.get("document_id", f"doc_{idx}"),
                            document_id=item.get("document_id", f"doc_{idx}"),
                            title=doc.get("title", "Documentation"),
                            category=doc.get("category", category or "general"),
                            text=doc.get("content", item.get("text", "")),
                            chunk_index=idx,
                            token_count=len(doc.get("content", "").split()),
                            content_hash="",
                            metadata=doc.get("metadata", {}),
                        )
                        chunks.append(
                            ScoredChunk(
                                chunk=chunk_obj,
                                score=float(item.get("similarity_score", item.get("score", 1.0))),
                                dense_score=float(item.get("similarity_score", item.get("score", 1.0))),
                                rank=idx + 1,
                            )
                        )
                    return chunks
                else:
                    logger.warning(f"RAG Service returned HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as exc:
            logger.warning(f"Remote RAG Service at {url} unreachable: {exc}")

        # Fallback to local RetrievalService
        if self.enable_fallback:
            retriever = self._get_local_retriever()
            if retriever:
                logger.info("Executing RAG search via local RetrievalService fallback.")
                return await retriever.retrieve(query=query, top_k=top_k)

        return []

    async def ingest(
        self,
        title: str,
        content: str,
        category: str = "general",
        metadata: Optional[dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Ingest document into the standalone RAG service."""
        url = f"{self.service_url}/api/v1/rag/ingest"
        payload = {
            "title": title,
            "content": content,
            "category": category,
            "metadata": metadata or {},
            "tags": tags or [],
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                return resp.json()
            raise RuntimeError(f"RAG ingestion failed with HTTP {resp.status_code}: {resp.text}")

    async def health(self) -> dict[str, Any]:
        """Check health status of the standalone RAG service."""
        url = f"{self.service_url}/health"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            return resp.json()

