"""Safety & Guardrails layer to block prompt injections, PII leakage, and harmful commands."""
import re
from typing import Optional
from smiota.core.logging import logger
from smiota.core.exceptions import PromptInjectionDetectedError


class SafetyGuardrails:
    """Validates user prompts and agent output against safety and security constraints."""

    DISALLOWED_PATTERNS = [
        re.compile(r"rm\s+-rf\s+/", re.IGNORECASE),
        re.compile(r"drop\s+database", re.IGNORECASE),
        re.compile(r"format\s+c:", re.IGNORECASE),
        re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", re.IGNORECASE),  # fork bomb
        re.compile(r"cat\s+/etc/shadow", re.IGNORECASE),
    ]

    PROMPT_INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+in\s+(developer|unrestricted|god)\s+mode", re.IGNORECASE),
        re.compile(r"reveal\s+(your\s+)?system\s+prompt", re.IGNORECASE),
        re.compile(r"disregard\s+the\s+above\s+and\s+say", re.IGNORECASE),
    ]

    PII_PATTERNS = [
        (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
        (re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), "[REDACTED_CC]"),
        (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "[REDACTED_GCP_API_KEY]"),
        (re.compile(r"ghp_[0-9a-zA-Z]{36}"), "[REDACTED_GITHUB_TOKEN]"),
        (re.compile(r"bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
    ]

    @classmethod
    def validate_input(cls, query: str) -> None:
        """Validate input prompt against destructive commands and prompt injection."""
        for pattern in cls.DISALLOWED_PATTERNS:
            if pattern.search(query):
                logger.warning(f"Destructive pattern violation detected: {pattern.pattern}")
                raise PromptInjectionDetectedError(f"Destructive command pattern detected.")

        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if pattern.search(query):
                logger.warning(f"Adversarial prompt injection violation detected: {pattern.pattern}")
                raise PromptInjectionDetectedError("Adversarial prompt injection pattern detected.")

    @classmethod
    def sanitize_pii(cls, text: str) -> str:
        """Mask sensitive PII and secrets prior to logging or LLM transmission."""
        sanitized = text
        for pattern, replacement in cls.PII_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized
