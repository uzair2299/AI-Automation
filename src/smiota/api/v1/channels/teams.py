from __future__ import annotations

"""Microsoft Teams Bot webhook and Adaptive Card adapter.

Handles incoming Microsoft Teams Bot Framework activities:
- Message events: cleans @mentions, builds AgentContext(channel="teams"), dispatches to AgentOrchestrator
- Outbound delivery: Posts the reply activity directly to Microsoft Bot Connector (serviceUrl)
- ConversationUpdate events: greets new members and channels
- Card actions & invocation payloads
"""
import os
import re
import time
from typing import Any, Dict, Optional, Tuple
import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from smiota.agents.base import AgentContext
from smiota.agents.orchestrator import AgentOrchestrator
from smiota.api.deps import get_orchestrator
from smiota.core.config import get_settings
from smiota.core.logging import logger

router = APIRouter(prefix="/teams", tags=["Channels - Microsoft Teams"])

# In-memory token cache: app_id -> (access_token, expiry_timestamp)
_BOT_TOKEN_CACHE: Dict[str, Tuple[str, float]] = {}


def _clean_teams_text(raw_text: str) -> str:
    """Strip XML/HTML Bot mention tags like <at>Smiota Bot</at> from message text."""
    if not raw_text:
        return ""
    cleaned = re.sub(r"<at[^>]*>.*?</at>", "", raw_text, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    return cleaned.strip()


async def _get_bot_framework_token(app_id: str, app_password: str) -> Optional[str]:
    """Obtain a Bearer token from Microsoft Bot Framework OAuth endpoint."""
    now = time.time()
    cached = _BOT_TOKEN_CACHE.get(app_id)
    if cached and cached[1] > now + 60:
        return cached[0]

    token_url = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": app_id,
        "client_secret": app_password,
        "scope": "https://api.botframework.com/.default",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(token_url, data=payload)
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                _BOT_TOKEN_CACHE[app_id] = (token, now + expires_in)
                logger.info("Successfully acquired Microsoft Bot Framework OAuth token")
                return token
            else:
                logger.error(
                    f"Failed to fetch Microsoft Bot token: HTTP {resp.status_code} - {resp.text}"
                )
                return None
    except Exception as e:
        logger.error(f"Exception fetching Microsoft Bot token: {e}", exc_info=True)
        return None


async def _post_reply_to_teams(
    service_url: str,
    conversation_id: str,
    reply_activity: Dict[str, Any],
    app_id: str,
    app_password: str,
) -> bool:
    """Send an activity message back to Teams via the Bot Connector REST API."""
    token = await _get_bot_framework_token(app_id, app_password)
    if not token:
        logger.warning("Could not dispatch reply to Teams serviceUrl: missing OAuth token")
        return False

    clean_service_url = service_url.rstrip("/")
    target_url = f"{clean_service_url}/v3/conversations/{conversation_id}/activities"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(target_url, headers=headers, json=reply_activity)
            if resp.status_code in (200, 201, 202):
                logger.info(
                    f"Successfully delivered Teams reply via Bot Connector [status={resp.status_code}, conv={conversation_id}]"
                )
                return True
            else:
                logger.error(
                    f"Bot Connector rejected activity [status={resp.status_code}, conv={conversation_id}]: {resp.text}"
                )
                return False
    except Exception as e:
        logger.error(f"Exception posting activity to Teams Bot Connector: {e}", exc_info=True)
        return False


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
    service_url = payload.get("serviceUrl")
    bot_recipient = payload.get("recipient", {"id": "bot", "name": "Smiota_ai"})

    settings = get_settings()
    app_id = settings.MICROSOFT_APP_ID or os.getenv("MICROSOFT_APP_ID")
    app_password = settings.MICROSOFT_APP_PASSWORD or os.getenv("MICROSOFT_APP_PASSWORD")

    logger.info(
        f"MS Teams activity received [type={activity_type}, user={user_name}, conv={conversation_id}]"
    )

    # 1. Handle member added / conversation update
    if activity_type == "conversationUpdate":
        logger.info(f"MS Teams conversationUpdate event acknowledged [user='{user_name}', conv='{conversation_id}']")
        welcome_text = (
            f"Hello {user_name}! 👋 I am your Smiota Assistant for Microsoft Teams.\n\n"
            "I can help you with:\n"
            "• 🔍 **AIOps & SRE**: Cluster health, pod metrics, Prometheus alerts, incident RCA\n"
            "• 📦 **Smart Lockers**: Parcel tracking, locker doors, and pickup diagnostics\n"
            "• 🛡️ **DevSecOps**: Security scans, dependency audits, and deployments"
        )
        reply_activity = {
            "type": "message",
            "from": bot_recipient,
            "recipient": from_user,
            "conversation": conversation,
            "replyToId": payload.get("id"),
            "text": welcome_text,
        }
        if service_url and app_id and app_password:
            await _post_reply_to_teams(
                service_url=service_url,
                conversation_id=conversation_id,
                reply_activity=reply_activity,
                app_id=app_id,
                app_password=app_password,
            )
        return reply_activity

    # 2. Handle incoming user message
    if activity_type == "message":
        raw_text = payload.get("text", "")
        cleaned_query = _clean_teams_text(raw_text)

        logger.info(
            f"MS Teams message received [user='{user_name}', conv='{conversation_id}', query='{cleaned_query[:120]}']"
        )

        if not cleaned_query:
            prompt_activity = {
                "type": "message",
                "from": bot_recipient,
                "recipient": from_user,
                "conversation": conversation,
                "replyToId": payload.get("id"),
                "text": "Hello! How can I assist you today? Ask me about cluster health, active incidents, or smart lockers.",
            }
            if service_url and app_id and app_password:
                await _post_reply_to_teams(
                    service_url=service_url,
                    conversation_id=conversation_id,
                    reply_activity=prompt_activity,
                    app_id=app_id,
                    app_password=app_password,
                )
            return prompt_activity

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
                "serviceUrl": service_url,
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
            reply_activity = {
                "type": "message",
                "from": bot_recipient,
                "recipient": from_user,
                "conversation": conversation,
                "replyToId": payload.get("id"),
                "text": agent_result.content,
            }
            if service_url and app_id and app_password:
                await _post_reply_to_teams(
                    service_url=service_url,
                    conversation_id=conversation_id,
                    reply_activity=reply_activity,
                    app_id=app_id,
                    app_password=app_password,
                )
            return reply_activity
        except Exception as err:
            logger.error(f"Error processing Teams message through orchestrator: {err}", exc_info=True)
            err_activity = {
                "type": "message",
                "from": bot_recipient,
                "recipient": from_user,
                "conversation": conversation,
                "replyToId": payload.get("id"),
                "text": "I encountered an error processing your request. Please try again or check the platform logs.",
            }
            if service_url and app_id and app_password:
                await _post_reply_to_teams(
                    service_url=service_url,
                    conversation_id=conversation_id,
                    reply_activity=err_activity,
                    app_id=app_id,
                    app_password=app_password,
                )
            return err_activity

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
