"""HTTP routes and API endpoints for RAG Knowledge Service."""

import logging
import time
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.document import (
    APIResponse,
    DocumentIngestionRequest,
    DocumentIngestionResponse,
    VectorSearchRequest,
    VectorSearchResponse,
)
from app.services import (
    get_chunker,
    get_embedding_service,
    get_retriever,
)
from app.storage import get_vector_store

logger = logging.getLogger("rag-service.api")

router = APIRouter()


@router.get("/health", summary="Health check")
async def health_check() -> Dict[str, Any]:
    """Return health status and count of indexed documents."""
    logger.info("Entering health_check endpoint")
    try:
        vector_store = get_vector_store()
        count = await vector_store.count()
        backend_name = type(vector_store).__name__
        logger.info(
            "health_check: backend=%s (%s), indexed_chunks=%d, status=ok",
            settings.VECTOR_STORE_BACKEND,
            backend_name,
            count,
        )
        logger.info("Exiting health_check endpoint")
        return {
            "status": "ok",
            "service": settings.SERVICE_NAME,
            "indexed_chunks": count,
            "version": "1.0.0",
        }
    except Exception as exc:
        logger.error("Error during health_check endpoint: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed")


@router.post(
    "/api/v1/rag/search",
    response_model=APIResponse[VectorSearchResponse],
    summary="Semantic vector search",
)
async def search_knowledge(payload: VectorSearchRequest):
    """Retrieve semantically relevant document chunks matching user query."""
    start_time = time.perf_counter()
    logger.info("Entering search_knowledge endpoint")
    logger.info(
        "search_knowledge: Request received -> query='%s', top_k=%d, category=%s",
        payload.query,
        payload.top_k,
        payload.category or "all",
    )
    try:
        retriever = get_retriever()
        results = await retriever.retrieve(
            query=payload.query,
            category=payload.category,
            top_k=payload.top_k,
        )
        data = VectorSearchResponse(
            query=payload.query,
            results=results,
            total_found=len(results),
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "search_knowledge: Completed in %.2fms. Returning %d matched chunks to client for query='%s'",
            elapsed_ms,
            len(results),
            payload.query,
        )
        logger.info("Exiting search_knowledge endpoint")
        return APIResponse(data=data, message="Search completed successfully.")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error during search_knowledge endpoint: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Vector search operation failed")


@router.post(
    "/api/v1/rag/ingest",
    response_model=APIResponse[DocumentIngestionResponse],
    summary="Ingest and chunk document",
)
async def ingest_document(payload: DocumentIngestionRequest):
    """Chunk, embed, and store document in vector storage."""
    start_time = time.perf_counter()
    logger.info("Entering ingest_document endpoint")
    logger.info(
        "ingest_document: Request received -> title='%s', category=%s, content_length=%d chars",
        payload.title,
        payload.category,
        len(payload.content),
    )
    try:
        chunker = get_chunker()
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()

        chunks = chunker.split_text(payload.content)
        logger.info(
            "ingest_document: Document split into %d chunks. Generating embeddings and storing into %s...",
            len(chunks),
            type(vector_store).__name__,
        )
        first_doc_id = ""

        for idx, chunk in enumerate(chunks):
            emb = await embedding_service.get_embedding(chunk)
            doc_id = await vector_store.insert_document(
                title=(
                    f"{payload.title} (Part {idx+1})"
                    if len(chunks) > 1
                    else payload.title
                ),
                content=chunk,
                embedding=emb,
                category=payload.category,
                metadata={**payload.metadata, "tags": payload.tags},
            )
            if not first_doc_id:
                first_doc_id = doc_id

        data = DocumentIngestionResponse(
            document_id=first_doc_id,
            chunks_created=len(chunks),
            status="indexed",
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "ingest_document: Completed in %.2fms. Ingested %d chunks (primary_id=%s) for title='%s'",
            elapsed_ms,
            len(chunks),
            first_doc_id[:8],
            payload.title,
        )
        logger.info("Exiting ingest_document endpoint")
        return APIResponse(data=data, message="Document indexed successfully.")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error during ingest_document endpoint: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Document ingestion failed")



