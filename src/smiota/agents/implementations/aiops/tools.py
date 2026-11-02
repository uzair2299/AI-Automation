"""Observability tool client bindings for AIOps Agent."""
from smiota.mcp.servers.observability.tools import (
    query_prometheus_metrics,
    search_opensearch_logs,
    restart_gke_deployment,
    get_pod_restart_reason,
    query_http_error_rates,
    query_latency_metrics,
    correlate_deployment_with_incident,
    get_recent_system_changes,
)

AIOPS_BOUND_TOOLS = [
    "query_prometheus_metrics",
    "search_opensearch_logs",
    "restart_gke_deployment",
    "get_pod_restart_reason",
    "query_http_error_rates",
    "query_latency_metrics",
    "correlate_deployment_with_incident",
    "get_recent_system_changes",
]

