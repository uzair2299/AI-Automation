"""In-memory Vector Store implementation with cosine similarity search."""
import logging
import math
from typing import Any, Dict, List, Optional
import uuid

from app.schemas.document import DocumentMetadata, DocumentSearchResult

logger = logging.getLogger("rag-service.storage.memory")


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two unit or raw vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStoreClient:
    """In-memory Vector Store client with cosine similarity search and category filtering."""

    def __init__(self):
        # document_id -> { "metadata": DocumentMetadata, "embedding": List[float] }
        self._storage: Dict[str, Dict[str, Any]] = {}

    async def insert_document(
        self,
        title: str,
        content: str,
        embedding: List[float],
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Insert embedded document chunk into store."""
        logger.debug("Entering VectorStoreClient.insert_document")
        try:
            doc_id = str(uuid.uuid4())
            doc_meta = DocumentMetadata(
                title=title,
                category=category,
                content=content,
                metadata=metadata or {},
                tags=metadata.get("tags", []) if metadata else [],
            )
            self._storage[doc_id] = {
                "metadata": doc_meta,
                "embedding": embedding,
            }
            logger.debug("Exiting VectorStoreClient.insert_document")
            return doc_id
        except Exception as exc:
            logger.error("Failed to insert document into VectorStoreClient: %s", exc, exc_info=True)
            raise

    async def insert_documents_batch(
        self,
        docs: List[Dict[str, Any]],
    ) -> List[str]:
        """Bulk insert multiple document chunks into in-memory store."""
        logger.info("Entering VectorStoreClient.insert_documents_batch")
        try:
            inserted_ids = []
            for d in docs:
                doc_id = str(d.get("document_id") or uuid.uuid4())
                meta = d.get("metadata") or {}
                tags = d.get("tags") or meta.get("tags", [])
                doc_meta = DocumentMetadata(
                    title=d.get("title", "Untitled"),
                    category=d.get("category", "general"),
                    content=d.get("content", ""),
                    metadata=meta,
                    tags=tags,
                )
                self._storage[doc_id] = {
                    "metadata": doc_meta,
                    "embedding": d.get("embedding", []),
                }
                inserted_ids.append(doc_id)
            logger.info("Exiting VectorStoreClient.insert_documents_batch")
            return inserted_ids
        except Exception as exc:
            logger.error("Failed to batch insert documents into VectorStoreClient: %s", exc, exc_info=True)
            raise

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> List[DocumentSearchResult]:
        """Perform nearest-neighbor search based on cosine similarity."""
        logger.info("Entering VectorStoreClient.search")
        try:
            scored: List[DocumentSearchResult] = []

            for doc_id, entry in self._storage.items():
                meta = entry["metadata"]
                if category and meta.category != category:
                    continue

                sim = cosine_similarity(query_embedding, entry["embedding"])
                scored.append(
                    DocumentSearchResult(
                        document_id=doc_id,
                        similarity_score=round(float(sim), 4),
                        document=meta,
                    )
                )

            scored.sort(key=lambda x: x.similarity_score, reverse=True)
            results = scored[:top_k]
            logger.info("Exiting VectorStoreClient.search")
            return results
        except Exception as exc:
            logger.error("Failed to execute search in VectorStoreClient: %s", exc, exc_info=True)
            raise

    async def count(self) -> int:
        """Return total number of stored documents."""
        logger.debug("Entering VectorStoreClient.count")
        cnt = len(self._storage)
        logger.debug("Exiting VectorStoreClient.count")
        return cnt

