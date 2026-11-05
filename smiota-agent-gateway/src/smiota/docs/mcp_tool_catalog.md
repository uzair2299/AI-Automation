# Smiota Customer AI MCP Tool Catalog & Traceability Matrix

This document provides the authoritative, machine-verified catalog of MCP tools exposed to the Smiota Customer AI agent, traceable to underlying internal Smiota Server APIs and database catalogs.

## Summary of Implemented Tools

| Tool Name | Access Level | Upstream Endpoint | Source Document | Auth Required |
| :--- | :--- | :--- | :--- | :--- |
| `search_packages` | `read_only` | `GET /internal/ai/packages` | smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-1 | True |
| `get_package_details` | `read_only` | `GET /internal/ai/packages/{identifier}` | smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-2 | True |
| `get_package_timeline` | `read_only` | `GET /internal/ai/packages/{identifier}/timeline` | smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-3 | True |
| `get_user_preferences_and_services` | `read_only` | `GET /internal/ai/users/profile-and-services` | smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-4 | True |
| `get_my_pickup_pin` | `read_only` | `GET /internal/ai/packages/{identifier} or /internal/ai/packages?status_group=PENDING` | smiota_ai_consolidated_api_architecture.md | True |
| `get_my_locker_details` | `read_only` | `GET /internal/ai/packages/{identifier}` | smiota_ai_consolidated_api_architecture.md | True |
| `query_locker_door_status` | `read_only` | `TELEMETRY_POLL Locker Controller Hardware Telemetry` | smiota_ai_api_documentation.md | False |
| `create_support_ticket` | `read_only` | `POST ITSM Service Portal API` | smiota_ai_api_documentation.md | False |
| `remote_unlock_locker_door` | `remediation` | `COMMAND_UNLOCK Locker Controller Solenoid Actuator API` | smiota_ai_api_documentation.md | True |

---

## Detailed Tool Specifications

### Tool: `search_packages` (v1.0.0)

- **Category:** Customer Parcel Management
- **Access Level:** `read_only`
- **Authentication Required:** `True`
- **Authorization Scope:** Resident and Tenant scope derived strictly from session context (CallerContext).
- **Upstream Source API:** `GET /internal/ai/packages`
- **Source Reference:** `smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-1`

#### Description
```text
1. Purpose: Search, filter, and list packages for the authenticated resident.
2. When to use: When the customer asks 'Where are my packages?', 'Do I have any deliveries waiting?', 'Show my package history', or filters by carrier (e.g. FedEx, Amazon), perishable items, or past days.
3. When not to use: When the customer asks for a specific 6-digit pickup PIN (use get_my_pickup_pin) or asks about locker door troubleshooting (use query_locker_door_status).
4. Required arguments: None.
5. Optional arguments: status_group ('PENDING', 'RELEASED', 'OUTBOUND', 'ALL'), carrier (string), storage_type ('ALL', 'LOCKER', 'SHELF'), days (0-365), is_perishable (boolean).
6. Authentication: Required. Unauthenticated guests are rejected with AUTHENTICATION_REQUIRED.
7. Authorization: Customer and tenant scope derived exclusively from verified session context.
8. Data returned: List of packages with tracking numbers, carriers, status, received/released timestamps, and locker compartment assignments.
9. Limitations: Returns maximum 50 records per query; historical queries beyond 365 days are truncated.
10. Failure behavior: Returns standard envelope with success=false and status code if unauthenticated, rate limited, timed out, or unavailable.
```

#### Input Schema
```json
{
  "description": "Input parameters for searching and summarizing packages.",
  "properties": {
    "status_group": {
      "anyOf": [
        {
          "enum": [
            "PENDING",
            "RELEASED",
            "OUTBOUND",
            "ALL"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "PENDING",
      "description": "Filter by package lifecycle group: PENDING (awaiting pickup), RELEASED (collected history), OUTBOUND (returns), ALL.",
      "title": "Status Group"
    },
    "carrier": {
      "anyOf": [
        {
          "maxLength": 50,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional carrier filter (e.g., 'Amazon', 'FedEx', 'UPS', 'USPS', 'DHL'). Substring match.",
      "title": "Carrier"
    },
    "storage_type": {
      "anyOf": [
        {
          "enum": [
            "ALL",
            "LOCKER",
            "SHELF"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "ALL",
      "description": "Filter by storage location: 'LOCKER' (smart locker compartment), 'SHELF' (mailroom shelf/counter), or 'ALL'.",
      "title": "Storage Type"
    },
    "days": {
      "anyOf": [
        {
          "maximum": 365,
          "minimum": 0,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Historical lookback window in days (e.g. 0 for today, 30 for past month, 90 for past quarter). Maximum 365.",
      "title": "Days"
    },
    "is_perishable": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Filter for temperature-sensitive / cold storage / grocery items.",
      "title": "Is Perishable"
    }
  },
  "title": "SearchPackagesInput",
  "type": "object"
}
```

#### Example Arguments
```json
{
  "status_group": "PENDING",
  "carrier": "FedEx",
  "storage_type": "LOCKER",
  "days": 7,
  "is_perishable": false
}
```

#### Example Successful Result
```json
{
  "success": true,
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
          "locker_door_name": "Door 14"
        }
      }
    ]
  }
}
```

#### Possible Errors
- `AUTHENTICATION_REQUIRED: Guest user attempting to access private delivery data.`
- `ACCESS_DENIED: Tenant ID mismatch or missing authorization header.`
- `INVALID_INPUT: Invalid carrier name or days outside [0, 365].`
- `RATE_LIMITED: Upstream 429 rate limit reached.`
- `UPSTREAM_TIMEOUT: Upstream package repository exceeded 10s request timeout.`
- `SERVICE_UNAVAILABLE: Upstream 503 maintenance mode.`

#### Test References
- `tests/unit/test_smiota_mcp_tools.py::test_search_packages_success`
- `tests/unit/test_smiota_mcp_security.py::test_search_packages_guest_blocked`
- `tests/integration/test_smiota_api_client.py::test_search_packages_http_request`

### Tool: `get_package_details` (v1.0.0)

- **Category:** Customer Parcel Management
- **Access Level:** `read_only`
- **Authentication Required:** `True`
- **Authorization Scope:** Direct object reference protection; recipient ownership validated at DB/API layer.
- **Upstream Source API:** `GET /internal/ai/packages/{identifier}`
- **Source Reference:** `smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-2`

#### Description
```text
1. Purpose: Retrieve comprehensive 360-degree attributes of a specific package.
2. When to use: When customer provides a tracking number, package UUID, PO number, or release passcode and asks for detailed package status, locker compartment, carrier, or expiration.
3. When not to use: When searching across multiple packages without an identifier (use search_packages).
4. Required arguments: identifier (carrier tracking number, UUID, or PO number).
5. Optional arguments: None.
6. Authentication: Required. Anonymous guests cannot retrieve protected package records.
7. Authorization: Tenant and recipient ownership enforced at API and database query level.
8. Data returned: Package UUID, tracking number, courier, status, received time, expiration time, storage type (LOCKER/SHELF), locker compartment door, building, and pickup verification details.
9. Limitations: Returns NOT_FOUND if identifier does not exist or belongs to another tenant/resident.
10. Failure behavior: Returns error envelope with NOT_FOUND, INVALID_IDENTIFIER, or AUTHENTICATION_REQUIRED.
```

#### Input Schema
```json
{
  "description": "Input parameters for retrieving 360-degree attributes of a specific package.",
  "properties": {
    "identifier": {
      "description": "Carrier tracking number (e.g. '1Z9999999999999999'), package UUID, PO number (e.g. 'PO-88421'), or release passcode.",
      "maxLength": 100,
      "minLength": 1,
      "title": "Identifier",
      "type": "string"
    }
  },
  "required": [
    "identifier"
  ],
  "title": "GetPackageDetailsInput",
  "type": "object"
}
```

#### Example Arguments
```json
{
  "identifier": "1Z9999999999999999"
}
```

#### Example Successful Result
```json
{
  "success": true,
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
      "locker_bank": "Main Pod Bank 1"
    }
  }
}
```

#### Possible Errors
- `AUTHENTICATION_REQUIRED: Guest user attempting to access package details.`
- `NOT_FOUND: Tracking number or UUID not found or belongs to another resident.`
- `INVALID_INPUT: Empty identifier or forbidden characters.`
- `UPSTREAM_TIMEOUT: Upstream service exceeded read timeout.`

#### Test References
- `tests/unit/test_smiota_mcp_tools.py::test_get_package_details_success`
- `tests/unit/test_smiota_mcp_tools.py::test_get_package_details_not_found`
- `tests/unit/test_smiota_mcp_security.py::test_get_package_details_guest_blocked`

### Tool: `get_package_timeline` (v1.0.0)

- **Category:** Customer Parcel Management
- **Access Level:** `read_only`
- **Authentication Required:** `True`
- **Authorization Scope:** Authorized recipient of the package.
- **Upstream Source API:** `GET /internal/ai/packages/{identifier}/timeline`
- **Source Reference:** `smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-3`

#### Description
```text
1. Purpose: Retrieve complete chain-of-custody timeline and dock reconciliation events for a package.
2. When to use: When customer asks 'When was my package delivered?', 'Who accepted my parcel at the dock?', 'Show delivery timeline', or wants to audit carrier handoff.
3. When not to use: When the customer only needs current delivery status or pickup PIN (use get_package_details).
4. Required arguments: identifier (tracking number or package UUID).
5. Optional arguments: None.
6. Authentication: Required.
7. Authorization: Enforced by server session token.
8. Data returned: Chronological event list with event type (DOCK_RECEIVE, LOCKER_DEPOSIT, CUSTOMER_PICKUP, etc.), operator, timestamp, and location notes.
9. Limitations: Timeline is only available for packages that have undergone dock scan or locker deposit.
10. Failure behavior: Returns NOT_FOUND or EMPTY_RESULT if package has no recorded audit events.
```

#### Input Schema
```json
{
  "description": "Input parameters for retrieving package chain-of-custody and delivery audit timeline.",
  "properties": {
    "identifier": {
      "description": "Carrier tracking number or package ID to trace audit timeline and dock reconciliation for.",
      "maxLength": 100,
      "minLength": 1,
      "title": "Identifier",
      "type": "string"
    }
  },
  "required": [
    "identifier"
  ],
  "title": "GetPackageTimelineInput",
  "type": "object"
}
```

#### Example Arguments
```json
{
  "identifier": "1Z9999999999999999"
}
```

#### Example Successful Result
```json
{
  "success": true,
  "status": "SUCCESS",
  "message": "Retrieved 3 timeline events for package '1Z9999999999999999'.",
  "data": {
    "tracking_number": "1Z9999999999999999",
    "timeline": [
      {
        "event_type": "DOCK_RECEIVE",
        "timestamp": "2026-10-23T08:30:00Z",
        "operator": "Dock Agent"
      },
      {
        "event_type": "LOCKER_DEPOSIT",
        "timestamp": "2026-10-23T09:15:00Z",
        "location": "Door 14"
      }
    ]
  }
}
```

#### Possible Errors
- `AUTHENTICATION_REQUIRED: Unauthenticated session.`
- `NOT_FOUND: Package not found in chain-of-custody audit repository.`
- `UPSTREAM_TIMEOUT: Backend lookup timeout.`

#### Test References
- `tests/unit/test_smiota_mcp_tools.py::test_get_package_timeline_success`
- `tests/unit/test_smiota_mcp_security.py::test_get_package_timeline_guest_blocked`

### Tool: `get_user_preferences_and_services` (v1.0.0)

- **Category:** Resident Profile & Accessibility
- **Access Level:** `read_only`
- **Authentication Required:** `True`
- **Authorization Scope:** Authenticated resident profile strictly.
- **Upstream Source API:** `GET /internal/ai/users/profile-and-services`
- **Source Reference:** `smiota_ai_consolidated_api_architecture.md#consolidated-endpoint-4`

#### Description
```text
1. Purpose: Retrieve resident ADA accessibility settings, authorized pickup proxies, and active day-use lockers.
2. When to use: When customer asks 'Are my packages assigned to bottom lockers?', 'Who can pick up for me?', 'Check my accessibility settings', or 'Do I have a personal locker assigned?'.
3. When not to use: When looking up parcel delivery or tracking status (use search_packages).
4. Required arguments: None.
5. Optional arguments: None.
6. Authentication: Required.
7. Authorization: Returns profile strictly for the authenticated resident.
8. Data returned: ADA bottom-tier locker flag, authorized proxy delegate names/contacts, and active day-use pods.
9. Limitations: Modifications to proxies or ADA settings must be performed through the resident portal.
10. Failure behavior: Returns AUTHENTICATION_REQUIRED or SERVICE_UNAVAILABLE on failure.
```

#### Input Schema
```json
{
  "description": "Input parameters for checking accessibility, proxy delegates, and personal day-use pods.",
  "properties": {},
  "title": "GetUserPreferencesAndServicesInput",
  "type": "object"
}
```

#### Example Arguments
```json
{}
```

#### Example Successful Result
```json
{
  "success": true,
  "status": "SUCCESS",
  "message": "Retrieved resident preferences, proxies, and locker services.",
  "data": {
    "user_id": 10790,
    "first_name": "Alex",
    "last_name": "Morgan",
    "accessibility": {
      "bottom_tier_lockers_required": true
    },
    "proxies": [
      {
        "name": "Jordan Lee",
        "relationship": "Roommate"
      }
    ],
    "active_day_use_lockers": []
  }
}
```

#### Possible Errors
- `AUTHENTICATION_REQUIRED: Guest user attempting to read profile.`
- `SERVICE_UNAVAILABLE: User profile service down.`

#### Test References
- `tests/unit/test_smiota_mcp_tools.py::test_get_user_preferences_success`
- `tests/unit/test_smiota_mcp_security.py::test_get_user_preferences_guest_blocked`

### Tool: `get_my_pickup_pin` (v1.0.0)

- **Category:** Customer Parcel Pickup
- **Access Level:** `read_only`
- **Authentication Required:** `True`
- **Authorization Scope:** Owner of the pending package.
- **Upstream Source API:** `GET /internal/ai/packages/{identifier} or /internal/ai/packages?status_group=PENDING`
- **Source Reference:** `smiota_ai_consolidated_api_architecture.md`

#### Description
```text
1. Purpose: Retrieve the active 6-digit pickup PIN and locker door number to collect a package.
2. When to use: When customer asks 'What is my pickup PIN?', 'Resend my access code', 'How do I open my locker?', or 'Send me the PIN for package SM-1234'.
3. When not to use: When customer wants general tracking status or package history (use search_packages).
4. Required arguments: None.
5. Optional arguments: identifier (tracking number or package ID if resident has multiple packages).
6. Authentication: Required. Highly sensitive operation; guests must authenticate.
7. Authorization: Customer context verified via server session.
8. Data returned: 6-digit PIN code, locker bank, door number, building name, expiration time, and kiosk instructions.
9. Limitations: Only active for packages currently stored and awaiting pickup (READY_FOR_PICKUP).
10. Failure behavior: Returns EMPTY_RESULT if no packages are awaiting pickup, or AUTHENTICATION_REQUIRED.
```

#### Input Schema
```json
{
  "description": "Input parameters for retrieving the 6-digit pickup PIN and locker door.",
  "properties": {
    "identifier": {
      "anyOf": [
        {
          "maxLength": 100,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional tracking number, package UUID, or PO number. If omitted, retrieves PIN for the resident's active pending delivery.",
      "title": "Identifier"
    }
  },
  "title": "GetPickupPinInput",
  "type": "object"
}
```

#### Example Arguments
```json
{
  "identifier": "1Z9999999999999999"
}
```

#### Example Successful Result
```json
{
  "success": true,
  "status": "SUCCESS",
  "message": "Pickup PIN retrieved successfully.",
  "data": {
    "pickup_pin": "482910",
    "locker_door": "Door 14",
    "locker_bank": "Main Pod Bank 1",
    "building": "East Campus Commons",
    "instructions": "Enter your 6-digit PIN 482910 on the touchscreen console at Main Pod Bank 1."
  }
}
```

#### Possible Errors
- `AUTHENTICATION_REQUIRED: Guest user requesting pickup PIN.`
- `EMPTY_RESULT: No active packages awaiting pickup.`

#### Test References
- `tests/unit/test_smiota_mcp_tools.py::test_get_my_pickup_pin_success`
- `tests/unit/test_smiota_mcp_security.py::test_get_my_pickup_pin_guest_blocked`

### Tool: `get_my_locker_details` (v1.0.0)

- **Category:** Smart Locker Navigation
- **Access Level:** `read_only`
- **Authentication Required:** `True`
- **Authorization Scope:** Authenticated resident delivery location.
- **Upstream Source API:** `GET /internal/ai/packages/{identifier}`
- **Source Reference:** `smiota_ai_consolidated_api_architecture.md`

#### Description
```text
1. Purpose: Retrieve smart locker physical compartment location, bank name, door number, and console instructions.
2. When to use: When customer asks 'Which locker is my package in?', 'What door number should I go to?', 'Where is my locker compartment located?'.
3. When not to use: When customer asks why a door didn't open (use query_locker_door_status).
4. Required arguments: None.
5. Optional arguments: identifier (tracking number or package ID).
6. Authentication: Required.
7. Authorization: Scope enforced by caller context.
8. Data returned: Building name, locker bank name, door number/name, compartment size, storage type (LOCKER/SHELF).
9. Limitations: Only packages in smart lockers have compartment door numbers assigned; mailroom shelf items will indicate 'SHELF'.
10. Failure behavior: Returns EMPTY_RESULT if no packages are stored in lockers, or AUTHENTICATION_REQUIRED.
```

#### Input Schema
```json
{
  "description": "Input parameters for looking up locker compartment door, bank, and location.",
  "properties": {
    "identifier": {
      "anyOf": [
        {
          "maxLength": 100,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional tracking number or package ID. If omitted, retrieves locker details for the resident's active pending delivery.",
      "title": "Identifier"
    }
  },
  "title": "GetLockerDetailsInput",
  "type": "object"
}
```

#### Example Arguments
```json
{}
```

#### Example Successful Result
```json
{
  "success": true,
  "status": "SUCCESS",
  "message": "Found 1 active locker compartment(s) awaiting pickup.",
  "data": {
    "total_active_lockers": 1,
    "lockers": [
      {
        "tracking_number": "1Z9999999999999999",
        "building_name": "East Campus Commons",
        "locker_bank": "Main Pod Bank 1",
        "locker_door_name": "Door 14"
      }
    ]
  }
}
```

#### Possible Errors
- `AUTHENTICATION_REQUIRED: Guest user requesting locker compartment details.`
- `EMPTY_RESULT: No deliveries currently stored in smart lockers.`

#### Test References
- `tests/unit/test_smiota_mcp_tools.py::test_get_my_locker_details_success`
- `tests/unit/test_smiota_mcp_security.py::test_get_my_locker_details_guest_blocked`

### Tool: `query_locker_door_status` (v1.0.0)

- **Category:** IoT Diagnostics
- **Access Level:** `read_only`
- **Authentication Required:** `False`
- **Authorization Scope:** Read-only sensor diagnostic state.
- **Upstream Source API:** `TELEMETRY_POLL Locker Controller Hardware Telemetry`
- **Source Reference:** `smiota_ai_api_documentation.md`

#### Description
```text
1. Purpose: Query IoT telemetry for smart locker compartment door sensors and controller status.
2. When to use: When customer reports 'The locker door didn't pop open', 'Is the door jammed?', or asks for sensor diagnostic checks.
3. When not to use: When customer just needs their PIN or locker door number (use get_my_pickup_pin).
4. Required arguments: locker_id (string or integer ID), compartment (integer door number).
5. Optional arguments: None.
6. Authentication: Optional/Public IoT telemetry check.
7. Authorization: Read-only sensor state.
8. Data returned: Door state ('closed'/'open'), lock solenoid state ('engaged'/'disengaged'), controller latency, battery percentage.
9. Limitations: Does not perform physical unlocking; read-only sensor check.
10. Failure behavior: Returns sensor communication error if locker controller is offline.
```

#### Input Schema
```json
{
  "type": "object",
  "properties": {}
}
```

#### Example Arguments
```json
{
  "locker_id": "LK-SF-102",
  "compartment": 7
}
```

#### Example Successful Result
```json
{
  "locker_id": "LK-SF-102",
  "compartment": 7,
  "status": "closed",
  "lock_state": "engaged",
  "battery_pct": 98.4
}
```

#### Possible Errors
- `Sensor communication error.`

#### Test References
- `tests/unit/test_smiota_mcp_tools.py::test_query_locker_door_status`

### Tool: `create_support_ticket` (v1.0.0)

- **Category:** Customer Support Escalation
- **Access Level:** `read_only`
- **Authentication Required:** `False`
- **Authorization Scope:** Customer session ticket queue.
- **Upstream Source API:** `POST ITSM Service Portal API`
- **Source Reference:** `smiota_ai_api_documentation.md`

#### Description
```text
1. Purpose: Create or escalate a customer support case in ServiceNow or Zendesk.
2. When to use: When customer requests human concierge escalation, lost package investigation, or building maintenance.
3. When not to use: For automated package tracking or PIN inquiries.
4. Required arguments: user_id (string), subject (string), description (string).
5. Optional arguments: priority ('low', 'medium', 'high', 'urgent'). Default 'medium'.
6. Authentication: Required or guest support context.
7. Authorization: Scope tied to session.
8. Data returned: ticket_id, status, assigned queue.
9. Limitations: Escalation only.
10. Failure behavior: Returns error if ticketing system is unreachable.
```

#### Input Schema
```json
{
  "type": "object",
  "properties": {}
}
```

#### Example Arguments
```json
{
  "user_id": "10790",
  "subject": "Compartment door latch stuck",
  "description": "Door 14 did not release after entering PIN.",
  "priority": "high"
}
```

#### Example Successful Result
```json
{
  "ticket_id": "INC-2026-9042",
  "status": "assigned_to_support_tier2"
}
```

#### Possible Errors
- `Ticketing gateway unreachable.`

#### Test References
- `tests/unit/test_smiota_mcp_tools.py::test_create_support_ticket`

### Tool: `remote_unlock_locker_door` (v1.0.0)

- **Category:** Physical Remediation (HITL)
- **Access Level:** `remediation`
- **Authentication Required:** `True`
- **Authorization Scope:** Human-in-the-loop (HITL) approval token required.
- **Upstream Source API:** `COMMAND_UNLOCK Locker Controller Solenoid Actuator API`
- **Source Reference:** `smiota_ai_api_documentation.md`

#### Description
```text
1. Purpose: Send remote solenoid unlock command to IoT smart locker door (Requires Human Approval / Token).
2. When to use: When customer is physically in front of locker and authorized staff triggers emergency door release.
3. When not to use: Never execute automatically without verification.
4. Required arguments: locker_id (string), compartment (integer).
5. Optional arguments: approval_token (string required for remediation execution).
6. Authentication: Strict authorization required.
7. Authorization: Property Manager or Support Concierge token required.
8. Data returned: Unlock confirmation status and timestamp.
9. Limitations: Physical door release command.
10. Failure behavior: Raises RemediationApprovalRequiredError if approval_token is missing.
```

#### Input Schema
```json
{
  "type": "object",
  "properties": {}
}
```

#### Example Arguments
```json
{
  "locker_id": "LK-SF-102",
  "compartment": 7,
  "approval_token": "MGR-APPROVAL-TOKEN-8831"
}
```

#### Example Successful Result
```json
{
  "status": "door_unlocked",
  "locker_id": "LK-SF-102",
  "compartment": 7,
  "approved_by_token": "MGR-APPROVAL-TOKEN-8831"
}
```

#### Possible Errors
- `RemediationApprovalRequiredError: Execution blocked without cryptographic approval token.`

#### Test References
- `tests/unit/test_smiota_mcp_security.py::test_remote_unlock_requires_approval`
- `tests/unit/test_smiota_mcp_security.py::test_remote_unlock_with_valid_token`

---

## Blocked & Unimplemented Operations

The following operations are documented in the system catalogs but are deliberately excluded, blocked, or deferred from exposure to the customer-facing AI agent:

| Operation Name | Status | Justification / Security Boundary | Source Document |
| :--- | :--- | :--- | :--- |
| `direct_carrier_return_label_generation` | `BLOCKED` | Upstream carrier outbound return label generation API requires warehouse dispatcher credentials and binary PDF thermal print streams not exposed to resident AI session. | `smiota_ai_consolidated_api_architecture.md` |
| `arbitrary_sql_execution` | `PROHIBITED` | Prohibited by architectural design. Raw database query execution from customer-facing agent violates the security boundary and multi-tenant isolation. | `smiota_database_queries_catalog.md` |
| `modify_resident_proxy_delegates` | `UNIMPLEMENTED_READ_ONLY_BOUNDARY` | State-changing resident profile and proxy mutation requires MFA-authenticated web portal flow; internal API contract /internal/ai/users/profile-and-services is strictly read-only. | `smiota_ai_consolidated_api_architecture.md` |
| `remote_firmware_update` | `EXCLUDED_PRIVILEGED` | Hardware firmware operations are administrative capabilities reserved for internal SREs and excluded from customer AI agent scope. | `smiota_ai_api_documentation.md` |
