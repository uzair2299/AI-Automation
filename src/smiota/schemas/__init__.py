"""Pydantic validation contracts and API schemas."""
from smiota.schemas.chat import ChatMessageRequest, ChatMessageResponse
from smiota.schemas.approvals import (
    ApprovalStatus,
    ApprovalRequestCreate,
    ApprovalDecision,
)
from smiota.schemas.mcp import (
    ToolAccessLevel,
    MCPToolDefinition,
    MCPToolExecutionResult,
)
from smiota.schemas.common import (
    APIResponse,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse,
)
from smiota.schemas.agents import (
    AgentCapability,
    AgentMetadataResponse,
    IntentClassificationDiagnostic,
)
from smiota.schemas.rag import (
    DocumentIngestionRequest,
    DocumentIngestionResponse,
    VectorSearchRequest,
    DocumentSearchResult,
    VectorSearchResponse,
)
from smiota.schemas.health import ComponentHealth, SystemHealthResponse
from smiota.schemas.auth import (
    AuthExchangeRequest,
    AuthExchangeResponse,
    UserIdentityInfo,
)

__all__ = [
    "AuthExchangeRequest",
    "AuthExchangeResponse",
    "UserIdentityInfo",
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ApprovalStatus",
    "ApprovalRequestCreate",
    "ApprovalDecision",
    "ToolAccessLevel",
    "MCPToolDefinition",
    "MCPToolExecutionResult",
    "APIResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginatedResponse",
    "AgentCapability",
    "AgentMetadataResponse",
    "IntentClassificationDiagnostic",
    "DocumentIngestionRequest",
    "DocumentIngestionResponse",
    "VectorSearchRequest",
    "DocumentSearchResult",
    "VectorSearchResponse",
    "ComponentHealth",
    "SystemHealthResponse",
]
