"""Automated remediation background task executing approved infrastructure changes."""
from smiota.core.logging import logger
from smiota.mcp.client import MCPClient


async def execute_approved_remediation(
    action_name: str,
    resource_id: str,
    approval_token: str,
    params: dict | None = None,
) -> dict:
    """Execute remediation action once human approval token has been validated."""
    logger.info(
        f"Executing approved remediation '{action_name}' on '{resource_id}' with token '{approval_token}'"
    )

    client = MCPClient()
    tool_args = params or {}
    tool_args["resource_id"] = resource_id

    result = await client.execute_tool(
        tool_name=action_name,
        arguments=tool_args,
        approval_token=approval_token,
    )

    return {
        "status": "completed" if result.success else "failed",
        "output": result.output,
        "error": result.error,
        "execution_time_ms": result.execution_time_ms,
    }
