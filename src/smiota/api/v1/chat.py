"""Core conversational and task-planning chat endpoint with HTTP and WebSocket streaming."""
import uuid
import asyncio
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

    try:
        while True:
            raw_data = await websocket.receive_text()
            # Handle heartbeat ping
            if raw_data.strip() == "ping":
                await websocket.send_text("pong")
                continue

            # Parse plain text or JSON envelope
            user_message = raw_data
            req_resident_id = resident_id or "ws-resident"
            try:
                parsed = json.loads(raw_data)
                if isinstance(parsed, dict):
                    if "text" in parsed and parsed["text"] is not None:
                        user_message = str(parsed["text"])
                    if parsed.get("resident_id"):
                        req_resident_id = str(parsed["resident_id"])
            except Exception:
                pass

            if not req_resident_id:
                req_resident_id = "ws-resident"

            if not user_message.strip():
                continue

            context = AgentContext(
                session_id=session_id,
                user_id=req_resident_id,
                tenant_id="default",
                channel="webchat",
            )

            try:
                # Route to agent core
                result = await orchestrator.route_and_execute(user_message, context)

                # Stream response tokens
                for token in result.content.split():
                    await websocket.send_json({
                        "type": "token",
                        "token": token + " ",
                        "agent": result.agent_name,
                    })
                    await asyncio.sleep(0.02)

                # Send completion envelope with actions & approval flag
                await websocket.send_json({
                    "type": "done",
                    "agent": result.agent_name,
                    "requires_approval": result.requires_approval,
                    "suggested_actions": result.suggested_actions,
                })
            except Exception as agent_err:
                logger.error(f"Error processing message in session {session_id}: {agent_err}", exc_info=True)
                await websocket.send_json({
                    "type": "token",
                    "token": "I'm having trouble retrieving that information right now. Please try again or ask our concierge.",
                    "agent": "Customer",
                })
                await websocket.send_json({
                    "type": "done",
                    "agent": "Customer",
                    "suggested_actions": ["Where is my package?", "Resend pickup PIN", "Locker location and hours"],
                })
    except WebSocketDisconnect:
        await ws_manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket fatal error on session {session_id}: {e}", exc_info=True)
        await ws_manager.disconnect(session_id)
