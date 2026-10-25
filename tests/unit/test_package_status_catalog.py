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
