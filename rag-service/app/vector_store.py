"""Vector Store backend for storing and querying embedded documents."""
import math
import uuid
from typing import Any, Dict, List, Optional
from app.models import DocumentMetadata, DocumentSearchResult


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
        return doc_id

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> List[DocumentSearchResult]:
        """Perform nearest-neighbor search based on cosine similarity."""
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

        # Sort descending by similarity score
        scored.sort(key=lambda x: x.similarity_score, reverse=True)
        return scored[:top_k]

    async def count(self) -> int:
        """Return total indexed chunks."""
        return len(self._storage)

