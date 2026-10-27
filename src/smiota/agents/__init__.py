from smiota.agents.implementations.aiops.agent import AIOpsAgent
from smiota.agents.implementations.customer.agent import CustomerAgent
from smiota.agents.implementations.developer.agent import DeveloperAgent
from smiota.agents.implementations.knowledge.agent import KnowledgeAssistantAgent
from smiota.agents.implementations.qa.agent import QAAgent
from smiota.agents.implementations.security.agent import SecurityAgent
from smiota.agents.registry import AgentRegistry


def register_default_agents() -> None:
    """Bootstrap default specialized agents into the AgentRegistry."""
    AgentRegistry.register(AIOpsAgent())
    AgentRegistry.register(SecurityAgent())
    AgentRegistry.register(DeveloperAgent())
    AgentRegistry.register(QAAgent())
    AgentRegistry.register(CustomerAgent())
    AgentRegistry.register(KnowledgeAssistantAgent())
