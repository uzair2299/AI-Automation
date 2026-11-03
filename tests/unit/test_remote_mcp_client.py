"""Unit tests for RemoteMCPClient and distributed JSON-RPC 2.0 execution with local fallback."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from smiota.mcp.client import MCPClient, RemoteMCPClient
from smiota.mcp.registry import MCPToolRegistry
from smiota.schemas.mcp import MCPToolExecutionResult


def test_remote_mcp_client_tool_routing():
    """Verify RemoteMCPClient accurately routes tools to authoritative microservices."""
    client = RemoteMCPClient(
        k8s_url="http://k8s-sre:8080",
        observability_url="http://observability:8081",
        locker_url="http://smart-locker:8082",
    )

    # Kubernetes SRE tools
    assert client.route_tool("k8s_list_pods") == "http://k8s-sre:8080"
    assert client.route_tool("diagnose_crashloop") == "http://k8s-sre:8080"
    assert client.route_tool("check_dns_resolution") == "http://k8s-sre:8080"
    assert client.route_tool("check_pvc_status") == "http://k8s-sre:8080"
    assert client.route_tool("get_cluster_info") == "http://k8s-sre:8080"

    # Observability tools
    assert client.route_tool("query_prometheus_metrics") == "http://observability:8081"
    assert client.route_tool("query_http_error_rates") == "http://observability:8081"
    assert client.route_tool("search_opensearch_logs") == "http://observability:8081"
    assert client.route_tool("correlate_deployment_with_incident") == "http://observability:8081"
    assert client.route_tool("get_service_logs") == "http://observability:8081"

    # Locker tools
    assert client.route_tool("locker_open_compartment") == "http://smart-locker:8082"
    assert client.route_tool("package_lookup") == "http://smart-locker:8082"
    assert client.route_tool("resident_verify_pin") == "http://smart-locker:8082"


@pytest.mark.asyncio
async def test_remote_mcp_client_call_tool_remote_success():
    """Verify JSON-RPC 2.0 tool execution over HTTP."""
    client = RemoteMCPClient(k8s_url="http://k8s-sre:8080")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "jsonrpc": "2.0",
        "id": "123",
        "result": {
            "content": [{"type": "text", "text": '{"pods_total": 42, "phase": "Healthy"}'}]
        },
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await client.call_tool_remote(
            server_url="http://k8s-sre:8080",
            tool_name="k8s_list_pods",
            arguments={"namespace": "default"},
        )

        assert result == {"pods_total": 42, "phase": "Healthy"}
        assert mock_post.called
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["method"] == "tools/call"
        assert call_kwargs["json"]["params"]["name"] == "k8s_list_pods"


@pytest.mark.asyncio
async def test_mcp_client_local_execution():
    """Verify local in-memory execution when remote_enabled is False."""
    client = MCPClient(remote_enabled=False)

    # Register dummy tool in registry
    async def sample_tool(val: int):
        return {"doubled": val * 2}

    MCPToolRegistry.register_tool(
        name="test_doubler",
        description="Double an integer",
        func=sample_tool,
    )

    result = await client.execute_tool("test_doubler", {"val": 21})
    assert isinstance(result, MCPToolExecutionResult)
    assert result.success is True
    assert result.output == {"doubled": 42}


@pytest.mark.asyncio
async def test_mcp_client_remote_fallback_to_local_on_error():
    """Verify seamless fallback to local registry when remote service is unreachable."""
    client = MCPClient(remote_enabled=True, remote_fallback=True)

    async def fallback_tool():
        return {"source": "local_fallback"}

    MCPToolRegistry.register_tool(
        name="test_fallback_tool",
        description="Fallback test",
        func=fallback_tool,
    )

    # Remote call raises ConnectionError
    with patch.object(
        client.remote_client, "call_tool_remote", side_effect=ConnectionError("Server offline")
    ):
        result = await client.execute_tool("test_fallback_tool", {})
        assert result.success is True
        assert result.output == {"source": "local_fallback"}

