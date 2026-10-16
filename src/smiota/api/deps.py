"""FastAPI dependency injection utilities."""
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from smiota.core.security import AuthenticatedUser, get_current_user_stub
from smiota.agents.orchestrator import AgentOrchestrator
from smiota.core.database import get_db_session
from smiota.core.cache import get_cache_service, CacheService
from smiota.rag.retriever import KnowledgeRetriever
from smiota.mcp.client import MCPClient


async def get_current_user() -> AuthenticatedUser:
    """Dependency returning authenticated user and roles."""
    return await get_current_user_stub()


def get_orchestrator() -> AgentOrchestrator:
    """Dependency returning the multi-agent orchestrator instance."""
    return AgentOrchestrator()


def get_mcp_client() -> MCPClient:
    """Dependency returning the MCP client."""
    return MCPClient()


def get_knowledge_retriever() -> KnowledgeRetriever:
    """Dependency returning the RAG KnowledgeRetriever instance."""
    return KnowledgeRetriever()
