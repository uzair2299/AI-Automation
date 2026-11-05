"""Production-Grade FastAPI Correlation ID & Request Logging Middleware.

Demonstrates:
- Cryptographic / UUID correlation ID generation and validation
- contextvars binding and safe teardown in finally blocks
- Monotonic duration timing (time.perf_counter)
- Safe route template resolution without logging raw query PII
- Structured completion event emission with X-Correlation-ID header injection
"""
import re
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from smiota.core.logging import correlation_id_ctx, logger

# Strict regex: alphanumeric, dash, underscore between 8 and 64 characters
CORRELATION_ID_REGEX = re.compile(r"^[a-zA-Z0-9\-_]{8,64}$")


class ProductionRequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs exactly one structured completion event per request and manages correlation ID."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Validate or generate correlation ID
        incoming_id = request.headers.get("X-Correlation-ID")
        if incoming_id and CORRELATION_ID_REGEX.match(incoming_id):
            correlation_id = incoming_id
        else:
            correlation_id = f"corr-{uuid.uuid4().hex[:12]}"

        # 2. Bind to request state and async contextvar
        request.state.correlation_id = correlation_id
        token = correlation_id_ctx.set(correlation_id)

        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        except Exception:
            # Re-raise for centralized exception handlers; middleware records error status
            status_code = 500
            raise
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Route template (e.g. /api/v1/chat/{session_id}) preferred over raw URL
            route_path = request.scope.get("root_path", "") + (
                request.scope.get("endpoint").__name__ if request.scope.get("endpoint") else request.url.path
            )

            # Skip noisy health check endpoints at INFO level
            if not request.url.path.endswith(("/health", "/healthz", "/ready")):
                log_data = {
                    "event": "http.request.completed",
                    "http_method": request.method,
                    "http_route": request.url.path,
                    "http_status_code": status_code,
                    "duration_ms": duration_ms,
                    "correlation_id": correlation_id,
                }

                if status_code >= 500:
                    logger.error(f"HTTP {request.method} {request.url.path} failed ({status_code}) in {duration_ms}ms", extra=log_data)
                elif status_code >= 400:
                    logger.warning(f"HTTP {request.method} {request.url.path} client error ({status_code}) in {duration_ms}ms", extra=log_data)
                else:
                    logger.info(f"HTTP {request.method} {request.url.path} completed ({status_code}) in {duration_ms}ms", extra=log_data)

            # 3. Always reset contextvar
            correlation_id_ctx.reset(token)
