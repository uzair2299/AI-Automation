"""Core conversational and task-planning chat endpoint with HTTP and WebSocket streaming."""
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, Query

from smiota.agents.base import AgentContext
from smiota.agents.orchestrator import AgentOrchestrator
from smiota.api.deps import get_chat_repo, get_current_user, get_orchestrator
from smiota.api.v1.websocket_handler import WebSocketChatHandler
from smiota.core.exceptions import AuthorizationError
from smiota.core.security import AuthenticatedUser
from smiota.repositories.chat_repository import BaseChatRepository
from smiota.schemas.chat import ChatMessageRequest, ChatMessageResponse
from smiota.schemas.chat_session import ChatHistoryResponse

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
    handler: WebSocketChatHandler = Depends(),
):
    """Real-time WebSocket endpoint for instant token streaming, agent responses, and RabbitMQ push alerts."""
    await handler.handle()

