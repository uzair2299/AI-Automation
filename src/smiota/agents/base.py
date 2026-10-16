"""BaseAgent abstraction and Context for all specialized Smiota agents."""
from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field

from smiota.schemas.agents import AgentCapability


class AgentContext(BaseModel):
    """Contextual metadata passed to each agent execution."""
    session_id: str
    user_id: str
    tenant_id: str
    channel: str
    roles: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    conversation_history: list[dict[str, str]] = Field(default_factory=list)


class AgentResult(BaseModel):
    """Normalized response from any Smiota agent."""
    agent_name: str
    content: str
    requires_approval: bool = False
    approval_details: Optional[dict[str, Any]] = None
    approval_id: Optional[str] = None
    suggested_actions: list[str] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract Base Class for all domain-specific AI agents."""

    def __init__(
        self,
        name: str,
        description: str,
        domain: str = "general",
        capabilities: Optional[list[AgentCapability]] = None,
        system_prompt: str = "",
        bound_tools: Optional[list[str]] = None,
    ):
        self.name = name
        self.description = description
        self.domain = domain
        self.capabilities = capabilities or []
        self.system_prompt = system_prompt
        self.bound_tools = bound_tools or []

    @abstractmethod
    async def process(self, query: str, context: AgentContext) -> AgentResult:
        """Process a user query within the provided context."""
        pass

    def get_metadata(self) -> dict[str, Any]:
        """Return standardized agent manifest."""
        return {
            "name": self.name,
            "domain": self.domain,
            "description": self.description,
            "capabilities": [c.model_dump() for c in self.capabilities],
            "bound_tools": self.bound_tools,
        }
