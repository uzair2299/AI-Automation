"""Asynchronous MCP Client for invoking local and distributed MCP servers."""
import time
from typing import Any, Optional
from smiota.mcp.registry import MCPToolRegistry
from smiota.schemas.mcp import MCPToolExecutionResult
from smiota.core.logging import logger
from smiota.core.exceptions import MCPToolExecutionError, RemediationApprovalRequiredError


class MCPClient:
    """Dispatches tool execution requests to registered MCP tools with safety auditing."""

    def __init__(self):
        self.registry = MCPToolRegistry

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        approval_token: Optional[str] = None,
    ) -> MCPToolExecutionResult:
        """Execute an MCP tool and return a standardized execution envelope."""
        start_time = time.perf_counter()
        logger.info(f"MCPClient executing tool: {tool_name}")

        try:
            tool_fn = self.registry.get_tool(tool_name)
            kwargs = dict(arguments)
            if approval_token:
                kwargs["approval_token"] = approval_token

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
