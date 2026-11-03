"""Common Diagnosis and Troubleshooting output schema."""
from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class TargetResource(BaseModel):
    """Target Kubernetes resource identifier."""
    kind: str
    name: str
    namespace: Optional[str] = None
    cluster: Optional[str] = None


class Finding(BaseModel):
    """Specific diagnosis finding with actionable next steps."""
    severity: Literal["critical", "warning", "info"]
    title: str
    evidence: List[str] = Field(default_factory=list)
    probable_cause: str
    suggested_next_steps: List[str] = Field(default_factory=list)


class DiagnosisReport(BaseModel):
    """Unified diagnosis contract across all SRE troubleshooting tools."""
    target: TargetResource
    status: Literal["healthy", "degraded", "failing", "unknown"]
    findings: List[Finding] = Field(default_factory=list)
    checked: List[str] = Field(default_factory=list)
    truncated: bool = False

