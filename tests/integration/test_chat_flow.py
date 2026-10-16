"""Integration test for /api/v1/chat endpoint and multi-agent routing."""
from fastapi.testclient import TestClient
from smiota.main import app

client = TestClient(app)


def test_chat_aiops_routing():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Investigate CPU memory spike in GKE pods",
            "channel": "webchat",
        },
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
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_used"] == "Customer"
