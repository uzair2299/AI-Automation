"""Observability & Logs MCP Tools (Prometheus, OpenSearch, GCP Monitoring, Grafana)."""
from smiota.mcp.security import mcp_tool
from smiota.schemas.mcp import ToolAccessLevel


@mcp_tool(name="query_prometheus_metrics", access_level=ToolAccessLevel.READ_ONLY)
async def query_prometheus_metrics(promql: str, duration: str = "1h") -> dict:
    """Execute PromQL query against Prometheus to inspect CPU/memory/error rates."""
    # Production: call Prometheus HTTP API
    return {
        "status": "success",
        "query": promql,
        "results": [{"metric": "container_cpu_usage", "value": "85.2%"}]
    }


@mcp_tool(name="search_opensearch_logs", access_level=ToolAccessLevel.READ_ONLY)
async def search_opensearch_logs(query: str, time_range_minutes: int = 15) -> list[dict]:
    """Search application and system logs via OpenSearch."""
    # Production: execute OpenSearch DSL query
    return [
        {"timestamp": "2026-10-15T11:20:00Z", "level": "ERROR", "message": "Connection pool exhausted"}
    ]


@mcp_tool(name="restart_gke_deployment", access_level=ToolAccessLevel.REMEDIATION)
async def restart_gke_deployment(namespace: str, deployment_name: str, approval_token: str | None = None) -> dict:
    """Restart a deployment in Kubernetes / GKE (Remediation action - requires human approval)."""
    # Production: execute kubectl rollout restart deployment
    return {
        "status": "restarted",
        "deployment": deployment_name,
        "namespace": namespace,
        "approved_by_token": approval_token
    }


@mcp_tool(name="get_pod_restart_reason", access_level=ToolAccessLevel.READ_ONLY)
async def get_pod_restart_reason(service_name: str, namespace: str = "production") -> dict:
    """Inspect Kubernetes / GKE pod termination state, exit codes, and restart telemetry."""
    svc = service_name.lower().replace("-", "").replace("_", "")
    if "smiota" in svc or "server" in svc or "payment" in svc:
        return {
            "status": "success",
            "service": service_name,
            "namespace": namespace,
            "restart_count_1h": 4,
            "exit_code": 137,
            "termination_reason": "OOMKilled",
            "memory_limit": "4096Mi",
            "peak_memory_observed": "4128Mi",
            "last_crash_timestamp": "12 minutes ago",
            "recent_error": "java.lang.OutOfMemoryError: Java heap space at com.smiota.service.ParcelSyncService",
            "message": "Container exceeded 4096Mi memory limit and was terminated by Linux kernel OOM killer."
        }
    return {
        "status": "success",
        "service": service_name,
        "namespace": namespace,
        "restart_count_1h": 0,
        "exit_code": 0,
        "termination_reason": "Completed",
        "message": f"Service '{service_name}' is healthy with 0 abnormal terminations."
    }

