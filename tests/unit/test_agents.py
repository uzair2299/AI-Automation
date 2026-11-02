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
    """Verify 'Why is smiotaserver restarting?' queries live Prometheus without approval gate."""
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
    assert "smiotaserver" in result.content
    assert "Live Prometheus" in result.content
    assert "Telemetry Provenance" in result.content


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


@pytest.mark.asyncio
async def test_aiops_investigate_api_5xx_increase():
    """Verify Scenario 2: 'Why did production API 5xx increase?' queries live Prometheus HTTP metrics."""
    orchestrator = AgentOrchestrator()
    context = AgentContext(
        session_id="teams-session-5xx",
        user_id="sre-user",
        tenant_id="default",
        channel="teams",
    )

    result = await orchestrator.route_and_execute("Why did production API 5xx increase?", context)
    assert result.agent_name == "AIOps"
    assert result.requires_approval is False
    assert "5xx" in result.content
    assert "Live Prometheus" in result.content


@pytest.mark.asyncio
async def test_aiops_investigate_latency_increase():
    """Verify Scenario 3: 'Why did API latency increase?' queries live Prometheus latency percentiles."""
    orchestrator = AgentOrchestrator()
    context = AgentContext(
        session_id="teams-session-latency",
        user_id="sre-user",
        tenant_id="default",
        channel="teams",
    )

    result = await orchestrator.route_and_execute("Why did API latency increase?", context)
    assert result.agent_name == "AIOps"
    assert result.requires_approval is False
    assert "Latency" in result.content
    assert "Live Prometheus" in result.content


@pytest.mark.asyncio
async def test_aiops_investigate_latest_deployment_cause():
    """Verify Scenario 4: 'Did the latest deployment cause the problem?' checks live deployment telemetry."""
    orchestrator = AgentOrchestrator()
    context = AgentContext(
        session_id="teams-session-deployment",
        user_id="sre-user",
        tenant_id="default",
        channel="teams",
    )

    result = await orchestrator.route_and_execute("Did the latest deployment cause the problem?", context)
    assert result.agent_name == "AIOps"
    assert result.requires_approval is False
    assert "Deployment" in result.content
    assert "Live Prometheus" in result.content


@pytest.mark.asyncio
async def test_aiops_investigate_what_changed_before_incident():
    """Verify Scenario 5: 'What changed before the incident?' queries live GCP Cloud Audit."""
    orchestrator = AgentOrchestrator()
    context = AgentContext(
        session_id="teams-session-changes",
        user_id="sre-user",
        tenant_id="default",
        channel="teams",
    )

    result = await orchestrator.route_and_execute("What changed before the incident?", context)
    assert result.agent_name == "AIOps"
    assert result.requires_approval is False
    assert "GCP Cloud Audit" in result.content
    assert "project-smiota-psi-1" in result.content


@pytest.mark.asyncio
async def test_aiops_service_logs_inspection():
    """Verify log inspection reports real cluster location without mock data."""
    orchestrator = AgentOrchestrator()
    context = AgentContext(
        session_id="teams-session-logs",
        user_id="sre-user",
        tenant_id="default",
        channel="teams",
    )

    # General log question
    res_general = await orchestrator.route_and_execute("can i check the logs of a specfic servcie?", context)
    assert res_general.agent_name == "AIOps"
    assert "OpenSearch" in res_general.content

    # Specific service logs
    res_svc = await orchestrator.route_and_execute("show logs for payments-service", context)
    assert res_svc.agent_name == "AIOps"
    assert "payments-service" in res_svc.content


