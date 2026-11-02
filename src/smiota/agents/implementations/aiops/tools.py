"""Observability tool client bindings for AIOps Agent."""
from smiota.mcp.servers.observability.tools import (
    query_prometheus_metrics,
    search_opensearch_logs,
    restart_gke_deployment,
    get_pod_restart_reason,
)

AIOPS_BOUND_TOOLS = [
    "query_prometheus_metrics",
    "search_opensearch_logs",
    "restart_gke_deployment",
    "get_pod_restart_reason",
]

