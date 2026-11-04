"""PostgreSQL pgvector storage adapter for RAG Knowledge Service."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
import uuid

import asyncpg

from app.core.config import settings
from app.schemas.document import DocumentMetadata, DocumentSearchResult

logger = logging.getLogger("rag-service.storage.pgvector")


class PgVectorStoreClient:
    """PostgreSQL storage backend leveraging the pgvector extension for similarity search."""

    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or settings.DATABASE_URL
        self._pool: Optional[asyncpg.Pool] = None

    async def get_pool(self) -> asyncpg.Pool:
        """Initialize or retrieve connection pool and ensure table schema exists."""
        if self._pool is None:
            clean_dsn = self.dsn.replace("postgresql+asyncpg://", "postgresql://")
            try:
                self._pool = await asyncpg.create_pool(clean_dsn, min_size=1, max_size=10, timeout=10.0)
                await self._init_schema()
            except Exception as exc:
                logger.error("Failed to initialize PostgreSQL connection pool: %s", exc, exc_info=True)
                raise
        return self._pool

    async def _init_schema(self) -> None:
        """Create pgvector extension and rag_documents table if not present."""
        logger.info("Entering PgVectorStoreClient._init_schema")
        if not self._pool:
            logger.warning("No pool available for PgVectorStoreClient._init_schema")
            return
        try:
            async with self._pool.acquire() as conn:
                try:
                    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                except Exception as e:
                    logger.warning("Could not create vector extension (may require superuser or pre-enabled): %s", e)

                await conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS rag_documents (
                        document_id VARCHAR(64) PRIMARY KEY,
                        title TEXT NOT NULL,
                        category VARCHAR(64) NOT NULL DEFAULT 'general',
                        content TEXT NOT NULL,
                        metadata JSONB DEFAULT '{{}}'::jsonb,
                        tags TEXT[] DEFAULT ARRAY[]::TEXT[],
                        embedding vector({settings.EMBEDDING_DIMENSION})
                    );
                    """
                )
            logger.info("Exiting PgVectorStoreClient._init_schema")
        except Exception as exc:
            logger.error("Database schema initialization failed in PgVectorStoreClient: %s", exc, exc_info=True)
            raise

    async def insert_document(
        self,
        title: str,
        content: str,
        embedding: List[float],
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Insert document chunk and its embedding vector into PostgreSQL."""
        logger.info("Entering PgVectorStoreClient.insert_document")
        try:
            pool = await self.get_pool()
            doc_id = str(uuid.uuid4())
            meta = metadata or {}
            tags = meta.get("tags", [])
            vector_str = f"[{','.join(str(x) for x in embedding)}]"

            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO rag_documents (document_id, title, category, content, metadata, tags, embedding)
                    VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7::vector)
                    ON CONFLICT (document_id) DO UPDATE
                    SET title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding;
                    """,
                    doc_id,
                    title,
                    category,
                    content,
                    json.dumps(meta),
                    tags,
                    vector_str,
                )
            logger.info("Exiting PgVectorStoreClient.insert_document")
            return doc_id
        except Exception as exc:
            logger.error("Failed to insert document into pgvector: %s", exc, exc_info=True)
            raise

    async def insert_documents_batch(
        self,
        docs: List[Dict[str, Any]],
    ) -> List[str]:
        """Bulk insert multiple document chunks into PostgreSQL with pgvector."""
        logger.info("Entering PgVectorStoreClient.insert_documents_batch")
        if not docs:
            logger.info("Exiting PgVectorStoreClient.insert_documents_batch (empty batch)")
            return []
        try:
            pool = await self.get_pool()
            records = []
            doc_ids = []
            for d in docs:
                doc_id = str(d.get("document_id") or uuid.uuid4())
                doc_ids.append(doc_id)
                meta = d.get("metadata") or {}
                tags = d.get("tags") or meta.get("tags", [])
                emb = d.get("embedding", [])
                vector_str = f"[{','.join(str(x) for x in emb)}]"
                records.append((
                    doc_id,
                    d.get("title", "Untitled"),
                    d.get("category", "general"),
                    d.get("content", ""),
                    json.dumps(meta),
                    tags,
                    vector_str,
                ))
            async with pool.acquire() as conn:
                await conn.executemany(
                    """
                    INSERT INTO rag_documents (document_id, title, category, content, metadata, tags, embedding)
                    VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7::vector)
                    ON CONFLICT (document_id) DO NOTHING;
                    """,
                    records,
                )
            logger.info("Exiting PgVectorStoreClient.insert_documents_batch")
            return doc_ids
        except Exception as exc:
            logger.error("Failed to insert documents batch into pgvector: %s", exc, exc_info=True)
            raise

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> List[DocumentSearchResult]:
        """Nearest-neighbor cosine distance search using pgvector (<=> operator)."""
        logger.info("Entering PgVectorStoreClient.search")
        try:
            pool = await self.get_pool()
            vector_str = f"[{','.join(str(x) for x in query_embedding)}]"

            async with pool.acquire() as conn:
                if category:
                    rows = await conn.fetch(
                        """
                        SELECT document_id, title, category, content, metadata, tags,
                               1 - (embedding <=> $1::vector) AS similarity_score
                        FROM rag_documents
                        WHERE category = $2
                        ORDER BY embedding <=> $1::vector
                        LIMIT $3;
                        """,
                        vector_str,
                        category,
                        top_k,
                    )
                else:
                    rows = await conn.fetch(
                        """
                        SELECT document_id, title, category, content, metadata, tags,
                               1 - (embedding <=> $1::vector) AS similarity_score
                        FROM rag_documents
                        ORDER BY embedding <=> $1::vector
                        LIMIT $2;
                        """,
                        vector_str,
                        top_k,
                    )

                results: List[DocumentSearchResult] = []
                for r in rows:
                    meta = json.loads(r["metadata"]) if isinstance(r["metadata"], str) else (r["metadata"] or {})
                    doc_meta = DocumentMetadata(
                        title=r["title"],
                        category=r["category"],
                        content=r["content"],
                        metadata=meta,
                        tags=r["tags"] or [],
                    )
                    results.append(
                        DocumentSearchResult(
                            document_id=r["document_id"],
                            similarity_score=round(float(r["similarity_score"]), 4),
                            document=doc_meta,
                        )
                    )
                logger.info("Exiting PgVectorStoreClient.search")
                return results
        except Exception as exc:
            logger.error("Failed to execute search in pgvector: %s", exc, exc_info=True)
            raise

    async def count(self) -> int:
        """Count total stored document chunks."""
        logger.debug("Entering PgVectorStoreClient.count")
        try:
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                val = await conn.fetchval("SELECT COUNT(*) FROM rag_documents;")
                res = int(val or 0)
                logger.debug("Exiting PgVectorStoreClient.count")
                return res
        except Exception as exc:
            logger.error("Failed to get document count from pgvector: %s", exc, exc_info=True)
            raise

