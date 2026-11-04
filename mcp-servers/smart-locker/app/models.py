"""Data schemas for Smart Locker MCP Server."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CompartmentInfo(BaseModel):
    compartment_id: str
    size: str = "M"  # S, M, L, XL
    door_state: str = "CLOSED"  # OPEN, CLOSED
    lock_state: str = "LOCKED"  # LOCKED, UNLOCKED
    occupied: bool = False
    temperature_zone: str = "ambient"  # ambient, refrigerated, frozen
    current_temperature_f: Optional[float] = None
    assigned_package_id: Optional[str] = None


class LockerStatusResponse(BaseModel):
    locker_id: str
    status: str = "ONLINE"  # ONLINE, OFFLINE, MAINTENANCE
    network_connection: str = "ETHERNET"
    battery_backup_status: str = "CHARGED"
    battery_level_percent: int = 100
    total_compartments: int = 24
    compartments_free: int = 14
    temperature_zones: Dict[str, Any] = Field(
        default_factory=lambda: {
            "ambient": {"compartments": 16, "status": "NOMINAL"},
            "refrigerated": {"compartments": 8, "status": "NOMINAL", "current_temp_f": 38.0},
        }
    )

