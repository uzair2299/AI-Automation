"""Unit tests for shared foundation library (smiota-common)."""
import json
import logging
import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from smiota_common.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    SmiotaException,
)
from smiota_common.logging import (
    CloudJSONFormatter,
    CorrelationFilter,
    correlation_id_ctx,
    setup_logging,
)
from smiota_common.middleware import CorrelationIdMiddleware
from smiota_common.models import APIResponse, ErrorDetail


def test_api_response_success():
    """Verify APIResponse serializes data, message, and default status."""
    res = APIResponse(data={"key": "value"}, message="Operation succeeded")
    assert res.status == "success"
    assert res.data == {"key": "value"}
    assert res.message == "Operation succeeded"
    assert res.errors is None


def test_api_response_error():
    """Verify APIResponse serializes structured error details."""
    detail = ErrorDetail(code="INVALID_ARGUMENT", message="Field 'query' is required", field="query")
    res = APIResponse[None](status="error", message="Validation failed", errors=[detail])
    assert res.status == "error"
    assert res.data is None
    assert len(res.errors) == 1
    assert res.errors[0].code == "INVALID_ARGUMENT"
    assert res.errors[0].field == "query"


def test_exceptions_hierarchy():
    """Verify exception hierarchy and status codes."""
    exc = SmiotaException("Base error", details={"trace": "abc"}, status_code=400, error_code="BAD_REQUEST")
    assert str(exc) == "Base error"
    assert exc.status_code == 400
    assert exc.error_code == "BAD_REQUEST"

    svc_err = ServiceUnavailableError("rag-service")
    assert svc_err.status_code == 503
    assert svc_err.error_code == "SERVICE_UNAVAILABLE"
    assert "rag-service" in svc_err.message

    res_err = ResourceNotFoundError("package", "PKG-1234")
    assert res_err.status_code == 404
    assert res_err.error_code == "NOT_FOUND"

    auth_err = AuthenticationError()
    assert auth_err.status_code == 401
    assert auth_err.error_code == "UNAUTHENTICATED"

    perm_err = AuthorizationError()
    assert perm_err.status_code == 403
    assert perm_err.error_code == "PERMISSION_DENIED"


def test_correlation_filter_and_formatter():
    """Verify CorrelationFilter injects correlation ID and CloudJSONFormatter formats record."""
    token = correlation_id_ctx.set("corr-test-abc")
    try:
        formatter = CloudJSONFormatter(service_name="test-service", environment="production")
        record = logging.LogRecord(
            name="test-logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="Test log message",
            args=(),
            exc_info=None,
        )
        filt = CorrelationFilter()
        filt.filter(record)
        assert record.correlation_id == "corr-test-abc"

        formatted = formatter.format(record)
        payload = json.loads(formatted)
        assert payload["service"] == "test-service"
        assert payload["environment"] == "production"
        assert payload["correlation_id"] == "corr-test-abc"
        assert payload["message"] == "Test log message"
        assert payload["level"] == "INFO"
    finally:
        correlation_id_ctx.reset(token)


def test_correlation_id_middleware():
    """Verify CorrelationIdMiddleware propagates incoming or generates new correlation ID."""
    async def endpoint(request):
        cid = correlation_id_ctx.get()
        return JSONResponse({"correlation_id": cid})

    app = Starlette(routes=[Route("/test", endpoint)])
    app.add_middleware(CorrelationIdMiddleware, id_prefix="test-corr")
    client = TestClient(app)

    # 1. Custom correlation ID passed
    resp1 = client.get("/test", headers={"X-Correlation-ID": "custom-uuid-123"})
    assert resp1.status_code == 200
    assert resp1.headers.get("X-Correlation-ID") == "custom-uuid-123"
    assert resp1.json()["correlation_id"] == "custom-uuid-123"

    # 2. Auto-generated correlation ID
    resp2 = client.get("/test")
    assert resp2.status_code == 200
    cid2 = resp2.headers.get("X-Correlation-ID")
    assert cid2 is not None
    assert cid2.startswith("test-corr-")
    assert resp2.json()["correlation_id"] == cid2
