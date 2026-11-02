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


@pytest.mark.asyncio
async def test_aiops_investigate_smiotaserver_restarting():
    """Verify 'Why is smiotaserver restarting?' performs RCA investigation without approval gate."""
    orchestrator = AgentOrchestrator()
    context = AgentContext(
        session_id="teams-session-1",
        user_id="sre-user",
        tenant_id="default",
        channel="teams",
    )

    result = await orchestrator.route_and_execute("Why is smiotaserver restarting?", context)
    assert result.agent_name == "AIOps"
    assert result.requires_approval is False
    assert "OOMKilled" in result.content
    assert "Exit Code 137" in result.content
    assert "smiotaserver" in result.content


@pytest.mark.asyncio
async def test_aiops_remediation_requires_approval():
    """Verify mutating restart command still requires Human-in-the-Loop approval."""
    orchestrator = AgentOrchestrator()
    context = AgentContext(
        session_id="teams-session-2",
        user_id="sre-user",
        tenant_id="default",
        channel="teams",
    )

    result = await orchestrator.route_and_execute("Restart the deployment payments-service immediately", context)
    assert result.agent_name == "AIOps"
    assert result.requires_approval is True
    assert result.approval_details["tool_name"] == "restart_gke_deployment"
    assert result.approval_details["deployment_name"] == "payments-service"

