from fastapi import Header

from smiota.agents.orchestrator import AgentOrchestrator
from smiota.core.exceptions import AuthenticationError
from smiota.core.security import AuthenticatedUser, verify_session_token
from smiota.mcp.client import MCPClient
from smiota.rag.retriever import KnowledgeRetriever
from smiota.services.auth_service import SmiotaBackendAuthService, backend_auth_service


def get_backend_auth_service() -> SmiotaBackendAuthService:
    """Dependency returning the Spring Boot internal auth service client."""
    return backend_auth_service


async def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
) -> AuthenticatedUser:
    """Dependency returning authenticated user and roles from signed JWT session token.

    Rejects requests with missing, invalid, or expired session credentials.
    """
    if not authorization:
        raise AuthenticationError(
            "Authentication credentials were not provided. Missing 'Authorization: Bearer <session_token>' header."
        )

    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError(
            "Invalid authorization header format. Expected 'Authorization: Bearer <session_token>'."
        )

    token = parts[1].strip()
    if not token:
        raise AuthenticationError("Bearer token is empty.")

    payload = verify_session_token(token)
    user_data = payload.get("user") or {}
    return AuthenticatedUser(
        user_id=payload["sub"],
        tenant_id=payload["tenant_id"],
        roles=payload.get("roles", ["user"]),
        email=payload.get("email") or user_data.get("email", ""),
        name=payload.get("name") or user_data.get("name", ""),
        first_name=payload.get("first_name") or user_data.get("first_name", ""),
        last_name=payload.get("last_name") or user_data.get("last_name", ""),
        phone=payload.get("phone") or user_data.get("phone", ""),
        tenant_name=payload.get("tenant_name") or user_data.get("tenant_name", ""),
        location_id=payload.get("location_id") or user_data.get("location_id", ""),
        location_name=payload.get("location_name") or user_data.get("location_name", ""),
        building_id=payload.get("building_id") or user_data.get("building_id", ""),
        building_name=payload.get("building_name") or user_data.get("building_name", ""),
        unit_no=payload.get("unit_no") or user_data.get("unit_no", ""),
        parent_token=payload.get("parent_token") or user_data.get("parent_token") or None,
        session_id=payload.get("session_id"),
        user_profile=user_data,
    )


def get_orchestrator() -> AgentOrchestrator:
    """Dependency returning the multi-agent orchestrator instance."""
    return AgentOrchestrator()


def get_mcp_client() -> MCPClient:
    """Dependency returning the MCP client."""
    return MCPClient()


def get_knowledge_retriever() -> KnowledgeRetriever:
    """Dependency returning the RAG KnowledgeRetriever instance."""
    return KnowledgeRetriever()


from smiota.repositories.chat_repository import BaseChatRepository, get_chat_repository


def get_chat_repo() -> BaseChatRepository:
    """Dependency returning the active chat session repository."""
    return get_chat_repository()

