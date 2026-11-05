"""Model Context Protocol (MCP) tool integration layer."""
import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)

from mcp.security import mcp_tool, RemediationApprovalRequired
from mcp.registry import MCPToolRegistry
from mcp.client import MCPClient
import mcp.manifest  # noqa: F401

__all__ = [
    "mcp_tool",
    "RemediationApprovalRequired",
    "MCPToolRegistry",
    "MCPClient",
]
