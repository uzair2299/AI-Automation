"""Unit tests for Model Context Protocol (MCP) Security and HITL Enforcement."""
import pytest
from smiota.mcp.security import mcp_tool, RemediationApprovalRequiredError
from smiota.schemas.mcp import ToolAccessLevel


@mcp_tool(name="test_read_tool", access_level=ToolAccessLevel.READ_ONLY)
async def sample_read_tool(param: str) -> dict:
    return {"status": "read_ok", "param": param}


@mcp_tool(name="test_remediation_tool", access_level=ToolAccessLevel.REMEDIATION)
async def sample_remediation_tool(target: str, approval_token: str | None = None) -> dict:
    return {"status": "mutated", "target": target}


@pytest.mark.asyncio
async def test_read_only_tool_executes_freely():
    res = await sample_read_tool(param="test")
    assert res["status"] == "read_ok"


@pytest.mark.asyncio
async def test_remediation_tool_blocks_without_token():
    with pytest.raises(RemediationApprovalRequiredError):
        await sample_remediation_tool(target="pod-xyz")


@pytest.mark.asyncio
async def test_remediation_tool_executes_with_token():
    res = await sample_remediation_tool(target="pod-xyz", approval_token="valid-token-123")
    assert res["status"] == "mutated"
