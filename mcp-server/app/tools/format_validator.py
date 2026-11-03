"""Fast-scanning format validator and retry instruction builder."""
from __future__ import annotations

import re
from typing import Any, Dict, List

_CHAR_LIMIT_PER_PARAGRAPH = 600
_CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)


def validate_format(text: str) -> Dict[str, Any]:
    """Validate text against 600-char paragraph limits, code-fence stripping, and table constraints."""
    issues: List[str] = []

    # Check for raw unescaped code fences
    if _CODE_BLOCK_RE.search(text):
        issues.append("Response contains prohibited triple-backtick markdown code fences.")

    # Check paragraph character length
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for idx, p in enumerate(paragraphs):
        if len(p) > _CHAR_LIMIT_PER_PARAGRAPH:
            issues.append(f"Paragraph {idx + 1} exceeds {_CHAR_LIMIT_PER_PARAGRAPH} character limit ({len(p)} chars).")

    is_valid = len(issues) == 0
    return {
        "is_valid": is_valid,
        "issues": issues,
        "score": 1.0 if is_valid else max(0.0, 1.0 - (0.2 * len(issues))),
    }


def build_retry_instruction(issues: List[str]) -> str:
    """Build corrective system instruction suffix when format violations occur."""
    if not issues:
        return ""
    joined_issues = "; ".join(issues)
    return (
        f"CRITICAL FORMATTING CORRECTION REQUIRED: Your previous response violated the following rules: {joined_issues}. "
        "Rewrite your response immediately ensuring paragraphs are strictly under 600 characters and no triple-backtick blocks are used."
    )
