"""Workflow state machine, checkpoints, and execution tracking."""
from enum import Enum
from typing import Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    INITIALIZED = "initialized"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class WorkflowContext(BaseModel):
    """Execution context and state for long-running workflows."""
    workflow_id: str
    workflow_type: str
    status: WorkflowStatus = WorkflowStatus.INITIALIZED
    payload: dict[str, Any] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None
