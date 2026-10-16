"""Token usage, cost accounting, and FinOps telemetry for LLM requests."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from smiota.core.logging import logger


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CostTracker:
    """Calculates approximate Vertex AI Gemini 1.5 costs and tracks token budgets."""

    # Approximate rates per 1k tokens (USD)
    PRICE_INPUT_PER_1K = 0.00125
    PRICE_OUTPUT_PER_1K = 0.00500

    @classmethod
    def calculate_cost(cls, prompt_tokens: int, completion_tokens: int) -> TokenUsage:
        input_cost = (prompt_tokens / 1000.0) * cls.PRICE_INPUT_PER_1K
        output_cost = (completion_tokens / 1000.0) * cls.PRICE_OUTPUT_PER_1K
        total_cost = round(input_cost + output_cost, 6)

        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=total_cost,
        )
        logger.debug(f"FinOps Token Usage: {usage.total_tokens} tokens (~${usage.estimated_cost_usd} USD)")
        return usage
