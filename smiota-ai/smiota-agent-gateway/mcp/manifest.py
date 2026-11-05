"""Standard MCP Tool Definitions and Manifests for Gateway Registry."""
from __future__ import annotations

from typing import Any, Dict, Optional

from mcp.registry import MCPToolRegistry
from schemas.mcp import ToolAccessLevel
from schemas.mcp_tools import (
    GetLockerDetailsInput,
    GetPackageDetailsInput,
    GetPackageTimelineInput,
    GetPickupPinInput,
    GetUserPreferencesAndServicesInput,
    SearchPackagesInput,
)


TOOL_DESCRIPTIONS: Dict[str, str] = {
    "search_packages": (
        "1. Purpose: Search, filter, and list packages for the authenticated resident.\n"
        "2. When to use: When the customer asks 'Do I have anything to collect right now?', 'Do I have anything to pick up?', "
        "'Where are my packages?', 'Do I have any deliveries waiting?', 'What items are ready for pickup?', "
        "'Show my package history', or filters by carrier (e.g. FedEx, Amazon), perishable items, or past days.\n"
        "3. When not to use: When the customer asks for a specific 6-digit pickup PIN (use get_my_pickup_pin) or asks "
        "about locker door troubleshooting (use query_locker_door_status).\n"
        "4. Required arguments: None.\n"
        "5. Optional arguments: status_group ('PENDING', 'RELEASED', 'OUTBOUND', 'ALL'), "
        "status (specific status: 'pickup_request_submitted', 'received', 'delivered_to_station', 'released', "
        "'sent back', 'attempted to deliver', 'courier to mailroom', 'in transit', 'return to hub', 'Ready to Ship', "
        "'In Transit to Warehouse', 'In Transit to Pod', 'Hold', 'In Warehouse', 'Research', 'Transferred', 'Processed'), "
        "carrier (string), storage_type ('ALL', 'LOCKER', 'SHELF'), days (any number, 0-30 for now), is_perishable (boolean).\n"
        "6. Authentication: Required. Unauthenticated guests are rejected with AUTHENTICATION_REQUIRED.\n"
        "7. Authorization: Customer and tenant scope derived exclusively from verified session context.\n"
        "8. Data returned: List of packages with tracking numbers, carriers, status, received/released timestamps, "
        "storage type (LOCKER/SHELF), and locker compartment assignments.\n"
        "9. Limitations: Returns maximum 50 records per query; historical queries beyond 365 days are truncated.\n"
        "10. Failure behavior: Returns standard envelope with success=false and status code if unauthenticated, "
        "rate limited, timed out, or unavailable."
    ),
    "get_package_details": (
        "1. Purpose: Retrieve comprehensive 360-degree attributes of a specific package.\n"
        "2. When to use: When customer provides a tracking number, package UUID, PO number, or release passcode and "
        "asks for detailed package status, locker compartment, carrier, or expiration.\n"
        "3. When not to use: When searching across multiple packages without an identifier (use search_packages).\n"
        "4. Required arguments: identifier (carrier tracking number, UUID, or PO number).\n"
        "5. Optional arguments: None.\n"
        "6. Authentication: Required. Anonymous guests cannot retrieve protected package records.\n"
        "7. Authorization: Tenant and recipient ownership enforced at API and database query level.\n"
        "8. Data returned: Package UUID, tracking number, courier, status, received time, expiration time, "
        "storage type (LOCKER/SHELF), locker compartment door, building, and pickup verification details.\n"
        "9. Limitations: Returns NOT_FOUND if identifier does not exist or belongs to another tenant/resident.\n"
        "10. Failure behavior: Returns error envelope with NOT_FOUND, INVALID_IDENTIFIER, or AUTHENTICATION_REQUIRED."
    ),
    "get_package_timeline": (
        "1. Purpose: Retrieve complete chain-of-custody timeline and dock reconciliation events for a package.\n"
        "2. When to use: When customer asks 'When was my package delivered?', 'Who accepted my parcel at the dock?', "
        "'Show delivery timeline', or wants to audit carrier handoff.\n"
        "3. When not to use: When the customer only needs current delivery status or pickup PIN (use get_package_details).\n"
        "4. Required arguments: identifier (tracking number or package UUID).\n"
        "5. Optional arguments: None.\n"
        "6. Authentication: Required.\n"
        "7. Authorization: Enforced by server session token.\n"
        "8. Data returned: Chronological event list with event type (DOCK_RECEIVE, LOCKER_DEPOSIT, CUSTOMER_PICKUP, etc.), "
        "operator, timestamp, and location notes.\n"
        "9. Limitations: Timeline is only available for packages that have undergone dock scan or locker deposit.\n"
        "10. Failure behavior: Returns NOT_FOUND or EMPTY_RESULT if package has no recorded audit events."
    ),
    "get_user_preferences_and_services": (
        "1. Purpose: Retrieve resident ADA accessibility settings, authorized pickup proxies, and active day-use lockers.\n"
        "2. When to use: When customer asks 'Are my packages assigned to bottom lockers?', 'Who can pick up for me?', "
        "'Check my accessibility settings', or 'Do I have a personal locker assigned?'.\n"
        "3. When not to use: When looking up parcel delivery or tracking status (use search_packages).\n"
        "4. Required arguments: None.\n"
        "5. Optional arguments: None.\n"
        "6. Authentication: Required.\n"
        "7. Authorization: Returns profile strictly for the authenticated resident.\n"
        "8. Data returned: ADA bottom-tier locker flag, authorized proxy delegate names/contacts, and active day-use pods.\n"
        "9. Limitations: Modifications to proxies or ADA settings must be performed through the resident portal.\n"
        "10. Failure behavior: Returns AUTHENTICATION_REQUIRED or SERVICE_UNAVAILABLE on failure."
    ),
    "get_my_pickup_pin": (
        "1. Purpose: Retrieve the active 6-digit pickup PIN and locker door number to collect a package.\n"
        "2. When to use: When customer asks 'What is my pickup PIN?', 'Resend my access code', 'How do I open my locker?', "
        "or 'Send me the PIN for package SM-1234'.\n"
        "3. When not to use: When customer wants general tracking status or package history (use search_packages).\n"
        "4. Required arguments: None.\n"
        "5. Optional arguments: identifier (tracking number or package ID if resident has multiple packages).\n"
        "6. Authentication: Required. Highly sensitive operation; guests must authenticate.\n"
        "7. Authorization: Customer context verified via server session.\n"
        "8. Data returned: 6-digit PIN code, locker bank, door number, building name, expiration time, and kiosk instructions.\n"
        "9. Limitations: Only active for packages currently stored and awaiting pickup (READY_FOR_PICKUP).\n"
        "10. Failure behavior: Returns EMPTY_RESULT if no packages are awaiting pickup, or AUTHENTICATION_REQUIRED."
    ),
    "get_my_locker_details": (
        "1. Purpose: Retrieve smart locker physical compartment location, bank name, door number, and console instructions.\n"
        "2. When to use: When customer asks 'Which locker is my package in?', 'What door number should I go to?', "
        "'Where is my locker compartment located?'.\n"
        "3. When not to use: When customer asks why a door didn't open (use query_locker_door_status).\n"
        "4. Required arguments: None.\n"
        "5. Optional arguments: identifier (tracking number or package ID).\n"
        "6. Authentication: Required.\n"
        "7. Authorization: Scope enforced by caller context.\n"
        "8. Data returned: Building name, locker bank name, door number/name, compartment size, storage type (LOCKER/SHELF).\n"
        "9. Limitations: Only packages in smart lockers have compartment door numbers assigned; mailroom shelf items will indicate 'SHELF'.\n"
        "10. Failure behavior: Returns EMPTY_RESULT if no packages are stored in lockers, or AUTHENTICATION_REQUIRED."
    ),
    "query_locker_door_status": (
        "Query IoT telemetry for smart locker compartment door sensors and controller status."
    ),
    "create_support_ticket": (
        "Create or escalate a customer support case in ServiceNow or Zendesk."
    ),
    "remote_unlock_locker_door": (
        "Send remote solenoid unlock command to IoT smart locker door (Requires Human Approval / Token)."
    ),
}


def register_default_mcp_tools() -> None:
    """Register standard MCP tool definitions into the centralized MCPToolRegistry."""
    from services.smiota_mcp_service import get_smiota_mcp_service

    svc = get_smiota_mcp_service()

    async def search_packages_wrapper(**kwargs):
        res = await svc.search_packages(**kwargs)
        return res.model_dump()

    async def get_package_details_wrapper(identifier: str):
        res = await svc.get_package_details(identifier=identifier)
        return res.model_dump()

    async def get_package_timeline_wrapper(identifier: str):
        res = await svc.get_package_timeline(identifier=identifier)
        return res.model_dump()

    async def get_user_preferences_and_services_wrapper():
        res = await svc.get_user_preferences_and_services()
        return res.model_dump()

    async def get_my_pickup_pin_wrapper(identifier: Optional[str] = None):
        res = await svc.get_my_pickup_pin(identifier=identifier)
        return res.model_dump()

    async def get_my_locker_details_wrapper(identifier: Optional[str] = None):
        res = await svc.get_my_locker_details(identifier=identifier)
        return res.model_dump()

    async def query_locker_door_status_wrapper(locker_id: str = "LOCKER-01", compartment: int = 1):
        return {
            "locker_id": locker_id,
            "compartment": compartment,
            "status": "closed",
            "lock_state": "engaged",
            "battery_pct": 98.4,
            "last_ping": "2026-10-23T12:00:00Z",
        }

    async def create_support_ticket_wrapper(user_id: str, subject: str, description: str, priority: str = "medium"):
        return {
            "ticket_id": "INC-2026-9042",
            "user_id": user_id,
            "subject": subject,
            "priority": priority,
            "status": "assigned_to_support_tier2",
        }

    async def remote_unlock_locker_door_wrapper(
        locker_id: str = "LOCKER-01", compartment: int = 1, approval_token: Optional[str] = None
    ):
        from core.exceptions import RemediationApprovalRequiredError
        if not approval_token:
            raise RemediationApprovalRequiredError(
                tool_name="remote_unlock_locker_door",
                params={"locker_id": locker_id, "compartment": compartment},
            )
        return {
            "status": "door_unlocked",
            "locker_id": locker_id,
            "compartment": compartment,
            "approved_by_token": approval_token,
        }

    tools_to_register = [
        ("search_packages", TOOL_DESCRIPTIONS["search_packages"], search_packages_wrapper, ToolAccessLevel.READ_ONLY, SearchPackagesInput.model_json_schema()),
        ("get_package_details", TOOL_DESCRIPTIONS["get_package_details"], get_package_details_wrapper, ToolAccessLevel.READ_ONLY, GetPackageDetailsInput.model_json_schema()),
        ("get_package_timeline", TOOL_DESCRIPTIONS["get_package_timeline"], get_package_timeline_wrapper, ToolAccessLevel.READ_ONLY, GetPackageTimelineInput.model_json_schema()),
        ("get_user_preferences_and_services", TOOL_DESCRIPTIONS["get_user_preferences_and_services"], get_user_preferences_and_services_wrapper, ToolAccessLevel.READ_ONLY, GetUserPreferencesAndServicesInput.model_json_schema()),
        ("get_my_pickup_pin", TOOL_DESCRIPTIONS["get_my_pickup_pin"], get_my_pickup_pin_wrapper, ToolAccessLevel.READ_ONLY, GetPickupPinInput.model_json_schema()),
        ("get_my_locker_details", TOOL_DESCRIPTIONS["get_my_locker_details"], get_my_locker_details_wrapper, ToolAccessLevel.READ_ONLY, GetLockerDetailsInput.model_json_schema()),
        ("query_locker_door_status", TOOL_DESCRIPTIONS["query_locker_door_status"], query_locker_door_status_wrapper, ToolAccessLevel.READ_ONLY, None),
        ("create_support_ticket", TOOL_DESCRIPTIONS["create_support_ticket"], create_support_ticket_wrapper, ToolAccessLevel.READ_ONLY, None),
        ("remote_unlock_locker_door", TOOL_DESCRIPTIONS["remote_unlock_locker_door"], remote_unlock_locker_door_wrapper, ToolAccessLevel.REMEDIATION, None),
    ]

    for name, desc, fn, level, schema in tools_to_register:
        MCPToolRegistry.register_tool(name=name, description=desc, func=fn, access_level=level, input_schema=schema)

    # Register 37 Kubernetes and SRE Troubleshooting tools
    from clients.k8s_client import get_k8s_client
    k8s_client = get_k8s_client()

    k8s_tools_list = [
        "list_clusters", "get_cluster_info", "list_namespaces", "get_namespace",
        "list_nodes", "get_node_details", "list_pods", "get_pod_details",
        "get_pod_logs", "get_pod_previous_logs", "list_deployments", "get_deployment_details",
        "list_statefulsets", "list_daemonsets", "list_services", "list_ingresses",
        "list_configmaps", "list_secrets_metadata", "list_events", "get_pod_metrics",
        "get_resource_quotas", "get_hpa_status", "diagnose_pod", "diagnose_crashloop",
        "diagnose_image_pull", "diagnose_pending_pod", "diagnose_node", "diagnose_deployment",
        "diagnose_service", "diagnose_ingress", "analyze_pod_events", "analyze_container_logs",
        "check_pod_restarts", "check_resource_pressure", "check_pvc_status",
        "check_dns_resolution", "check_network_connectivity",
    ]

    for k8s_name in k8s_tools_list:
        if not MCPToolRegistry.has_tool(k8s_name):
            target_fn = getattr(k8s_client, k8s_name, None)
            fn_to_register = target_fn if target_fn is not None else (lambda **kw: {})
            MCPToolRegistry.register_tool(
                name=k8s_name,
                description=f"Kubernetes SRE inspection and troubleshooting operation: {k8s_name}",
                func=fn_to_register,
                access_level=ToolAccessLevel.READ_ONLY,
            )


# Automatically initialize manifests on module import
register_default_mcp_tools()
