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
from smiota.workflows.pubsub_listener import launch_listener_daemon


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    settings = get_settings()
    logger.info(f"Initializing {settings.PROJECT_NAME} in [{settings.ENVIRONMENT}] mode...")

    # 1. Register specialized AI Agents (AIOps, Security, Developer, QA, Customer)
    register_default_agents()

    # 2. Setup Telemetry & OpenTelemetry Tracing
    setup_telemetry(app)

    # 3. Launch background RabbitMQ event listener for real-time WebSocket push
    launch_listener_daemon()

    logger.info("Smiota Agent Core + MCP successfully initialized and ready to serve requests.")
    yield

    logger.info("Shutting down Smiota AI Platform services...")
    await RabbitMQService.close()
    await close_cache()
    await close_db()


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

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("smiota.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
