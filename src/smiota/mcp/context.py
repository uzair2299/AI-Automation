from __future__ import annotations

"""Server-side MCP Caller Context & Tenant Isolation Boundaries.

Provides thread-safe and coroutine-safe storage of authenticated caller identity,
enforcing that MCP tools resolve customer/tenant scope strictly from server-validated
session tokens rather than LLM-generated arguments.
"""
from dataclasses import dataclass, field
from contextvars import ContextVar
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from smiota.agents.base import AgentContext
from smiota.core.logging import correlation_id_ctx


@dataclass
class CallerContext:
    """Server-verified identity and authorization boundaries for an active MCP execution."""
    user_id: Optional[str] = None
    customer_id: Optional[int] = None
    tenant_id: Optional[int] = None
    location_id: Optional[int] = None
    building_id: Optional[int] = None
    unit_no: Optional[str] = None
    roles: list[str] = field(default_factory=list)
    parent_token: Optional[str] = None
    session_id: Optional[str] = None
    is_authenticated: bool = False
    correlation_id: Optional[str] = None
    raw_user: dict[str, Any] = field(default_factory=dict)

    def mask_for_logs(self) -> dict[str, Any]:
        """Safe sanitized representation for structured audit logs without leaking PII."""
        tok = self.parent_token or ""
        masked_tok = f"{tok[:6]}...{tok[-4:]}" if len(tok) >= 12 else ("***" if tok else "none")
        return {
            "user_id": self.user_id,
            "customer_id": self.customer_id,
            "tenant_id": self.tenant_id,
            "location_id": self.location_id,
            "is_authenticated": self.is_authenticated,
            "roles": self.roles,
            "session_id": self.session_id,
            "has_parent_token": bool(self.parent_token),
            "parent_token_preview": masked_tok,
            "correlation_id": self.correlation_id,
        }


_caller_context_var: ContextVar[Optional[CallerContext]] = ContextVar("mcp_caller_context", default=None)


def set_caller_context(context: CallerContext) -> Any:
    """Set the active caller context for the current async task execution."""
    return _caller_context_var.set(context)


def reset_caller_context(token: Any) -> None:
    """Reset the caller context to a previous token."""
    _caller_context_var.reset(token)


def clear_caller_context() -> None:
    """Clear the active caller context."""
    _caller_context_var.set(None)


def get_caller_context() -> Optional[CallerContext]:
    """Retrieve the current server-validated caller context."""
    return _caller_context_var.get()


def build_caller_context_from_agent_context(
    agent_context: Any,
    correlation_id: Optional[str] = None,
) -> CallerContext:
    """Extract and validate caller boundaries from an AgentContext.
    
    Guarantees:
    - Guests with no valid parent_token or anonymous IDs are marked is_authenticated=False.
    - Customer and Tenant IDs are derived exclusively from verified user dictionaries.
    """
    user_data = dict(agent_context.user or {})
    metadata = dict(agent_context.metadata or {})
    if not user_data and "user" in metadata and isinstance(metadata["user"], dict):
        user_data = metadata["user"]

    parent_token = (
        getattr(agent_context, "parent_token", None)
        or user_data.get("parent_token")
        or metadata.get("parent_token")
        or metadata.get("token")
        or None
    )

    user_id = str(agent_context.user_id or user_data.get("user_id") or user_data.get("id") or "").strip()
    is_guest = user_id.lower() in {"ws-resident", "anonymous", "guest", "", "none"}

    # Extract integer customer_id safely
    raw_cid = user_data.get("customerId") or user_data.get("customer_id") or metadata.get("customer_id")
    customer_id: Optional[int] = None
    if raw_cid is not None:
        try:
            customer_id = int(raw_cid)
        except (ValueError, TypeError):
            pass

    # Extract integer tenant_id safely
    raw_tid = user_data.get("tenantId") or user_data.get("tenant_id") or agent_context.tenant_id
    tenant_id: Optional[int] = None
    if raw_tid is not None and str(raw_tid).lower() != "default":
        try:
            tenant_id = int(raw_tid)
        except (ValueError, TypeError):
            pass

    # Extract location_id and building_id safely
    raw_lid = user_data.get("locationId") or user_data.get("location_id")
    location_id: Optional[int] = None
    if raw_lid is not None:
        try:
            location_id = int(raw_lid)
        except (ValueError, TypeError):
            pass

    raw_bid = user_data.get("buildingId") or user_data.get("building_id")
    building_id: Optional[int] = None
    if raw_bid is not None:
        try:
            building_id = int(raw_bid)
        except (ValueError, TypeError):
            pass

    # An authenticated caller has explicit auth flag, active parent token, or verified user profile
    explicit_auth = bool(
        user_data.get("is_authenticated")
        or metadata.get("is_authenticated")
        or getattr(agent_context, "is_authenticated", False)
    )
    is_authenticated = bool(explicit_auth or parent_token or (not is_guest and (customer_id or tenant_id or user_id)))

    roles = list(agent_context.roles or user_data.get("roles") or [])
    active_corr_id = correlation_id or correlation_id_ctx.get()

    return CallerContext(
        user_id=None if is_guest else user_id,
        customer_id=customer_id,
        tenant_id=tenant_id,
        location_id=location_id,
        building_id=building_id,
        unit_no=user_data.get("unitNo") or user_data.get("unit_no"),
        roles=roles,
        parent_token=parent_token,
        session_id=agent_context.session_id,
        is_authenticated=is_authenticated,
        correlation_id=active_corr_id,
        raw_user=user_data,
    )
