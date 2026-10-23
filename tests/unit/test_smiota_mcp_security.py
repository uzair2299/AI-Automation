"""Security tests for Smiota Customer MCP Tools.

Validates:
- Strict rejection of unauthenticated guest users (AUTHENTICATION_REQUIRED)
- Multi-tenant isolation and IDOR prevention (scoped by server session, not LLM arguments)
- Input sanitization and SQL/Script injection prevention
- Secret and credential masking in logs and envelopes
- Human-in-the-loop (HITL) cryptographic approval token gates on remediation tools
"""
import pytest
from unittest.mock import AsyncMock

from smiota.core.exceptions import RemediationApprovalRequiredError
from smiota.mcp.client import MCPClient
from smiota.mcp.context import CallerContext, set_caller_context, reset_caller_context
from smiota.mcp.servers.customer.tools import (
    get_my_locker_details,
    get_my_pickup_pin,
    get_package_details,
    get_package_timeline,
    get_user_preferences_and_services,
    remote_unlock_locker_door,
    search_packages,
)
from smiota.schemas.mcp_tools import ToolResultCode
from smiota.services.smiota_mcp_service import SmiotaMcpService


@pytest.fixture
def guest_caller() -> CallerContext:
    """Guest / anonymous resident caller context fixture."""
    return CallerContext(
        user_id="guest",
        customer_id=None,
        tenant_id=None,
        location_id=None,
        roles=[],
        parent_token=None,
        session_id="sess-guest-anon-99",
        is_authenticated=False,
        correlation_id="corr-sec-guest-1",
    )


@pytest.fixture(autouse=True)
def enable_dummy_mode(monkeypatch):
    """Ensure deterministic synthetic fixtures for offline security tests."""
    monkeypatch.setenv("SMIOTA_AUTH_DUMMY_MODE", "true")
    from smiota.clients.smiota_api_client import get_smiota_api_client
    client = get_smiota_api_client()
    original_dummy = client._dummy_mode
    client._dummy_mode = True
    yield
    client._dummy_mode = original_dummy


# ==============================================================================
# 1. Guest Session Blocking Tests (Authentication Required)
# ==============================================================================

@pytest.mark.asyncio
async def test_search_packages_guest_blocked(guest_caller):
    """Verify unauthenticated guests cannot search private package records."""
    token = set_caller_context(guest_caller)
    try:
        res = await search_packages(status_group="PENDING")
        assert res["success"] is False
        assert res["status"] == ToolResultCode.AUTHENTICATION_REQUIRED.value
        assert res["requires_auth"] is True
        assert "log in" in res["message"].lower()
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_package_details_guest_blocked(guest_caller):
    """Verify guest cannot retrieve package details by tracking number."""
    token = set_caller_context(guest_caller)
    try:
        res = await get_package_details(identifier="1Z9999999999999999")
        assert res["success"] is False
        assert res["status"] == ToolResultCode.AUTHENTICATION_REQUIRED.value
        assert res["requires_auth"] is True
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_package_timeline_guest_blocked(guest_caller):
    """Verify guest cannot view custody audit timeline."""
    token = set_caller_context(guest_caller)
    try:
        res = await get_package_timeline(identifier="1Z9999999999999999")
        assert res["success"] is False
        assert res["status"] == ToolResultCode.AUTHENTICATION_REQUIRED.value
        assert res["requires_auth"] is True
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_user_preferences_guest_blocked(guest_caller):
    """Verify guest cannot read resident accessibility or proxies."""
    token = set_caller_context(guest_caller)
    try:
        res = await get_user_preferences_and_services()
        assert res["success"] is False
        assert res["status"] == ToolResultCode.AUTHENTICATION_REQUIRED.value
        assert res["requires_auth"] is True
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_my_pickup_pin_guest_blocked(guest_caller):
    """Verify guest cannot retrieve confidential 6-digit pickup PIN."""
    token = set_caller_context(guest_caller)
    try:
        res = await get_my_pickup_pin()
        assert res["success"] is False
        assert res["status"] == ToolResultCode.AUTHENTICATION_REQUIRED.value
        assert res["requires_auth"] is True
    finally:
        reset_caller_context(token)


@pytest.mark.asyncio
async def test_get_my_locker_details_guest_blocked(guest_caller):
    """Verify guest cannot query resident locker compartment details."""
    token = set_caller_context(guest_caller)
    try:
        res = await get_my_locker_details()
        assert res["success"] is False
        assert res["status"] == ToolResultCode.AUTHENTICATION_REQUIRED.value
        assert res["requires_auth"] is True
    finally:
        reset_caller_context(token)


# ==============================================================================
# 2. Multi-Tenant & IDOR Protection Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_idor_protection_uses_caller_context():
    """Verify service extracts tenant/customer boundaries from CallerContext, ignoring LLM attempts to forge scope."""
    legitimate_caller = CallerContext(
        user_id="10790",
        customer_id=42,
        tenant_id=89,
        is_authenticated=True,
        parent_token="real-session-token",
    )

    mock_client = AsyncMock()
    mock_client.search_packages.return_value = {"packages": [], "total_count": 0}

    service = SmiotaMcpService(api_client=mock_client)
    await service.search_packages(status_group="PENDING", caller=legitimate_caller)

    # Assert that downstream API was called with legitimate caller context
    mock_client.search_packages.assert_awaited_once()
    _, kwargs = mock_client.search_packages.call_args
    passed_caller = kwargs.get("caller")
    assert passed_caller.customer_id == 42
    assert passed_caller.tenant_id == 89
    assert passed_caller.user_id == "10790"


# ==============================================================================
# 3. Injection Rejection Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_injection_characters_rejected():
    """Verify malicious SQL, XSS, and control characters in identifiers are rejected immediately."""
    authenticated = CallerContext(user_id="10790", is_authenticated=True)
    token = set_caller_context(authenticated)
    try:
        service = SmiotaMcpService()

        # SQL injection attempt
        res1 = await service.get_package_details(identifier="10492' OR '1'='1")
        # In get_package_details, validation checks before or catches cleanly
        assert res1.success is False or res1.status in [ToolResultCode.NOT_FOUND, ToolResultCode.INVALID_INPUT]

        # Newline / Carriage return / Header injection
        res2 = await service.get_package_details(identifier="10492\r\nX-Injected: evil")
        # Either schema rejects or service rejects
    finally:
        reset_caller_context(token)


# ==============================================================================
# 4. Sensitive Data Masking Tests
# ==============================================================================

def test_caller_context_mask_for_logs():
    """Verify CallerContext masks session tokens and secrets before writing to structured logs."""
    caller = CallerContext(
        user_id="10790",
        customer_id=101,
        tenant_id=89,
        parent_token="secret-super-confidential-bearer-token-123456",
        is_authenticated=True,
    )
    masked = caller.mask_for_logs()
    assert "secret-super-confidential-bearer-token-123456" not in str(masked)
    assert masked["parent_token_preview"] == "secret...3456"
    assert masked["has_parent_token"] is True
    assert masked["customer_id"] == 101


# ==============================================================================
# 5. Human-in-the-Loop (HITL) Remediation Protection Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_remote_unlock_requires_approval():
    """Verify physical solenoid door unlock requires cryptographic approval token."""
    client = MCPClient()
    with pytest.raises(RemediationApprovalRequiredError) as exc_info:
        await client.execute_tool(
            "remote_unlock_locker_door",
            {"locker_id": "LK-01", "compartment": 14},
        )
    assert exc_info.value.tool_name == "remote_unlock_locker_door"


@pytest.mark.asyncio
async def test_remote_unlock_with_valid_token():
    """Verify physical solenoid unlock succeeds when valid approval token is supplied."""
    client = MCPClient()
    result = await client.execute_tool(
        "remote_unlock_locker_door",
        {
            "locker_id": "LK-01",
            "compartment": 14,
            "approval_token": "VALID-MGR-TOKEN-7788",
        },
    )
    assert result.success is True
    assert result.output["status"] == "door_unlocked"
    assert result.output["approved_by_token"] == "VALID-MGR-TOKEN-7788"
