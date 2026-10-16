"""Smiota Agent Core and domain agent registrations."""
from smiota.agents.registry import AgentRegistry
from smiota.agents.implementations.aiops.agent import AIOpsAgent
from smiota.agents.implementations.security.agent import SecurityAgent
from smiota.agents.implementations.developer.agent import DeveloperAgent
from smiota.agents.implementations.qa.agent import QAAgent
from smiota.agents.implementations.customer.agent import CustomerAgent


def register_default_agents() -> None:
    """Bootstrap default specialized agents into the AgentRegistry."""
    AgentRegistry.register(AIOpsAgent())
    AgentRegistry.register(SecurityAgent())
    AgentRegistry.register(DeveloperAgent())
    AgentRegistry.register(QAAgent())
    AgentRegistry.register(CustomerAgent())
