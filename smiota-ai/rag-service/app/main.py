"""Standalone RAG Knowledge Microservice FastAPI Application."""
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure rag-service root directory is in sys.path when running from workspace root
_RAG_SERVICE_DIR = str(Path(__file__).resolve().parent.parent)
if _RAG_SERVICE_DIR not in sys.path:
    sys.path.insert(0, _RAG_SERVICE_DIR)

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import CorrelationIdMiddleware, setup_logging
from app.schemas.document import APIResponse
from app.services import (
    DocumentChunker,
    EmbeddingService,
    KnowledgeRetriever,
    get_chunker,
    get_embedding_service,
    get_retriever,
    load_real_knowledge_base,
    set_retriever,
)
from app.storage import (
    PgVectorStoreClient,
    VectorStoreClient,
    get_vector_store,
    set_vector_store,
)

# Initialize structured logging engine with correlation filter
logger = setup_logging()

# Expose module-level singletons for backward compatibility and test mockability
vector_store = get_vector_store()
embedding_service = get_embedding_service()
chunker = get_chunker()
retriever = get_retriever()


async def seed_initial_documents():
    """Seed knowledge base using real website content JSONL."""
    logger.info("Entering seed_initial_documents")
    global vector_store, retriever
    current_store = get_vector_store()
    try:
        if await current_store.count() > 0:
            logger.info("Vector store already contains documents, skipping initial seed")
            logger.info("Exiting seed_initial_documents")
            return
    except Exception as exc:
        logger.warning(
            "Could not connect to PostgreSQL pgvector (%s). Falling back to in-memory vector storage: %s",
            exc,
            exc,
            exc_info=True,
        )
        current_store = VectorStoreClient()
        set_vector_store(current_store)
        vector_store = current_store
        new_retriever = KnowledgeRetriever(
            vector_store=current_store,
            embedding_service=get_embedding_service(),
        )
        set_retriever(new_retriever)
        retriever = new_retriever

    try:
        # Index real knowledge base strictly from website_content.jsonl
        stats = await load_real_knowledge_base(
            vector_store=current_store,
            embedding_service=get_embedding_service(),
            chunker=get_chunker(),
            max_pages=getattr(settings, "SEED_MAX_PAGES", 50),
        )
        if stats.get("chunks_indexed", 0) > 0:
            logger.info(
                "Successfully seeded real knowledge base: %d chunks indexed",
                stats.get("chunks_indexed", 0),
            )
            logger.info("Exiting seed_initial_documents (indexed real knowledge base)")
            return
        logger.warning(
            "No chunks indexed from knowledge file (stats: %s). Vector store remains empty without mocked fallbacks.",
            stats,
        )
    except Exception as exc:
        logger.error(
            "Error loading real knowledge base during seed: %s. Vector store remains unseeded.",
            exc,
            exc_info=True,
        )

    logger.info("Exiting seed_initial_documents")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up RAG service lifespan")
    try:
        await seed_initial_documents()
    except Exception as exc:
        logger.error("Error during RAG service startup lifespan: %s", exc, exc_info=True)
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
    logger.warning("Request validation failed on %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Request validation failed", "errors": exc.errors()},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Log HTTP exceptions with proper details."""
    logger.warning("HTTPException on %s [%d]: %s", request.url.path, exc.status_code, exc.detail)
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


# Mount all API routes
app.include_router(api_router)


__all__ = [
    "app",
    "chunker",
    "embedding_service",
    "retriever",
    "seed_initial_documents",
    "vector_store",
]
