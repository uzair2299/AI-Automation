"""Unit tests for Smiota Package Status Catalog, Lifecycle Enums, and Agent Explanations."""
import pytest
from smiota.schemas.package_status import (
    PackageStatus,
    PackageLifecycleGroup,
    PACKAGE_STATUS_CATALOG,
    get_status_definition,
    normalize_status_key,
    get_status_resident_explanation,
)
from smiota.schemas.mcp_tools import SearchPackagesInput
from smiota.agents.implementations.customer.agent import CustomerAgent
from smiota.agents.base import AgentContext
from smiota.mcp.context import CallerContext, set_caller_context


def test_package_status_catalog_completeness():
    """Verify all 16 canonical statuses + Processed alias exist with metadata."""
    expected_statuses = [
        "pickup_request_submitted",
        "received",
        "delivered_to_station",
        "released",
        "sent back",
        "attempted to deliver",
        "courier to mailroom",
        "in transit",
        "return to hub",
        "Ready to Ship",
        "In Transit to Warehouse",
        "In Transit to Pod",
        "Hold",
        "In Warehouse",
        "Research",
        "Transferred",
        "Processed",
    ]
    for status in expected_statuses:
        key = normalize_status_key(status)
        defn = PACKAGE_STATUS_CATALOG.get(key)
        assert defn is not None, f"Status '{status}' (key='{key}') missing from catalog"
        assert defn.display_name
        assert defn.customer_summary
        assert defn.resident_guidance
        assert isinstance(defn.status_group, PackageLifecycleGroup)


def test_status_normalization():
    """Verify normalization handles case, spaces, and hyphens."""
    assert normalize_status_key("delivered_to_station") == "delivered_to_station"
    assert normalize_status_key("Delivered To Station") == "delivered_to_station"
    assert normalize_status_key("  In Transit to Pod  ") == "in_transit_to_pod"
    assert normalize_status_key("Ready to Ship") == "ready_to_ship"
    assert normalize_status_key("attempted to deliver") == "attempted_to_deliver"
    assert normalize_status_key("Hold") == "hold"
    assert normalize_status_key("Research") == "research"
    assert normalize_status_key("") == ""
    assert normalize_status_key(None) == ""


def test_get_status_definition_and_resident_explanation():
    """Verify metadata lookup and resident-facing guidance strings."""
    defn = get_status_definition("Delivered To Station")
    assert defn is not None
    assert defn.is_collectible_now is True
    assert defn.status_group == PackageLifecycleGroup.PENDING

    hold_defn = get_status_definition("Hold")
    assert hold_defn is not None
    assert hold_defn.is_collectible_now is False
    assert hold_defn.status_group == PackageLifecycleGroup.HOLD

    expl = get_status_resident_explanation("Research")
    assert "Research" in expl
    assert "Mailroom staff are researching" in expl


def test_search_packages_input_schema_with_status():
    """Verify SearchPackagesInput accepts status argument."""
    inp = SearchPackagesInput(status="delivered_to_station", carrier="UPS")
    assert inp.status == "delivered_to_station"
    assert inp.carrier == "UPS"
    assert inp.status_group == "PENDING"


@pytest.mark.asyncio
async def test_customer_agent_status_explanation_inquiry():
    """Verify CustomerAgent answers 'what does status X mean' queries without LLM."""
    agent = CustomerAgent()
    context = AgentContext(
        session_id="test-status-sess",
        user_id="user-123",
        tenant_id="tenant-abc",
        channel="webchat",
        user={"is_authenticated": True, "name": "Resident Alex"},
    )
    res = await agent.process("What does status Research mean?", context=context)
    assert res.agent_name == "Customer"
    assert "Research" in res.content
    assert "Mailroom staff are researching" in res.content
    assert res.requires_approval is False


def test_format_package_record_with_status_decoration():
    """Verify _format_package_record decorates statuses with friendly summaries."""
    agent = CustomerAgent()
    pkg = {
        "id": 12345,
        "trackingNumber": "TRACK-999",
        "status": "In Transit to Pod",
        "storageType": "LOCKER",
    }
    lines = agent._format_package_record(pkg)
    status_line = next(line for line in lines if "Delivery Status" in line)
    assert "In Transit to Pod" in status_line
    assert "En route to designated smart locker pod" in status_line


def test_format_package_record_with_human_readable_timestamps():
    """Verify ISO timestamps and epochs are converted to human-readable strings."""
    agent = CustomerAgent()
    pkg = {
        "id": 330790,
        "trackingNumber": "85366e70244e",
        "status": "Processed",
        "storageType": "SHELF",
        "carrier": "Associate",
        "receivedTime": "2026-07-06T16:57:43Z",
        "expirationTime": "2026-07-07T08:00:00Z",
    }
    lines = agent._format_package_record(pkg)
    rec_line = next(line for line in lines if "Received At" in line)
    exp_line = next(line for line in lines if "Expires At" in line)
    assert "July 6, 2026 at 4:57 PM" in rec_line
    assert "July 7, 2026 at 8:00 AM" in exp_line


@pytest.mark.asyncio
async def test_customer_agent_uncollected_parcels_inquiry():
    """Verify logged-in user asking 'Show me all my uncollected parcels' returns pending packages directly."""
    from unittest.mock import AsyncMock, patch
    from smiota.mcp.client import MCPClient
    from smiota.schemas.mcp import MCPToolExecutionResult

    agent = CustomerAgent()
    context = AgentContext(
        session_id="test-uncollected-sess",
        user_id="10063863",
        tenant_id="413",
        channel="webchat",
        user={
            "is_authenticated": True,
            "user_id": "10063863",
            "customer_id": 2,
            "tenant_id": 413,
            "location_id": 37,
            "parent_token": "test-token",
        },
    )
    mock_packages = [
        {
            "id": 330790,
            "trackingNumber": "85366e70244e",
            "status": "Processed",
            "storageType": "SHELF",
            "receivedTime": "2026-07-06T16:57:43Z",
        }
    ]
    mock_res = MCPToolExecutionResult(
        tool_name="search_packages",
        success=True,
        output={"success": True, "data": {"packages": mock_packages, "total_count": 1}},
        execution_time_ms=10.0,
    )
    with patch.object(MCPClient, "execute_tool", new_callable=AsyncMock, return_value=mock_res):
        res = await agent.process("Show me all my uncollected parcels.", context=context)
        assert res.agent_name == "Customer"
        assert "pending package" in res.content.lower() or "awaiting pickup" in res.content.lower()
        assert "85366e70244e" in res.content
        assert "July 6, 2026 at 4:57 PM" in res.content
        assert res.requires_approval is False


@pytest.mark.asyncio
async def test_customer_agent_pickup_history_inquiry():
    """Verify logged-in user asking 'My past 30 days pickup history' queries status_group=RELEASED."""
    from unittest.mock import AsyncMock, patch
    from smiota.mcp.client import MCPClient
    from smiota.schemas.mcp import MCPToolExecutionResult

    agent = CustomerAgent()
    context = AgentContext(
        session_id="test-history-sess",
        user_id="10063863",
        tenant_id="413",
        channel="webchat",
        user={
            "is_authenticated": True,
            "user_id": "10063863",
            "customer_id": 2,
            "tenant_id": 413,
            "location_id": 37,
            "parent_token": "test-token",
        },
    )
    mock_released = [
        {
            "id": 330100,
            "trackingNumber": "REL-12345",
            "status": "released",
            "storageType": "LOCKER",
            "timeReleased": "2026-07-05T14:30:00Z",
        }
    ]
    mock_res = MCPToolExecutionResult(
        tool_name="search_packages",
        success=True,
        output={"success": True, "data": {"packages": mock_released, "total_count": 1}},
        execution_time_ms=10.0,
    )
    with patch.object(MCPClient, "execute_tool", new_callable=AsyncMock, return_value=mock_res):
        res = await agent.process("My past 30 days pickup history.", context=context)
        assert res.agent_name == "Customer"
        assert "pickup history" in res.content.lower() or "past 30 days" in res.content.lower()
        assert "REL-12345" in res.content
        assert "July 5, 2026 at 2:30 PM" in res.content
        assert res.requires_approval is False


@pytest.mark.asyncio
async def test_customer_agent_pending_packages_lookback_inquiry():
    """Verify user asking 'Show me a list of all pending packages over the last 30 days?' queries status_group=PENDING."""
    from unittest.mock import AsyncMock, patch
    from smiota.mcp.client import MCPClient
    from smiota.schemas.mcp import MCPToolExecutionResult

    agent = CustomerAgent()
    context = AgentContext(
        session_id="test-pending-30-sess",
        user_id="10063863",
        tenant_id="413",
        channel="webchat",
        user={
            "is_authenticated": True,
            "user_id": "10063863",
            "customer_id": 2,
            "tenant_id": 413,
            "location_id": 37,
            "parent_token": "test-token",
        },
    )
    mock_packages = [
        {
            "id": 330790,
            "trackingNumber": "85366e70244e",
            "status": "Processed",
            "storageType": "SHELF",
            "receivedTime": "2026-07-06T16:57:43Z",
        }
    ]
    mock_res = MCPToolExecutionResult(
        tool_name="search_packages",
        success=True,
        output={"success": True, "data": {"packages": mock_packages, "total_count": 1}},
        execution_time_ms=10.0,
    )
    with patch.object(MCPClient, "execute_tool", new_callable=AsyncMock, return_value=mock_res):
        res = await agent.process("Show me a list of all pending packages over the last 30 days?", context=context)
        assert res.agent_name == "Customer"
        assert "pending package" in res.content.lower()
        assert "85366e70244e" in res.content
        assert "July 6, 2026 at 4:57 PM" in res.content
        assert res.requires_approval is False

