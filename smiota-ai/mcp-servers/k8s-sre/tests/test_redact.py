"""Unit tests for shared redaction utilities."""
from app.k8s.redact import redact_data, redact_text


def test_redact_bearer_token():
    text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.secretpayload.signature"
    redacted = redact_text(text)
    assert "Bearer [REDACTED_TOKEN]" in redacted
    assert "secretpayload" not in redacted


def test_redact_basic_auth_url():
    url = "Connecting to https://admin:superSecretPassword@database.internal.net:5432/db"
    redacted = redact_text(url)
    assert "https://admin:***@database.internal.net:5432/db" in redacted
    assert "superSecretPassword" not in redacted


def test_redact_pem_block():
    pem = (
        "Logs starting...\n"
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA0m4b...SECRET KEY DATA...\n"
        "-----END RSA PRIVATE KEY-----\n"
        "Server listening on 8080"
    )
    redacted = redact_text(pem)
    assert "[REDACTED_PEM_BLOCK]" in redacted
    assert "SECRET KEY DATA" not in redacted


def test_redact_dict_sensitive_keys():
    spec = {
        "env": [
            {"name": "DB_PASSWORD", "value": "mySecretPassword123"},
            {"name": "API_KEY", "value": "ak_live_8391823912"},
            {"name": "PUBLIC_HOST", "value": "api.smiota.com"},
        ],
        "secret_token": "sk-12345",
        "nested": {
            "private_key": "raw-key-content",
            "normal_field": "visible",
        }
    }
    redacted = redact_data(spec)
    assert redacted["secret_token"] == "[REDACTED]"
    assert redacted["nested"]["private_key"] == "[REDACTED]"
    assert redacted["nested"]["normal_field"] == "visible"
