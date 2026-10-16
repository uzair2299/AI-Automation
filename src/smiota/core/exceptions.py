"""Enterprise exception hierarchy for Smiota AI Platform."""
from typing import Any, Optional


class SmiotaException(Exception):
    """Base exception for all domain errors within Smiota AI Platform."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AgentNotFoundError(SmiotaException):
    """Raised when an orchestrator or user requests an unregistered agent."""
    pass


class AgentExecutionError(SmiotaException):
    """Raised when an agent fails during reasoning or task execution."""
    pass


class MCPToolExecutionError(SmiotaException):
    """Raised when an MCP tool invocation fails or returns an error response."""
    pass


class RemediationApprovalRequiredError(SmiotaException):
    """Raised when an agent attempts a mutating tool action without an approved token."""

    def __init__(self, tool_name: str, params: dict[str, Any]):
        super().__init__(
            message=f"Action '{tool_name}' mutates state/infrastructure and requires Human-in-the-Loop approval.",
            details={"tool_name": tool_name, "params": params},
        )
        self.tool_name = tool_name
        self.params = params


class LLMProviderError(SmiotaException):
    """Raised when Gemini / Vertex AI API fails or returns invalid response."""
    pass


class PromptInjectionDetectedError(SmiotaException):
    """Raised when input safety guardrail detects adversarial prompt injection."""
    pass


class VectorStoreError(SmiotaException):
    """Raised when RAG vector search or embedding store encounters a failure."""
    pass


class ResourceNotFoundError(SmiotaException):
    """Raised when an entity (approval, session, log) is not found."""
    pass


class AuthenticationError(SmiotaException):
    """Raised on authentication failure."""
    pass


class AuthorizationError(SmiotaException):
    """Raised when user lacks permissions for an action or tool."""
    pass
