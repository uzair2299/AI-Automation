"""Shared redaction utilities for logs, events, specs, and config maps."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Union

# Sensitive variable names matching rule 3:
# (password|passwd|secret|token|api[_-]?key|credential|private[_-]?key)
_SENSITIVE_KEY_RE = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|credential|private[_-]?key)",
    re.IGNORECASE,
)

# Bearer token regex: Bearer eyJ... or Bearer [A-Za-z0-9\._\-+=]+
_BEARER_TOKEN_RE = re.compile(
    r"(Bearer\s+)[A-Za-z0-9\-_\.\+=]{8,}",
    re.IGNORECASE,
)

# Basic-auth URLs: https://user:pass@host...
_BASIC_AUTH_URL_RE = re.compile(
    r"(https?://)([^:\s/@]+):([^@\s/]+)@",
    re.IGNORECASE,
)

# PEM Blocks (private keys, certificates)
_PEM_BLOCK_RE = re.compile(
    r"-----BEGIN [A-Z0-9\s_-]+-----[^-]+-----END [A-Z0-9\s_-]+-----",
    re.DOTALL,
)


def redact_text(text: str) -> str:
    """Redact sensitive patterns in raw text strings (logs, event messages)."""
    if not text:
        return text

    # 1. Redact PEM blocks
    res = _PEM_BLOCK_RE.sub("[REDACTED_PEM_BLOCK]", text)

    # 2. Redact Bearer tokens
    res = _BEARER_TOKEN_RE.sub(r"\1[REDACTED_TOKEN]", res)

    # 3. Redact Basic-auth URLs: https://user:***@host
    res = _BASIC_AUTH_URL_RE.sub(r"\1\2:***@", res)

    # 4. In-line key-value redaction (e.g. password=xyz, "token": "xyz")
    kv_pattern = re.compile(
        r'((?:password|passwd|secret|token|api[_-]?key|credential|private[_-]?key)[\'"\s:=]+)([^\s,;\'"\}\]]+)',
        re.IGNORECASE,
    )
    res = kv_pattern.sub(r"\1[REDACTED]", res)

    return res


def redact_data(obj: Any) -> Any:
    """Recursively scrub sensitive keys and patterns in arbitrary dict/list structures."""
    if isinstance(obj, dict):
        cleaned: Dict[str, Any] = {}
        for k, v in obj.items():
            if _SENSITIVE_KEY_RE.search(str(k)):
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = redact_data(v)
        return cleaned
    elif isinstance(obj, list):
        return [redact_data(item) for item in obj]
    elif isinstance(obj, str):
        return redact_text(obj)
    return obj
