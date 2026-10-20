"""Integration test for /api/v1/approvals endpoint."""
from fastapi.testclient import TestClient
from smiota.main import app

client = TestClient(app)

from smiota.core.security import create_session_token
admin_token, _, _ = create_session_token(
    user_id="usr-admin-1",
    tenant_id="smiota-internal",
    roles=["admin", "sre"],
    email="admin@smiota.com",
)
AUTH_HEADERS = {"Authorization": f"Bearer {admin_token}"}


def test_list_pending_approvals():
    response = client.get("/api/v1/approvals", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_decide_approval():
    response = client.post(
        "/api/v1/approvals/appr-101/decide",
        json={
            "decision": "approved",
            "decided_by_user_id": "usr-admin-1",
            "comment": "Verified incident metrics, safe to execute rollout restart.",
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["approval_id"] == "appr-101"
    assert data["status"] == "approved"
