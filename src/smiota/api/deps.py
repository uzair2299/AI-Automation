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
    return AuthenticatedUser(
        user_id=payload["sub"],
        tenant_id=payload["tenant_id"],
        roles=payload.get("roles", ["user"]),
        email=payload.get("email", ""),
        name=payload.get("name", ""),
        location_id=payload.get("location_id", ""),
        session_id=payload.get("session_id"),
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
