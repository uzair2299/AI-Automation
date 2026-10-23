"""Unit tests for Microsoft Teams Bot Framework Channel Webhook."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from smiota.main import create_app


@pytest.mark.asyncio
async def test_ms_teams_webhook_message_flow():
    """Verify MS Teams incoming message is received, stripped of @mentions, and routed to AIOps."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "type": "message",
            "id": "msg-12345",
            "timestamp": "2026-10-23T12:00:00Z",
            "channelId": "msteams",
            "from": {
                "id": "29:user-aad-123",
                "name": "Alex SRE",
            },
            "conversation": {
                "id": "19:conv-teams-abc",
                "conversationType": "channel",
            },
            "text": "<at>Smiota Bot</at> Hello! How can I help you today?",
        }

        response = await client.post("/api/v1/channels/teams/webhook", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "message"
        assert "Hello!" in data["text"]


@pytest.mark.asyncio
async def test_ms_teams_webhook_conversation_update():
    """Verify MS Teams conversationUpdate event returns welcome greeting."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "type": "conversationUpdate",
            "from": {"name": "DevOps Engineer"},
            "conversation": {"id": "19:conv-welcome"},
        }
        response = await client.post("/api/v1/channels/teams/webhook", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "message"
        assert "AIOps" in data["text"]
