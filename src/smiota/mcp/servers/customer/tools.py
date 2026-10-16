"""Customer Support & Smart Locker IoT MCP Tools (Hardware Telemetry, Ticket Creation, Remote Unlock)."""
from typing import Optional
from smiota.mcp.security import mcp_tool
from smiota.schemas.mcp import ToolAccessLevel


@mcp_tool(
    name="query_locker_door_status",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Query IoT telemetry for smart locker compartment door sensors and controller status.",
)
async def query_locker_door_status(locker_id: str, compartment: int) -> dict:
    """Fetch live IoT telemetry for smart locker door."""
    return {
        "locker_id": locker_id,
        "compartment": compartment,
        "status": "closed",
        "lock_state": "engaged",
        "battery_pct": 98.4,
        "last_ping": "2026-10-15T11:58:12Z",
    }


@mcp_tool(
    name="lookup_parcel_delivery_event",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Retrieve delivery barcode event history, courier drop-off, and resident pickup logs.",
)
async def lookup_parcel_delivery_event(tracking_number: str) -> dict:
    """Lookup parcel delivery status."""
    return {
        "tracking_number": tracking_number,
        "carrier": "FedEx",
        "deposited_at": "2026-10-15T09:30:00Z",
        "locker_id": "LK-SF-102",
        "compartment": 7,
        "pickup_code_sent": True,
        "picked_up": False,
    }


@mcp_tool(
    name="create_support_ticket",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Create or escalate a support case in ServiceNow or Zendesk.",
)
async def create_support_ticket(
    user_id: str,
    subject: str,
    description: str,
    priority: str = "medium",
) -> dict:
    """Create support ticket."""
    return {
        "ticket_id": "INC-2026-9042",
        "user_id": user_id,
        "subject": subject,
        "priority": priority,
        "status": "assigned_to_support_tier2",
    }


@mcp_tool(
    name="remote_unlock_locker_door",
    access_level=ToolAccessLevel.REMEDIATION,
    description="Send remote solenoid unlock command to IoT smart locker door (Requires Human Approval).",
)
async def remote_unlock_locker_door(
    locker_id: str,
    compartment: int,
    approval_token: Optional[str] = None,
) -> dict:
    """Execute remote locker door unlock."""
    return {
        "status": "door_unlocked",
        "locker_id": locker_id,
        "compartment": compartment,
        "approved_by_token": approval_token,
    }
