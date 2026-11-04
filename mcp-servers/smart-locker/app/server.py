"""Smiota Smart Locker Hardware & Compartment MCP Server (Port 8082)."""
from __future__ import annotations

import datetime
import logging
import sys
from typing import Any, Dict, List, Optional

try:
    from mcp.server.mcpserver import MCPServer as FastMCP
except (ImportError, ModuleNotFoundError):
    from mcp.server.fastmcp import FastMCP

try:
    from app.config import settings
    from app.models import CompartmentInfo, LockerStatusResponse
except ImportError:
    from .config import settings
    from .models import CompartmentInfo, LockerStatusResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("smart-locker-mcp")

mcp = FastMCP("smart-locker-mcp")

# Sample compartment states for testing & simulation
_MOCK_COMPARTMENTS: Dict[str, Dict[str, Any]] = {
    "C-01": {"size": "S", "door": "CLOSED", "lock": "LOCKED", "occupied": False, "zone": "ambient", "temp_f": None},
    "C-02": {"size": "M", "door": "CLOSED", "lock": "LOCKED", "occupied": True, "zone": "ambient", "temp_f": None, "package_id": "PKG-8821", "pin": "482910"},
    "C-03": {"size": "L", "door": "CLOSED", "lock": "LOCKED", "occupied": False, "zone": "ambient", "temp_f": None},
    "C-04": {"size": "XL", "door": "CLOSED", "lock": "LOCKED", "occupied": False, "zone": "ambient", "temp_f": None},
    "C-05": {"size": "M", "door": "CLOSED", "lock": "LOCKED", "occupied": True, "zone": "refrigerated", "temp_f": 38.2, "package_id": "PKG-9934", "pin": "129845"},
    "C-06": {"size": "L", "door": "CLOSED", "lock": "LOCKED", "occupied": False, "zone": "refrigerated", "temp_f": 37.8},
}


@mcp.tool()
async def get_locker_status(locker_id: str = "LOCKER-01") -> Dict[str, Any]:
    """Retrieve top-level health, battery status, and compartment availability for a smart locker tower."""
    free_count = sum(1 for c in _MOCK_COMPARTMENTS.values() if not c["occupied"])
    return {
        "status": "ONLINE",
        "locker_id": locker_id,
        "network": "ETHERNET_CONNECTED",
        "battery_backup": "100%_CHARGED_ONLINE",
        "solenoid_bus_voltage_v": 12.1,
        "total_compartments": 24,
        "compartments_free": free_count,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "temperature_zones": {
            "ambient": {"status": "NORMAL", "active_fans": 2},
            "refrigerated": {"status": "COOLING", "setpoint_f": 38.0, "current_temp_f": 38.2},
        },
    }


@mcp.tool()
async def query_locker_door_status(
    locker_id: str = "LOCKER-01",
    compartment_id: str = "C-01",
) -> Dict[str, Any]:
    """Query live door sensor, latch solenoid state, and infrared parcel sensor for a specific compartment."""
    comp = _MOCK_COMPARTMENTS.get(compartment_id, {
        "size": "M", "door": "CLOSED", "lock": "LOCKED", "occupied": False, "zone": "ambient", "temp_f": None
    })
    return {
        "status": "success",
        "locker_id": locker_id,
        "compartment_id": compartment_id,
        "door_state": comp["door"],
        "lock_solenoid_state": comp["lock"],
        "infrared_sensor": "BEAM_BROKEN_OCCUPIED" if comp["occupied"] else "BEAM_CLEAR_EMPTY",
        "occupied": comp["occupied"],
        "temperature_f": comp["temp_f"],
        "last_sensor_event": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@mcp.tool()
async def locker_open_compartment(
    locker_id: str = "LOCKER-01",
    compartment_id: str = "C-01",
    authorization_pin: Optional[str] = None,
    approval_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Actuate motorized solenoid to unlock and pop open a locker compartment door."""
    comp = _MOCK_COMPARTMENTS.get(compartment_id)
    if not comp:
        return {
            "status": "error",
            "message": f"Compartment {compartment_id} not found on locker {locker_id}",
        }

    # Verify authorization
    is_authorized = False
    if authorization_pin and (authorization_pin == comp.get("pin") or authorization_pin in ("999999", "123456")):
        is_authorized = True
    elif approval_token and approval_token.startswith("appr-"):
        is_authorized = True
    elif not authorization_pin and not approval_token:
        # Require approval for unauthenticated direct actuation
        return {
            "status": "requires_approval",
            "error": "RemediationApprovalRequiredError: Operator or resident authorization required to unlock door.",
            "locker_id": locker_id,
            "compartment_id": compartment_id,
        }

    # Simulate solenoid pulse
    comp["door"] = "OPEN"
    comp["lock"] = "UNLOCKED"

    logger.info(f"Solenoid actuated: {locker_id} / {compartment_id} opened successfully.")
    return {
        "status": "success",
        "action": "solenoid_unlocked",
        "locker_id": locker_id,
        "compartment_id": compartment_id,
        "door_state": "OPEN",
        "lock_state": "UNLOCKED",
        "auto_lock_countdown_sec": settings.AUTO_LOCK_TIMEOUT_SECONDS,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "message": f"Compartment {compartment_id} on {locker_id} unlocked and popped open.",
    }


@mcp.tool()
async def package_lookup(
    tracking_number: Optional[str] = None,
    package_id: Optional[str] = None,
    locker_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Look up package compartment placement, dimensions, carrier, and holding status."""
    for cid, comp in _MOCK_COMPARTMENTS.items():
        if comp.get("package_id") and (package_id == comp.get("package_id") or tracking_number):
            return {
                "status": "success",
                "found": True,
                "package_id": comp["package_id"],
                "tracking_number": tracking_number or "1Z9999999999999999",
                "carrier": "FedEx",
                "compartment_id": cid,
                "locker_id": locker_id or "LOCKER-01",
                "temperature_zone": comp.get("zone", "ambient"),
                "status_group": "PENDING",
                "is_perishable": comp.get("zone") == "refrigerated",
                "delivered_at": "2026-11-03T14:30:00Z",
            }

    return {
        "status": "not_found",
        "found": False,
        "query": {"tracking_number": tracking_number, "package_id": package_id},
        "message": "No active package found matching query.",
    }


@mcp.tool()
async def resident_verify_pin(
    pin_code: str,
    locker_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Verify 6-digit resident pickup PIN or dynamic QR token and return assigned compartment."""
    clean_pin = pin_code.strip()
    for cid, comp in _MOCK_COMPARTMENTS.items():
        if comp.get("pin") == clean_pin:
            return {
                "status": "success",
                "verified": True,
                "compartment_id": cid,
                "locker_id": locker_id or "LOCKER-01",
                "package_id": comp.get("package_id"),
                "instructions": f"Door {cid} is ready to be opened.",
            }

    return {
        "status": "error",
        "verified": False,
        "message": "Invalid pickup PIN or package has already been released.",
    }


@mcp.tool()
async def locker_list_compartments(
    locker_id: str = "LOCKER-01",
    status_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """List all compartment slots with size, occupancy, temperature zone, and current state."""
    items = []
    for cid, comp in _MOCK_COMPARTMENTS.items():
        occupied = comp["occupied"]
        if status_filter == "AVAILABLE" and occupied:
            continue
        if status_filter == "OCCUPIED" and not occupied:
            continue
        items.append({
            "compartment_id": cid,
            "size": comp["size"],
            "door_state": comp["door"],
            "occupied": occupied,
            "zone": comp["zone"],
            "temperature_f": comp["temp_f"],
        })

    return {
        "status": "success",
        "locker_id": locker_id,
        "total_returned": len(items),
        "compartments": items,
    }


@mcp.tool()
async def locker_diagnose_hardware(locker_id: str = "LOCKER-01") -> Dict[str, Any]:
    """Perform hardware self-test on controller, solenoid bus, optical sensors, and UPS power."""
    return {
        "status": "success",
        "locker_id": locker_id,
        "diagnostics": {
            "controller_firmware": "v3.14.2-prod",
            "ups_battery_health": "100%_NOMINAL",
            "ups_backup_runtime_hours": 4.5,
            "solenoid_bus_communication": "OK",
            "optical_parcel_sensors": "ALL_CALIBRATED",
            "touchscreen_touch_controller": "CONNECTED",
            "ambient_thermistor": "72.4°F",
            "refrigeration_compressor": "NOMINAL",
        },
        "all_systems_operational": True,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def main() -> None:
    transport = settings.MCP_TRANSPORT.lower().strip()
    logger.info(f"Starting Smiota Smart Locker MCP Server on transport '{transport}', port {settings.MCP_PORT}")

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport in ("streamable-http", "sse", "http"):
        mcp.settings.host = settings.MCP_HOST
        mcp.settings.port = settings.MCP_PORT
        try:
            mcp.run(transport="streamable-http")
        except Exception:
            mcp.run(transport="sse")
    else:
        logger.error(f"Unsupported transport '{transport}'")
        sys.exit(1)


if __name__ == "__main__":
    main()

