"""Production Structured Logging Patterns for Agents, Services, and Tasks.

Demonstrates:
- Emitting machine-readable structured logs with contextual fields
- Masking sensitive tokens and resident parameters
- Logging exceptions once at the boundary without duplication
- Safe dictionary allowlisting
"""
import logging
import time
from typing import Any, Optional
from smiota.core.logging import correlation_id_ctx, logger

# Approved metadata fields allowed in agent execution logs
APPROVED_AGENT_METADATA_KEYS = {
    "agent_name",
    "domain",
    "session_id",
    "channel",
    "requires_approval",
    "action",
    "duration_ms",
    "matched_intent",
    "routing_method",
    "confidence",
}


def log_agent_lifecycle(
    event: str,
    message: str,
    level: int = logging.INFO,
    **kwargs: Any,
) -> None:
    """Emits an event-driven structured log with allowlisted fields and active correlation ID."""
    sanitized_fields = {
        k: v for k, v in kwargs.items() if k in APPROVED_AGENT_METADATA_KEYS
    }

    extra_payload = {
        "event": event,
        "correlation_id": correlation_id_ctx.get() or "-",
        **sanitized_fields,
    }

    logger.log(level, message, extra=extra_payload)


async def execute_agent_with_observability(
    agent_name: str,
    query: str,
    session_id: str,
    process_fn,
) -> Any:
    """Pattern showing duration tracking, boundary exception logging, and structured events."""
    start_time = time.perf_counter()

    log_agent_lifecycle(
        event="agent.execution.started",
        message=f"Agent '{agent_name}' execution started for session {session_id}",
        level=logging.DEBUG,
        agent_name=agent_name,
        session_id=session_id,
    )

    try:
        result = await process_fn()
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        log_agent_lifecycle(
            event="agent.execution.completed",
            message=f"Agent '{agent_name}' finished in {duration_ms}ms",
            level=logging.INFO,
            agent_name=agent_name,
            session_id=session_id,
            duration_ms=duration_ms,
            requires_approval=getattr(result, "requires_approval", False),
        )
        return result

    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Log once at boundary with exception traceback and stable error event
        logger.exception(
            f"Agent '{agent_name}' failed after {duration_ms}ms: {exc}",
            extra={
                "event": "agent.execution.failed",
                "agent_name": agent_name,
                "session_id": session_id,
                "error_type": type(exc).__name__,
                "duration_ms": duration_ms,
                "correlation_id": correlation_id_ctx.get() or "-",
            },
        )
        # Re-raise or convert to normalized domain result
        raise
