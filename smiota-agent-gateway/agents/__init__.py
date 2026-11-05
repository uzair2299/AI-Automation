from agents.implementations.aiops.agent import AIOpsAgent
from agents.implementations.customer.agent import CustomerAgent
from agents.implementations.developer.agent import DeveloperAgent
from agents.implementations.knowledge.agent import KnowledgeAssistantAgent
from agents.implementations.qa.agent import QAAgent
from agents.implementations.security.agent import SecurityAgent
from agents.registry import AgentRegistry


def register_default_agents() -> None:
    """Bootstrap default specialized agents into the AgentRegistry."""
    AgentRegistry.register(AIOpsAgent())
    AgentRegistry.register(SecurityAgent())
    AgentRegistry.register(DeveloperAgent())
    AgentRegistry.register(QAAgent())
    AgentRegistry.register(CustomerAgent())
    AgentRegistry.register(KnowledgeAssistantAgent())
