"""Model Context Protocol (MCP) tool integration layer."""
from mcp.security import mcp_tool, RemediationApprovalRequired
from mcp.registry import MCPToolRegistry
from mcp.client import MCPClient

__all__ = [
    "mcp_tool",
    "RemediationApprovalRequired",
    "MCPToolRegistry",
    "MCPClient",
]
