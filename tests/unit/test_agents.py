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


@pytest.mark.asyncio
async def test_aiops_investigate_api_5xx_increase():
    """Verify Scenario 2: 'Why did production API 5xx increase?' performs RCA investigation."""
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
    assert "Connection Pool" in result.content
    assert "HikariPool" in result.content
    assert "5xx" in result.content
    assert "query_http_error_rates" in result.content


@pytest.mark.asyncio
async def test_aiops_investigate_latency_increase():
    """Verify Scenario 3: 'Why did API latency increase?' performs latency & cache investigation."""
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
    assert "Redis" in result.content
    assert "p95" in result.content
    assert "query_latency_metrics" in result.content


@pytest.mark.asyncio
async def test_aiops_investigate_latest_deployment_cause():
    """Verify Scenario 4: 'Did the latest deployment cause the problem?' correlates deployment."""
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
    assert "v2.4.1" in result.content
    assert "PR #342" in result.content
    assert "correlate_deployment_with_incident" in result.content


@pytest.mark.asyncio
async def test_aiops_investigate_what_changed_before_incident():
    """Verify Scenario 5: 'What changed before the incident?' audits chronological system changes."""
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
    assert "PARCEL_SYNC_BATCH_SIZE" in result.content
    assert "ConfigMap" in result.content
    assert "get_recent_system_changes" in result.content


@pytest.mark.asyncio
async def test_aiops_service_logs_inspection():
    """Verify log inspection for a specific service returns pod logs."""
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
    assert "Yes, absolutely!" in res_general.content

    # Specific service logs
    res_svc = await orchestrator.route_and_execute("show logs for payments-service", context)
    assert res_svc.agent_name == "AIOps"
    assert "payments-service" in res_svc.content
    assert "StripeWebhookHandler" in res_svc.content


