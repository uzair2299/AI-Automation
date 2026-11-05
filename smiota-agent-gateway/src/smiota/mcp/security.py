"""Model Context Protocol (MCP) Security Layer.

Enforces: 'Read-only investigation first, with human approval for remediation'.
"""
from functools import wraps
from typing import Callable, Any, Optional
from smiota.schemas.mcp import ToolAccessLevel
from smiota.core.config import get_settings
from smiota.core.logging import logger
from smiota.core.exceptions import RemediationApprovalRequiredError
from smiota.mcp.registry import MCPToolRegistry

# Alias for backward compatibility
RemediationApprovalRequired = RemediationApprovalRequiredError


def mcp_tool(
    name: str,
    access_level: ToolAccessLevel = ToolAccessLevel.READ_ONLY,
    description: Optional[str] = None,
    input_schema: Optional[dict[str, Any]] = None,
):
    """Decorator to secure MCP tools and automatically register them in MCPToolRegistry."""
    def decorator(func: Callable):
        tool_desc = description or func.__doc__ or f"MCP tool {name}"
        setattr(func, "__mcp_tool_name__", name)
        setattr(func, "__mcp_access_level__", access_level)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            settings = get_settings()
            if access_level == ToolAccessLevel.REMEDIATION and settings.REQUIRE_HUMAN_APPROVAL_FOR_REMEDIATION:
                approval_token = kwargs.get("approval_token")
                if not approval_token:
                    logger.warning(f"Blocked unapproved remediation action: {name}")
                    raise RemediationApprovalRequiredError(tool_name=name, params=kwargs)

            logger.info(f"Executing MCP Tool [{name}] with access level [{access_level}]")
            return await func(*args, **kwargs)

        # Register in central registry
        MCPToolRegistry.register_tool(
            name=name,
            description=tool_desc,
            func=wrapper,
            access_level=access_level,
            input_schema=input_schema,
        )

        return wrapper
    return decorator
