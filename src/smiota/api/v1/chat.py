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
    session_id = payload.session_id or f"sess-{uuid.uuid4().hex[:8]}"

    context = AgentContext(
        session_id=session_id,
        user_id=current_user.user_id,
        tenant_id=current_user.tenant_id,
        channel=payload.channel,
        roles=current_user.roles,
        metadata=payload.metadata,
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


@router.websocket("/ws/{session_id}")
async def websocket_chat_stream(websocket: WebSocket, session_id: str):
    """Real-time WebSocket endpoint for instant token streaming and agent responses."""
    await websocket.accept()
    orchestrator = AgentOrchestrator()
    logger.info(f"WebSocket client connected for session: {session_id}")

    try:
        while True:
            user_message = await websocket.receive_text()
            context = AgentContext(
                session_id=session_id,
                user_id="ws-client",
                tenant_id="default",
                channel="webchat",
            )

            # Route to agent core
            result = await orchestrator.route_and_execute(user_message, context)

            # Stream response tokens
            for token in result.content.split():
                await websocket.send_json({
                    "type": "token",
                    "token": token + " ",
                    "agent": result.agent_name,
                })
                await asyncio.sleep(0.03)

            # Send completion envelope with actions & approval flag
            await websocket.send_json({
                "type": "done",
                "agent": result.agent_name,
                "requires_approval": result.requires_approval,
                "suggested_actions": result.suggested_actions,
            })
    except WebSocketDisconnect:
        logger.info(f"WebSocket session {session_id} disconnected.")
