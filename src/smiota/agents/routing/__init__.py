"""Smiota Agent Intent Routing & Classification Layer."""
from typing import Optional
from smiota.agents.routing.base import BaseIntentRouter
from smiota.agents.routing.composite import CompositeIntentRouter
from smiota.agents.routing.rules import (
    GREETINGS,
    INFORMATIONAL_CATEGORIES,
    INFORMATIONAL_PREFIXES,
    RuleBasedRouter,
)
from smiota.agents.routing.schema import RouteDecision
from smiota.agents.routing.semantic import SemanticRouter

__all__ = [
    "GREETINGS",
    "INFORMATIONAL_PREFIXES",
    "INFORMATIONAL_CATEGORIES",
    "BaseIntentRouter",
    "RouteDecision",
    "RuleBasedRouter",
    "SemanticRouter",
    "CompositeIntentRouter",
    "get_intent_router",
]

_default_router: Optional[BaseIntentRouter] = None


def get_intent_router() -> BaseIntentRouter:
    """Return the global intent router singleton."""
    global _default_router
    if _default_router is None:
        _default_router = CompositeIntentRouter()
    return _default_router
