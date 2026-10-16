"""Channel webhook notifications for pending HITL remediation approvals."""
from smiota.core.logging import logger


async def dispatch_approval_notification(
    channel: str,
    target_id: str,
    action_name: str,
    approval_id: str,
    reason: str,
) -> bool:
    """Send interactive approval card to MS Teams, Slack, or Webhook."""
    logger.info(
        f"Dispatching HITL notification to channel [{channel}] for action '{action_name}' (Approval ID: {approval_id})"
    )
    # Production: Post Adaptive Card to MS Teams Webhook or Slack block kit
    return True
