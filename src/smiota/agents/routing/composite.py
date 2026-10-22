"""Composite Intent Router combining fast rules with AI semantic fallback."""
from typing import Optional
from smiota.agents.base import AgentContext
from smiota.agents.routing.base import BaseIntentRouter
from smiota.agents.routing.rules import RuleBasedRouter
from smiota.agents.routing.schema import RouteDecision
from smiota.agents.routing.semantic import SemanticRouter
from smiota.core.logging import logger


class CompositeIntentRouter(BaseIntentRouter):
    """Production-grade composite intent router.

    1. Fast path: Evaluates pattern rules, keyword weights, and continuity (< 1ms).
       If confidence >= threshold (default 0.75), returns immediately.
    2. AI fallback: If rule confidence is low (< 0.75), invokes Gemini semantic
       classification to disambiguate natural phrasing.
    """

    def __init__(
        self,
        rule_router: Optional[RuleBasedRouter] = None,
        semantic_router: Optional[SemanticRouter] = None,
        confidence_threshold: float = 0.75,
    ):
        self.rule_router = rule_router or RuleBasedRouter()
        self.semantic_router = semantic_router or SemanticRouter()
        self.confidence_threshold = confidence_threshold

    async def classify(self, query: str, context: AgentContext) -> RouteDecision:
        """Route query using rules first, falling back to semantic classification if needed."""
        # 1. Fast path: Pattern rules (< 1ms)
        rule_decision = await self.rule_router.classify(query, context)

        # If rules matched with high confidence, return immediately
        if rule_decision.confidence >= self.confidence_threshold:
            logger.debug(
                f"RuleBasedRouter matched [{rule_decision.agent_name}] "
                f"with confidence {rule_decision.confidence:.2f} (Method: {rule_decision.routing_method})"
            )
            return rule_decision

        # 2. AI Fallback: Disambiguate with Gemini Semantic Router
        logger.info(
            f"Rule confidence ({rule_decision.confidence:.2f}) is below threshold "
            f"({self.confidence_threshold:.2f}). Consulting SemanticRouter..."
        )
        try:
            semantic_decision = await self.semantic_router.classify(query, context)
            if semantic_decision.confidence > rule_decision.confidence:
                return semantic_decision
        except Exception as e:
            logger.warning(f"SemanticRouter consultation failed: {e}. Falling back to rule decision.")

        return rule_decision
