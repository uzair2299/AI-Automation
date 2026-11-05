"""Configuration management for SRE Kubernetes MCP Server."""
from __future__ import annotations

import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPSettings(BaseSettings):
    """Configuration loaded strictly from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server & Transport
    MCP_TRANSPORT: str = "stdio"  # "stdio" or "streamable-http"
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8080
    LOG_LEVEL: str = "INFO"

    # Multi-Cluster & Kubeconfig
    KUBECONFIG: Optional[str] = None
    K8S_DEFAULT_CLUSTER: str = "default"
    K8S_CLUSTERS_CONFIG: str = "clusters.yaml"

    # Namespace Restrictions
    K8S_ALLOWED_NAMESPACES: List[str] = []  # Empty means all allowed except denied
    K8S_DENIED_NAMESPACES: List[str] = ["kube-system-sensitive"]

    # Security & Guardrails
    K8S_ALLOW_CONFIGMAP_VALUES: bool = False
    K8S_DEFAULT_TIMEOUT_SECONDS: int = 10

    # Response Limits
    K8S_MAX_LIST_ITEMS: int = 200
    K8S_DEFAULT_LOG_LINES: int = 500
    K8S_HARD_CAP_LOG_LINES: int = 5000
    K8S_MAX_LOG_BYTES: int = 2 * 1024 * 1024  # 2 MB cap


settings = MCPSettings()

