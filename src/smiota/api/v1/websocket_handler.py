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

from fastapi import Depends, Query, WebSocket, WebSocketDisconnect

from smiota.agents.base import AgentContext, AgentResult
from smiota.agents.orchestrator import AgentOrchestrator
from smiota.api.deps import get_chat_repo, get_orchestrator
from smiota.api.v1.websocket_manager import ws_manager
from smiota.core.logging import logger
from smiota.repositories.chat_repository import BaseChatRepository


class WebSocketChatHandler:
    """Manages the full lifecycle of a single client's WebSocket chat stream."""

    def __init__(
        self,
        websocket: WebSocket,
        session_id: str,
        resident_id: Optional[str] = Query(None),
        orchestrator: AgentOrchestrator = Depends(get_orchestrator),
        chat_repo: BaseChatRepository = Depends(get_chat_repo),
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

        user_info: dict[str, Any] = {}
        merged_metadata = dict(existing_session.metadata or {}) if existing_session else {}
        if existing_session and existing_session.user:
            user_info = dict(existing_session.user)
        elif merged_metadata.get("user"):
            user_info = dict(merged_metadata["user"])

        # Client metadata can provide auxiliary context
        merged_metadata.update(client_metadata)
        if user_info:
            merged_metadata.setdefault("user", user_info)

        # Authenticate via signed session token in client_metadata if present
        session_token = client_metadata.get("session_token") or client_metadata.get("token")
        if session_token:
            try:
                from smiota.core.security import verify_session_token
                tok_payload = verify_session_token(session_token)
                if tok_payload.get("parent_token"):
                    parent_token = tok_payload["parent_token"]
                user_data = tok_payload.get("user") or tok_payload.get("user_profile")
                if user_data and isinstance(user_data, dict):
                    user_info.update(user_data)
                if tok_payload.get("sub") and req_resident_id in {"ws-resident", "anonymous", "guest", ""}:
                    req_resident_id = tok_payload["sub"]
                if tok_payload.get("tenant_id") and tenant_id == "default":
                    tenant_id = tok_payload["tenant_id"]
            except Exception:
                pass

        if not parent_token:
            parent_token = (
                (existing_session.metadata.get("parent_token") if existing_session and existing_session.metadata else None)
                or (user_info.get("parent_token") if isinstance(user_info, dict) else None)
                or client_metadata.get("parent_token")
                or client_metadata.get("token")
                or None
            )

        if parent_token:
            merged_metadata.setdefault("parent_token", parent_token)
            if isinstance(user_info, dict):
                user_info.setdefault("parent_token", parent_token)

        context = AgentContext(
            session_id=self.session_id,
            user_id=req_resident_id,
            tenant_id=tenant_id,
            channel="webchat",
            user=user_info,
            parent_token=parent_token,
            metadata=merged_metadata,
        )

        try:
            # Route to multi-agent core
            result = await self.orchestrator.route_and_execute(user_message, context)
            await self._stream_response(result)
        except Exception as agent_err:
            logger.error(f"Error processing message in session {self.session_id}: {agent_err}", exc_info=True)
            await self._send_error_fallback()

    def _parse_incoming(self, raw_data: str) -> tuple[str, str, dict[str, Any], list[dict[str, Any]]]:
        """Parse incoming raw frame enforcing the Standard Message Envelope."""
        user_message = ""
        req_resident_id = self.resident_id or "ws-resident"
        client_metadata: dict[str, Any] = {}
        attachments: list[dict[str, Any]] = []

        try:
            parsed = json.loads(raw_data)
            if isinstance(parsed, dict) and parsed.get("type") == "user_message":
                content = parsed.get("content")
                if isinstance(content, dict):
                    user_message = str(content.get("text", "")).strip()
                    raw_attachments = content.get("attachments")
                    if isinstance(raw_attachments, list):
                        attachments = raw_attachments

                sender = parsed.get("sender")
                if isinstance(sender, dict) and sender.get("id"):
                    req_resident_id = str(sender["id"])

                if isinstance(parsed.get("metadata"), dict):
                    client_metadata = parsed["metadata"]
        except Exception:
            pass

        return user_message, req_resident_id, client_metadata, attachments

    async def _stream_response(self, result: AgentResult) -> None:
        """Stream response tokens and final completion/card envelope over the WebSocket."""
        resp_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        agent_display = result.agent_name

        # Stream response tokens using Standard Envelope
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
                },
                "metadata": {},
                "created_at": datetime.now(UTC).isoformat(),
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

        user_info = result.metadata.get("user") or {}
        completion_metadata: dict[str, Any] = {
            "requires_approval": result.requires_approval,
        }
        if user_info:
            completion_metadata["user"] = user_info

        completion_payload: dict[str, Any] = {
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
            "metadata": completion_metadata,
            "created_at": datetime.now(UTC).isoformat(),
        }
        if user_info:
            completion_payload["user"] = user_info

        await self.ws.send_json(completion_payload)

    async def _send_error_fallback(self) -> None:
        """Send a graceful fallback error envelope when agent execution fails."""
        err_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        err_text = "I'm having trouble retrieving that information right now. Please try again or ask our concierge."
        await self.ws.send_json({
            "message_id": err_msg_id,
            "conversation_id": self.session_id,
            "type": "stream_token",
            "sender": {"role": "assistant", "name": "Customer", "id": "agent-customer"},
            "content": {"token": err_text},
            "metadata": {},
            "created_at": datetime.now(UTC).isoformat(),
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
            "created_at": datetime.now(UTC).isoformat(),
        })
