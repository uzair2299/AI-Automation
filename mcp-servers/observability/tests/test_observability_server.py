"""Unit tests for standalone Observability MCP Server."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.server import (
    query_prometheus_metrics,
    query_http_error_rates,
    query_latency_metrics,
    get_pod_restart_reason,
    get_cluster_pod_counts,
    search_opensearch_logs,
    get_service_logs,
    correlate_deployment_with_incident,
    get_recent_system_changes,
    restart_gke_deployment,
)


@pytest.mark.asyncio
async def test_query_prometheus_metrics_mocked():
    """Verify Prometheus PromQL query execution with mocked client."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "success",
        "data": {
            "result": [
                {"metric": {"pod": "smiotaserver-abc"}, "value": [1700000000, "0.15"]}
            ]
        },
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await query_prometheus_metrics(promql="up")
        assert res["status"] == "success"
        assert res["results_count"] == 1
        assert res["results"][0]["metric"]["pod"] == "smiotaserver-abc"


@pytest.mark.asyncio
async def test_query_http_error_rates():
    """Verify HTTP error rate query generation."""
    with patch("app.server.query_prometheus_metrics", new_callable=AsyncMock) as mock_q:
        mock_q.return_value = {"status": "success", "results": []}
        res = await query_http_error_rates(service_name="auth-service", namespace="smiota-prod")
        assert res["status"] == "success"
        mock_q.assert_awaited_once()
        assert 'service="auth-service"' in mock_q.call_args.kwargs["promql"]


@pytest.mark.asyncio
async def test_query_latency_metrics():
    """Verify latency metrics percentile query."""
    with patch("app.server.query_prometheus_metrics", new_callable=AsyncMock) as mock_q:
        mock_q.return_value = {"status": "success", "results": []}
        res = await query_latency_metrics(percentile="p99")
        assert res["status"] == "success"
        assert "0.99" in mock_q.call_args.kwargs["promql"]


@pytest.mark.asyncio
async def test_get_pod_restart_reason():
    """Verify pod restart diagnostic info."""
    res = await get_pod_restart_reason(service_name="gateway", namespace="smiota-prod")
    assert res["service"] == "gateway"
    assert res["status"] == "Healthy"
    assert "last_restart_time" in res


@pytest.mark.asyncio
async def test_search_opensearch_logs():
    """Verify OpenSearch log querying."""
    logs = await search_opensearch_logs(query="NullPointerException", time_range_minutes=30)
    assert len(logs) > 0
    assert "NullPointerException" in logs[0]["message"]


@pytest.mark.asyncio
async def test_get_service_logs():
    """Verify service log tailing."""
    res = await get_service_logs(service_name="payment-svc", lines=50)
    assert res["service"] == "payment-svc"
    assert len(res["logs"]) == 2


@pytest.mark.asyncio
async def test_correlate_deployment_with_incident():
    """Verify deployment incident correlation."""
    res = await correlate_deployment_with_incident(service_name="auth-svc")
    assert res["service"] == "auth-svc"
    assert res["correlation_found"] is False


@pytest.mark.asyncio
async def test_get_recent_system_changes():
    """Verify recent system change audits."""
    res = await get_recent_system_changes(namespace="smiota-prod", hours_back=6)
    assert res["hours_back"] == 6
    assert res["total_changes"] == 0


@pytest.mark.asyncio
async def test_restart_gke_deployment_requires_approval():
    """Verify restart requires approval token."""
    res = await restart_gke_deployment(deployment_name="backend-api")
    assert res["status"] == "approval_required"
    assert "RemediationApprovalRequiredError" in res["error"]

    # With approval token
    approved_res = await restart_gke_deployment(deployment_name="backend-api", approval_token="OP-APPROVED-99")
    assert approved_res["status"] == "success"
    assert approved_res["action"] == "rollout_restart"

