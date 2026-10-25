"""Official Smiota Package Status Catalog, Lifecycle Enums, and Normalization.

Defines the complete canonical list of package statuses used across Smiota
Smart Locker systems, Mailroom operations, and Internal AI endpoints.
"""
from __future__ import annotations

import re
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class PackageLifecycleGroup(str, Enum):
    """Broad lifecycle groupings for Smiota packages."""
    PENDING = "PENDING"          # Awaiting pickup / active intake in building or locker
    RELEASED = "RELEASED"        # Successfully collected by resident or proxy
    OUTBOUND = "OUTBOUND"        # Outbound shipping, returns, or sent back
    IN_TRANSIT = "IN_TRANSIT"    # Moving between hub, warehouse, mailroom, or pod
    HOLD = "HOLD"                # Vacation hold, perishable pause, or admin hold
    EXCEPTION = "EXCEPTION"      # Under research, label discrepancy, or delivery failure
    ALL = "ALL"                  # All lifecycle phases


class PackageStatus(str, Enum):
    """Canonical Smiota package status values."""
    PICKUP_REQUEST_SUBMITTED = "pickup_request_submitted"
    RECEIVED = "received"
    DELIVERED_TO_STATION = "delivered_to_station"
    RELEASED = "released"
    SENT_BACK = "sent back"
    ATTEMPTED_TO_DELIVER = "attempted to deliver"
    COURIER_TO_MAILROOM = "courier to mailroom"
    IN_TRANSIT = "in transit"
    RETURN_TO_HUB = "return to hub"
    READY_TO_SHIP = "Ready to Ship"
    IN_TRANSIT_TO_WAREHOUSE = "In Transit to Warehouse"
    IN_TRANSIT_TO_POD = "In Transit to Pod"
    HOLD = "Hold"
    IN_WAREHOUSE = "In Warehouse"
    RESEARCH = "Research"
    TRANSFERRED = "Transferred"
    # Live backend alias for ingested/staged parcels
    PROCESSED = "Processed"


class PackageStatusDefinition(BaseModel):
    """Metadata describing a specific Smiota package status."""
    canonical_key: str
    display_name: str
    status_group: PackageLifecycleGroup
    is_collectible_now: bool = False
    customer_summary: str
    resident_guidance: str
    icon: str = "📦"


PACKAGE_STATUS_CATALOG: Dict[str, PackageStatusDefinition] = {
    "pickup_request_submitted": PackageStatusDefinition(
        canonical_key="pickup_request_submitted",
        display_name="Pickup Request Submitted",
        status_group=PackageLifecycleGroup.PENDING,
        is_collectible_now=False,
        customer_summary="Pickup request has been logged by resident or sender.",
        resident_guidance="Your pickup request has been received. Mailroom staff or carrier courier will collect the package soon.",
        icon="📋",
    ),
    "received": PackageStatusDefinition(
        canonical_key="received",
        display_name="Received",
        status_group=PackageLifecycleGroup.PENDING,
        is_collectible_now=False,
        customer_summary="Arrived at property; intake scan complete.",
        resident_guidance="Package has been received at the facility. It is currently being prepped for locker loading or shelf placement.",
        icon="📥",
    ),
    "delivered_to_station": PackageStatusDefinition(
        canonical_key="delivered_to_station",
        display_name="Delivered to Station",
        status_group=PackageLifecycleGroup.PENDING,
        is_collectible_now=True,
        customer_summary="Delivered and ready at smart locker kiosk or station.",
        resident_guidance="Your package is ready for collection at your locker bank or station.",
        icon="✅",
    ),
    "released": PackageStatusDefinition(
        canonical_key="released",
        display_name="Released",
        status_group=PackageLifecycleGroup.RELEASED,
        is_collectible_now=False,
        customer_summary="Package has been picked up and released.",
        resident_guidance="This package was already collected by you or an authorized proxy.",
        icon="🚪",
    ),
    "sent_back": PackageStatusDefinition(
        canonical_key="sent back",
        display_name="Sent Back",
        status_group=PackageLifecycleGroup.OUTBOUND,
        is_collectible_now=False,
        customer_summary="Package was returned to sender.",
        resident_guidance="This parcel was sent back to the sender (e.g. expired hold period or undeliverable). Contact support if unexpected.",
        icon="↩️",
    ),
    "attempted_to_deliver": PackageStatusDefinition(
        canonical_key="attempted to deliver",
        display_name="Attempted to Deliver",
        status_group=PackageLifecycleGroup.PENDING,
        is_collectible_now=False,
        customer_summary="Delivery was attempted but could not be completed.",
        resident_guidance="Delivery was attempted (e.g., lockers currently full). Mailroom staff will re-attempt delivery or place it on shelf.",
        icon="⚠️",
    ),
    "courier_to_mailroom": PackageStatusDefinition(
        canonical_key="courier to mailroom",
        display_name="Courier to Mailroom",
        status_group=PackageLifecycleGroup.IN_TRANSIT,
        is_collectible_now=False,
        customer_summary="Carrier courier handed parcel over to mailroom.",
        resident_guidance="Carrier courier handed over the parcel to building staff; pending intake and shelf/locker allocation.",
        icon="🚚",
    ),
    "in_transit": PackageStatusDefinition(
        canonical_key="in transit",
        display_name="In Transit",
        status_group=PackageLifecycleGroup.IN_TRANSIT,
        is_collectible_now=False,
        customer_summary="En route between campus buildings or facilities.",
        resident_guidance="Your package is currently in transit between campus facilities.",
        icon="🚚",
    ),
    "return_to_hub": PackageStatusDefinition(
        canonical_key="return to hub",
        display_name="Return to Hub",
        status_group=PackageLifecycleGroup.IN_TRANSIT,
        is_collectible_now=False,
        customer_summary="Routing back to central mailroom hub.",
        resident_guidance="Package is en route back to the central mailroom hub for re-sorting or customer assistance.",
        icon="🔄",
    ),
    "ready_to_ship": PackageStatusDefinition(
        canonical_key="Ready to Ship",
        display_name="Ready to Ship",
        status_group=PackageLifecycleGroup.OUTBOUND,
        is_collectible_now=False,
        customer_summary="Outbound package staged for carrier dispatch.",
        resident_guidance="Outbound shipment is packaged and awaiting carrier courier pickup.",
        icon="🏷️",
    ),
    "in_transit_to_warehouse": PackageStatusDefinition(
        canonical_key="In Transit to Warehouse",
        display_name="In Transit to Warehouse",
        status_group=PackageLifecycleGroup.IN_TRANSIT,
        is_collectible_now=False,
        customer_summary="En route to central distribution warehouse.",
        resident_guidance="Package is in transit to the central warehouse distribution center.",
        icon="🚛",
    ),
    "in_transit_to_pod": PackageStatusDefinition(
        canonical_key="In Transit to Pod",
        display_name="In Transit to Pod",
        status_group=PackageLifecycleGroup.IN_TRANSIT,
        is_collectible_now=False,
        customer_summary="En route to designated smart locker pod.",
        resident_guidance="Your parcel is being transported directly to your locker pod. You will receive a pickup PIN as soon as it is loaded.",
        icon="📦",
    ),
    "hold": PackageStatusDefinition(
        canonical_key="Hold",
        display_name="Hold",
        status_group=PackageLifecycleGroup.HOLD,
        is_collectible_now=False,
        customer_summary="Placed on temporary hold.",
        resident_guidance="Your package is currently on hold (vacation hold or admin hold). Contact the mailroom or your portal to release.",
        icon="⏸️",
    ),
    "in_warehouse": PackageStatusDefinition(
        canonical_key="In Warehouse",
        display_name="In Warehouse",
        status_group=PackageLifecycleGroup.PENDING,
        is_collectible_now=False,
        customer_summary="Stored at central sorting warehouse.",
        resident_guidance="Stored at the central warehouse and queued for delivery to your building.",
        icon="🏢",
    ),
    "research": PackageStatusDefinition(
        canonical_key="Research",
        display_name="Research",
        status_group=PackageLifecycleGroup.EXCEPTION,
        is_collectible_now=False,
        customer_summary="Staff investigating label, name, or unit discrepancy.",
        resident_guidance="Mailroom staff are researching this package (e.g. verifying recipient name or damaged barcode). They will resolve it shortly.",
        icon="🔍",
    ),
    "transferred": PackageStatusDefinition(
        canonical_key="Transferred",
        display_name="Transferred",
        status_group=PackageLifecycleGroup.IN_TRANSIT,
        is_collectible_now=False,
        customer_summary="Transferred to alternate facility or locker bank.",
        resident_guidance="Package was transferred to another building, overflow room, or locker bank. Check your notification for the updated pickup point.",
        icon="🔀",
    ),
    "processed": PackageStatusDefinition(
        canonical_key="Processed",
        display_name="Processed",
        status_group=PackageLifecycleGroup.PENDING,
        is_collectible_now=True,
        customer_summary="Processed and staged on shelf or locker.",
        resident_guidance="Your package has been processed and is ready for pickup on shelf or at your smart locker.",
        icon="📦",
    ),
}


def normalize_status_key(status: Optional[str]) -> str:
    """Normalize arbitrary status strings into standard canonical lookup key."""
    if not status:
        return ""
    # Strip, lowercase, replace spaces/dashes with underscores
    s = status.strip().lower()
    s = re.sub(r"[\s-]+", "_", s)
    return s


def get_status_definition(status: Optional[str]) -> Optional[PackageStatusDefinition]:
    """Retrieve detailed metadata for any raw status string."""
    if not status:
        return None
    key = normalize_status_key(status)
    return PACKAGE_STATUS_CATALOG.get(key)


def get_status_resident_explanation(status: Optional[str]) -> str:
    """Return a polite, helpful explanation of a package status for a resident."""
    defn = get_status_definition(status)
    if defn:
        return f"{defn.icon} **{defn.display_name}**: {defn.resident_guidance}"
    return f"**{status}**: Contact mailroom staff if you need assistance with this delivery."
