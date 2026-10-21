"""Dedicated WebSocket Chat Session Handler.

Encapsulates socket lifecycle, heartbeat ping/pong, standard message envelope parsing,
agent response streaming, and error handling into a modular session worker.
Architected to decouple socket transport from business logic, enabling seamless
future scaling with message brokers (RabbitMQ / Redis PubSub).
"""
import asyncio
from datetime import UTC, datetime
import json
from typing import Any, Optional
import uuid

from fastapi import WebSocket, WebSocketDisconnect

from smiota.agents.base import AgentContext, AgentResult
from smiota.agents.orchestrator import AgentOrchestrator
from smiota.api.v1.websocket_manager import ws_manager
from smiota.core.logging import logger
from smiota.repositories.chat_repository import BaseChatRepository


class WebSocketChatHandler:
    """Manages the full lifecycle of a single client's WebSocket chat stream."""

    def __init__(
        self,
        websocket: WebSocket,
        session_id: str,
        resident_id: Optional[str],
        orchestrator: AgentOrchestrator,
        chat_repo: BaseChatRepository,
    ):
        self.ws = websocket
        self.session_id = session_id
        self.resident_id = resident_id
        self.orchestrator = orchestrator
        self.chat_repo = chat_repo

    async def handle(self) -> None:
        """Main lifecycle entrypoint: connect, process incoming frames, and gracefully clean up."""
        await ws_manager.connect(self.session_id, self.ws, self.resident_id)

        try:
            async for raw_data in self.ws.iter_text():
                await self._process_frame(raw_data)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket fatal error on session {self.session_id}: {e}", exc_info=True)
        finally:
            await ws_manager.disconnect(self.session_id)

    async def _process_frame(self, raw_data: str) -> None:
        """Process a single incoming frame from the client."""
        # Handle heartbeat ping
        if raw_data.strip() == "ping":
            await self.ws.send_text("pong")
            return

        # Parse standard envelope or plain text
        user_message, req_resident_id, client_metadata, attachments = self._parse_incoming(raw_data)
        if not user_message.strip():
            return

        # Resolve tenant & user from session state if available
        existing_session = await self.chat_repo.get_session(self.session_id)
        tenant_id = existing_session.tenant_id if existing_session else "default"
        if existing_session and existing_session.user_id != "anonymous" and req_resident_id == "ws-resident":
            req_resident_id = existing_session.user_id

        context = AgentContext(
            session_id=self.session_id,
            user_id=req_resident_id,
            tenant_id=tenant_id,
            channel="webchat",
        )

        try:
            # Route to multi-agent core
            result = await self.orchestrator.route_and_execute(user_message, context)
            await self._stream_response(result)
        except Exception as agent_err:
            logger.error(f"Error processing message in session {self.session_id}: {agent_err}", exc_info=True)
            await self._send_error_fallback()

    def _parse_incoming(self, raw_data: str) -> tuple[str, str, dict[str, Any], list[dict[str, Any]]]:
        """Parse incoming raw frame into user message, resident ID, metadata, and attachments."""
        user_message = raw_data
        req_resident_id = self.resident_id or "ws-resident"
        client_metadata: dict[str, Any] = {}
        attachments: list[dict[str, Any]] = []

        try:
            parsed = json.loads(raw_data)
            if isinstance(parsed, dict):
                # Standard Dynamic Envelope
                if parsed.get("type") == "user_message" and isinstance(parsed.get("content"), dict):
                    user_message = str(parsed["content"].get("text", ""))
                    attachments = parsed["content"].get("attachments", [])
                elif "text" in parsed and parsed["text"] is not None:
                    user_message = str(parsed["text"])

                if parsed.get("sender") and isinstance(parsed["sender"], dict) and parsed["sender"].get("id"):
                    req_resident_id = str(parsed["sender"]["id"])
                elif parsed.get("resident_id"):
                    req_resident_id = str(parsed["resident_id"])

                if isinstance(parsed.get("metadata"), dict):
                    client_metadata = parsed["metadata"]
        except Exception:
            pass

        return user_message, req_resident_id, client_metadata, attachments

    async def _stream_response(self, result: AgentResult) -> None:
        """Stream response tokens and final completion/card envelope over the WebSocket."""
        resp_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        agent_display = result.agent_name

        # Stream response tokens (standard envelope + legacy compatibility fields)
        for token in result.content.split():
            await self.ws.send_json({
                "message_id": resp_msg_id,
                "conversation_id": self.session_id,
                "type": "stream_token",
                "sender": {
                    "role": "assistant",
                    "name": agent_display,
                    "id": f"agent-{agent_display.lower()}",
                },
                "content": {
                    "token": token + " ",
                    "agent": agent_display,
                },
                "metadata": {},
                # Backward-compatibility fields:
                "token": token + " ",
                "agent": agent_display,
            })
            await asyncio.sleep(0.02)

        # Send completion envelope with dynamic card / action payload
        card_data = getattr(result, "card_payload", None) or result.metadata.get("card_payload")
        event_type = "agent_card" if card_data else "agent_message"
        content_payload: dict[str, Any] = {
            "text": result.content,
            "suggested_actions": result.suggested_actions,
        }
        if card_data:
            content_payload["card_data"] = card_data
            content_payload["card_type"] = card_data.get("card_type", "package_pickup")

        await self.ws.send_json({
            "message_id": resp_msg_id,
            "conversation_id": self.session_id,
            "type": "done",
            "event": event_type,
            "sender": {
                "role": "assistant",
                "name": agent_display,
                "id": f"agent-{agent_display.lower()}",
            },
            "content": content_payload,
            "metadata": {
                "requires_approval": result.requires_approval,
            },
            # Backward-compatibility fields:
            "agent": agent_display,
            "requires_approval": result.requires_approval,
            "suggested_actions": result.suggested_actions,
            "created_at": datetime.now(UTC).isoformat(),
        })

    async def _send_error_fallback(self) -> None:
        """Send a graceful fallback error envelope when agent execution fails."""
        err_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        err_text = "I'm having trouble retrieving that information right now. Please try again or ask our concierge."
        await self.ws.send_json({
            "message_id": err_msg_id,
            "conversation_id": self.session_id,
            "type": "stream_token",
            "sender": {"role": "assistant", "name": "Customer", "id": "agent-customer"},
            "content": {"token": err_text, "agent": "Customer"},
            "token": err_text,
            "agent": "Customer",
        })
        await self.ws.send_json({
            "message_id": err_msg_id,
            "conversation_id": self.session_id,
            "type": "done",
            "event": "agent_message",
            "sender": {"role": "assistant", "name": "Customer", "id": "agent-customer"},
            "content": {
                "text": err_text,
                "suggested_actions": ["Where is my package?", "Resend pickup PIN", "Locker location and hours"],
            },
            "metadata": {"error": True},
            "agent": "Customer",
            "suggested_actions": ["Where is my package?", "Resend pickup PIN", "Locker location and hours"],
            "created_at": datetime.now(UTC).isoformat(),
        })
