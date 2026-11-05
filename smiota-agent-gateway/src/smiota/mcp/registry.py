"""Centralized Model Context Protocol (MCP) Tool Registry."""
from typing import Callable, Any, Optional
from smiota.schemas.mcp import MCPToolDefinition, ToolAccessLevel
from smiota.core.logging import logger


class MCPToolRegistry:
    """Registry maintaining active MCP tool manifests, schemas, and invokers."""

    _tools: dict[str, Callable] = {}
    _definitions: dict[str, MCPToolDefinition] = {}

    @classmethod
    def register_tool(
        cls,
        name: str,
        description: str,
        func: Callable,
        access_level: ToolAccessLevel = ToolAccessLevel.READ_ONLY,
        input_schema: Optional[dict[str, Any]] = None,
    ) -> None:
        """Register a tool callable and its formal MCP definition."""
        cls._tools[name] = func
        cls._definitions[name] = MCPToolDefinition(
            name=name,
            description=description,
            access_level=access_level,
            input_schema=input_schema or {"type": "object", "properties": {}},
        )
        logger.debug(f"Registered MCP tool: {name} [{access_level}]")

    @classmethod
    def get_tool(cls, name: str) -> Callable:
        """Retrieve registered tool callable."""
        if name not in cls._tools:
            raise KeyError(f"Tool '{name}' is not registered in MCP registry.")
        return cls._tools[name]

    @classmethod
    def get_definition(cls, name: str) -> MCPToolDefinition:
        """Retrieve tool metadata definition."""
        if name not in cls._definitions:
            raise KeyError(f"Tool '{name}' definition not found.")
        return cls._definitions[name]

    @classmethod
    def list_tools(cls) -> list[MCPToolDefinition]:
        """List all registered MCP tools."""
        return list(cls._definitions.values())

    @classmethod
    def export_gemini_functions(cls) -> list[dict[str, Any]]:
        """Export registered tools formatted for Gemini / Vertex AI Function Calling."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema,
            }
            for tool in cls._definitions.values()
        ]
