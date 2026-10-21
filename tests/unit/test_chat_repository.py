"""Unit tests for Chat Repository, In-Memory Session Storage, and History Endpoint."""
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from smiota.agents.base import AgentResult
from smiota.core.security import create_session_token
from smiota.main import app
from smiota.repositories.chat_repository import (
    InMemoryChatRepository,
    get_chat_repository,
)
from smiota.schemas.chat_session import ChatMessage, ChatSession

client = TestClient(app)


# ==============================================================================
# 1. In-Memory Repository Direct Operations
# ==============================================================================

@pytest.mark.asyncio
async def test_in_memory_repository_get_or_create():
    """Verify session creation, metadata tracking, and re-fetching."""
    repo = InMemoryChatRepository(ttl_hours=1, max_turns=10)

    session = await repo.get_or_create_session(
        session_id="sess-unit-001",
        user_id="10790",
        tenant_id="89",
        channel="webchat",
        metadata={"building": "North Tower", "unit": "Suite 400"},
    )

    assert session.session_id == "sess-unit-001"
    assert session.user_id == "10790"
    assert session.tenant_id == "89"
    assert session.channel == "webchat"
    assert session.metadata["building"] == "North Tower"
    assert len(session.messages) == 0

    # Re-fetch should return the same active session
    fetched = await repo.get_session("sess-unit-001")
    assert fetched is not None
    assert fetched.session_id == "sess-unit-001"
    assert fetched.user_id == "10790"


@pytest.mark.asyncio
async def test_in_memory_repository_append_messages_text_and_cards():
    """Verify storing user text, agent cards, and approval gates with full attribution."""
    repo = InMemoryChatRepository(ttl_hours=1, max_turns=10)
    await repo.get_or_create_session("sess-unit-002", "10790", "89")

    # 1. User message turn
    user_msg = await repo.append_message(
        session_id="sess-unit-002",
        role="user",
        content="Where is my Amazon package?",
        sender_name="Alex Morgan",
        message_type="text",
    )
    assert user_msg.role == "user"
    assert user_msg.sender_name == "Alex Morgan"
    assert user_msg.agent_name is None
    assert user_msg.message_type == "text"
    assert user_msg.card_payload is None

    # 2. Agent rich card message turn
    card_data = {
        "card_type": "package_pickup",
        "tracking_number": "SM-9941",
        "compartment": "12",
        "pickup_pin": "842910",
    }
    agent_msg = await repo.append_message(
        session_id="sess-unit-002",
        role="assistant",
        content="Your package is in Locker Compartment 12.",
        agent_name="Customer",
        sender_name="Customer Assistant",
        message_type="card",
        card_payload=card_data,
        suggested_actions=["Open door remotely", "Resend PIN"],
    )
    assert agent_msg.role == "assistant"
    assert agent_msg.agent_name == "Customer"
    assert agent_msg.sender_name == "Customer Assistant"
    assert agent_msg.message_type == "card"
    assert agent_msg.card_payload == card_data
    assert agent_msg.suggested_actions == ["Open door remotely", "Resend PIN"]

    # 3. Security approval gate turn
    gate_msg = await repo.append_message(
        session_id="sess-unit-002",
        role="assistant",
        content="Remote unlock requires verification.",
        agent_name="Security",
        message_type="approval_gate",
        card_payload={"action": "unlock_door", "compartment": "12"},
    )
    assert gate_msg.message_type == "approval_gate"
    assert gate_msg.agent_name == "Security"

    # Verify session message list order
    messages = await repo.get_messages("sess-unit-002")
    assert len(messages) == 3
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert messages[2].role == "assistant"


@pytest.mark.asyncio
async def test_in_memory_repository_sliding_window():
    """Verify repository prunes history according to max_turns sliding window."""
    repo = InMemoryChatRepository(ttl_hours=1, max_turns=2)  # Max 4 messages (2 turns)
    await repo.get_or_create_session("sess-window", "10790", "89")

    for i in range(1, 7):
        await repo.append_message(
            session_id="sess-window",
            role="user" if i % 2 == 1 else "assistant",
            content=f"Message {i}",
        )

    messages = await repo.get_messages("sess-window")
    assert len(messages) == 4  # 2 turns * 2 = 4
    # Earliest messages (1, 2) should have been pruned
    assert messages[0].content["text"] == "Message 3"
    assert messages[3].content["text"] == "Message 6"


@pytest.mark.asyncio
async def test_in_memory_repository_ttl_eviction():
    """Verify expired sessions are evicted based on TTL."""
    repo = InMemoryChatRepository(ttl_hours=2, max_turns=10)
    session = await repo.get_or_create_session("sess-expired", "10790", "89")

    # Manually backdate the session's updated_at beyond TTL
    session.updated_at = datetime.now(UTC) - timedelta(hours=3)

    # Calling get_session triggers _evict_expired
    expired = await repo.get_session("sess-expired")
    assert expired is None


# ==============================================================================
# 2. REST API Chat History Endpoint Tests
# ==============================================================================

def test_chat_history_endpoint_returns_stored_turns():
    """Verify /api/v1/chat/history/{session_id} returns conversation turns recorded during chat."""
    token, session_id, _ = create_session_token(
        user_id="10790",
        tenant_id="89",
        roles=["recipient"],
        name="Alex Morgan",
    )
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 1. Send chat message: Mock the underlying agent process so orchestrator records to repository
    mock_agent = AsyncMock()
    mock_agent.name = "Customer"
    mock_agent.process.return_value = AgentResult(
        agent_name="Customer",
        content="Your package is in Locker Compartment 12. Pickup PIN: 842910.",
        requires_approval=False,
        suggested_actions=["Resend pickup PIN"],
    )

    with patch("smiota.agents.registry.AgentRegistry.get", return_value=mock_agent):
        chat_resp = client.post(
            "/api/v1/chat",
            json={"message": "Where is my parcel?", "session_id": session_id},
            headers=auth_headers,
        )
        assert chat_resp.status_code == 200

    # 2. Fetch history via the new endpoint
    history_resp = client.get(
        f"/api/v1/chat/history/{session_id}",
        headers=auth_headers,
    )
    assert history_resp.status_code == 200
    data = history_resp.json()

    assert data["session_id"] == session_id
    assert data["conversation_id"] == session_id
    assert data["user_id"] == "10790"
    assert data["tenant_id"] == "89"
    assert data["total_messages"] >= 2

    # Check that user turn and assistant turn are properly recorded in standard envelope format
    user_turn = data["messages"][0]
    assert user_turn["role"] == "user"
    assert user_turn["type"] == "user_message"
    assert user_turn["sender"]["name"] == "Alex Morgan"
    assert user_turn["content"]["text"] == "Where is my parcel?"
    assert user_turn["content"]["attachments"] == []
    assert user_turn["message_id"].startswith("msg_")
    assert user_turn["conversation_id"] == session_id

    assistant_turn = data["messages"][1]
    assert assistant_turn["role"] == "assistant"
    assert assistant_turn["agent_name"] == "Customer"
    assert "Compartment 12" in assistant_turn["content"]["text"]
    assert assistant_turn["suggested_actions"] == ["Resend pickup PIN"]


def test_chat_history_multi_tenant_isolation_forbidden():
    """Verify User B cannot access User A's chat session history (multi-tenant boundary)."""
    # Session owned by User A (10790, tenant 89)
    repo = get_chat_repository()
    # Create session directly in repo
    import asyncio
    asyncio.run(repo.get_or_create_session("sess-private-a", "10790", "89"))

    # User B token (User 9999, tenant 42)
    token_b, _, _ = create_session_token(
        user_id="9999",
        tenant_id="42",
        roles=["recipient"],
    )

    response = client.get(
        "/api/v1/chat/history/sess-private-a",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 403
    assert response.json()["success"] is False
    assert response.json()["error_code"] == "FORBIDDEN"



def test_chat_history_non_existent_session_graceful_empty():
    """Non-existent session returns empty message array instead of hard 404 for smooth UI init."""
    token, _, _ = create_session_token(
        user_id="10790",
        tenant_id="89",
        roles=["recipient"],
    )

    response = client.get(
        "/api/v1/chat/history/sess-unknown-9999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_messages"] == 0
    assert data["messages"] == []


def test_standard_message_envelope_websocket_and_polymorphic_payloads():
    """Verify WebSocket accepts standard user_message envelope and responds with standard stream/done envelopes."""
    import json
    session_id = "sess-standard-envelope-01"

    # Use TestClient websocket context
    with client.websocket_connect(f"/api/v1/chat/ws/{session_id}") as ws:
        # 1. Send keep-alive ping
        ws.send_text("ping")
        assert ws.receive_text() == "pong"

        # 2. Send standard user_message envelope with dynamic content
        incoming_envelope = {
            "message_id": "msg_01JABC123",
            "conversation_id": session_id,
            "type": "user_message",
            "sender": {
                "role": "user",
                "name": "Alex Morgan",
                "id": "10790"
            },
            "content": {
                "text": "Where is my parcel?",
                "attachments": []
            },
            "metadata": {
                "locale": "en-US",
                "timezone": "Asia/Karachi",
                "client": "web"
            },
            "created_at": "2026-10-21T08:00:00Z"
        }
        ws.send_text(json.dumps(incoming_envelope))

        # 3. Read streamed tokens until 'done'
        received_tokens = []
        done_envelope = None

        while True:
            resp = ws.receive_json()
            if resp.get("type") == "stream_token":
                assert resp["conversation_id"] == session_id
                assert "sender" in resp
                assert "content" in resp
                assert "token" in resp["content"]
                received_tokens.append(resp["content"]["token"])
            elif resp.get("type") == "done":
                done_envelope = resp
                break

        assert len(received_tokens) > 0
        assert done_envelope is not None
        assert done_envelope["conversation_id"] == session_id
        assert "sender" in done_envelope
        assert "content" in done_envelope
        assert "text" in done_envelope["content"]
        assert "suggested_actions" in done_envelope["content"]

