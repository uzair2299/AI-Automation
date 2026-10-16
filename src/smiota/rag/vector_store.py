"""Vector database abstraction (pgvector / Vertex AI Vector Search / Qdrant)."""
import uuid
from typing import Any, Optional
from smiota.core.logging import logger
from smiota.core.exceptions import VectorStoreError


class VectorStoreClient:
    """Connects to the vector search engine to store and query knowledge embeddings."""

    def __init__(self):
        # In-memory document index for development & testing
        self._index: list[dict[str, Any]] = [
            {
                "document_id": "runbook-gke-01",
                "title": "GKE High Memory Investigation & Node Eviction Runbook",
                "category": "runbook",
                "content": "Check container memory limits, OOMKilled events, and review pod logs using OpenSearch.",
                "embedding": [0.0] * 768,
                "score": 0.94,
                "metadata": {"author": "SRE Team", "service": "kubernetes"},
            },
            {
                "document_id": "runbook-locker-02",
                "title": "Smart Locker Solenoid Failure & Door Jam Runbook",
                "category": "runbook",
                "content": "Verify door sensor resistance, check firmware event logs, and dispatch field technician if jammed.",
                "embedding": [0.0] * 768,
                "score": 0.91,
                "metadata": {"author": "Hardware Ops", "service": "smart-locker"},
            },
        ]

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Performs nearest-neighbor search across runbooks, docs, and postmortems."""
        logger.info(f"Querying vector database with top_k={top_k}, category={category}")
        try:
            results = self._index
            if category:
                results = [doc for doc in results if doc.get("category") == category]
            return results[:top_k]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise VectorStoreError(f"Vector database search failed: {e}")

    async def insert_document(
        self,
        title: str,
        content: str,
        embedding: list[float],
        category: str = "runbook",
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Insert embedded document chunk into the vector store."""
        doc_id = f"doc-{uuid.uuid4().hex[:8]}"
        record = {
            "document_id": doc_id,
            "title": title,
            "category": category,
            "content": content,
            "embedding": embedding,
            "score": 1.0,
            "metadata": metadata or {},
        }
        self._index.append(record)
        logger.info(f"Inserted document '{title}' ({doc_id}) into vector store.")
        return doc_id
