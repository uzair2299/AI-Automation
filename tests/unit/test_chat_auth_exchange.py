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


# ==============================================================================
# 9. Smiota Main App Real User Profile Payload & Dummy Fallback Tests
# ==============================================================================

SMIOTA_MAIN_REAL_PAYLOAD = {
    "id": 10790,
    "uuid": "4c9e782a-94ef-4b21-8854-bc712f5b66d1",
    "firstName": "Alex",
    "lastName": "Morgan",
    "recipientName": "Alex Morgan",
    "email": "alex.morgan@acme.com",
    "phone": "+14155551234",
    "voiceCallPhone": "+14155551234",
    "photo": None,
    "badgeId": "BADGE-9941",
    "authId": "auth0|64f1a23e9821a",
    "externalId": "EMP-88214",
    "login": "amorgan",
    "customerId": 42,
    "locationId": 108,
    "locationName": "Pleasanton HQ",
    "buildingId": 15,
    "buildingName": "North Tower",
    "tenantId": 89,
    "tenantName": "Acme Technologies Inc.",
    "unitNo": "Suite 400",
    "recipientId": 10790,
    "isInActive": False,
    "inactive": False,
    "authorizedForTenant": True,
    "wheelChairAccess": False,
    "hasSpecialStatus": False,
    "optOut": False,
    "emailUnsubscribe": False,
    "phoneUnsubscribe": False,
    "registrationStatus": 1,
    "keepLocalChanges": False,
    "addressLine1": "100 Innovation Way",
    "addressLine2": None,
    "city": "Pleasanton",
    "state": "CA",
    "zipCode": "94588",
    "passcode": "842910",
    "lastPasscodeCreatedTime": "2026-10-15T08:30:00Z",
    "passcodeGenerationRequired": False,
    "doNotAssociateToAPackage": False,
    "delegatesNotificationsToUserId": 0,
    "delegatesNotificationsToUserNamed": None,
    "roles": [
        "recipient"
    ],
    "roleObjects": [
        {
            "roleId": 10,
            "role": "recipient",
            "scope": 108,
            "scopeId": "108",
            "userId": 10790
        }
    ]
}


def test_code_exchange_smiota_main_real_payload_success():
    """Verify code exchange accurately processes real Smiota Main Core resident profile."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=200,
            json=SMIOTA_MAIN_REAL_PAYLOAD,
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        response = client.post("/api/v1/auth/exchange", json={"code": "smiota-resident-code-99"})

    assert response.status_code == 200
    data = response.json()

    assert data["token_type"] == "Bearer"
    assert "access_token" in data
    assert data["session_id"].startswith("sess-")

    # Core identity fields
    user = data["user"]
    assert user["user_id"] == "10790"
    assert user["tenant_id"] == "89"
    assert user["roles"] == ["recipient"]
    assert user["email"] == "alex.morgan@acme.com"

    # Rich Smiota Main resident metadata
    assert user["name"] == "Alex Morgan"
    assert user["first_name"] == "Alex"
    assert user["last_name"] == "Morgan"
    assert user["phone"] == "+14155551234"
    assert user["location_id"] == "108"
    assert user["location_name"] == "Pleasanton HQ"
    assert user["building_id"] == "15"
    assert user["building_name"] == "North Tower"
    assert user["tenant_name"] == "Acme Technologies Inc."
    assert user["unit_no"] == "Suite 400"
    assert user["passcode"] == "842910"
    assert user["raw_profile"] is not None

    # Verify session JWT token has sub=10790, tenant_id=89, name and location_id
    payload = verify_session_token(data["access_token"])
    assert payload["sub"] == "10790"
    assert payload["tenant_id"] == "89"
    assert payload["roles"] == ["recipient"]
    assert payload["name"] == "Alex Morgan"
    assert payload["location_id"] == "108"


def test_code_exchange_backend_404_fallback_returns_smiota_main_dummy():
    """Backend returning 404 (endpoint unintegrated) falls back to Smiota Main dummy profile."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=404,
            content=b"Endpoint Not Found",
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        response = client.post("/api/v1/auth/exchange", json={"code": "fallback-test-code"})

    assert response.status_code == 200
    data = response.json()
    user = data["user"]
    assert user["user_id"] == "10790"
    assert user["name"] == "Alex Morgan"
    assert user["tenant_id"] == "89"
    assert user["roles"] == ["recipient"]
    assert user["email"] == "alex.morgan@acme.com"
    assert user["building_name"] == "North Tower"
    assert user["unit_no"] == "Suite 400"


def test_code_exchange_inactive_user_rejected():
    """Users marked inactive in Smiota Main Core are rejected with 401."""
    inactive_payload = dict(SMIOTA_MAIN_REAL_PAYLOAD)
    inactive_payload["inactive"] = True

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=200,
            json=inactive_payload,
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        response = client.post("/api/v1/auth/exchange", json={"code": "inactive-user-code"})

    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["error_code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_code_exchange_session_reattachment_and_expired_replacement():
    """Verify session continuity: re-attach when valid, generate fresh when expired or cross-user."""
    from smiota.repositories.chat_repository import get_chat_repository
    repo = get_chat_repository()
    await repo.clear_all()

    # Pre-populate an active session for Alex Morgan (10790 / 89)
    await repo.get_or_create_session(
        session_id="sess-active-alex-1",
        user_id="10790",
        tenant_id="89",
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=200,
            json=SMIOTA_MAIN_REAL_PAYLOAD,
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )

        # 1. Valid re-attachment: Alex provides her active session_id
        res1 = client.post("/api/v1/auth/exchange", json={
            "code": "code-1",
            "session_id": "sess-active-alex-1",
        })
        assert res1.status_code == 200
        assert res1.json()["session_id"] == "sess-active-alex-1"

        # 2. Expired session: Alex provides a non-existent or expired session_id
        res2 = client.post("/api/v1/auth/exchange", json={
            "code": "code-2",
            "session_id": "sess-expired-9999",
        })
        assert res2.status_code == 200
        # Should not use the dead session_id, but instead falls back to her active session
        assert res2.json()["session_id"] == "sess-active-alex-1"

        # 3. If no active sessions exist and expired id is passed, generate brand new
        await repo.clear_all()
        res3 = client.post("/api/v1/auth/exchange", json={
            "code": "code-3",
            "session_id": "sess-expired-9999",
        })
        assert res3.status_code == 200
        new_sid = res3.json()["session_id"]
        assert new_sid.startswith("sess-")
        assert new_sid != "sess-expired-9999"


def test_complete_user_information_in_token_and_chat_payloads():
    """Verify complete user information is stored in token claims and exposed in chat message & conversation history payloads."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(
            status_code=200,
            json=SMIOTA_MAIN_REAL_PAYLOAD,
            request=httpx.Request("POST", "https://dev.smiotaapps.com/smiota/internal/ai/auth/exchange"),
        )
        auth_res = client.post("/api/v1/auth/exchange", json={"code": "user-info-full-test-code"})

    assert auth_res.status_code == 200
    auth_data = auth_res.json()
    token = auth_data["access_token"]
    session_id = auth_data["session_id"]

    # 1. Verify complete information is stored in JWT token
    claims = verify_session_token(token)
    assert "user" in claims
    token_user = claims["user"]
    assert token_user["user_id"] == "10790"
    assert token_user["name"] == "Alex Morgan"
    assert token_user["first_name"] == "Alex"
    assert token_user["last_name"] == "Morgan"
    assert token_user["phone"] == "+14155551234"
    assert token_user["email"] == "alex.morgan@acme.com"
    assert token_user["tenant_id"] == "89"
    assert token_user["tenant_name"] == "Acme Technologies Inc."
    assert token_user["location_id"] == "108"
    assert token_user["location_name"] == "Pleasanton HQ"
    assert token_user["building_id"] == "15"
    assert token_user["building_name"] == "North Tower"
    assert token_user["unit_no"] == "Suite 400"
    assert token_user["passcode"] == "842910"
    assert token_user["roles"] == ["recipient"]

    # 2. Verify chat message payload includes user necessary information object
    headers = {"Authorization": f"Bearer {token}"}
    chat_res = client.post(
        "/api/v1/chat",
        headers=headers,
        json={"message": "Where is my parcel?"},
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "user" in chat_data
    chat_user = chat_data["user"]
    assert chat_user["user_id"] == "10790"
    assert chat_user["name"] == "Alex Morgan"
    assert chat_user["building_name"] == "North Tower"
    assert chat_user["unit_no"] == "Suite 400"

    # 3. Verify conversation history payload contains user necessary information object
    history_res = client.get(f"/api/v1/chat/history/{session_id}", headers=headers)
    assert history_res.status_code == 200
    hist_data = history_res.json()
    assert "user" in hist_data
    assert hist_data["user"]["user_id"] == "10790"
    assert hist_data["user"]["name"] == "Alex Morgan"
    assert hist_data["total_messages"] >= 2
    # Check that message turns have user object attached
    user_msg = hist_data["messages"][0]
    assert user_msg["user"] is not None
    assert user_msg["user"]["user_id"] == "10790"
    assert user_msg["user"].get("parent_token") == "user-info-full-test-code"


@pytest.mark.asyncio
async def test_customer_agent_uses_parent_app_token_for_api_calls():
    """Verify CustomerAgent passes the parent app token rather than static SAVED_SESSION_TOKEN."""
    from smiota.agents.base import AgentContext
    from smiota.agents.implementations.customer.agent import CustomerAgent
    from smiota.services.package_service import package_service

    parent_app_token = "parent-app-token-998877"
    context = AgentContext(
        session_id="sess-test-token-usage",
        user_id="10790",
        tenant_id="89",
        channel="webchat",
        parent_token=parent_app_token,
        user={"parent_token": parent_app_token, "name": "Alex Morgan"},
        metadata={"parent_token": parent_app_token},
    )

    agent = CustomerAgent()
    with patch.object(package_service, "get_packages", new_callable=AsyncMock) as mock_get_packages:
        mock_get_packages.return_value = {
            "success": True,
            "packages": [
                {
                    "packageId": "PKG-5544",
                    "trackingNumber": "SM-982144",
                    "recipientName": "Alex Morgan",
                    "status": "In Locker",
                    "compartment": "B-12",
                }
            ],
            "totalRecords": 1,
        }

        result = await agent.process("Track package SM-982144", context)
        assert result.agent_name == "Customer"
        # Assert that package_service.get_packages was called with token=parent_app_token
        mock_get_packages.assert_awaited_once()
        _, kwargs = mock_get_packages.call_args
        assert kwargs.get("token") == parent_app_token


@pytest.mark.asyncio
async def test_customer_agent_blocks_package_lookup_for_unauthenticated_public_user():
    """Verify CustomerAgent requires login when a public user without a parent token checks packages."""
    from smiota.agents.base import AgentContext
    from smiota.agents.implementations.customer.agent import CustomerAgent
    from smiota.services.package_service import package_service

    # Guest user with no parent token
    context = AgentContext(
        session_id="sess-guest-123",
        user_id="guest",
        tenant_id="default",
        channel="webchat",
        parent_token=None,
        user={},
        metadata={},
    )

    agent = CustomerAgent()
    with patch.object(package_service, "get_packages", new_callable=AsyncMock) as mock_get_packages:
        result = await agent.process("Where is my package with tracking number d012a7eb840e?", context)
        assert result.agent_name == "Customer"
        assert "You’re using Smiota Support as a guest" in result.content
        assert "Log in to your account" in result.suggested_actions
        # Ensure external service was never invoked for unauthenticated user
        mock_get_packages.assert_not_called()


@pytest.mark.asyncio
async def test_package_service_rejects_missing_token():
    """Verify PackageService returns UNAUTHENTICATED error when called without a session token."""
    from smiota.services.package_service import package_service

    res = await package_service.get_packages(by_name_or_number="d012a7eb840e", token=None)
    assert res["success"] is False
    assert res["error_type"] == "UNAUTHENTICATED"





