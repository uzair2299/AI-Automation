"""Standalone RAG Knowledge Microservice FastAPI Application."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure rag-service root directory is in sys.path when running from workspace root
_RAG_SERVICE_DIR = str(Path(__file__).resolve().parent.parent)
if _RAG_SERVICE_DIR not in sys.path:
    sys.path.insert(0, _RAG_SERVICE_DIR)

try:
    from app.chunking import DocumentChunker
    from app.config import settings
    from app.embeddings import EmbeddingService
    from app.loader import load_real_knowledge_base
    from app.logging import CorrelationIdMiddleware, setup_logging
    from app.models import (
        APIResponse,
        DocumentIngestionRequest,
        DocumentIngestionResponse,
        VectorSearchRequest,
        VectorSearchResponse,
    )
    from app.pgvector_store import PgVectorStoreClient
    from app.retriever import KnowledgeRetriever
    from app.vector_store import VectorStoreClient
except ImportError:
    from .chunking import DocumentChunker
    from .config import settings
    from .embeddings import EmbeddingService
    from .loader import load_real_knowledge_base
    from .logging import CorrelationIdMiddleware, setup_logging
    from .models import (
        APIResponse,
        DocumentIngestionRequest,
        DocumentIngestionResponse,
        VectorSearchRequest,
        VectorSearchResponse,
    )
    from .pgvector_store import PgVectorStoreClient
    from .retriever import KnowledgeRetriever
    from .vector_store import VectorStoreClient

# Initialize structured logging engine with correlation filter
logger = setup_logging()

# Shared service singletons with pgvector support
if getattr(settings, "VECTOR_STORE_BACKEND", "memory").lower() == "pgvector":
    vector_store = PgVectorStoreClient()
else:
    vector_store = VectorStoreClient()

embedding_service = EmbeddingService(dimension=settings.EMBEDDING_DIMENSION)
chunker = DocumentChunker(
    target_chunk_size=settings.TARGET_CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP
)
retriever = KnowledgeRetriever(
    vector_store=vector_store, embedding_service=embedding_service
)


async def seed_initial_documents():
    """Seed knowledge base using real website content JSONL, with graceful bootstrap fallback."""
    logger.info("Entering seed_initial_documents")
    global vector_store, retriever
    try:
        if await vector_store.count() > 0:
            logger.info(
                "Vector store already contains documents, skipping initial seed"
            )
            logger.info("Exiting seed_initial_documents")
            return
    except Exception as exc:
        logger.warning(
            "Could not connect to PostgreSQL pgvector (%s). Falling back to in-memory vector storage: %s",
            exc,
            exc,
            exc_info=True,
        )
        vector_store = VectorStoreClient()
        retriever = KnowledgeRetriever(
            vector_store=vector_store, embedding_service=embedding_service
        )

    try:
        # 1. Attempt to index real scraped knowledge base from website_content.jsonl
        stats = await load_real_knowledge_base(
            vector_store=vector_store,
            embedding_service=embedding_service,
            chunker=chunker,
            max_pages=getattr(settings, "SEED_MAX_PAGES", 50),
        )
        if stats.get("chunks_indexed", 0) > 0:
            logger.info("Exiting seed_initial_documents (indexed real knowledge base)")
            return
    except Exception as exc:
        logger.error("Error loading knowledge base during seed: %s", exc, exc_info=True)

    # 2. Minimal fallback only if knowledge file is missing
    logger.info("Falling back to builtin bootstrap seed documents")
    sample_docs = [
        (
            "Smiota Smart Locker Hardware Specs",
            "Smiota smart lockers feature NEMA 4 rated steel enclosures, dual-locking motorized solenoids, internal infrared parcel sensors, and high-resolution touchscreen control terminals.",
            "hardware",
        ),
        (
            "Smiota Resident Delivery Workflow",
            "When a carrier deposits a package, the locker controller captures dimensions and weight, closes the door, and issues a 6-digit numeric pickup PIN and dynamic QR code to the resident via SMS and email.",
            "workflow",
        ),
        (
            "Smiota Refrigerated & Cold Storage Lockers",
            "Smiota refrigerated smart lockers maintain strict temperature control between 34°F and 40°F (1°C to 4°C) for perishable groceries, meal kits, and temperature-sensitive pharmaceutical supplies.",
            "hardware",
        ),
    ]
    try:
        for title, content, cat in sample_docs:
            emb = await embedding_service.get_embedding(content)
            await vector_store.insert_document(
                title=title, content=content, embedding=emb, category=cat
            )
        logger.info("Exiting seed_initial_documents (bootstrap documents seeded)")
    except Exception as exc:
        logger.error(
            "Failed to insert sample bootstrap documents: %s", exc, exc_info=True
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up RAG service lifespan")
    try:
        await seed_initial_documents()
    except Exception as exc:
        logger.error(
            "Error during RAG service startup lifespan: %s", exc, exc_info=True
        )
    yield
    logger.info("Shutting down RAG service lifespan")


app = FastAPI(
    title="Smiota RAG Knowledge Service",
    description="Standalone REST microservice providing document ingestion and semantic vector retrieval.",
    version="1.0.0",
    lifespan=lifespan,
)

# Distributed correlation tracing and CORS middleware
app.add_middleware(CorrelationIdMiddleware, id_prefix="rag")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation failures and return structured response."""
    logger.warning(
        "Request validation failed on %s: %s", request.url.path, exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Request validation failed",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Log HTTP exceptions with proper details."""
    logger.warning(
        "HTTPException on %s [%d]: %s", request.url.path, exc.status_code, exc.detail
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions with full traceback logging."""
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An internal server error occurred"},
    )


@app.get("/health", summary="Health check")
async def health_check() -> Dict[str, Any]:
    """Return health status and count of indexed documents."""
    logger.info("Entering health_check endpoint")
    try:
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


@app.post(
    "/api/v1/rag/search",
    response_model=APIResponse[VectorSearchResponse],
    summary="Semantic vector search",
)
async def search_knowledge(payload: VectorSearchRequest):
    """Retrieve semantically relevant document chunks matching user query."""
    logger.info("Entering search_knowledge endpoint")
    try:
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


@app.post(
    "/api/v1/rag/ingest",
    response_model=APIResponse[DocumentIngestionResponse],
    summary="Ingest and chunk document",
)
async def ingest_document(payload: DocumentIngestionRequest):
    """Chunk, embed, and store document in vector storage."""
    logger.info("Entering ingest_document endpoint")
    try:
        chunks = chunker.split_text(payload.content)
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
        logger.info("Exiting ingest_document endpoint")
        return APIResponse(data=data, message="Document indexed successfully.")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error during ingest_document endpoint: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Document ingestion failed")


@app.post(
    "/api/v1/rag/sync",
    summary="Synchronize and ingest real website knowledge",
)
async def sync_knowledge():
    """Trigger on-demand ingestion of real website_content.jsonl knowledge."""
    logger.info("Entering sync_knowledge endpoint")
    try:
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
