"""High-performance in-memory vector store with cosine similarity, deduplication, and BM25 index."""
import asyncio
import math
import re
from typing import Any

from smiota.core.logging import logger
from smiota.rag.config import RAGConfig
from smiota.rag.models import DocumentChunk, ScoredChunk
from smiota.rag.retrieval.similarity import cosine_similarity, dot_product
from smiota.rag.vector_store.base import BaseVectorStore


class InMemoryVectorStore(BaseVectorStore):
    """Thread-safe in-memory vector store supporting dense similarity and BM25 keyword search."""

    def __init__(self, config: RAGConfig | None = None):
        self.config = config or RAGConfig()
        self._chunks: dict[str, DocumentChunk] = {}
        self._content_hashes: dict[str, str] = {}  # content_hash -> chunk_id
        self._inverted_index: dict[str, set[str]] = {}  # token -> set of chunk_ids
        self._doc_lens: dict[str, int] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Normalize text into alphanumeric lowercase tokens."""
        return re.findall(r"\w+", text.lower())

    async def upsert(self, chunks: list[DocumentChunk]) -> int:
        """Insert or update chunks, deduplicating via content hash."""
        async with self._lock:
            upserted_count = 0

            for chunk in chunks:
                existing_cid = self._content_hashes.get(chunk.content_hash)
                if existing_cid and existing_cid != chunk.chunk_id:
                    # Duplicate content already exists under different ID
                    continue

                # Add to primary chunk store
                self._chunks[chunk.chunk_id] = chunk
                self._content_hashes[chunk.content_hash] = chunk.chunk_id

                # Update inverted index for BM25
                tokens = self._tokenize(chunk.text)
                self._doc_lens[chunk.chunk_id] = len(tokens)
                for token in set(tokens):
                    if token not in self._inverted_index:
                        self._inverted_index[token] = set()
                    self._inverted_index[token].add(chunk.chunk_id)

                upserted_count += 1

            logger.debug(
                f"Upserted {upserted_count}/{len(chunks)} chunks into InMemoryVectorStore (total: {len(self._chunks)})",
                extra={
                    "event": "vector_store.upserted",
                    "upserted_count": upserted_count,
                    "total_chunks": len(self._chunks),
                },
            )
            return upserted_count

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        category: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[ScoredChunk]:
        """Perform dense vector similarity search."""
        if not self._chunks:
            return []

        use_cosine = self.config.similarity_metric == "cosine"
        scored: list[ScoredChunk] = []

        for chunk in self._chunks.values():
            # Category filter
            if category and chunk.category.lower() != category.lower():
                continue

            # Metadata key-value filters
            if filters:
                match = True
                for k, v in filters.items():
                    if chunk.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            # Similarity computation
            if chunk.embedding and query_embedding:
                score = (
                    cosine_similarity(query_embedding, chunk.embedding)
                    if use_cosine
                    else dot_product(query_embedding, chunk.embedding)
                )
            else:
                score = 0.0

            scored.append(
                ScoredChunk(
                    chunk=chunk,
                    score=score,
                    dense_score=score,
                    sparse_score=0.0,
                )
            )

        # Sort descending by similarity score
        scored.sort(key=lambda x: x.score, reverse=True)
        top_candidates = scored[:top_k]

        for rank, item in enumerate(top_candidates, start=1):
            item.rank = rank

        return top_candidates

    async def search_bm25(
        self,
        query_text: str,
        top_k: int = 20,
        category: str | None = None,
    ) -> list[ScoredChunk]:
        """Perform sparse BM25 ranking across stored chunks."""
        query_tokens = self._tokenize(query_text)
        if not query_tokens or not self._chunks:
            return []

        num_docs = len(self._chunks)
        avg_doc_len = sum(self._doc_lens.values()) / max(1, num_docs)
        k1 = 1.5
        b = 0.75

        scores: dict[str, float] = {}

        for token in query_tokens:
            posting_list = self._inverted_index.get(token, set())
            if not posting_list:
                continue

            # BM25 IDF
            df = len(posting_list)
            idf = math.log((num_docs - df + 0.5) / (df + 0.5) + 1.0)

            for cid in posting_list:
                chunk = self._chunks.get(cid)
                if not chunk:
                    continue
                if category and chunk.category.lower() != category.lower():
                    continue

                doc_len = self._doc_lens.get(cid, 1)
                # Term frequency
                tf = chunk.text.lower().count(token)
                numerator = tf * (k1 + 1.0)
                denominator = tf + k1 * (1.0 - b + b * (doc_len / avg_doc_len))
                bm25_term = idf * (numerator / max(1e-6, denominator))
                scores[cid] = scores.get(cid, 0.0) + bm25_term

        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        results: list[ScoredChunk] = []

        for rank, (cid, score) in enumerate(sorted_items, start=1):
            results.append(
                ScoredChunk(
                    chunk=self._chunks[cid],
                    score=score,
                    dense_score=0.0,
                    sparse_score=score,
                    rank=rank,
                )
            )

        return results

    async def delete(self, chunk_ids: list[str]) -> int:
        """Remove chunks by ID."""
        async with self._lock:
            deleted = 0
            for cid in chunk_ids:
                chunk = self._chunks.pop(cid, None)
                if chunk:
                    self._content_hashes.pop(chunk.content_hash, None)
                    self._doc_lens.pop(cid, None)
                    deleted += 1

            # Clean inverted index
            for token, id_set in list(self._inverted_index.items()):
                id_set.difference_update(chunk_ids)
                if not id_set:
                    del self._inverted_index[token]

            return deleted

    async def count(self) -> int:
        return len(self._chunks)

    async def health_check(self) -> bool:
        return True


class VectorStoreClient:
    """Backward-compatible client adapter for legacy imports."""

    def __init__(self, store: InMemoryVectorStore | None = None):
        self._store = store or InMemoryVectorStore()
        self._seed_default_runbooks()

    def _seed_default_runbooks(self) -> None:
        """Seed default sample runbooks synchronously to preserve test fixtures."""
        sample_chunks = [
            DocumentChunk(
                chunk_id="runbook-gke-01",
                document_id="runbook-gke-01",
                title="GKE High Memory Investigation & Node Eviction Runbook",
                category="runbook",
                text="Check container memory limits, OOMKilled events, and review pod logs using OpenSearch.",
                chunk_index=0,
                token_count=18,
                content_hash="seed-hash-gke",
                embedding=[0.0] * 768,
                metadata={"author": "SRE Team", "service": "kubernetes"},
            ),
            DocumentChunk(
                chunk_id="runbook-locker-02",
                document_id="runbook-locker-02",
                title="Smart Locker Solenoid Failure & Door Jam Runbook",
                category="runbook",
                text="Verify door sensor resistance, check firmware event logs, and dispatch field technician if jammed.",
                chunk_index=0,
                token_count=19,
                content_hash="seed-hash-locker",
                embedding=[0.0] * 768,
                metadata={"author": "Hardware Ops", "service": "smart-locker"},
            ),
        ]
        for chunk in sample_chunks:
            self._store._chunks[chunk.chunk_id] = chunk
            self._store._content_hashes[chunk.content_hash] = chunk.chunk_id
            tokens = self._store._tokenize(chunk.text)
            self._store._doc_lens[chunk.chunk_id] = len(tokens)
            for token in set(tokens):
                if token not in self._store._inverted_index:
                    self._store._inverted_index[token] = set()
                self._store._inverted_index[token].add(chunk.chunk_id)

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        results = await self._store.search(query_embedding=query_embedding, top_k=top_k, category=category)
        return [
            {
                "document_id": r.chunk.document_id,
                "title": r.chunk.title,
                "category": r.chunk.category,
                "content": r.chunk.text,
                "embedding": r.chunk.embedding,
                "score": r.score,
                "metadata": r.chunk.metadata,
            }
            for r in results
        ]

    async def insert_document(
        self,
        title: str,
        content: str,
        embedding: list[float],
        category: str = "runbook",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        import uuid
        doc_id = f"doc-{uuid.uuid4().hex[:8]}"
        chunk = DocumentChunk(
            chunk_id=f"{doc_id}-chk-0",
            document_id=doc_id,
            title=title,
            category=category,
            text=content,
            chunk_index=0,
            token_count=len(content.split()),
            content_hash=f"hash-{doc_id}",
            embedding=embedding,
            metadata=metadata or {},
        )
        await self._store.upsert([chunk])
        return doc_id
