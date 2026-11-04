"""HTTP routes and API endpoints for RAG Knowledge Service."""
import logging
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
    load_real_knowledge_base,
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
    logger.info("Entering search_knowledge endpoint")
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
    logger.info("Entering ingest_document endpoint")
    try:
        chunker = get_chunker()
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()

        chunks = chunker.split_text(payload.content)
        first_doc_id = ""

        for idx, chunk in enumerate(chunks):
            emb = await embedding_service.get_embedding(chunk)
            doc_id = await vector_store.insert_document(
                title=f"{payload.title} (Part {idx+1})" if len(chunks) > 1 else payload.title,
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
        logger.info("Exiting ingest_document endpoint")
        return APIResponse(data=data, message="Document indexed successfully.")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error during ingest_document endpoint: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Document ingestion failed")


@router.post(
    "/api/v1/rag/sync",
    summary="Synchronize and ingest real website knowledge",
)
async def sync_knowledge():
    """Trigger on-demand ingestion of real website_content.jsonl knowledge."""
    logger.info("Entering sync_knowledge endpoint")
    try:
        vector_store = get_vector_store()
        embedding_service = get_embedding_service()
        chunker = get_chunker()

        stats = await load_real_knowledge_base(
            vector_store=vector_store,
            embedding_service=embedding_service,
            chunker=chunker,
        )
        count = await vector_store.count()
        logger.info("Exiting sync_knowledge endpoint")
        return APIResponse(
            data={"stats": stats, "total_chunks": count},
            message="Knowledge synchronization completed.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error during sync_knowledge endpoint: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Knowledge synchronization failed")

