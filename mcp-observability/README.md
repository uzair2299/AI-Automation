# Smiota Observability MCP Server

**Port**: `8081`  
**Protocol**: Model Context Protocol (FastMCP over Streamable-HTTP / SSE)  
**Role**: Provides Prometheus metric queries, latency percentile calculations, OpenSearch log searches, and incident correlation.

---

## Exposed MCP Tools

1. `query_prometheus_metrics(promql: str, duration: str = "1h")`
2. `query_http_error_rates(service_name: str, namespace: str, duration: str)`
3. `query_latency_metrics(service_name: str, namespace: str, percentile: str)`
4. `get_pod_restart_reason(service_name: str, namespace: str)`
5. `get_cluster_pod_counts(namespace: Optional[str])`
6. `search_opensearch_logs(query: str, time_range_minutes: int)`
7. `get_service_logs(service_name: str, namespace: str, lines: int)`
8. `correlate_deployment_with_incident(service_name: str, namespace: str, incident_time_iso: Optional[str])`
9. `get_recent_system_changes(namespace: str, hours_back: int)`
10. `restart_gke_deployment(deployment_name: str, namespace: str, reason: str, approval_token: Optional[str])`

---

## Local Development & Docker

```bash
cd mcp-observability
pip install -r requirements.txt
python -m app.server
```

Or via Docker:
```bash
docker build -t smiota-observability-mcp:latest -f mcp-observability/Dockerfile mcp-observability/
docker run -p 8081:8081 smiota-observability-mcp:latest
```

