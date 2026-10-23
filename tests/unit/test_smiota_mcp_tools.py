"""Unit tests for Smiota Customer MCP Tools.

Validates:
- Tool argument validation & constraints (Pydantic schemas)
- Standardized response envelopes (SmiotaToolResult)
- Successful data retrieval with synthetic fixtures
- Error handling & status code mapping (404, 429, timeouts, 503)
- Tool registry metadata and 10-point description completeness
- Sensitive data isolation and empty-result handling
"""
import pytest
from unittest.mock import AsyncMock, patch

from smiota.mcp.context import CallerContext, set_caller_context, reset_caller_context
from smiota.mcp.errors import (
    McpAccessDeniedError,
    McpAuthenticationRequiredError,
    McpInvalidInputError,
    McpUpstreamNotFoundError,
    McpUpstreamRateLimitedError,
    McpUpstreamServiceUnavailableError,
    McpUpstreamTimeoutError,
)
from smiota.mcp.registry import MCPToolRegistry
from smiota.mcp.servers.customer.tools import (
    get_my_locker_details,
    get_my_pickup_pin,
    get_package_details,
    get_package_timeline,
    get_user_preferences_and_services,
    query_locker_door_status,
    create_support_ticket,
    search_packages,
)
from smiota.schemas.mcp_tools import (
    GetLockerDetailsInput,
    GetPackageDetailsInput,
    GetPackageTimelineInput,
    GetPickupPinInput,
    SearchPackagesInput,
    ToolResultCode,
)
from smiota.services.smiota_mcp_service import SmiotaMcpService


@pytest.fixture
def auth_caller() -> CallerContext:
    """Standard authenticated resident caller context fixture."""
    return CallerContext(
        user_id="10790",
        customer_id=101,
        tenant_id=89,
        location_id=14,
        building_id=14,
        unit_no="4B",
        roles=["resident"],
        parent_token="test-parent-token-xyz-123456",
        session_id="sess-unit-test-1",
        is_authenticated=True,
        correlation_id="corr-unit-test-123",
    )


@pytest.fixture(autouse=True)
def enable_dummy_mode(monkeypatch):
    """Ensure deterministic synthetic fixtures for offline unit tests."""
    monkeypatch.setenv("SMIOTA_AUTH_DUMMY_MODE", "true")
    from smiota.clients.smiota_api_client import get_smiota_api_client
    client = get_smiota_api_client()
    original_dummy = client._dummy_mode
    client._dummy_mode = True
    yield
    client._dummy_mode = original_dummy


# ==============================================================================
# 1. Pydantic Input Schema Validation Tests
# ==============================================================================

def test_search_packages_input_validation():
    """Verify input validation, bounds, and carrier sanitization."""
    # Valid default input
    inp = SearchPackagesInput()
    assert inp.status_group == "PENDING"
    assert inp.storage_type == "ALL"

    # Valid custom filters
    inp2 = SearchPackagesInput(
        status_group="RELEASED",
        carrier="FedEx Express <script>",
        days=30,
        is_perishable=True,
    )
    assert inp2.carrier == "FedEx Express script"  # Sanitized
    assert inp2.days == 30
    assert inp2.is_perishable is True

    # Invalid days bound (> 365)
    with pytest.raises(ValueError):
        SearchPackagesInput(days=400)

    # Invalid status group
    with pytest.raises(ValueError):
        SearchPackagesInput(status_group="UNKNOWN_STATUS")  # type: ignore


def test_get_package_details_input_validation():
    """Verify identifier validation and rejection of dangerous characters."""
    valid = GetPackageDetailsInput(identifier="1Z9999999999999999")
    assert valid.identifier == "1Z9999999999999999"

    # Empty identifier rejected
    with pytest.raises(ValueError):
        GetPackageDetailsInput(identifier="   ")

    # Injected characters rejected
    with pytest.raises(ValueError):
        GetPackageDetailsInput(identifier="PKG-123; DROP TABLE users;")


def test_get_package_timeline_input_validation():
    """Verify timeline identifier validation."""
    valid = GetPackageTimelineInput(identifier="8f9a2b10-6a5c-4e89-b1d3-92f7a01d5e34")
    assert "8f9a2b10" in valid.identifier

    with pytest.raises(ValueError):
        GetPackageTimelineInput(identifier="<script>alert(1)</script>")


# ==============================================================================
# 2. Tool Execution & Response Normalization Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_search_packages_success(auth_caller):
    """Verify search_packages executes and returns normalized SmiotaToolResult envelope."""
    token = set_caller_context(auth_caller)
    try:
        res = await search_packages(status_group="PENDING", carrier="UPS")
        assert res["success"] is True
        assert res["status"] == ToolResultCode.SUCCESS.value
        assert "packages" in res["data"]
        assert len(res["data"]["packages"]) >= 1
        pkg = res["data"]["packages"][0]
        assert pkg["tracking_number"] == "1Z9999999999999999"
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_search_packages_empty_result(auth_caller):
    """Verify empty result returns success=True with EMPTY_RESULT status code."""
    token = set_caller_context(auth_caller)
    try:
        mock_api = AsyncMock()
        mock_api.search_packages.return_value = {"packages": [], "total_count": 0}
        service = SmiotaMcpService(api_client=mock_api)

        res = await service.search_packages(status_group="RELEASED", carrier="DHL")
        assert res.success is True
        assert res.status == ToolResultCode.EMPTY_RESULT
        assert "No packages found" in res.message
        assert res.data["total_count"] == 0
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_package_details_success(auth_caller):
    """Verify get_package_details returns 360-degree attributes."""
    token = set_caller_context(auth_caller)
    try:
        res = await get_package_details(identifier="1Z9999999999999999")
        assert res["success"] is True
        assert res["status"] == ToolResultCode.SUCCESS.value
        data = res["data"]
        assert data["tracking_number"] == "1Z9999999999999999"
        assert data["carrier"] == "UPS"
        assert data["location"]["storage_type"] == "LOCKER"
        assert data["location"]["locker_door_name"] == "Door 14"
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_package_details_not_found(auth_caller):
    """Verify get_package_details maps 404 to NOT_FOUND with safe error message."""
    token = set_caller_context(auth_caller)
    try:
        mock_api = AsyncMock()
        mock_api.get_package_details.side_effect = McpUpstreamNotFoundError("Package not found")
        service = SmiotaMcpService(api_client=mock_api)

        res = await service.get_package_details(identifier="NONEXISTENT-999")
        assert res.success is False
        assert res.status == ToolResultCode.NOT_FOUND
        assert "couldn't find any package" in res.message
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_package_timeline_success(auth_caller):
    """Verify get_package_timeline returns chain-of-custody audit events."""
    token = set_caller_context(auth_caller)
    try:
        res = await get_package_timeline(identifier="1Z9999999999999999")
        assert res["success"] is True
        assert res["status"] == ToolResultCode.SUCCESS.value
        events = res["data"]["timeline"]
        assert len(events) >= 1
        first_event = events[0]
        assert "action" in first_event or "event_type" in first_event
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_user_preferences_success(auth_caller):
    """Verify get_user_preferences_and_services returns accessibility and proxy info."""
    token = set_caller_context(auth_caller)
    try:
        res = await get_user_preferences_and_services()
        assert res["success"] is True
        assert res["status"] == ToolResultCode.SUCCESS.value
        data = res["data"]
        assert "accessibility" in data
        assert data["accessibility"]["needs_wheelchair_access"] is True
        assert data["delegation"]["has_delegate_assigned"] is True
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_my_pickup_pin_with_identifier(auth_caller):
    """Verify get_my_pickup_pin retrieves PIN and compartment instructions."""
    token = set_caller_context(auth_caller)
    try:
        res = await get_my_pickup_pin(identifier="1Z9999999999999999")
        assert res["success"] is True
        assert res["status"] == ToolResultCode.SUCCESS.value
        data = res["data"]
        assert data["pickup_pin"] == "482910"
        assert data["locker_door"] == "Door 14"
        assert "touchscreen console" in data["instructions"]
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_my_locker_details_success(auth_caller):
    """Verify get_my_locker_details retrieves physical compartment information."""
    token = set_caller_context(auth_caller)
    try:
        res = await get_my_locker_details(identifier="1Z9999999999999999")
        assert res["success"] is True
        assert res["status"] == ToolResultCode.SUCCESS.value
        data = res["data"]
        assert data["locker_door_name"] == "Door 14"
        assert data["locker_bank"] == "Main Pod Bank 1"
        assert data["building_name"] == "East Campus Commons"
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_query_locker_door_status():
    """Verify IoT hardware telemetry tool functions without error."""
    res = await query_locker_door_status(locker_id="LK-01", compartment=14)
    assert res["status"] == "closed"
    assert res["lock_state"] == "engaged"
    assert res["battery_pct"] > 90.0


@pytest.mark.asyncio
async def test_create_support_ticket():
    """Verify customer support ticket creation tool."""
    res = await create_support_ticket(
        user_id="10790",
        subject="Door 14 stuck",
        description="PIN accepted but solenoid did not release latch",
        priority="high",
    )
    assert "ticket_id" in res
    assert res["status"] == "assigned_to_support_tier2"


# ==============================================================================
# 3. Error Mapping & Upstream Resilience Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_upstream_timeout_error_handling(auth_caller):
    """Verify upstream timeout is mapped cleanly without leaking internal trace."""
    token = set_caller_context(auth_caller)
    try:
        mock_api = AsyncMock()
        mock_api.search_packages.side_effect = McpUpstreamTimeoutError("ReadTimeout: upstream 10s")
        service = SmiotaMcpService(api_client=mock_api)

        res = await service.search_packages()
        assert res.success is False
        assert res.status == ToolResultCode.UPSTREAM_TIMEOUT
        assert "timed out" in res.message
        assert "ReadTimeout" not in res.message  # No internal exception leaks
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_upstream_rate_limited_error_handling(auth_caller):
    """Verify 429 rate limit error mapping."""
    token = set_caller_context(auth_caller)
    try:
        mock_api = AsyncMock()
        mock_api.get_package_details.side_effect = McpUpstreamRateLimitedError("Rate limit exceeded")
        service = SmiotaMcpService(api_client=mock_api)

        res = await service.get_package_details(identifier="1Z9999999999999999")
        assert res.success is False
        assert res.status == ToolResultCode.RATE_LIMITED
        assert "Rate limit" in res.message
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_upstream_service_unavailable_error_handling(auth_caller):
    """Verify 503 maintenance mode mapping."""
    token = set_caller_context(auth_caller)
    try:
        mock_api = AsyncMock()
        mock_api.get_user_preferences_and_services.side_effect = McpUpstreamServiceUnavailableError("Service 503")
        service = SmiotaMcpService(api_client=mock_api)

        res = await service.get_user_preferences_and_services()
        assert res.success is False
        assert res.status == ToolResultCode.SERVICE_UNAVAILABLE
        assert "currently unavailable" in res.message
    finally:
        reset_caller_context(token)


# ==============================================================================
# 4. Registry Discovery & 10-Point Description Completeness Tests
# ==============================================================================

def test_tool_registry_and_10_point_descriptions():
    """Verify all 6 core Smiota tools are registered with complete 10-point documentation."""
    expected_tools = [
        "search_packages",
        "get_package_details",
        "get_package_timeline",
        "get_user_preferences_and_services",
        "get_my_pickup_pin",
        "get_my_locker_details",
        "query_locker_door_status",
        "create_support_ticket",
        "remote_unlock_locker_door",
    ]

    registered = {tool.name: tool for tool in MCPToolRegistry.list_tools()}
    for tool_name in expected_tools:
        assert tool_name in registered, f"Tool '{tool_name}' must be registered in MCPToolRegistry"
        definition = registered[tool_name]
        assert definition.description, f"Tool '{tool_name}' must have a description"

        if tool_name in [
            "search_packages",
            "get_package_details",
            "get_package_timeline",
            "get_user_preferences_and_services",
            "get_my_pickup_pin",
            "get_my_locker_details",
        ]:
            desc = definition.description
            # Assert all 10 documentation points are explicitly present
            for point_num in range(1, 11):
                assert f"{point_num}. " in desc, f"Tool '{tool_name}' missing section {point_num} in description"
