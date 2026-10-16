"""Microsoft Teams Bot webhook and Adaptive Card adapter."""
from fastapi import APIRouter, Request
from smiota.core.logging import logger

router = APIRouter(prefix="/teams", tags=["Channels - Microsoft Teams"])


@router.post("/webhook", summary="MS Teams Bot Framework webhook")
async def ms_teams_webhook(request: Request):
    """Handles incoming MS Teams conversation activities and Adaptive Card actions."""
    payload = await request.json()
    logger.info("Received MS Teams activity payload")
    # Production: Verify Bot Framework HMAC signature, parse activity, dispatch to Agent Orchestrator
    return {"type": "message", "text": "AIOps agent received your Teams query."}
