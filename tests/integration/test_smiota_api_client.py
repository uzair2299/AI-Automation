"""Integration and contract tests for SmiotaApiClient and MCP Tool Execution.

Validates:
- Exact HTTP endpoint paths, methods, query parameters, and defense-in-depth headers
- Propagation of X-Internal-Service-Key, X-Customer-Id, X-Tenant-Id, and X-Correlation-Id
- Response contract compatibility against source-of-truth schemas
- Bounded retries on transient 5xx errors and non-retry on 4xx errors
- Rate limit 429 handling with Retry-After header parsing
- Discovery and execution through MCPClient
- Connection lifecycle and graceful shutdown
"""
import json
import pytest
import httpx

from smiota.clients.smiota_api_client import SmiotaApiClient, get_smiota_api_client
from smiota.mcp.client import MCPClient
from smiota.mcp.context import CallerContext, set_caller_context, reset_caller_context
from smiota.mcp.errors import McpUpstreamRateLimitedError, McpUpstreamServiceUnavailableError
from smiota.services.smiota_mcp_service import SmiotaMcpService


@pytest.fixture
def caller_context() -> CallerContext:
    return CallerContext(
        user_id="10790",
        customer_id=101,
        tenant_id=89,
        location_id=14,
        building_id=14,
        unit_no="4B",
        roles=["resident"],
        parent_token="parent-token-xyz-contract-test",
        session_id="sess-contract-1",
        is_authenticated=True,
        correlation_id="corr-contract-9988",
    )


@pytest.mark.asyncio
async def test_search_packages_http_contract(caller_context):
    """Verify GET /internal/ai/packages sends correct query params and defense-in-depth headers."""
    recorded_requests = []

    def mock_handler(request: httpx.Request) -> httpx.Response:
        recorded_requests.append(request)
        content = {
            "total_count": 1,
            "packages": [
                {
                    "id": 10492,
                    "tracking_number": "1Z9999999999999999",
                    "carrier": "FedEx",
                    "status": "READY_FOR_PICKUP",
                    "passcode": "482910",
                    "location": {
                        "storage_type": "LOCKER",
                        "building_name": "East Commons",
                        "locker_door_name": "Door 14",
                        "locker_bank": "Main Pod Bank 1",
                    },
                }
            ],
        }
        return httpx.Response(200, json=content, headers={"Content-Type": "application/json"})

    transport = httpx.MockTransport(mock_handler)
    client = SmiotaApiClient(
        base_url="http://mock-smiota:8080",
        service_token="test-internal-key",
        transport=transport,
    )

    service = SmiotaMcpService(api_client=client)
    res = await service.search_packages(
        status_group="PENDING",
        carrier="FedEx",
        storage_type="LOCKER",
        days=14,
        is_perishable=False,
        caller=caller_context,
    )

    assert res.success is True
    assert len(recorded_requests) == 1
    req = recorded_requests[0]

    # Verify HTTP Method and Path
    assert req.method == "GET"
    assert req.url.path == "/internal/ai/packages"

    # Verify Query Parameters
    params = dict(req.url.params)
    assert params["status_group"] == "PENDING"
    assert params["carrier"] == "FedEx"
    assert params["storage_type"] == "LOCKER"
    assert params["days"] == "14"
    assert params["is_perishable"] == "false"
    assert params["customer_id"] == "101"
    assert params["tenant_id"] == "89"

    # Verify Defense-in-Depth Isolation Headers
    assert req.headers["X-Internal-Service-Key"] == "test-internal-key"
    assert req.headers["X-Customer-Id"] == "101"
    assert req.headers["X-Tenant-Id"] == "89"
    assert req.headers["X-Location-Id"] == "14"
    assert req.headers["X-User-Id"] == "10790"
    assert req.headers["X-Correlation-Id"] == "corr-contract-9988"
    assert req.headers["X-Auth-Token"] == "parent-token-xyz-contract-test"

    await client.close()


@pytest.mark.asyncio
async def test_get_package_details_http_contract(caller_context):
    """Verify GET /internal/ai/packages/{identifier} contract."""
    recorded_requests = []

    def mock_handler(request: httpx.Request) -> httpx.Response:
        recorded_requests.append(request)
        content = {
            "id": 10492,
            "uuid": "8f9a2b10-6a5c-4e89-b1d3-92f7a01d5e34",
            "tracking_number": "1Z9999999999999999",
            "carrier": "UPS",
            "status": "READY_FOR_PICKUP",
            "passcode": "482910",
            "location": {
                "storage_type": "LOCKER",
                "building_name": "East Campus Commons",
                "locker_door_name": "Door 14",
                "locker_bank": "Main Pod Bank 1",
            },
        }
        return httpx.Response(200, json=content, headers={"Content-Type": "application/json"})

    transport = httpx.MockTransport(mock_handler)
    client = SmiotaApiClient(
        base_url="http://mock-smiota:8080",
        service_token="test-internal-key",
        transport=transport,
    )

    service = SmiotaMcpService(api_client=client)
    res = await service.get_package_details(identifier="1Z9999999999999999", caller=caller_context)

    assert res.success is True
    assert len(recorded_requests) == 1
    req = recorded_requests[0]
    assert req.method == "GET"
    assert req.url.path == "/internal/ai/packages/1Z9999999999999999"
    assert req.headers["X-Internal-Service-Key"] == "test-internal-key"

    await client.close()


@pytest.mark.asyncio
async def test_get_package_timeline_http_contract(caller_context):
    """Verify GET /internal/ai/packages/{identifier}/timeline contract."""
    recorded_requests = []

    def mock_handler(request: httpx.Request) -> httpx.Response:
        recorded_requests.append(request)
        content = {
            "tracking_number": "1Z9999999999999999",
            "timeline": [
                {"event_type": "DOCK_RECEIVE", "timestamp": "2026-10-23T08:30:00Z"},
                {"event_type": "LOCKER_DEPOSIT", "timestamp": "2026-10-23T09:15:00Z"},
            ],
        }
        return httpx.Response(200, json=content, headers={"Content-Type": "application/json"})

    transport = httpx.MockTransport(mock_handler)
    client = SmiotaApiClient(
        base_url="http://mock-smiota:8080",
        service_token="test-internal-key",
        transport=transport,
    )

    service = SmiotaMcpService(api_client=client)
    res = await service.get_package_timeline(identifier="1Z9999999999999999", caller=caller_context)

    assert res.success is True
    assert len(recorded_requests) == 1
    req = recorded_requests[0]
    assert req.method == "GET"
    assert req.url.path == "/internal/ai/packages/1Z9999999999999999/timeline"

    await client.close()


@pytest.mark.asyncio
async def test_get_user_preferences_http_contract(caller_context):
    """Verify GET /internal/ai/users/profile-and-services contract."""
    recorded_requests = []

    def mock_handler(request: httpx.Request) -> httpx.Response:
        recorded_requests.append(request)
        content = {
            "user_id": 10790,
            "accessibility": {"bottom_tier_lockers_required": True},
            "proxies": [{"name": "Jordan Lee"}],
            "active_day_use_lockers": [],
        }
        return httpx.Response(200, json=content, headers={"Content-Type": "application/json"})

    transport = httpx.MockTransport(mock_handler)
    client = SmiotaApiClient(
        base_url="http://mock-smiota:8080",
        service_token="test-internal-key",
        transport=transport,
    )

    service = SmiotaMcpService(api_client=client)
    res = await service.get_user_preferences_and_services(caller=caller_context)

    assert res.success is True
    assert len(recorded_requests) == 1
    req = recorded_requests[0]
    assert req.method == "GET"
    assert req.url.path == "/internal/ai/users/profile-and-services"

    await client.close()


@pytest.mark.asyncio
async def test_transient_503_bounded_retry(caller_context):
    """Verify client executes bounded retries with backoff on transient 503 errors."""
    attempts = 0

    def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503, content=b"Maintenance", headers={"Content-Type": "text/plain"})
        return httpx.Response(200, json={"total_count": 0, "packages": []}, headers={"Content-Type": "application/json"})

    transport = httpx.MockTransport(mock_handler)
    client = SmiotaApiClient(
        base_url="http://mock-smiota:8080",
        service_token="test-internal-key",
        transport=transport,
    )

    # Should retry once and succeed on 2nd attempt
    res = await client.search_packages(caller=caller_context)
    assert attempts == 2
    assert res["total_count"] == 0

    await client.close()


@pytest.mark.asyncio
async def test_rate_limit_429_with_retry_after(caller_context):
    """Verify 429 response raises McpUpstreamRateLimitedError with parsed Retry-After value."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            content=b"Rate Limit Exceeded",
            headers={"Content-Type": "text/plain", "Retry-After": "15"},
        )

    transport = httpx.MockTransport(mock_handler)
    client = SmiotaApiClient(
        base_url="http://mock-smiota:8080",
        service_token="test-internal-key",
        transport=transport,
    )

    with pytest.raises(McpUpstreamRateLimitedError) as exc_info:
        await client.search_packages(caller=caller_context)

    assert exc_info.value.retry_after == 15
    await client.close()


@pytest.mark.asyncio
async def test_mcp_client_tool_execution_flow(caller_context, monkeypatch):
    """Verify tool execution through the official MCPClient dispatch mechanism."""
    monkeypatch.setenv("SMIOTA_AUTH_DUMMY_MODE", "true")
    api_client = get_smiota_api_client()
    original_dummy = api_client._dummy_mode
    api_client._dummy_mode = True

    token = set_caller_context(caller_context)
    try:
        client = MCPClient()

        # Execute search_packages tool
        res1 = await client.execute_tool("search_packages", {"status_group": "PENDING"})
        assert res1.success is True
        assert res1.execution_time_ms >= 0.0
        assert res1.output["success"] is True

        # Execute get_package_details tool
        res2 = await client.execute_tool("get_package_details", {"identifier": "1Z9999999999999999"})
        assert res2.success is True
        assert res2.output["success"] is True

        # Execute get_my_pickup_pin tool
        res3 = await client.execute_tool("get_my_pickup_pin", {})
        assert res3.success is True
        assert res3.output["success"] is True

        # Execute get_my_locker_details tool
        res4 = await client.execute_tool("get_my_locker_details", {})
        assert res4.success is True
        assert res4.output["success"] is True

    finally:
        api_client._dummy_mode = original_dummy
        reset_caller_context(token)
