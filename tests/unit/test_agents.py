"""Unit tests for Agent Orchestrator and Agent Registry."""
import pytest
from smiota.agents import register_default_agents
from smiota.agents.registry import AgentRegistry
from smiota.agents.orchestrator import AgentOrchestrator
from smiota.agents.base import AgentContext


@pytest.fixture(autouse=True)
def setup_agents():
    register_default_agents()


def test_agent_registration():
    agents = AgentRegistry.list_agents()
    names = [a["name"].lower() for a in agents]
    assert "aiops" in names
    assert "security" in names
    assert "developer" in names
    assert "qa" in names
    assert "customer" in names


@pytest.mark.asyncio
async def test_orchestrator_routing():
    orchestrator = AgentOrchestrator()
    context = AgentContext(
        session_id="test-session",
        user_id="user-1",
        tenant_id="default",
        channel="webchat"
    )

    result = await orchestrator.route_and_execute("Investigate high CPU in GKE pods", context)
    assert result.agent_name == "AIOps"

    sec_result = await orchestrator.route_and_execute("Check CVE vulnerability report in Wazuh", context)
    assert sec_result.agent_name == "Security"
