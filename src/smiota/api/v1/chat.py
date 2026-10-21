"""Core conversational and task-planning chat endpoint with HTTP and WebSocket streaming."""
import uuid
import asyncio
from datetime import UTC, datetime
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from smiota.schemas.chat import ChatMessageRequest, ChatMessageResponse
from smiota.agents.base import AgentContext
from smiota.agents.orchestrator import AgentOrchestrator
from smiota.core.security import AuthenticatedUser
from smiota.api.deps import get_current_user, get_orchestrator
from smiota.core.logging import logger

router = APIRouter(prefix="/chat", tags=["Agent Chat & Task Planning"])


@router.post("", response_model=ChatMessageResponse, summary="Send message to Smiota Agent Core")
async def send_message(
    payload: ChatMessageRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    session_id = payload.session_id or current_user.session_id or f"sess-{uuid.uuid4().hex[:8]}"

    # Prevent client-supplied metadata from overriding verified identity & tenant
    sanitized_metadata = dict(payload.metadata or {})
    sanitized_metadata.pop("user_id", None)
    sanitized_metadata.pop("tenant_id", None)
    sanitized_metadata.pop("roles", None)
    if current_user.email:
        sanitized_metadata.setdefault("user_email", current_user.email)
    if current_user.name:
        sanitized_metadata.setdefault("user_name", current_user.name)
    if current_user.location_id:
        sanitized_metadata.setdefault("location_id", current_user.location_id)

    context = AgentContext(
        session_id=session_id,
        user_id=current_user.user_id,
        tenant_id=current_user.tenant_id,
        channel=payload.channel,
        roles=current_user.roles,
        metadata=sanitized_metadata,
    )

    result = await orchestrator.route_and_execute(
        query=payload.message,
        context=context,
        preferred_agent=payload.target_agent,
    )

    return ChatMessageResponse(
        session_id=session_id,
        response=result.content,
        agent_used=result.agent_name,
        requires_approval=result.requires_approval,
        suggested_actions=result.suggested_actions,
    )


from typing import Optional
from fastapi import Query
from smiota.api.deps import get_chat_repo
from smiota.api.v1.websocket_manager import ws_manager
from smiota.core.exceptions import AuthorizationError
from smiota.repositories.chat_repository import BaseChatRepository
from smiota.schemas.chat_session import ChatHistoryResponse
import json


@router.get(
    "/history/{session_id}",
    response_model=ChatHistoryResponse,
    summary="Get Chat Session Conversation History",
    description="Retrieve all stored message turns and rich card payloads for an active conversation session.",
)
async def get_chat_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of recent message turns to retrieve"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    chat_repo: BaseChatRepository = Depends(get_chat_repo),
) -> ChatHistoryResponse:
    """Retrieve full conversation history for a given session with multi-tenant verification."""
    session = await chat_repo.get_session(session_id)
    if not session:
        return ChatHistoryResponse(
            session_id=session_id,
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            channel="webchat",
            total_messages=0,
            messages=[],
        )

    # Multi-tenant isolation enforcement
    is_admin = any(r.lower() in ("admin", "superadmin", "sre") for r in current_user.roles)
    if not is_admin and (session.user_id != current_user.user_id or session.tenant_id != current_user.tenant_id):
        raise AuthorizationError("Access denied: You do not have permission to access this chat session.")

    recent_messages = session.messages[-limit:]
    return ChatHistoryResponse(
        conversation_id=session.session_id,
        session_id=session.session_id,
        user_id=session.user_id,
        tenant_id=session.tenant_id,
        channel=session.channel,
        total_messages=len(session.messages),
        messages=recent_messages,
    )



@router.websocket("/ws/{session_id}")
async def websocket_chat_stream(
    websocket: WebSocket,
    session_id: str,
    resident_id: Optional[str] = Query(None),
):
    """Real-time WebSocket endpoint for instant token streaming, agent responses, and RabbitMQ push alerts."""
    await ws_manager.connect(session_id, websocket, resident_id)
    orchestrator = AgentOrchestrator()
    chat_repo = get_chat_repo()

    try:
        while True:
            raw_data = await websocket.receive_text()
            # Handle heartbeat ping
            if raw_data.strip() == "ping":
                await websocket.send_text("pong")
                continue

            # Parse plain text or standard dynamic JSON envelope
            user_message = raw_data
            req_resident_id = resident_id or "ws-resident"
            incoming_msg_id: Optional[str] = None
            client_metadata: dict[str, Any] = {}
            attachments: list[dict[str, Any]] = []

            try:
                parsed = json.loads(raw_data)
                if isinstance(parsed, dict):
                    # Standard Envelope: type == "user_message" and content is a dynamic dict
                    if parsed.get("type") == "user_message" and isinstance(parsed.get("content"), dict):
                        user_message = str(parsed["content"].get("text", ""))
                        attachments = parsed["content"].get("attachments", [])
                    elif "text" in parsed and parsed["text"] is not None:
                        user_message = str(parsed["text"])

                    if parsed.get("message_id"):
                        incoming_msg_id = str(parsed["message_id"])

                    if parsed.get("sender") and isinstance(parsed["sender"], dict) and parsed["sender"].get("id"):
                        req_resident_id = str(parsed["sender"]["id"])
                    elif parsed.get("resident_id"):
                        req_resident_id = str(parsed["resident_id"])

                    if isinstance(parsed.get("metadata"), dict):
                        client_metadata = parsed["metadata"]
            except Exception:
                pass

            if not user_message.strip():
                continue

            # Resolve tenant and user from active chat session if available
            existing_session = await chat_repo.get_session(session_id)
            tenant_id = existing_session.tenant_id if existing_session else "default"
            if existing_session and existing_session.user_id != "anonymous" and req_resident_id == "ws-resident":
                req_resident_id = existing_session.user_id

            context = AgentContext(
                session_id=session_id,
                user_id=req_resident_id,
                tenant_id=tenant_id,
                channel="webchat",
            )

            try:
                # Route to multi-agent core
                result = await orchestrator.route_and_execute(user_message, context)

                # Generate standard response message ID
                resp_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
                agent_display = result.agent_name

                # Stream response tokens using Standard Envelope (with legacy fields for backward compatibility)
                for token in result.content.split():
                    await websocket.send_json({
                        "message_id": resp_msg_id,
                        "conversation_id": session_id,
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

                await websocket.send_json({
                    "message_id": resp_msg_id,
                    "conversation_id": session_id,
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
            except Exception as agent_err:
                logger.error(f"Error processing message in session {session_id}: {agent_err}", exc_info=True)
                err_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
                err_text = "I'm having trouble retrieving that information right now. Please try again or ask our concierge."
                await websocket.send_json({
                    "message_id": err_msg_id,
                    "conversation_id": session_id,
                    "type": "stream_token",
                    "sender": {"role": "assistant", "name": "Customer", "id": "agent-customer"},
                    "content": {"token": err_text, "agent": "Customer"},
                    "token": err_text,
                    "agent": "Customer",
                })
                await websocket.send_json({
                    "message_id": err_msg_id,
                    "conversation_id": session_id,
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
    except WebSocketDisconnect:
        await ws_manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket fatal error on session {session_id}: {e}", exc_info=True)
        await ws_manager.disconnect(session_id)
