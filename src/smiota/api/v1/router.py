"""API v1 master router aggregating all sub-routes."""
from fastapi import APIRouter
from smiota.api.v1.health import router as health_router
from smiota.api.v1.chat import router as chat_router
from smiota.api.v1.approvals import router as approvals_router
from smiota.api.v1.agents import router as agents_router
from smiota.api.v1.rag import router as rag_router
from smiota.api.v1.channels.teams import router as teams_router
from smiota.api.v1.channels.ide import router as ide_router
from smiota.api.v1.channels.webchat import router as webchat_router

api_v1_router = APIRouter()

# Core Agent & Operational routes
api_v1_router.include_router(health_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(approvals_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(rag_router)

# Channel-specific endpoints
api_v1_router.include_router(teams_router, prefix="/channels")
api_v1_router.include_router(ide_router, prefix="/channels")
api_v1_router.include_router(webchat_router, prefix="/channels")
