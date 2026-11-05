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
import uuid
from typing import Any

import httpx
import jwt
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from agents.base import AgentContext
from agents.orchestrator import AgentOrchestrator
from api.deps import get_orchestrator
from core.config import get_settings
from core.logging import correlation_id_ctx, logger

router = APIRouter(prefix="/teams", tags=["Channels - Microsoft Teams"])

# Inbound Bot Framework OpenID / JWKS validation clients
_BOTFRAMEWORK_JWKS_CLIENT = jwt.PyJWKClient(
    "https://login.botframework.com/v1/.well-known/keys",
    cache_jwk_set=True,
    lifespan=86400,
)
_AAD_JWKS_CLIENT = jwt.PyJWKClient(
    "https://login.microsoftonline.com/common/discovery/v2.0/keys",
    cache_jwk_set=True,
    lifespan=86400,
)


def _verify_inbound_request(
    request: Request,
    payload: dict[str, Any],
    app_id: str,
    configured_tid: str | None = None,
) -> tuple[bool, str | None, dict[str, Any] | None]:
    """Cryptographically verify incoming Bot Framework JWT token and enforce tenant allowlist."""
    settings = get_settings()

    # 1. Check if inbound JWT validation is enforced in this environment
    if not getattr(settings, "TEAMS_VALIDATE_INBOUND_JWT", True):
        logger.debug(
            "Inbound Teams JWT validation is disabled (TEAMS_VALIDATE_INBOUND_JWT=False). Permitting request."
        )
        return True, None, {}

    # 2. Extract Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.startswith("Bearer "):
        # If in dev or test mode and no auth header, permit if configured
        if getattr(settings, "ENVIRONMENT", "").lower() in ("development", "test", "dev"):
            logger.warning(
                "⚠️ [0. TEAMS AUTH] No Bearer token provided, but running in development mode. Allowing request."
            )
            return True, None, {}
        logger.warning("❌ [0. TEAMS AUTH REJECTED] Missing or invalid Authorization header on webhook call")
        return False, "Missing or invalid Authorization header", None

    token = auth_header.split(" ", 1)[1].strip()

    # 3. Decode unverified claims to verify audience (app_id)
    try:
        unverified_claims = jwt.decode(token, options={"verify_signature": False})
    except Exception as err:
        logger.warning(f"❌ [0. TEAMS AUTH REJECTED] Invalid JWT format: {err}")
        return False, f"Malformed JWT: {err}", None

    token_aud = unverified_claims.get("aud")
    if token_aud != app_id:
        logger.warning(
            f"❌ [0. TEAMS AUTH REJECTED] Token audience mismatch: expected '{app_id}', got '{token_aud}'"
        )
        return False, f"Token audience mismatch (expected {app_id})", None

    # 4. Verify cryptographic signature against Microsoft's public JWKS keys
    decoded_claims = None
    verification_error = None
    for jwks_client in (_BOTFRAMEWORK_JWKS_CLIENT, _AAD_JWKS_CLIENT):
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            decoded_claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=app_id,
                options={"verify_exp": True},
            )
            break
        except Exception as err:
            verification_error = err
            continue

    if not decoded_claims:
        logger.warning(
            f"❌ [0. TEAMS AUTH REJECTED] JWT signature verification failed against Microsoft JWKS: {verification_error}"
        )
        return False, f"JWT signature verification failed: {verification_error}", None

    # 5. Enforce Tenant Allowlist
    if getattr(settings, "TEAMS_ENFORCE_TENANT_ID", True) and configured_tid:
        incoming_tid = _resolve_tenant_id(payload=payload, service_url=payload.get("serviceUrl"))
        token_tid = decoded_claims.get("tid")
        effective_tid = incoming_tid or token_tid
        if effective_tid and effective_tid != configured_tid:
            logger.warning(
                f"❌ [0. TEAMS TENANT REJECTED] Tenant ID mismatch: incoming '{effective_tid}' != authorized '{configured_tid}'"
            )
            return False, f"Tenant ID '{effective_tid}' is not authorized", decoded_claims

    logger.info(
        f"✅ [0. TEAMS INBOUND AUTH VERIFIED] Microsoft JWT signature & Tenant verified (AppId: {app_id})"
    )
    return True, None, decoded_claims

# In-memory token cache: app_id -> (access_token, expiry_timestamp)
_BOT_TOKEN_CACHE: dict[str, tuple[str, float]] = {}


def _clean_teams_text(raw_text: str) -> str:
    """Strip XML/HTML Bot mention tags like <at>Smiota Bot</at> from message text."""
    if not raw_text:
        return ""
    cleaned = re.sub(r"<at[^>]*>.*?</at>", "", raw_text, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    return cleaned.strip()


def _resolve_tenant_id(
    payload: dict[str, Any] | None = None, service_url: str | None = None
) -> str | None:
    """Resolve Microsoft Entra ID Tenant ID from payload, service URL, or environment."""
    if payload:
        tenant_from_channel = payload.get("channelData", {}).get("tenant", {}).get("id")
        if tenant_from_channel:
            return str(tenant_from_channel).strip()

    if service_url:
        for part in service_url.strip("/").split("/"):
            if len(part) == 36 and part.count("-") == 4:
                return part

    settings = get_settings()
    configured_tid = getattr(settings, "MICROSOFT_APP_TENANT_ID", None) or os.getenv(
        "MICROSOFT_APP_TENANT_ID"
    )
    if configured_tid:
        return str(configured_tid).strip()
    return None


async def _get_bot_framework_token(
    app_id: str, app_password: str, tenant_id: str | None = None
) -> str | None:
    """Obtain a Bearer token from Microsoft Bot Framework / Entra ID OAuth endpoint."""
    now = time.time()
    authority = tenant_id or "botframework.com"
    cache_key = f"{app_id}:{authority}"
    cached = _BOT_TOKEN_CACHE.get(cache_key)
    if cached and cached[1] > now + 60:
        return cached[0]

    # Try tenant-specific endpoint first if available, with botframework.com as fallback
    authorities_to_try = [authority]
    if authority != "botframework.com":
        authorities_to_try.append("botframework.com")

    payload = {
        "grant_type": "client_credentials",
        "client_id": app_id,
        "client_secret": app_password,
        "scope": "https://api.botframework.com/.default",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for auth_target in authorities_to_try:
            token_url = f"https://login.microsoftonline.com/{auth_target}/oauth2/v2.0/token"
            try:
                resp = await client.post(token_url, data=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    token = data.get("access_token")
                    expires_in = data.get("expires_in", 3600)
                    _BOT_TOKEN_CACHE[cache_key] = (token, now + expires_in)
                    logger.info(
                        f"Successfully acquired Microsoft Bot Framework OAuth token [authority={auth_target}]"
                    )
                    return token
                else:
                    logger.warning(
                        f"Failed to fetch Microsoft Bot token from {auth_target}: HTTP {resp.status_code} - {resp.text}"
                    )
            except Exception as e:
                logger.error(
                    f"Exception fetching Microsoft Bot token from {auth_target}: {e}", exc_info=True
                )

    return None


async def _post_reply_to_teams(
    service_url: str,
    conversation_id: str,
    reply_activity: dict[str, Any],
    app_id: str,
    app_password: str,
    tenant_id: str | None = None,
) -> bool:
    """Send an activity message back to Teams via the Bot Connector REST API."""
    if not app_password:
        logger.error(
            "Cannot dispatch reply to Teams: MICROSOFT_APP_PASSWORD is missing/empty! Please set it in environment variables."
        )
        return False

    token = await _get_bot_framework_token(app_id, app_password, tenant_id=tenant_id)
    if not token:
        logger.error("Could not dispatch reply to Teams: failed to obtain OAuth token")
        return False

    clean_service_url = service_url.rstrip("/")
    reply_to_id = reply_activity.get("replyToId")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # In Bot Framework REST API:
    # 1. Reply endpoint: POST /v3/conversations/{conversationId}/activities/{activityId}
    # 2. Direct conversation endpoint: POST /v3/conversations/{conversationId}/activities
    endpoints = []
    if reply_to_id:
        endpoints.append(
            f"{clean_service_url}/v3/conversations/{conversation_id}/activities/{reply_to_id}"
        )
    endpoints.append(f"{clean_service_url}/v3/conversations/{conversation_id}/activities")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            for target_url in endpoints:
                resp = await client.post(target_url, headers=headers, json=reply_activity)
                if resp.status_code in (200, 201, 202):
                    logger.info(
                        f"✅ [4. TEAMS DISPATCH SUCCESS] Delivered response via Bot Connector (HTTP {resp.status_code}) | Conv: '{conversation_id}'"
                    )
                    return True
                else:
                    corr_id = resp.headers.get("X-Correlating-OperationId", "")
                    logger.error(
                        f"❌ [4. TEAMS DISPATCH REJECTED] Bot Connector rejected activity [url={target_url}, status={resp.status_code}, corr={corr_id}]: {resp.text}"
                    )
            return False
    except Exception as e:
        logger.error(f"Exception posting activity to Teams Bot Connector: {e}", exc_info=True)
        return False


@router.post("/webhook", summary="MS Teams Bot Framework messaging endpoint")
async def ms_teams_webhook(
    request: Request,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
) -> dict[str, Any]:
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
    bot_recipient = payload.get("recipient", {})

    settings = get_settings()
    app_id = (
        settings.MICROSOFT_APP_ID
        or os.getenv("MICROSOFT_APP_ID")
        or "c93bfc04-2bf6-4c89-b04f-5d4ef6aa734a"
    )
    app_password = settings.MICROSOFT_APP_PASSWORD or os.getenv("MICROSOFT_APP_PASSWORD")
    tenant_id = _resolve_tenant_id(payload=payload, service_url=service_url)

    # Format bot sender identity (Teams expects 28:<app_id>)
    bot_from_id = bot_recipient.get("id") or f"28:{app_id}"
    bot_name = bot_recipient.get("name") or "Smiota_ai"
    bot_sender = {"id": bot_from_id, "name": bot_name}

    corr_id = correlation_id_ctx.get()
    if not corr_id or corr_id == "-":
        corr_id = f"corr-{uuid.uuid4().hex[:12]}"
        correlation_id_ctx.set(corr_id)

    # Authenticate inbound Microsoft Teams request
    is_authenticated, auth_err, _ = _verify_inbound_request(
        request=request,
        payload=payload,
        app_id=app_id,
        configured_tid=tenant_id,
    )
    if not is_authenticated:
        status_code = 403 if "Tenant" in str(auth_err) else 401
        return JSONResponse(
            status_code=status_code,
            content={"error": f"{'Forbidden' if status_code == 403 else 'Unauthorized'}: {auth_err}"},
        )

    logger.info(
        f"👉 [1. TEAMS INGRESS] Activity received [type='{activity_type}'] from user '{user_name}' (ID: {user_id}) | "
        f"Conv: '{conversation_id}' | ServiceUrl: {service_url} | HasPassword: {bool(app_password)}"
    )

    if not app_password:
        logger.error(
            "CRITICAL: MICROSOFT_APP_PASSWORD is not set in environment! Outbound replies to Teams cannot be sent."
        )

    # 1. Handle member added / conversation update
    if activity_type == "conversationUpdate":
        logger.info(
            f"MS Teams conversationUpdate event acknowledged [user='{user_name}', conv='{conversation_id}']"
        )
        welcome_text = (
            f"Hello {user_name}! 👋 I am your Smiota DevOps & SRE Assistant for Microsoft Teams.\n\n"
            "I can help you with:\n"
            "• ☸️ **Kubernetes Inspection**: Clusters, namespaces, nodes, pods, deployments, services, ingresses, configmaps, secrets metadata, HPAs, and quotas\n"
            "• 🩺 **SRE Troubleshooting**: Deep RCA for CrashLoopBackOff, ImagePullBackOff, pending pods, node conditions, PVC storage, internal DNS, and network connectivity\n"
            "• 📊 **AIOps & Observability**: Cluster health, live Prometheus telemetry, 5xx error rates, latency analysis, and container logs\n"
            "• 🛡️ **DevSecOps**: Security scans, dependency audits, and CI/CD pipelines\n"
            "• 📦 **Smart Lockers**: Parcel tracking and locker diagnostics"
        )
        reply_activity = {
            "type": "message",
            "from": bot_sender,
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
                tenant_id=tenant_id,
            )
        return reply_activity

    # 2. Handle incoming user message
    if activity_type == "message":
        raw_text = payload.get("text", "")
        cleaned_query = _clean_teams_text(raw_text)

        logger.info(
            f"📥 [1. TEAMS QUERY] User '{user_name}' asked: '{cleaned_query}' (conv: '{conversation_id}') -> Dispatching to Agent Orchestrator"
        )

        if not cleaned_query:
            prompt_activity = {
                "type": "message",
                "from": bot_sender,
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
                    tenant_id=tenant_id,
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
                f"🎯 [3. ORCHESTRATOR RESULT] Selected Agent: [{agent_result.agent_name}] | Requires Approval: {agent_result.requires_approval} | "
                f"Generated response: {len(agent_result.content)} chars | Conv: '{conversation_id}'"
            )
            reply_activity = {
                "type": "message",
                "from": bot_sender,
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
                    tenant_id=tenant_id,
                )
            return reply_activity
        except Exception as err:
            logger.error(
                f"Error processing Teams message through orchestrator: {err}", exc_info=True
            )
            err_activity = {
                "type": "message",
                "from": bot_sender,
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
                    tenant_id=tenant_id,
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
