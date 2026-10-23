"""Microsoft Teams Bot webhook and Adaptive Card adapter.

Handles incoming Microsoft Teams Bot Framework activities:
- Message events: cleans @mentions, builds AgentContext(channel="teams"), dispatches to AgentOrchestrator (defaults to AIOpsAgent)
- ConversationUpdate events: greets new members and channels
- Card actions & invocation payloads
"""
import re
from typing import Any, Dict
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from smiota.agents.base import AgentContext
from smiota.agents.orchestrator import AgentOrchestrator
from smiota.api.deps import get_orchestrator
from smiota.core.logging import logger

router = APIRouter(prefix="/teams", tags=["Channels - Microsoft Teams"])


def _clean_teams_text(raw_text: str) -> str:
    """Strip XML/HTML Bot mention tags like <at>Smiota Bot</at> from message text."""
    if not raw_text:
        return ""
    cleaned = re.sub(r"<at[^>]*>.*?</at>", "", raw_text, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    return cleaned.strip()


@router.post("/webhook", summary="MS Teams Bot Framework messaging endpoint")
async def ms_teams_webhook(
    request: Request,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
) -> Dict[str, Any]:
    """Handles incoming MS Teams conversation activities and dispatches them to Smiota Agents."""
    try:
        payload = await request.json()
    except Exception as e:
        logger.warning(f"Invalid JSON received on Teams webhook: {e}")
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})

    activity_type = payload.get("type", "message")
    from_user = payload.get("from", {})
    user_name = from_user.get("name", "Teams User")
    user_id = from_user.get("id") or from_user.get("aadObjectId") or "teams-user"
    conversation = payload.get("conversation", {})
    conversation_id = conversation.get("id", "teams-conversation")

    logger.info(
        f"MS Teams activity received [type={activity_type}, user={user_name}, conv={conversation_id}]"
    )

    # 1. Handle member added / conversation update
    if activity_type == "conversationUpdate":
        logger.info(f"MS Teams conversationUpdate event acknowledged [user='{user_name}', conv='{conversation_id}']")
        return {
            "type": "message",
            "text": (
                f"Hello {user_name}! 👋 I am your Smiota Assistant for Microsoft Teams.\n\n"
                "I can help you with:\n"
                "• 🔍 **AIOps & SRE**: Cluster health, pod metrics, Prometheus alerts, incident RCA\n"
                "• 📦 **Smart Lockers**: Parcel tracking, locker doors, and pickup diagnostics\n"
                "• 🛡️ **DevSecOps**: Security scans, dependency audits, and deployments"
            ),
        }

    # 2. Handle incoming user message
    if activity_type == "message":
        raw_text = payload.get("text", "")
        cleaned_query = _clean_teams_text(raw_text)

        logger.info(
            f"MS Teams message received [user='{user_name}', conv='{conversation_id}', query='{cleaned_query[:120]}']"
        )

        if not cleaned_query:
            return {
                "type": "message",
                "text": "Hello! How can I assist you today? Ask me about cluster health, active incidents, or smart lockers.",
            }

        # Build authorized AgentContext for the Teams channel
        context = AgentContext(
            session_id=conversation_id,
            user_id=str(user_id),
            tenant_id="default",
            channel="teams",
            roles=["sre", "devops", "team_member"],
            user={"id": str(user_id), "name": user_name},
            metadata={
                "channelId": "msteams",
                "serviceUrl": payload.get("serviceUrl"),
                "conversationType": conversation.get("conversationType", "personal"),
            },
        )

        # Route query through AgentOrchestrator (defaults to AIOps agent for Teams)
        try:
            agent_result = await orchestrator.route_and_execute(
                query=cleaned_query,
                context=context,
            )
            logger.info(
                f"MS Teams response ready [agent='{agent_result.agent_name}', conv='{conversation_id}', chars={len(agent_result.content)}]"
            )
            return {
                "type": "message",
                "text": agent_result.content,
            }
        except Exception as err:
            logger.error(f"Error processing Teams message through orchestrator: {err}", exc_info=True)
            return {
                "type": "message",
                "text": "I encountered an error processing your request. Please try again or check the platform logs.",
            }

    # 3. Handle Invoke / Adaptive Card actions
    if activity_type == "invoke":
        logger.info(f"MS Teams invoke action received [conv='{conversation_id}']")
        return {
            "status": 200,
            "body": {
                "type": "message",
                "text": "Action acknowledged.",
            },
        }

    logger.debug(f"MS Teams unhandled activity [type={activity_type}, conv={conversation_id}]")
    return {"status": "ignored", "activity_type": activity_type}
