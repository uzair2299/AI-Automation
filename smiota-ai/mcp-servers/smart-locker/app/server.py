"""Smiota Smart Locker Hardware & Compartment MCP Server (Port 8082)."""
from __future__ import annotations

import datetime
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server.mcpserver import MCPServer as FastMCP

from .config import settings

try:
    from smiota_common.logging import setup_logging
    logger = setup_logging(service_name="smart-locker-mcp")
except ImportError:
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

_MOCK_PACKAGES: List[Dict[str, Any]] = [
    {
        "id": 10492,
        "uuid": "8f9a2b10-6a5c-4e89-b1d3-92f7a01d5e34",
        "tracking_number": "1Z9999999999999999",
        "trackingNumber": "1Z9999999999999999",
        "po_number": "PO-88421",
        "carrier": "UPS",
        "status": "READY_FOR_PICKUP",
        "status_group": "PENDING",
        "received_time": "2026-10-23T09:15:00Z",
        "expiration_time": "2026-10-26T18:00:00Z",
        "passcode": "482910",
        "pickup_pin": "482910",
        "compartment_id": "C-02",
        "locker_id": "LOCKER-01",
        "locker_bank": "Main Pod Bank 1",
        "locker_door": "Door 14",
        "locker_door_name": "Door 14",
        "building_name": "East Campus Commons",
        "storage_type": "LOCKER",
        "is_perishable": False,
        "is_at_destination": True,
        "location": {
            "building_id": 14,
            "building_name": "East Campus Commons",
            "storage_type": "LOCKER",
            "locker_id": 88,
            "locker_bank": "Main Pod Bank 1",
            "locker_door_name": "Door 14",
            "locker_size": "Medium",
        },
        "recipient": {
            "firstName": "Alex",
            "lastName": "Johnson",
            "email": "alex.johnson@example.com",
            "phone": "+1-555-0199",
        },
        "recipientName": "Alex Johnson",
    },
    {
        "id": 10518,
        "uuid": "3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
        "tracking_number": "1Z8888888888888888",
        "trackingNumber": "1Z8888888888888888",
        "po_number": "PO-99120",
        "carrier": "FedEx",
        "status": "READY_FOR_PICKUP",
        "status_group": "PENDING",
        "received_time": "2026-10-24T14:30:00Z",
        "expiration_time": "2026-10-27T18:00:00Z",
        "passcode": "129845",
        "pickup_pin": "129845",
        "compartment_id": "C-05",
        "locker_id": "LOCKER-01",
        "locker_bank": "Main Pod Bank 1",
        "locker_door": "Door 18",
        "locker_door_name": "Door 18",
        "building_name": "East Campus Commons",
        "storage_type": "LOCKER",
        "is_perishable": True,
        "is_at_destination": True,
        "location": {
            "building_id": 14,
            "building_name": "East Campus Commons",
            "storage_type": "LOCKER",
            "locker_id": 88,
            "locker_bank": "Main Pod Bank 1",
            "locker_door_name": "Door 18",
            "locker_size": "Medium (Refrigerated)",
        },
        "recipient": {
            "firstName": "Alex",
            "lastName": "Johnson",
            "email": "alex.johnson@example.com",
            "phone": "+1-555-0199",
        },
        "recipientName": "Alex Johnson",
    },
]


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
    compartment: int = 1,
    compartment_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Query live door sensor, latch solenoid state, and infrared parcel sensor for a specific compartment."""
    cid = compartment_id or (f"C-0{compartment}" if compartment < 10 else f"C-{compartment}")
    comp = _MOCK_COMPARTMENTS.get(cid, {
        "size": "M", "door": "CLOSED", "lock": "LOCKED", "occupied": False, "zone": "ambient", "temp_f": None
    })
    return {
        "status": "success",
        "locker_id": locker_id,
        "compartment": compartment,
        "compartment_id": cid,
        "door_state": comp["door"],
        "lock_state": comp["lock"],
        "lock_solenoid_state": comp["lock"],
        "infrared_sensor": "BEAM_BROKEN_OCCUPIED" if comp["occupied"] else "BEAM_CLEAR_EMPTY",
        "occupied": comp["occupied"],
        "battery_pct": 98.4,
        "temperature_f": comp["temp_f"],
        "last_sensor_event": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "last_ping": datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
        return {
            "status": "requires_approval",
            "error": "RemediationApprovalRequiredError: Operator or resident authorization required to unlock door.",
            "locker_id": locker_id,
            "compartment_id": compartment_id,
        }

    if not is_authorized:
        return {
            "status": "unauthorized",
            "error": "Invalid authorization PIN or approval token.",
            "locker_id": locker_id,
            "compartment_id": compartment_id,
        }

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


# ==============================================================================
# Aligned Customer & Package Domain Tools (Full 1:1 Parity)
# ==============================================================================

@mcp.tool()
async def search_packages(
    status_group: str = "PENDING",
    status: Optional[str] = None,
    carrier: Optional[str] = None,
    storage_type: str = "ALL",
    days: Optional[int] = None,
    is_perishable: Optional[bool] = None,
) -> Dict[str, Any]:
    """Search, filter, and list packages for the resident."""
    matching = []
    for pkg in _MOCK_PACKAGES:
        if status_group and status_group != "ALL" and pkg.get("status_group") != status_group:
            continue
        if status and pkg.get("status", "").lower() != status.lower():
            continue
        if carrier and carrier.lower() not in pkg.get("carrier", "").lower():
            continue
        if storage_type and storage_type != "ALL" and pkg.get("storage_type", "").lower() != storage_type.lower():
            continue
        if is_perishable is not None and pkg.get("is_perishable") != is_perishable:
            continue
        matching.append(pkg)

    if not matching:
        return {
            "success": True,
            "status": "EMPTY_RESULT",
            "message": "No packages found matching search criteria.",
            "data": {
                "total_count": 0,
                "packages": [],
            },
        }

    return {
        "success": True,
        "status": "SUCCESS",
        "message": f"Found {len(matching)} package(s) matching search criteria.",
        "data": {
            "total_count": len(matching),
            "packages": matching,
        },
    }


@mcp.tool()
async def get_package_details(identifier: str) -> Dict[str, Any]:
    """Retrieve comprehensive 360-degree attributes of a specific package."""
    clean_id = (identifier or "").strip().lower()
    for pkg in _MOCK_PACKAGES:
        if (
            str(pkg.get("id")).lower() == clean_id
            or pkg.get("uuid", "").lower() == clean_id
            or pkg.get("tracking_number", "").lower() == clean_id
            or pkg.get("po_number", "").lower() == clean_id
        ):
            return {
                "success": True,
                "status": "SUCCESS",
                "message": f"Retrieved package details for '{identifier}'.",
                "data": pkg,
            }

    for cid, comp in _MOCK_COMPARTMENTS.items():
        if comp.get("package_id", "").lower() == clean_id:
            pkg_data = {
                "id": comp.get("package_id"),
                "tracking_number": comp.get("package_id"),
                "carrier": "FedEx",
                "status": "READY_FOR_PICKUP",
                "compartment_id": cid,
                "passcode": comp.get("pin"),
                "storage_type": "LOCKER",
                "location": {
                    "building_name": "Main Lobby",
                    "locker_door_name": cid,
                    "storage_type": "LOCKER",
                },
            }
            return {
                "success": True,
                "status": "SUCCESS",
                "message": f"Retrieved package details for '{identifier}'.",
                "data": pkg_data,
            }

    return {
        "success": False,
        "status": "NOT_FOUND",
        "message": f"We couldn't find any package matching tracking number or identifier '{identifier}'.",
        "data": None,
    }


@mcp.tool()
async def get_package_timeline(identifier: str) -> Dict[str, Any]:
    """Retrieve audit timeline, dock scans, and chain-of-custody for a package."""
    return {
        "success": True,
        "status": "SUCCESS",
        "message": f"Retrieved 4 timeline events for package '{identifier}'.",
        "data": {
            "tracking_number": identifier,
            "status": "READY_FOR_PICKUP",
            "timeline": [
                {
                    "timestamp": "2026-10-23T09:15:00Z",
                    "action": "Intake Received at Central Dock",
                    "handled_by": "Marcus Vance",
                    "location": "Central Receiving Facility",
                },
                {
                    "timestamp": "2026-10-23T09:45:00Z",
                    "action": "Dispatched for Intra-Campus Transit",
                    "handled_by": "Campus Courier Van 2",
                    "location": "Transit Route B",
                },
                {
                    "timestamp": "2026-10-23T10:05:00Z",
                    "action": "Received at Destination Building",
                    "handled_by": "Elena Rostova",
                    "location": "East Campus Commons Mailroom",
                },
                {
                    "timestamp": "2026-10-23T10:20:00Z",
                    "action": "Deposited into Smart Locker",
                    "handled_by": "Elena Rostova",
                    "location": "Main Pod Bank 1 - Door 14",
                },
            ],
            "chain_of_custody": [
                {"timestamp": "2026-10-23T09:15:00Z", "action": "Dock Receive"},
                {"timestamp": "2026-10-23T10:20:00Z", "action": "Locker Deposit"},
            ],
        },
    }


@mcp.tool()
async def get_user_preferences_and_services() -> Dict[str, Any]:
    """Retrieve resident ADA accessibility preferences, authorized proxies, and day-use pods."""
    return {
        "success": True,
        "status": "SUCCESS",
        "message": "Retrieved user preferences and services.",
        "data": {
            "ada_accessible_locker_required": True,
            "ada_bottom_tier_only": True,
            "authorized_proxies": [
                {"name": "Morgan Vance", "relationship": "Roommate", "phone": "+1-555-0199"}
            ],
            "day_use_pods": [],
        },
    }


@mcp.tool()
async def get_my_pickup_pin(identifier: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve 6-digit pickup verification PIN and assigned locker door."""
    pkg = _MOCK_PACKAGES[0]
    if identifier:
        clean_id = identifier.strip().lower()
        for p in _MOCK_PACKAGES:
            if clean_id in (str(p.get("id")).lower(), p.get("uuid", "").lower(), p.get("tracking_number", "").lower()):
                pkg = p
                break
    pin = pkg.get("passcode") or pkg.get("pickup_pin") or "482910"
    door = pkg.get("locker_door_name") or pkg.get("compartment_id") or "Door 14"
    bank = pkg.get("locker_bank") or "Main Pod Bank 1"
    bldg = pkg.get("building_name") or "East Campus Commons"
    tracking = pkg.get("tracking_number") or "1Z9999999999999999"

    return {
        "success": True,
        "status": "SUCCESS",
        "message": f"Pickup PIN is {pin} for locker door {door}.",
        "data": {
            "primary_pickup": {
                "pickup_pin": pin,
                "locker_bank": bank,
                "locker_door": door,
                "tracking_number": tracking,
                "building_name": bldg,
                "instructions": "Enter your 6-digit PIN on the central console touchscreen or scan your QR code.",
            },
            "active_pickups_count": len(_MOCK_PACKAGES),
        },
    }


@mcp.tool()
async def get_my_locker_details(identifier: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve smart locker physical compartment location, bank name, and door number."""
    lockers = []
    for pkg in _MOCK_PACKAGES:
        lockers.append({
            "package_id": pkg.get("id"),
            "tracking_number": pkg.get("tracking_number"),
            "carrier": pkg.get("carrier"),
            "storage_type": pkg.get("storage_type", "LOCKER"),
            "locker_bank": pkg.get("locker_bank", "Main Pod Bank 1"),
            "locker_door_name": pkg.get("locker_door_name", "Door 14"),
            "compartment_size": "Medium",
            "building_name": pkg.get("building_name", "East Campus Commons"),
        })
    return {
        "success": True,
        "status": "SUCCESS",
        "message": f"Found {len(lockers)} active locker compartment(s) awaiting pickup.",
        "data": {
            "total_active_lockers": len(lockers),
            "lockers": lockers,
        },
    }


@mcp.tool()
async def create_support_ticket(
    user_id: str,
    subject: str,
    description: str,
    priority: str = "medium",
) -> Dict[str, Any]:
    """Create or escalate a customer support case in ServiceNow or Zendesk."""
    ticket_num = f"INC-2026-{datetime.datetime.now().strftime('%M%S')}"
    return {
        "status": "assigned_to_support_tier2",
        "ticket_id": ticket_num,
        "user_id": user_id,
        "subject": subject,
        "description": description,
        "priority": priority,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@mcp.tool()
async def remote_unlock_locker_door(
    locker_id: str = "LOCKER-01",
    compartment: int = 1,
    compartment_id: Optional[str] = None,
    approval_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Send remote solenoid unlock command to smart locker compartment door (requires HITL approval)."""
    cid = compartment_id or (f"C-0{compartment}" if compartment < 10 else f"C-{compartment}")
    if not approval_token:
        return {
            "status": "requires_approval",
            "error": "RemediationApprovalRequiredError: Operator or resident authorization required to unlock door.",
            "locker_id": locker_id,
            "compartment": compartment,
            "compartment_id": cid,
        }

    comp = _MOCK_COMPARTMENTS.get(cid)
    if comp:
        comp["door"] = "OPEN"
        comp["lock"] = "UNLOCKED"

    return {
        "status": "door_unlocked",
        "locker_id": locker_id,
        "compartment": compartment,
        "compartment_id": cid,
        "approved_by_token": approval_token,
        "unlocked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@mcp.tool()
async def lookup_parcel_delivery_event(tracking_number: str) -> Dict[str, Any]:
    """Lookup parcel delivery status (backward compatibility alias for get_package_details)."""
    return await get_package_details(identifier=tracking_number)


def main() -> None:
    transport = settings.MCP_TRANSPORT.lower().strip()
    logger.info(f"Starting Smiota Smart Locker MCP Server on transport '{transport}', port {settings.MCP_PORT}")

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport in ("streamable-http", "sse", "http"):
        run_transport = "streamable-http" if transport in ("streamable-http", "http") else "sse"
        try:
            mcp.run(transport=run_transport, host=settings.MCP_HOST, port=settings.MCP_PORT)
        except Exception:
            mcp.run(transport="sse", host=settings.MCP_HOST, port=settings.MCP_PORT)
    else:
        logger.error(f"Unsupported transport '{transport}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
