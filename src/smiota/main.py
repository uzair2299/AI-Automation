"""FastAPI application factory and ASGI entrypoint for Smiota AI Platform."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from smiota.core.config import get_settings
from smiota.core.logging import logger
from smiota.core.telemetry import setup_telemetry
from smiota.core.exceptions import SmiotaException
from smiota.core.database import close_db
from smiota.core.cache import close_cache
from smiota.agents import register_default_agents
from smiota.api.v1.router import api_v1_router
from smiota.api.middleware.correlation import CorrelationIdMiddleware
from smiota.api.middleware.error_handler import smiota_exception_handler

# Ensure MCP domain tools are registered into registry
import smiota.mcp.servers.observability.tools  # noqa: F401
import smiota.mcp.servers.security.tools       # noqa: F401
import smiota.mcp.servers.devops.tools         # noqa: F401
import smiota.mcp.servers.qa.tools             # noqa: F401
import smiota.mcp.servers.customer.tools       # noqa: F401


from smiota.core.rabbitmq import RabbitMQService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    settings = get_settings()
    logger.info(f"Initializing {settings.PROJECT_NAME} in [{settings.ENVIRONMENT}] mode...")

    # 0. Ensure Google Cloud / Vertex AI credentials setup (local or Railway/Docker)
    from smiota.llm.provider import _ensure_gcp_credentials
    _ensure_gcp_credentials()

    # 1. Register specialized AI Agents (AIOps, Security, Developer, QA, Customer)
    register_default_agents()

    # 2. Setup Telemetry & OpenTelemetry Tracing
    setup_telemetry(app)

    # 3. Background indexing of public knowledge base
    import asyncio

    async def _index_public_knowledge_on_startup() -> None:
        from pathlib import Path

        from smiota.rag.config import RAGConfig
        from smiota.rag.ingestion.ingestion_service import IngestionService
        from smiota.rag.vector_store.factory import VectorStoreFactory

        try:
            config = RAGConfig.from_settings()
            store = VectorStoreFactory.get_vector_store(config=config)
            count = await store.count()
            if count == 0 and Path(config.knowledge_dir).exists():
                logger.info(
                    f"Indexing public knowledge directory: '{config.knowledge_dir}'",
                    extra={"event": "rag.startup.indexing_started", "dir": config.knowledge_dir},
                )
                service = IngestionService(vector_store=store, config=config)
                stats = await service.ingest_directory(config.knowledge_dir)
                logger.info(
                    f"Public knowledge indexed: {stats.chunks_upserted} chunks from {stats.valid_records} records",
                    extra={"event": "rag.startup.indexing_completed", "chunks": stats.chunks_upserted},
                )
        except (OSError, RuntimeError, ValueError) as exc:
            logger.warning(
                f"Startup knowledge indexing skipped: {exc}",
                extra={"event": "rag.startup.indexing_failed", "error": str(exc)},
            )

    asyncio.create_task(_index_public_knowledge_on_startup())

    logger.info("Smiota Agent Core + MCP successfully initialized and ready to serve requests.")
    yield

    logger.info("Shutting down Smiota AI Platform services...")
    await RabbitMQService.close()
    await close_cache()
    await close_db()
    try:
        from smiota.clients.smiota_api_client import get_smiota_api_client
        await get_smiota_api_client().close()
    except Exception as client_err:
        logger.debug(f"Error closing SmiotaApiClient: {client_err}")


def create_app() -> FastAPI:
    """Build and configure the enterprise FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        description="Unified AIOps, DevSecOps, and Customer AI Platform powered by Gemini & MCP.",
        lifespan=lifespan,
        docs_url="/docs" if settings.ENABLE_SWAGGER else None,
        redoc_url="/redoc" if settings.ENABLE_SWAGGER else None,
        openapi_url="/openapi.json" if settings.ENABLE_SWAGGER else None,
    )

    # 1. Distributed Tracing Correlation Middleware
    app.add_middleware(CorrelationIdMiddleware)

    # 2. Cross-Origin Resource Sharing (CORS) for Web Chat and IDE extensions
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. Global Exception Handler
    app.add_exception_handler(SmiotaException, smiota_exception_handler)

    # 4. Mount API v1 router
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    # 5. Direct root mount for auth exchange endpoint (/auth/exchange)
    from smiota.api.v1.auth import router as auth_router
    app.include_router(auth_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("smiota.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
