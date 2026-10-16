"""Schemas for Model Context Protocol (MCP) tool registrations and execution."""
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class ToolAccessLevel(str, Enum):
    READ_ONLY = "read_only"       # Can run autonomously (queries, log fetching)
    REMEDIATION = "remediation"   # Destructive/change action (requires human approval)


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    access_level: ToolAccessLevel = ToolAccessLevel.READ_ONLY
    input_schema: dict[str, Any]


class MCPToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time_ms: float
