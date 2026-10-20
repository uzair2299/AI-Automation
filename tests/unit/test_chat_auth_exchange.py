"""Unit tests for Chat Authentication Code Exchange and Session Enforcement.

Covers:
1. Successful code exchange and session establishment.
2. Request validation (empty, blank, missing code rejected).
3. Invalid code rejection (Spring Boot 400/401/404 or valid=false).
4. Expired or replayed code rejection (Spring Boot 410).
5. Backend timeout (503 Service Unavailable, fails closed).
6. Backend connection unavailability (503 Service Unavailable, fails closed).
7. Malformed backend response (fails closed, no session).
8. Protected chat endpoint rejects missing session credentials (401).
9. Protected chat endpoint rejects invalid and expired session credentials (401).
10. Authenticated session retains verified user_id and tenant_id.
11. Browser-supplied metadata cannot override verified identity.
12. Dual endpoint routing: /auth/exchange and /api/v1/auth/exchange.
"""
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import httpx
import jwt
import pytest
from fastapi.testclient import TestClient

from smiota.agents.base import AgentResult
from smiota.core.config import get_settings
from smiota.core.security import create_session_token, verify_session_token
from smiota.main import app

client = TestClient(app)


# ==============================================================================
# 1. Successful Code Exchange and Session Creation
# ==============================================================================

@pytest.mark.parametrize("endpoint_path", ["/auth/exchange", "/api/v1/auth/exchange"])
def test_code_exchange_success(endpoint_path):
    """Test successful exchange of a valid bootstrap code for a signed JWT session."""
    mock_backend_response = {
        "valid": True,
        "user_id": "user-corp-123",
        "tenant_id": "tenant-enterprise-99",
        "roles": ["CUSTOMER", "RESIDENT"],
        "email": "resident.user@corp.smiota.com",
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_resp = httpx.Response(
            status_code=200,
            json=mock_backend_response,
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        mock_post.return_value = mock_resp

        response = client.post(endpoint_path, json={"code": "valid-bootstrap-code-12345"})

    assert response.status_code == 200
    data = response.json()

    assert data["token_type"] == "Bearer"
    assert "access_token" in data
    assert data["expires_in"] > 0
    assert data["session_id"].startswith("sess-")
    assert data["user"]["user_id"] == "user-corp-123"
    assert data["user"]["tenant_id"] == "tenant-enterprise-99"
    assert data["user"]["roles"] == ["CUSTOMER", "RESIDENT"]
    assert data["user"]["email"] == "resident.user@corp.smiota.com"

    # Verify that the issued access_token is a valid signed JWT containing verified identity
    payload = verify_session_token(data["access_token"])
    assert payload["sub"] == "user-corp-123"
    assert payload["tenant_id"] == "tenant-enterprise-99"
    assert payload["roles"] == ["CUSTOMER", "RESIDENT"]
    assert payload["session_id"] == data["session_id"]
    assert payload["iss"] == "smiota-ai"
    assert payload["aud"] == "smiota-chat"


# ==============================================================================
# 2. Input Validation (Empty, Blank, Missing Code)
# ==============================================================================

def test_code_exchange_missing_code():
    """Endpoint rejects request body missing 'code' field."""
    response = client.post("/auth/exchange", json={})
    assert response.status_code == 422


def test_code_exchange_empty_code():
    """Endpoint rejects request body with empty string code."""
    response = client.post("/auth/exchange", json={"code": ""})
    assert response.status_code == 422


def test_code_exchange_whitespace_code():
    """Endpoint rejects request body with whitespace-only code."""
    response = client.post("/auth/exchange", json={"code": "    "})
    assert response.status_code == 422


# ==============================================================================
# 3. Invalid, Expired, or Already-Consumed Code Rejection
# ==============================================================================

def test_code_exchange_invalid_code_rejected():
    """Spring Boot HTTP 400/401/404 rejects code; fails closed with 401."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=401,
            json={"error": "invalid_code", "message": "The bootstrap code is invalid."},
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        response = client.post("/auth/exchange", json={"code": "bogus-code-999"})

    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "AUTHENTICATION_FAILED"
    assert "access_token" not in data


def test_code_exchange_expired_or_consumed_code_rejected():
    """Spring Boot HTTP 410 (Gone) for expired or already used code; returns 401."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=410,
            json={"error": "code_expired", "message": "Bootstrap code already consumed or expired."},
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        response = client.post("/auth/exchange", json={"code": "expired-code-123"})

    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "AUTHENTICATION_FAILED"


def test_code_exchange_valid_flag_false_fails_closed():
    """Spring Boot returns 200 but explicitly sets valid=False; must fail closed."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=200,
            json={"valid": False, "user_id": "user-123", "tenant_id": "tenant-45"},
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        response = client.post("/auth/exchange", json={"code": "code-marked-invalid"})

    assert response.status_code == 401
    assert response.json()["success"] is False


# ==============================================================================
# 4. Backend Timeout and Unavailability (Fail Closed, No Session)
# ==============================================================================

def test_code_exchange_backend_timeout():
    """Spring Boot timeout raises 503 Service Unavailable without session creation."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ReadTimeout("Connection timed out waiting for backend.")
        response = client.post("/auth/exchange", json={"code": "timeout-test-code"})

    assert response.status_code == 503
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "BACKEND_UNAVAILABLE"


def test_code_exchange_backend_connection_error():
    """Spring Boot unreachable / connection refused returns 503 Service Unavailable."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ConnectError("Connection refused by host.")
        response = client.post("/auth/exchange", json={"code": "connect-error-code"})

    assert response.status_code == 503
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "BACKEND_UNAVAILABLE"


# ==============================================================================
# 5. Malformed Backend Responses (Fail Closed)
# ==============================================================================

def test_code_exchange_malformed_json_response():
    """Backend returning non-JSON body triggers fail-closed error response."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=200,
            content=b"<html>502 Bad Gateway Nginx</html>",
            headers={"Content-Type": "text/html"},
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        response = client.post("/auth/exchange", json={"code": "malformed-html-code"})

    assert response.status_code == 401
    assert response.json()["success"] is False


def test_code_exchange_missing_user_id_in_backend_response():
    """Backend returning 200 without user_id fails closed."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=200,
            json={"valid": True, "tenant_id": "tenant-45"},
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        response = client.post("/auth/exchange", json={"code": "missing-user-id"})

    assert response.status_code == 401
    assert response.json()["success"] is False


def test_code_exchange_missing_tenant_id_in_backend_response():
    """Backend returning 200 without tenant_id fails closed."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=200,
            json={"valid": True, "user_id": "user-123"},
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        response = client.post("/auth/exchange", json={"code": "missing-tenant-id"})

    assert response.status_code == 401
    assert response.json()["success"] is False


# ==============================================================================
# 6. Protected Chat Endpoint Rejects Missing or Invalid Session Credentials
# ==============================================================================

def test_protected_chat_rejects_missing_credentials():
    """Calling protected /api/v1/chat without Authorization header returns 401."""
    response = client.post(
        "/api/v1/chat",
        json={"message": "Where is my parcel?"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "AUTHENTICATION_FAILED"


def test_protected_chat_rejects_invalid_token_format():
    """Calling with non-Bearer or malformed authorization header returns 401."""
    response = client.post(
        "/api/v1/chat",
        json={"message": "Open locker compartment 3"},
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert response.status_code == 401
    assert response.json()["error_code"] == "AUTHENTICATION_FAILED"


def test_protected_chat_rejects_tampered_token():
    """Calling with tampered / invalid JWT signature returns 401."""
    response = client.post(
        "/api/v1/chat",
        json={"message": "Open locker compartment 3"},
        headers={"Authorization": "Bearer invalid.jwt.token.here"},
    )
    assert response.status_code == 401
    assert response.json()["error_code"] == "AUTHENTICATION_FAILED"


def test_protected_chat_rejects_expired_session_token():
    """Expired JWT session token returns 401 Unauthorized."""
    settings = get_settings()
    past_time = datetime.now(UTC) - timedelta(minutes=10)
    expired_payload = {
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "sub": "user-expired",
        "tenant_id": "tenant-expired",
        "roles": ["CUSTOMER"],
        "iat": int((past_time - timedelta(minutes=60)).timestamp()),
        "exp": int(past_time.timestamp()),
        "jti": "expired-id-123",
    }
    expired_token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    response = client.post(
        "/api/v1/chat",
        json={"message": "Resend PIN"},
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert response.json()["error_code"] == "AUTHENTICATION_FAILED"


# ==============================================================================
# 7. Authenticated Session Retains Verified User & Tenant Identity
# ==============================================================================

def test_protected_chat_retains_verified_user_and_tenant():
    """Authenticated session binds verified user_id and tenant_id to AgentContext."""
    token, _, _ = create_session_token(
        user_id="verified-cust-789",
        tenant_id="tenant-building-4",
        roles=["RESIDENT"],
        email="cust789@building4.com",
    )

    with patch("smiota.agents.orchestrator.AgentOrchestrator.route_and_execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = AgentResult(
            agent_name="Customer",
            content="Your package is in locker compartment 12. Pickup PIN: 4821.",
            requires_approval=False,
            suggested_actions=["Resend pickup PIN"],
        )

        response = client.post(
            "/api/v1/chat",
            json={"message": "Where is my delivery?"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["agent_used"] == "Customer"
    assert "PIN: 4821" in data["response"]

    # Verify AgentContext captured the verified claims from the JWT token
    call_args = mock_exec.call_args
    assert call_args is not None
    _, kwargs = call_args
    context = kwargs.get("context") or call_args[0][1]
    assert context.user_id == "verified-cust-789"
    assert context.tenant_id == "tenant-building-4"
    assert context.roles == ["RESIDENT"]


# ==============================================================================
# 8. Browser-Supplied Identifiers Cannot Override Verified Identity
# ==============================================================================

def test_browser_supplied_identity_cannot_override_verified_session():
    """Metadata attempting to spoof user_id or tenant_id is stripped and ignored."""
    token, _, _ = create_session_token(
        user_id="legitimate-user-55",
        tenant_id="legitimate-tenant-10",
        roles=["CUSTOMER"],
    )

    with patch("smiota.agents.orchestrator.AgentOrchestrator.route_and_execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = AgentResult(
            agent_name="Customer",
            content="Verified operation.",
        )

        response = client.post(
            "/api/v1/chat",
            json={
                "message": "View restricted packages",
                "metadata": {
                    "user_id": "malicious-admin-user",
                    "tenant_id": "victim-tenant-999",
                    "roles": ["admin", "superadmin"],
                    "compartment": "5",
                },
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200

    # Ensure context holds legitimate verified identity, not the spoofed metadata values
    call_args = mock_exec.call_args
    context = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]["context"]
    assert context.user_id == "legitimate-user-55"
    assert context.tenant_id == "legitimate-tenant-10"
    assert context.roles == ["CUSTOMER"]
    # The valid non-identity metadata field ('compartment') is preserved
    assert context.metadata.get("compartment") == "5"
    assert "user_id" not in context.metadata
    assert "tenant_id" not in context.metadata
    assert "roles" not in context.metadata
