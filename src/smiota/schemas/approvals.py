"""Schemas for Human-in-the-Loop (HITL) remediation approval workflow."""
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class ApprovalRequestCreate(BaseModel):
    action_name: str
    target_resource: str
    command_or_params: dict[str, Any]
    agent_name: str
    reason: str
    requested_by_user_id: str


class ApprovalDecision(BaseModel):
    decision: ApprovalStatus = Field(..., description="'approved' or 'rejected'")
    decided_by_user_id: str
    comment: Optional[str] = None
