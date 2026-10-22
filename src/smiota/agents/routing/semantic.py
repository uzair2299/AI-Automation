"""Semantic AI Intent Router powered by Gemini & Vertex AI."""
import json
import re
from typing import Optional
from smiota.agents.base import AgentContext
from smiota.agents.registry import AgentRegistry
from smiota.agents.routing.base import BaseIntentRouter
from smiota.agents.routing.schema import RouteDecision
from smiota.core.logging import logger
from smiota.llm.provider import GeminiProvider


class SemanticRouter(BaseIntentRouter):
    """Uses Gemini / Vertex AI to perform zero-shot or few-shot semantic intent classification

    for queries that cannot be resolved with high confidence by rule patterns alone.
    """

    def __init__(self, provider: Optional[GeminiProvider] = None):
        self.provider = provider or GeminiProvider()

    async def classify(self, query: str, context: AgentContext) -> RouteDecision:
        """Classifies intent using Gemini Flash semantic reasoning."""
        channel = (context.channel or "webchat").lower()

        # Build candidate agents dynamically from registry
        all_agents = AgentRegistry.list_agents()
        if channel == "webchat":
            # Guardrail: For webchat, restrict candidates to customer and operational agents
            candidate_agents = [
                a for a in all_agents if a["name"].lower() in {"customer", "aiops", "security"}
            ]
        else:
            candidate_agents = all_agents

        agents_description = "\n".join(
            f"- {a['name'].lower()}: {a['description']}" for a in candidate_agents
        )

        prompt = f"""You are the intent router for the Smiota platform.
Your task is to classify the user query into the single most appropriate agent domain.

Available Candidate Agents:
{agents_description}

User Channel: {channel}
User Query: "{query}"

Respond strictly in valid JSON format with no markdown blocks:
{{
  "agent": "<agent_name_in_lowercase>",
  "confidence": <float between 0.0 and 1.0>,
  "intent": "<short_snake_case_intent_name>",
  "reasoning": "<one sentence explanation>"
}}
"""
        try:
            raw_response = await self.provider.generate_completion(
                prompt=prompt,
                temperature=0.0,
            )

            # Strip markdown ```json ``` markers if present
            cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw_response).strip()
            data = json.loads(cleaned)

            agent_name = str(data.get("agent", "")).lower().strip()
            confidence = float(data.get("confidence", 0.85))
            intent = str(data.get("intent", "semantic_classified"))
            reasoning = str(data.get("reasoning", "Classified by Gemini semantic router"))

            # Validate that agent exists in candidates
            valid_names = {a["name"].lower() for a in candidate_agents}
            if agent_name in valid_names:
                return RouteDecision(
                    agent_name=agent_name,
                    confidence=min(max(confidence, 0.0), 1.0),
                    matched_intent=intent,
                    routing_method="gemini_semantic",
                    reasoning=reasoning,
                )
        except Exception as e:
            logger.warning(f"SemanticRouter call failed: {e}. Falling back to default.")

        # Fallback if LLM classification fails
        fallback_agent = "customer" if channel == "webchat" else "aiops"
        return RouteDecision(
            agent_name=fallback_agent,
            confidence=0.50,
            matched_intent="semantic_fallback",
            routing_method="fallback",
            reasoning="Semantic classification unavailable or timed out; selected channel default",
        )
