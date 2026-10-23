"""Machine-readable MCP Tool Catalog & Traceability Matrix Generator.

Compiles registered MCP tools, schemas, example synthetic payloads, security
requirements, error definitions, and upstream API documentation mappings.
"""
import json
import os
from typing import Any, Dict, List

from smiota.mcp.registry import MCPToolRegistry
from smiota.schemas.mcp import ToolAccessLevel


TOOL_CATALOG_METADATA: Dict[str, Dict[str, Any]] = {
    "search_packages": {
        "version": "1.0.0",
        "category": "Customer Parcel Management",
        "source_api": {
            "endpoint": "/internal/ai/packages",
            "method": "GET",
            "source_document": "smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-1",
            "database_queries": ["Q1", "Q2", "Q4", "Q11", "Q13"],
        },
        "authentication_required": True,
        "authorization_scope": "Resident and Tenant scope derived strictly from session context (CallerContext).",
        "example_valid_arguments": {
            "status_group": "PENDING",
            "carrier": "FedEx",
            "storage_type": "LOCKER",
            "days": 7,
            "is_perishable": False,
        },
        "example_successful_result": {
            "success": True,
            "status": "SUCCESS",
            "message": "Found 1 package(s) matching search criteria.",
            "data": {
                "total_count": 1,
                "packages": [
                    {
                        "id": 10492,
                        "uuid": "8f9a2b10-6a5c-4e89-b1d3-92f7a01d5e34",
                        "tracking_number": "1Z9999999999999999",
                        "carrier": "UPS",
                        "status": "READY_FOR_PICKUP",
                        "received_time": "2026-10-23T09:15:00Z",
                        "passcode": "482910",
                        "location": {
                            "building_name": "East Campus Commons",
                            "storage_type": "LOCKER",
                            "locker_bank": "Main Pod Bank 1",
                            "locker_door_name": "Door 14",
                        },
                    }
                ],
            },
        },
        "possible_errors": [
            "AUTHENTICATION_REQUIRED: Guest user attempting to access private delivery data.",
            "ACCESS_DENIED: Tenant ID mismatch or missing authorization header.",
            "INVALID_INPUT: Invalid carrier name or days outside [0, 365].",
            "RATE_LIMITED: Upstream 429 rate limit reached.",
            "UPSTREAM_TIMEOUT: Upstream package repository exceeded 10s request timeout.",
            "SERVICE_UNAVAILABLE: Upstream 503 maintenance mode.",
        ],
        "test_references": [
            "tests/unit/test_smiota_mcp_tools.py::test_search_packages_success",
            "tests/unit/test_smiota_mcp_security.py::test_search_packages_guest_blocked",
            "tests/integration/test_smiota_api_client.py::test_search_packages_http_request",
        ],
    },
    "get_package_details": {
        "version": "1.0.0",
        "category": "Customer Parcel Management",
        "source_api": {
            "endpoint": "/internal/ai/packages/{identifier}",
            "method": "GET",
            "source_document": "smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-2",
            "database_queries": ["Q3", "Q6", "Q7", "Q8", "Q9", "Q10", "Q16", "Q17"],
        },
        "authentication_required": True,
        "authorization_scope": "Direct object reference protection; recipient ownership validated at DB/API layer.",
        "example_valid_arguments": {
            "identifier": "1Z9999999999999999",
        },
        "example_successful_result": {
            "success": True,
            "status": "SUCCESS",
            "message": "Retrieved package details for '1Z9999999999999999'.",
            "data": {
                "id": 10492,
                "uuid": "8f9a2b10-6a5c-4e89-b1d3-92f7a01d5e34",
                "tracking_number": "1Z9999999999999999",
                "carrier": "UPS",
                "status": "READY_FOR_PICKUP",
                "passcode": "482910",
                "location": {
                    "storage_type": "LOCKER",
                    "building_name": "East Campus Commons",
                    "locker_door_name": "Door 14",
                    "locker_bank": "Main Pod Bank 1",
                },
            },
        },
        "possible_errors": [
            "AUTHENTICATION_REQUIRED: Guest user attempting to access package details.",
            "NOT_FOUND: Tracking number or UUID not found or belongs to another resident.",
            "INVALID_INPUT: Empty identifier or forbidden characters.",
            "UPSTREAM_TIMEOUT: Upstream service exceeded read timeout.",
        ],
        "test_references": [
            "tests/unit/test_smiota_mcp_tools.py::test_get_package_details_success",
            "tests/unit/test_smiota_mcp_tools.py::test_get_package_details_not_found",
            "tests/unit/test_smiota_mcp_security.py::test_get_package_details_guest_blocked",
        ],
    },
    "get_package_timeline": {
        "version": "1.0.0",
        "category": "Customer Parcel Management",
        "source_api": {
            "endpoint": "/internal/ai/packages/{identifier}/timeline",
            "method": "GET",
            "source_document": "smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-3",
            "database_queries": ["Q5", "Q12", "Q14"],
        },
        "authentication_required": True,
        "authorization_scope": "Authorized recipient of the package.",
        "example_valid_arguments": {
            "identifier": "1Z9999999999999999",
        },
        "example_successful_result": {
            "success": True,
            "status": "SUCCESS",
            "message": "Retrieved 3 timeline events for package '1Z9999999999999999'.",
            "data": {
                "tracking_number": "1Z9999999999999999",
                "timeline": [
                    {"event_type": "DOCK_RECEIVE", "timestamp": "2026-10-23T08:30:00Z", "operator": "Dock Agent"},
                    {"event_type": "LOCKER_DEPOSIT", "timestamp": "2026-10-23T09:15:00Z", "location": "Door 14"},
                ],
            },
        },
        "possible_errors": [
            "AUTHENTICATION_REQUIRED: Unauthenticated session.",
            "NOT_FOUND: Package not found in chain-of-custody audit repository.",
            "UPSTREAM_TIMEOUT: Backend lookup timeout.",
        ],
        "test_references": [
            "tests/unit/test_smiota_mcp_tools.py::test_get_package_timeline_success",
            "tests/unit/test_smiota_mcp_security.py::test_get_package_timeline_guest_blocked",
        ],
    },
    "get_user_preferences_and_services": {
        "version": "1.0.0",
        "category": "Resident Profile & Accessibility",
        "source_api": {
            "endpoint": "/internal/ai/users/profile-and-services",
            "method": "GET",
            "source_document": "smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-4",
            "database_queries": ["Q15", "Q18", "Q19", "Q20"],
        },
        "authentication_required": True,
        "authorization_scope": "Authenticated resident profile strictly.",
        "example_valid_arguments": {},
        "example_successful_result": {
            "success": True,
            "status": "SUCCESS",
            "message": "Retrieved resident preferences, proxies, and locker services.",
            "data": {
                "user_id": 10790,
                "first_name": "Alex",
                "last_name": "Morgan",
                "accessibility": {"bottom_tier_lockers_required": True},
                "proxies": [{"name": "Jordan Lee", "relationship": "Roommate"}],
                "active_day_use_lockers": [],
            },
        },
        "possible_errors": [
            "AUTHENTICATION_REQUIRED: Guest user attempting to read profile.",
            "SERVICE_UNAVAILABLE: User profile service down.",
        ],
        "test_references": [
            "tests/unit/test_smiota_mcp_tools.py::test_get_user_preferences_success",
            "tests/unit/test_smiota_mcp_security.py::test_get_user_preferences_guest_blocked",
        ],
    },
    "get_my_pickup_pin": {
        "version": "1.0.0",
        "category": "Customer Parcel Pickup",
        "source_api": {
            "endpoint": "/internal/ai/packages/{identifier} or /internal/ai/packages?status_group=PENDING",
            "method": "GET",
            "source_document": "smiota_ai_consolidated_api_architecture.md",
            "database_queries": ["Q8", "Q17"],
        },
        "authentication_required": True,
        "authorization_scope": "Owner of the pending package.",
        "example_valid_arguments": {
            "identifier": "1Z9999999999999999",
        },
        "example_successful_result": {
            "success": True,
            "status": "SUCCESS",
            "message": "Pickup PIN retrieved successfully.",
            "data": {
                "pickup_pin": "482910",
                "locker_door": "Door 14",
                "locker_bank": "Main Pod Bank 1",
                "building": "East Campus Commons",
                "instructions": "Enter your 6-digit PIN 482910 on the touchscreen console at Main Pod Bank 1.",
            },
        },
        "possible_errors": [
            "AUTHENTICATION_REQUIRED: Guest user requesting pickup PIN.",
            "EMPTY_RESULT: No active packages awaiting pickup.",
        ],
        "test_references": [
            "tests/unit/test_smiota_mcp_tools.py::test_get_my_pickup_pin_success",
            "tests/unit/test_smiota_mcp_security.py::test_get_my_pickup_pin_guest_blocked",
        ],
    },
    "get_my_locker_details": {
        "version": "1.0.0",
        "category": "Smart Locker Navigation",
        "source_api": {
            "endpoint": "/internal/ai/packages/{identifier}",
            "method": "GET",
            "source_document": "smiota_ai_consolidated_api_architecture.md",
            "database_queries": ["Q6", "Q7", "Q9"],
        },
        "authentication_required": True,
        "authorization_scope": "Authenticated resident delivery location.",
        "example_valid_arguments": {},
        "example_successful_result": {
            "success": True,
            "status": "SUCCESS",
            "message": "Found 1 active locker compartment(s) awaiting pickup.",
            "data": {
                "total_active_lockers": 1,
                "lockers": [
                    {
                        "tracking_number": "1Z9999999999999999",
                        "building_name": "East Campus Commons",
                        "locker_bank": "Main Pod Bank 1",
                        "locker_door_name": "Door 14",
                    }
                ],
            },
        },
        "possible_errors": [
            "AUTHENTICATION_REQUIRED: Guest user requesting locker compartment details.",
            "EMPTY_RESULT: No deliveries currently stored in smart lockers.",
        ],
        "test_references": [
            "tests/unit/test_smiota_mcp_tools.py::test_get_my_locker_details_success",
            "tests/unit/test_smiota_mcp_security.py::test_get_my_locker_details_guest_blocked",
        ],
    },
    "query_locker_door_status": {
        "version": "1.0.0",
        "category": "IoT Diagnostics",
        "source_api": {
            "endpoint": "Locker Controller Hardware Telemetry",
            "method": "TELEMETRY_POLL",
            "source_document": "smiota_ai_api_documentation.md",
            "database_queries": [],
        },
        "authentication_required": False,
        "authorization_scope": "Read-only sensor diagnostic state.",
        "example_valid_arguments": {"locker_id": "LK-SF-102", "compartment": 7},
        "example_successful_result": {
            "locker_id": "LK-SF-102",
            "compartment": 7,
            "status": "closed",
            "lock_state": "engaged",
            "battery_pct": 98.4,
        },
        "possible_errors": ["Sensor communication error."],
        "test_references": ["tests/unit/test_smiota_mcp_tools.py::test_query_locker_door_status"],
    },
    "create_support_ticket": {
        "version": "1.0.0",
        "category": "Customer Support Escalation",
        "source_api": {
            "endpoint": "ITSM Service Portal API",
            "method": "POST",
            "source_document": "smiota_ai_api_documentation.md",
            "database_queries": [],
        },
        "authentication_required": False,
        "authorization_scope": "Customer session ticket queue.",
        "example_valid_arguments": {
            "user_id": "10790",
            "subject": "Compartment door latch stuck",
            "description": "Door 14 did not release after entering PIN.",
            "priority": "high",
        },
        "example_successful_result": {
            "ticket_id": "INC-2026-9042",
            "status": "assigned_to_support_tier2",
        },
        "possible_errors": ["Ticketing gateway unreachable."],
        "test_references": ["tests/unit/test_smiota_mcp_tools.py::test_create_support_ticket"],
    },
    "remote_unlock_locker_door": {
        "version": "1.0.0",
        "category": "Physical Remediation (HITL)",
        "source_api": {
            "endpoint": "Locker Controller Solenoid Actuator API",
            "method": "COMMAND_UNLOCK",
            "source_document": "smiota_ai_api_documentation.md",
            "database_queries": [],
        },
        "authentication_required": True,
        "authorization_scope": "Human-in-the-loop (HITL) approval token required.",
        "example_valid_arguments": {
            "locker_id": "LK-SF-102",
            "compartment": 7,
            "approval_token": "MGR-APPROVAL-TOKEN-8831",
        },
        "example_successful_result": {
            "status": "door_unlocked",
            "locker_id": "LK-SF-102",
            "compartment": 7,
            "approved_by_token": "MGR-APPROVAL-TOKEN-8831",
        },
        "possible_errors": [
            "RemediationApprovalRequiredError: Execution blocked without cryptographic approval token.",
        ],
        "test_references": [
            "tests/unit/test_smiota_mcp_security.py::test_remote_unlock_requires_approval",
            "tests/unit/test_smiota_mcp_security.py::test_remote_unlock_with_valid_token",
        ],
    },
}

BLOCKED_OR_UNIMPLEMENTED_OPERATIONS = [
    {
        "operation_name": "direct_carrier_return_label_generation",
        "reason": "Upstream carrier outbound return label generation API requires warehouse dispatcher credentials and binary PDF thermal print streams not exposed to resident AI session.",
        "source_document": "smiota_ai_consolidated_api_architecture.md",
        "status": "BLOCKED",
    },
    {
        "operation_name": "arbitrary_sql_execution",
        "reason": "Prohibited by architectural design. Raw database query execution from customer-facing agent violates the security boundary and multi-tenant isolation.",
        "source_document": "smiota_database_queries_catalog.md",
        "status": "PROHIBITED",
    },
    {
        "operation_name": "modify_resident_proxy_delegates",
        "reason": "State-changing resident profile and proxy mutation requires MFA-authenticated web portal flow; internal API contract /internal/ai/users/profile-and-services is strictly read-only.",
        "source_document": "smiota_ai_consolidated_api_architecture.md",
        "status": "UNIMPLEMENTED_READ_ONLY_BOUNDARY",
    },
    {
        "operation_name": "remote_firmware_update",
        "reason": "Hardware firmware operations are administrative capabilities reserved for internal SREs and excluded from customer AI agent scope.",
        "source_document": "smiota_ai_api_documentation.md",
        "status": "EXCLUDED_PRIVILEGED",
    },
]


def generate_tool_catalog() -> Dict[str, Any]:
    """Generate complete structured tool catalog from registered definitions and metadata."""
    tools = []
    registered_defs = {d.name: d for d in MCPToolRegistry.list_tools()}

    for name, meta in TOOL_CATALOG_METADATA.items():
        definition = registered_defs.get(name)
        input_schema = definition.input_schema if definition else {}
        access_level = definition.access_level.value if definition else "read_only"
        description = definition.description if definition else ""

        tools.append({
            "name": name,
            "version": meta["version"],
            "category": meta["category"],
            "access_level": access_level,
            "description": description,
            "input_schema": input_schema,
            "source_api": meta["source_api"],
            "authentication_required": meta["authentication_required"],
            "authorization_scope": meta["authorization_scope"],
            "example_valid_arguments": meta["example_valid_arguments"],
            "example_successful_result": meta["example_successful_result"],
            "possible_errors": meta["possible_errors"],
            "test_references": meta["test_references"],
        })

    return {
        "title": "Smiota Customer AI MCP Tool Catalog & Traceability Matrix",
        "schema_version": "1.0.0",
        "total_implemented_tools": len(tools),
        "tools": tools,
        "blocked_and_unimplemented_operations": BLOCKED_OR_UNIMPLEMENTED_OPERATIONS,
    }


def export_catalog_files(docs_dir: str) -> None:
    """Write mcp_tool_catalog.json and mcp_tool_catalog.md to docs_dir."""
    os.makedirs(docs_dir, exist_ok=True)
    catalog = generate_tool_catalog()

    # 1. JSON
    json_path = os.path.join(docs_dir, "mcp_tool_catalog.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    # 2. Markdown
    md_path = os.path.join(docs_dir, "mcp_tool_catalog.md")
    lines = [
        "# Smiota Customer AI MCP Tool Catalog & Traceability Matrix",
        "",
        "This document provides the authoritative, machine-verified catalog of MCP tools exposed to the Smiota Customer AI agent, traceable to underlying internal Smiota Server APIs and database catalogs.",
        "",
        "## Summary of Implemented Tools",
        "",
        "| Tool Name | Access Level | Upstream Endpoint | Source Document | Auth Required |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for tool in catalog["tools"]:
        src = f"`{tool['source_api']['method']} {tool['source_api']['endpoint']}`"
        lines.append(
            f"| `{tool['name']}` | `{tool['access_level']}` | {src} | {tool['source_api']['source_document']} | {tool['authentication_required']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Detailed Tool Specifications",
        "",
    ])

    for tool in catalog["tools"]:
        lines.extend([
            f"### Tool: `{tool['name']}` (v{tool['version']})",
            "",
            f"- **Category:** {tool['category']}",
            f"- **Access Level:** `{tool['access_level']}`",
            f"- **Authentication Required:** `{tool['authentication_required']}`",
            f"- **Authorization Scope:** {tool['authorization_scope']}",
            f"- **Upstream Source API:** `{tool['source_api']['method']} {tool['source_api']['endpoint']}`",
            f"- **Source Reference:** `{tool['source_api']['source_document']}`",
            "",
            "#### Description",
            "```text",
            tool["description"],
            "```",
            "",
            "#### Input Schema",
            "```json",
            json.dumps(tool["input_schema"], indent=2),
            "```",
            "",
            "#### Example Arguments",
            "```json",
            json.dumps(tool["example_valid_arguments"], indent=2),
            "```",
            "",
            "#### Example Successful Result",
            "```json",
            json.dumps(tool["example_successful_result"], indent=2),
            "```",
            "",
            "#### Possible Errors",
        ])
        for err in tool["possible_errors"]:
            lines.append(f"- `{err}`")

        lines.extend([
            "",
            "#### Test References",
        ])
        for t in tool["test_references"]:
            lines.append(f"- `{t}`")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Blocked & Unimplemented Operations",
        "",
        "The following operations are documented in the system catalogs but are deliberately excluded, blocked, or deferred from exposure to the customer-facing AI agent:",
        "",
        "| Operation Name | Status | Justification / Security Boundary | Source Document |",
        "| :--- | :--- | :--- | :--- |",
    ])

    for blocked in catalog["blocked_and_unimplemented_operations"]:
        lines.append(
            f"| `{blocked['operation_name']}` | `{blocked['status']}` | {blocked['reason']} | `{blocked['source_document']}` |"
        )

    lines.append("")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    import smiota.mcp.servers.customer.tools  # Register tools
    export_catalog_files("d:/repos/smiota-ai/src/smiota/docs")
