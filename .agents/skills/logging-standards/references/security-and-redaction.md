# Security & Redaction Standards

This document establishes the strict confidentiality, privacy, and data-sanitization policies required before emitting logs to any output sink.

---

## 1. Prohibited Logging Data

Under NO circumstances may any log entry contain:

1. **Authentication Credentials**:
   - Passwords, password hashes, and PIN codes.
   - Bearer tokens, JWTs, OAuth access/refresh tokens.
   - API keys (OpenAI, Gemini, Vertex, GCP service account JSON, AWS keys).
   - Internal service shared secrets (`X-Internal-Service-Key`).
2. **Session & Cookie Data**:
   - `Set-Cookie` or `Cookie` header values.
   - Raw session identifiers or CSRF tokens.
3. **Personally Identifiable Information (PII)**:
   - Full names, email addresses, phone numbers, apartment/unit numbers, credit card details.
   - Resident locker pickup codes or master unlock keys.
4. **Raw Database Payloads & Secrets**:
   - Connection strings containing database user credentials (`postgres://user:pass@host/db`).
   - Raw SQL statements containing parameterized bind values.
5. **Raw LLM Prompts & Chain-of-Thought**:
   - Internal system prompts or proprietary model reasoning paths.
   - Customer conversation bodies unless explicitly masked and hashed for debugging.

---

## 2. Redaction Patterns & Techniques

### Pattern 1: Automatic Header Redaction
When logging HTTP request headers, always filter against an approved allowlist:
```python
SAFE_HEADERS = {"user-agent", "x-correlation-id", "content-type", "host", "x-forwarded-for"}

def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        k.lower(): ("[REDACTED]" if k.lower() not in SAFE_HEADERS else v)
        for k, v in headers.items()
    }
```

### Pattern 2: Secret Masking in Strings & URLs
Any string that may contain keys or query tokens must be masked before formatting:
```python
import re

TOKEN_REGEX = re.compile(r"(?i)(token|key|secret|password|bearer|authorization)=([^\s&]+)")
JWT_REGEX = re.compile(r"eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+")

def redact_secrets(text: str) -> str:
    text = TOKEN_REGEX.sub(r"\1=[REDACTED]", text)
    text = JWT_REGEX.sub(r"[REDACTED_JWT]", text)
    return text
```

---

## 3. Log Injection Prevention

Attackers may attempt log injection by sending newlines (`\r\n`) or ANSI escape codes in query parameters or user-agent headers to forge log lines.

### Sanitization Rule:
All untrusted user input that is passed to a log message must be sanitized:
```python
def sanitize_log_input(user_str: str, max_length: int = 128) -> str:
    # Replace control characters and newlines with space
    clean = re.sub(r"[\r\n\x00-\x1f\x7f-\x9f]", " ", user_str)
    # Enforce strict length boundary
    return clean[:max_length].strip()
```
