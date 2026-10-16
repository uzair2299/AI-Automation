"""Prompts package."""
from smiota.llm.prompts.base import GLOBAL_SYSTEM_PROMPT
from smiota.llm.prompts.templates import INTENT_ROUTING_PROMPT, HITL_EXPLANATION_TEMPLATE

__all__ = [
    "GLOBAL_SYSTEM_PROMPT",
    "INTENT_ROUTING_PROMPT",
    "HITL_EXPLANATION_TEMPLATE",
]
