"""Model Context Protocol (MCP) tool integration layer."""
from smiota.mcp.security import mcp_tool, RemediationApprovalRequired
from smiota.mcp.registry import MCPToolRegistry
from smiota.mcp.client import MCPClient

__all__ = [
    "mcp_tool",
    "RemediationApprovalRequired",
    "MCPToolRegistry",
    "MCPClient",
]
