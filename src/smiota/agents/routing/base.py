"""Base interface for intent routing algorithms."""
from abc import ABC, abstractmethod
from smiota.agents.base import AgentContext
from smiota.agents.routing.schema import RouteDecision


class BaseIntentRouter(ABC):
    """Abstract contract for classifying user queries into agent routing decisions."""

    @abstractmethod
    async def classify(self, query: str, context: AgentContext) -> RouteDecision:
        """Classify user query and context into a target agent with confidence score."""
        pass
