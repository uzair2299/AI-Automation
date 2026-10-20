"""Integration test for /api/v1/chat endpoint and multi-agent routing."""
from fastapi.testclient import TestClient
from smiota.main import app

client = TestClient(app)

from smiota.core.security import create_session_token
chat_token, _, _ = create_session_token(
    user_id="user-123",
    tenant_id="smiota-internal",
    roles=["developer", "sre"],
    email="dev@smiota.com",
)
AUTH_HEADERS = {"Authorization": f"Bearer {chat_token}"}


def test_chat_aiops_routing():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Investigate CPU memory spike in GKE pods",
            "channel": "teams",
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_used"] == "AIOps"
    assert "session_id" in data
    assert data["requires_approval"] is False


def test_chat_remediation_flagging():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Restart production deployment smiota-api now",
            "channel": "teams",
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_used"] == "AIOps"
    assert data["requires_approval"] is True


def test_chat_customer_agent_routing():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Check package status in locker compartment 4",
            "channel": "webchat",
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_used"] == "Customer"
