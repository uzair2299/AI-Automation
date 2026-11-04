"""Correlation ID / Request ID tracking middleware for distributed tracing."""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from smiota_common.logging import correlation_id_ctx


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Ensures every HTTP request has an X-Correlation-ID header for logging and tracing."""

    def __init__(self, app, id_prefix: str = "corr"):
        super().__init__(app)
        self.id_prefix = id_prefix

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or f"{self.id_prefix}-{uuid.uuid4().hex[:12]}"
        request.state.correlation_id = correlation_id
        token = correlation_id_ctx.set(correlation_id)

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            correlation_id_ctx.reset(token)
