"""Asynchronous MCP Client for invoking local and distributed MCP servers via JSON-RPC 2.0."""
from __future__ import annotations

import time
import uuid
from typing import Any, Optional

import httpx

from smiota.core.config import get_settings
from smiota.core.exceptions import MCPToolExecutionError, RemediationApprovalRequiredError
from smiota.core.logging import logger
from smiota.mcp.registry import MCPToolRegistry
from smiota.schemas.mcp import MCPToolExecutionResult


class RemoteMCPClient:
    """Dispatches JSON-RPC 2.0 requests to dedicated distributed MCP microservices over HTTP."""

    def __init__(
        self,
        k8s_url: Optional[str] = None,
        observability_url: Optional[str] = None,
        locker_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        settings = get_settings()
        self.k8s_url = (k8s_url or getattr(settings, "MCP_K8S_SERVER_URL", "http://localhost:8080")).rstrip("/")
        self.observability_url = (
            observability_url or getattr(settings, "MCP_OBSERVABILITY_SERVER_URL", "http://localhost:8081")
        ).rstrip("/")
        self.locker_url = (
            locker_url or getattr(settings, "MCP_LOCKER_SERVER_URL", "http://localhost:8082")
        ).rstrip("/")
        self.timeout = timeout or getattr(settings, "MCP_CLIENT_TIMEOUT_SECONDS", 15.0)

    def route_tool(self, tool_name: str) -> str:
        """Route tool to its authoritative distributed MCP microservice."""
        name = tool_name.lower()
        if (
            name.startswith("k8s_")
            or name.startswith("diagnose_")
            or name.startswith("check_dns")
            or name.startswith("check_network")
            or name.startswith("check_pvc")
            or name.startswith("check_resource")
            or name.startswith("check_pod_restart")
            or name.startswith("analyze_")
            or name.startswith("list_")
            or name.startswith("get_cluster")
            or name.startswith("get_node")
            or name.startswith("get_namespace")
            or name.startswith("get_deployment")
            or name.startswith("get_pod")
            or name.startswith("get_hpa")
            or name.startswith("get_resource_quota")
        ):
            return self.k8s_url

        if (
            name.startswith("query_prometheus")
            or name.startswith("search_opensearch")
            or name.startswith("query_http")
            or name.startswith("query_latency")
            or name.startswith("correlate_")
            or name.startswith("get_recent_system")
            or name.startswith("get_service_logs")
            or name.startswith("restart_gke")
            or name.startswith("get_cluster_pod_counts")
            or name.startswith("get_pod_restart_reason")
            or name.startswith("observability_")
        ):
            return self.observability_url

        if (
            name.startswith("locker_")
            or name.startswith("package_")
            or name.startswith("resident_")
            or name.startswith("compartment_")
            or name.startswith("smart_locker_")
            or name.startswith("hardware_")
        ):
            return self.locker_url

        # Default to k8s server for infrastructure, or observability
        return self.k8s_url

    async def call_tool_remote(
        self,
        server_url: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """Send JSON-RPC 2.0 tools/call request to remote MCP server."""
        req_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        # Try standard FastMCP endpoint /mcp first, fallback to root /
        endpoints = [f"{server_url}/mcp", f"{server_url}/"]
        last_error = None

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for ep in endpoints:
                try:
                    resp = await client.post(
                        ep,
                        json=payload,
                        headers={"Content-Type": "application/json", "Accept": "application/json"},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if "error" in data and data["error"]:
                            err_msg = data["error"].get("message", str(data["error"]))
                            raise MCPToolExecutionError(f"Remote MCP error: {err_msg}")
                        result = data.get("result", {})
                        if isinstance(result, dict) and "content" in result:
                            # Parse FastMCP text content envelope
                            content_items = result.get("content", [])
                            if content_items and isinstance(content_items, list):
                                first = content_items[0]
                                if isinstance(first, dict) and first.get("type") == "text":
                                    import json
                                    try:
                                        return json.loads(first.get("text", "{}"))
                                    except Exception:
                                        return first.get("text")
                            return result
                        return result
                    elif resp.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        raise MCPToolExecutionError(
                            f"Remote MCP server {server_url} returned HTTP {resp.status_code}: {resp.text[:200]}"
                        )
                except httpx.RequestError as exc:
                    last_error = exc
                    continue

        if last_error:
            raise ConnectionError(f"Failed to connect to remote MCP server at {server_url}: {last_error}")
        raise MCPToolExecutionError(f"No suitable MCP endpoint responded at {server_url}")


class MCPClient:
    """Dispatches tool execution requests to distributed MCP servers with fallback to local registry."""

    def __init__(
        self,
        remote_enabled: Optional[bool] = None,
        remote_fallback: Optional[bool] = None,
    ):
        settings = get_settings()
        self.remote_enabled = (
            remote_enabled
            if remote_enabled is not None
            else getattr(settings, "MCP_REMOTE_ENABLED", False)
        )
        self.remote_fallback = (
            remote_fallback
            if remote_fallback is not None
            else getattr(settings, "MCP_REMOTE_FALLBACK", True)
        )
        self.remote_client = RemoteMCPClient()
        self.registry = MCPToolRegistry

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        approval_token: Optional[str] = None,
    ) -> MCPToolExecutionResult:
        """Execute an MCP tool via remote microservice or local registry with standardized response envelope."""
        start_time = time.perf_counter()
        logger.info(f"MCPClient executing tool: {tool_name}")

        kwargs = dict(arguments)
        if approval_token:
            kwargs["approval_token"] = approval_token

        # 1. Distributed Remote Dispatch (if enabled)
        if self.remote_enabled:
            server_url = self.remote_client.route_tool(tool_name)
            try:
                result = await self.remote_client.call_tool_remote(server_url, tool_name, kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return MCPToolExecutionResult(
                    tool_name=tool_name,
                    success=True,
                    output=result,
                    execution_time_ms=round(duration_ms, 2),
                )
            except RemediationApprovalRequiredError:
                raise
            except Exception as e:
                logger.warning(
                    f"Remote execution failed for tool '{tool_name}' on {server_url}: {e}."
                    + (" Falling back to local registry..." if self.remote_fallback else "")
                )
                if not self.remote_fallback:
                    duration_ms = (time.perf_counter() - start_time) * 1000.0
                    return MCPToolExecutionResult(
                        tool_name=tool_name,
                        success=False,
                        output=None,
                        error=str(e),
                        execution_time_ms=round(duration_ms, 2),
                    )

        # 2. Local Registry Execution (Fallback or Local Mode)
        try:
            tool_fn = self.registry.get_tool(tool_name)
            result = await tool_fn(**kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000.0

            return MCPToolExecutionResult(
                tool_name=tool_name,
                success=True,
                output=result,
                execution_time_ms=round(duration_ms, 2),
            )
        except RemediationApprovalRequiredError:
            raise
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Failed to execute MCP tool '{tool_name}': {e}")
            return MCPToolExecutionResult(
                tool_name=tool_name,
                success=False,
                output=None,
                error=str(e),
                execution_time_ms=round(duration_ms, 2),
            )
