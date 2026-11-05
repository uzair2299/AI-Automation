"""Human-in-the-Loop (HITL) approval endpoints for remediation actions."""
from fastapi import APIRouter, Depends, HTTPException
from smiota.schemas.approvals import ApprovalDecision, ApprovalStatus
from smiota.core.security import AuthenticatedUser
from smiota.api.deps import get_current_user

router = APIRouter(prefix="/approvals", tags=["Remediation Approvals (HITL)"])

# Mock in-memory state store for demonstration
PENDING_APPROVALS: dict[str, dict] = {}


@router.get("", summary="List pending remediation actions")
async def list_pending_approvals(current_user: AuthenticatedUser = Depends(get_current_user)):
    return list(PENDING_APPROVALS.values())


@router.post("/{approval_id}/decide", summary="Approve or reject remediation action")
async def decide_approval(
    approval_id: str,
    decision: ApprovalDecision,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    if "admin" not in current_user.roles and "sre" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Insufficient privileges to approve remediation actions.")

    return {
        "approval_id": approval_id,
        "status": decision.decision,
        "decided_by": current_user.email,
        "message": f"Remediation action successfully {decision.decision.value}."
    }
