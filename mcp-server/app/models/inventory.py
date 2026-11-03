"""Pydantic v2 models for Kubernetes inventory data."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ClusterInfo(BaseModel):
    name: str
    kubernetes_version: str
    api_endpoint_host: str
    node_count: int


class NodeDetails(BaseModel):
    name: str
    kubelet_version: str
    conditions: Dict[str, str] = Field(default_factory=dict)
    capacity: Dict[str, str] = Field(default_factory=dict)
    allocatable: Dict[str, str] = Field(default_factory=dict)
    taints: List[Dict[str, str]] = Field(default_factory=list)


class ContainerStatus(BaseModel):
    name: str
    ready: bool
    restart_count: int
    state: str
    reason: Optional[str] = None
    exit_code: Optional[int] = None


class PodDetails(BaseModel):
    name: str
    namespace: str
    phase: str
    node_name: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    containers: List[ContainerStatus] = Field(default_factory=list)
    conditions: Dict[str, str] = Field(default_factory=dict)
    recent_events: List[str] = Field(default_factory=list)


class SecretMetadata(BaseModel):
    """CRITICAL: Contains ONLY metadata and key names. NEVER secret data values."""
    name: str
    namespace: str
    type: str
    keys: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)


class PaginatedList(BaseModel):
    total: int
    items: List[Any]
    truncated: bool = False
