"""Dynamic plugin registry for Smiota AI Agents."""
from typing import Any, Optional
from smiota.agents.base import BaseAgent
from smiota.core.logging import logger


class AgentRegistry:
    """Registry supporting dynamic discovery and injection of domain agents."""

    _agents: dict[str, BaseAgent] = {}

    @classmethod
    def register(cls, agent_instance: BaseAgent) -> None:
        """Register an instantiated agent into the platform core."""
        logger.info(f"Registering AI Agent: [{agent_instance.name}] (Domain: {agent_instance.domain})")
        cls._agents[agent_instance.name.lower()] = agent_instance
        cls._agents[agent_instance.domain.lower()] = agent_instance

    @classmethod
    def get(cls, name: str) -> BaseAgent:
        """Retrieve an agent by name or domain."""
        name_key = name.lower()
        if name_key not in cls._agents:
            raise KeyError(f"Agent '{name}' is not registered. Available agents: {list(cls._agents.keys())}")
        return cls._agents[name_key]

    @classmethod
    def list_agents(cls) -> list[dict[str, Any]]:
        """List all unique registered agents and their capabilities."""
        unique_agents: dict[str, BaseAgent] = {}
        for agent in cls._agents.values():
            unique_agents[agent.name.lower()] = agent

        return [
            {
                "name": agent.name,
                "domain": agent.domain,
                "description": agent.description,
                "capabilities": [c.model_dump() for c in agent.capabilities],
                "bound_tools": agent.bound_tools,
            }
            for agent in unique_agents.values()
        ]
