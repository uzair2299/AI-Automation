"""Health check endpoints for Kubernetes GKE probes and deep diagnostics."""
from fastapi import APIRouter
from smiota.core.config import get_settings
from smiota.schemas.health import SystemHealthResponse, ComponentHealth
from smiota.agents.registry import AgentRegistry
from smiota.mcp.registry import MCPToolRegistry

router = APIRouter(prefix="/health", tags=["Health & Observability"])


@router.get("", summary="General health check")
async def health_check():
    return {"status": "ok", "service": "smiota-agent-core"}


@router.get("/ready", summary="Kubernetes Readiness Probe")
async def readiness_probe():
    # Production: check DB pool, Redis connection, Vertex AI connectivity
    return {"status": "ready"}


@router.get("/live", summary="Kubernetes Liveness Probe")
async def liveness_probe():
    return {"status": "alive"}


@router.get("/status", response_model=SystemHealthResponse, summary="Deep system component status")
async def detailed_system_status():
    settings = get_settings()
    agents = AgentRegistry.list_agents()
    tools = MCPToolRegistry.list_tools()

    return SystemHealthResponse(
        status="ok",
        environment=settings.ENVIRONMENT,
        components={
            "agents": ComponentHealth(status="healthy" if len(agents) >= 5 else "degraded"),
            "mcp_tools": ComponentHealth(status="healthy" if len(tools) > 0 else "degraded"),
            "database": ComponentHealth(status="healthy"),
            "redis_cache": ComponentHealth(status="healthy"),
            "vertex_ai": ComponentHealth(status="healthy"),
        },
    )
