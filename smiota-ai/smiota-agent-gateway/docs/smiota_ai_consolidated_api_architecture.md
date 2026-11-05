# Smiota AI Automation: Consolidated Minimal API Architecture & LLM Extraction Specification

This document defines the consolidated, minimal API architecture designed for the Smiota AI Agent system (`smiota-ai` and `smiota-server`). 

By condensing all parcel, locker, audit, communication, and accessibility queries into **4 unified endpoints**, this architecture eliminates LLM tool-selection latency, prevents hallucination, optimizes database access patterns, and enables the LLM to selectively extract and return **only** the data requested by the customer.

---

## Table of Contents
1. [Architectural Overview & Design Principles](#1-architectural-overview--design-principles)
2. [The 4 Consolidated APIs Specification](#2-the-4-consolidated-apis-specification)
   - [API 1: Package Search & Summaries (`search_packages`)](#api-1-get-internalaipackages-search_packages)
   - [API 2: 360° Package Details (`get_package_details`)](#api-2-get-internalaipackagesidentifier-get_package_details)
   - [API 3: Chain of Custody & Audit Timeline (`get_package_timeline`)](#api-3-get-internalaipackagesidentifiertimeline-get_package_timeline)
   - [API 4: User Profile, Preferences & Day-Use Pods (`get_user_preferences_and_services`)](#api-4-get-internalaiusersprofile-and-services-get_user_preferences_and_services)
3. [Exhaustive Query-to-API Coverage Matrix](#3-exhaustive-query-to-api-coverage-matrix)
4. [LLM Selective Extraction & System Prompt Rules](#4-llm-selective-extraction--system-prompt-rules)
5. [Backend Implementation Blueprint (Java Spark DAO & Controller)](#5-backend-implementation-blueprint-java-spark-dao--controller)
6. [Agent Tool Definitions (Python Pydantic Schemas for `smiota-ai`)](#6-agent-tool-definitions-python-pydantic-schemas-for-smiota-ai)

---

## 1. Architectural Overview & Design Principles

### Why 4 Consolidated APIs Instead of 40 Granular Endpoints?
1. **Zero LLM Tool Confusion**: LLMs struggle to disambiguate between dozens of overlapping tool schemas. 4 domain-aligned tools provide 100% deterministic routing.
2. **Reduced Token Overhead**: Passing 4 concise tool schemas into the system prompt saves thousands of tokens per turn compared to massive API suites.
3. **Database Join Efficiency**: The backend compiles related data in a single parameterized SQL join rather than requiring the LLM to execute 4-5 sequential round-trips.
4. **Selective Synthesis**: Rich JSON payloads allow the LLM to answer primary questions while immediately possessing the context to answer follow-up questions without additional latency.

```
                  ┌───────────────────────────────────────────────┐
                  │                 User Prompt                   │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                         LLM Intent Classifier / Tool Router
                                          │
       ┌──────────────────┬───────────────┴───────────────┬──────────────────┐
       ▼                  ▼                               ▼                  ▼
┌──────────────┐   ┌──────────────┐               ┌──────────────┐   ┌──────────────┐
│    API 1     │   │    API 2     │               │    API 3     │   │    API 4     │
│ search_      │   │ get_package_ │               │ get_package_ │   │ get_user_    │
│ packages     │   │ details      │               │ timeline     │   │ profile_     │
│              │   │              │               │              │   │ services     │
│ (Summaries,  │   │ (360° Parcel │               │ (Chain of    │   │ (ADA, Proxy, │
│  Filters,    │   │  Attributes, │               │  Custody,    │   │  Channels &  │
│  Counts)     │   │  Locker/PIN) │               │  POD, Delays)│   │  Day-Use)    │
└──────┬───────┘   └──────┬───────┘               └──────┬───────┘   └──────┬───────┘
       │                  │                               │                  │
       └──────────────────┴───────────────┬───────────────┴──────────────────┘
                                          ▼
                               Rich JSON Data Payload
                                          │
                                          ▼
                        LLM Selective Synthesizer
                 (Extracts ONLY what the user asked for)
                                          │
                                          ▼
                        Precise, Natural User Response
```

---

## 2. The 4 Consolidated APIs Specification

### API 1: `GET /internal/ai/packages` (`search_packages`)
* **Primary Responsibility**: Multi-package inquiries, counts, category filters, overviews, and historical searches.
* **Security & Isolation**: Authenticated via `X-Internal-Service-Key`; `recipient_id`, `customer_id`, and `location_id` are enforced.
* **Query Parameters**:
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `status_group` | string | No | Filter: `PENDING` (default), `RELEASED`, `OUTBOUND`, `ALL` |
  | `carrier` | string | No | Substring carrier search (e.g., `Amazon`, `FedEx`, `UPS`, `USPS`, `DHL`) |
  | `storage_type` | string | No | Filter by storage mechanism: `ALL`, `LOCKER`, `SHELF` |
  | `days` | integer | No | Historical window (e.g., `30` for past 30 days, `0` for today) |
  | `is_perishable`| boolean| No | Filter for temperature-sensitive items |
* **JSON Response Schema**:
  ```json
  {
    "total_count": 3,
    "summary": {
      "in_locker": 2,
      "on_shelf": 1,
      "perishable_count": 1,
      "urgent_count": 0
    },
    "packages": [
      {
        "id": 10492,
        "tracking_number": "1Z9999999999999999",
        "carrier": "Amazon",
        "status": "READY_FOR_PICKUP",
        "storage_type": "LOCKER",
        "building_name": "East Campus Commons",
        "locker_bank": "Main Pod Bank 1",
        "locker_name": "Door 14",
        "received_time": "2026-10-23T09:15:00Z",
        "expiration_time": "2026-10-26T18:00:00Z",
        "is_perishable": false,
        "didnt_fit": false,
        "is_priority_mail": false
      },
      {
        "id": 10501,
        "tracking_number": "9400100000000000000000",
        "carrier": "USPS",
        "status": "READY_FOR_PICKUP",
        "storage_type": "SHELF",
        "building_name": "East Campus Commons",
        "locker_bank": null,
        "locker_name": null,
        "received_time": "2026-10-23T11:30:00Z",
        "expiration_time": "2026-10-28T18:00:00Z",
        "is_perishable": true,
        "didnt_fit": true,
        "is_priority_mail": true
      }
    ]
  }
  ```

---

### API 2: `GET /internal/ai/packages/{identifier}` (`get_package_details`)
* **Primary Responsibility**: Unified 360° inspection of a single package by tracking number, package UUID, PO number, or release passcode.
* **Path Parameter**: `identifier` (Tracking number, e.g., `1Z9999999999999999`, package UUID, or PO number)
* **JSON Response Schema**:
  ```json
  {
    "id": 10492,
    "uuid": "8f9a2b10-6a5c-4e89-b1d3-92f7a01d5e34",
    "tracking_number": "1Z9999999999999999",
    "po_number": "PO-88421",
    "carrier": "UPS",
    "status": "READY_FOR_PICKUP",
    "received_time": "2026-10-23T09:15:00Z",
    "expiration_time": "2026-10-26T18:00:00Z",
    "passcode": "482910",
    "is_at_destination": true,
    "location": {
      "building_id": 14,
      "building_name": "East Campus Commons",
      "storage_type": "LOCKER",
      "locker_id": 88,
      "locker_bank": "Main Pod Bank 1",
      "locker_door_name": "Door 14",
      "locker_size": "Medium"
    },
    "physical_specs": {
      "dimensions": {
        "length_in": 14.5,
        "width_in": 10.0,
        "height_in": 8.0
      },
      "didnt_fit": false,
      "is_perishable": false,
      "is_priority_mail": false,
      "package_type": "Standard Box",
      "number_of_subitems": 1
    },
    "origin_info": {
      "sender_name": "Amazon Fulfillment Services",
      "sender_company": "Amazon.com",
      "has_label_photo": true,
      "ocr_text_preview": "SHIP TO: ALEX JOHNSON APARTMENT 4B..."
    }
  }
  ```

---

### API 3: `GET /internal/ai/packages/{identifier}/timeline` (`get_package_timeline`)
* **Primary Responsibility**: Chain of custody, dock vs. intake reconciliation, courier handoffs, proof of delivery, and failure diagnostics.
* **Path Parameter**: `identifier` (Tracking number or package ID)
* **JSON Response Schema**:
  ```json
  {
    "tracking_number": "1Z9999999999999999",
    "status": "READY_FOR_PICKUP",
    "carrier_reconciliation": {
      "carrier_reported_dock_arrival": "2026-10-23T09:00:00Z",
      "smiota_central_intake_scan": "2026-10-23T09:15:00Z",
      "building_transit_arrival": "2026-10-23T10:05:00Z",
      "locker_deposit_time": "2026-10-23T10:20:00Z",
      "status_explanation": "Package was checked in at the central loading dock at 9:15 AM and deposited into Locker Door 14 at 10:20 AM."
    },
    "chain_of_custody": [
      {
        "timestamp": "2026-10-23T09:15:00Z",
        "action": "Intake Received at Central Dock",
        "handled_by": "Marcus Vance",
        "location": "Central Receiving Facility"
      },
      {
        "timestamp": "2026-10-23T09:45:00Z",
        "action": "Dispatched for Intra-Campus Transit",
        "handled_by": "Campus Courier Van 2 (Driver: Sam Lee)",
        "location": "Transit Route B"
      },
      {
        "timestamp": "2026-10-23T10:05:00Z",
        "action": "Received at Destination Building",
        "handled_by": "Elena Rostova",
        "location": "East Campus Commons Mailroom"
      },
      {
        "timestamp": "2026-10-23T10:20:00Z",
        "action": "Deposited into Smart Locker",
        "handled_by": "Elena Rostova",
        "location": "Main Pod Bank 1 - Door 14"
      }
    ],
    "proof_of_delivery": {
      "is_released": false,
      "released_at": null,
      "released_to_name": null,
      "released_by_staff": null,
      "id_type_verified": null,
      "has_signature": false,
      "has_id_photo": false
    },
    "communications": [
      {
        "channel": "SMS",
        "dispatched_at": "2026-10-23T10:21:00Z",
        "status": "DELIVERED",
        "destination": "+1 (555) ***-4892",
        "error_message": null
      },
      {
        "channel": "EMAIL",
        "dispatched_at": "2026-10-23T10:21:00Z",
        "status": "DELIVERED",
        "destination": "a.johnson@campus.edu",
        "error_message": null
      }
    ],
    "exceptions_and_notes": {
      "has_problem_flag": false,
      "problem_reason": null,
      "staff_intake_notes": "Carton in good condition."
    }
  }
  ```

---

### API 4: `GET /internal/ai/users/profile-and-services` (`get_user_preferences_and_services`)
* **Primary Responsibility**: Accessibility compliance, delegated proxy pickups, notification settings, and day-use locker pods.
* **Headers**: `X-Internal-Service-Key`, User session context
* **JSON Response Schema**:
  ```json
  {
    "user_id": 4021,
    "full_name": "Alex Johnson",
    "unit_no": "Apartment 4B",
    "building_name": "East Campus Commons",
    "accessibility": {
      "needs_wheelchair_access": true,
      "preference_status": "Active: System restricts locker assignment to lower tiers (bottom 3 rows)."
    },
    "delegation": {
      "has_delegate_assigned": true,
      "delegate_user_id": 5120,
      "delegate_name": "Jordan Smith (Roommate)",
      "delegate_email": "j.smith@campus.edu",
      "alternate_recipients": ["Jordan Smith"],
      "alternate_address": null
    },
    "communication_preferences": {
      "preferred_channel_1": "SMS",
      "preferred_channel_2": "EMAIL",
      "preferred_channel_3": "APP_PUSH",
      "is_opted_out_sms": false,
      "is_opted_out_email": false
    },
    "day_use_storage": {
      "has_active_reservation": true,
      "active_reservations": [
        {
          "reservation_id": "res-9912",
          "pod_name": "Rec Center Gym Pod 3",
          "door_name": "Pod Door 06",
          "start_time": "2026-10-23T08:00:00Z",
          "end_time": "2026-10-23T18:00:00Z",
          "status": "CHECKED_OUT"
        }
      ]
    }
  }
  ```

---

## 3. Exhaustive Query-to-API Coverage Matrix

| # | User Inquiries & Queries | Mapped API | Fields Used by LLM |
|---|---|---|---|
| **1** | *"Where is my package? Tracking 1Z9999999999999999?"* | `API 2: details` | `status`, `building_name`, `storage_type`, `locker_door_name` |
| **2** | *"Did my Amazon order arrive at the mailroom today?"* | `API 1: packages` (`carrier=Amazon&days=0`) | `total_count`, `packages[].received_time`, `packages[].locker_name` |
| **3** | *"How many packages do I currently have waiting for me?"* | `API 1: packages` (`status_group=PENDING`) | `total_count`, `summary.in_locker`, `summary.on_shelf` |
| **4** | *"Show me a list of all packages I picked up over the last 30 days?"* | `API 1: packages` (`status_group=RELEASED&days=30`) | `packages[].tracking_number`, `packages[].carrier`, `packages[].received_time` |
| **5** | *"Are my packages sitting on the desk shelf or locked inside a PoD locker?"* | `API 1: packages` or `API 2` | `summary.in_locker`, `summary.on_shelf`, `storage_type` |
| **6** | *"Carrier says 'Delivered to Dock' at 9 AM, but Smiota says 'In Transit'?"* | `API 3: timeline` | `carrier_reconciliation.status_explanation`, `chain_of_custody` |
| **7** | *"Show me step-by-step history of who moved my package since arrival?"* | `API 3: timeline` | `chain_of_custody[].{timestamp, action, handled_by, location}` |
| **8** | *"Can I see the sender information and package type for my incoming parcel?"* | `API 2: details` | `origin_info.sender_name`, `physical_specs.package_type` |
| **9** | *"What is my pickup code / PIN for the locker?"* | `API 2: details` | `passcode`, `location.locker_door_name` |
| **10** | *"Are my packages assigned to accessible bottom-tier lockers for wheelchair access?"* | `API 4: profile` | `accessibility.needs_wheelchair_access`, `accessibility.preference_status` |
| **11** | *"Can my assistant or roommate pick up my packages for me?"* | `API 4: profile` | `delegation.has_delegate_assigned`, `delegation.delegate_name` |
| **12** | *"Why didn't I get a text message (SMS) or email notification?"* | `API 3: timeline` | `communications[].{channel, status, error_message}` |
| **13** | *"Is my package marked as perishable or cold storage?"* | `API 2: details` | `physical_specs.is_perishable` |
| **14** | *"Why wasn't my parcel put in a locker? (Did it not fit?)"* | `API 2: details` | `physical_specs.didnt_fit`, `physical_specs.dimensions` |
| **15** | *"When does my package expire or get returned to sender?"* | `API 2: details` | `expiration_time` |
| **16** | *"Who actually picked up or signed for my package?"* | `API 3: timeline` | `proof_of_delivery.{released_at, released_to_name, released_by_staff}` |
| **17** | *"Was my package marked damaged, leaking, or crushed upon arrival?"* | `API 3: timeline` | `exceptions_and_notes.{has_problem_flag, problem_reason, staff_intake_notes}` |
| **18** | *"What is the status of my outbound return package?"* | `API 1: packages` (`status_group=OUTBOUND`) | `packages[].status`, `packages[].carrier` |
| **19** | *"Do I have an active Day-Use personal storage locker checked out right now?"* | `API 4: profile` | `day_use_storage.has_active_reservation`, `active_reservations[]` |
| **20** | *"When does my day-use locker reservation expire?"* | `API 4: profile` | `day_use_storage.active_reservations[].end_time` |

---

## 4. LLM Selective Extraction & System Prompt Rules

Place this prompt directly into your agent execution context (in `smiota-ai` routing or composite agents):

```text
You are the Smiota Smart Locker AI Assistant.
You have access to 4 consolidated tools:
- search_packages: Multi-package counts, dates, filters, carriers, and historical lists.
- get_package_details: Deep 360-degree attributes of a specific package (passcode, door, size, sender).
- get_package_timeline: End-to-end chain of custody, carrier dock reconciliation, POD, and alert logs.
- get_user_preferences_and_services: ADA wheelchair preferences, proxy pickup delegation, and day-use pods.

CRITICAL SELECTIVE EXTRACTION RULES:
1. SELECTIVE SYNTHESIS: The backend returns rich, comprehensive JSON payloads. You must extract and output ONLY the exact detail the user requested.
2. DO NOT DUMP RAW FIELDS:
   - If the user asks: "What is my passcode?", reply: "Your pickup code is 482910. Your package is in Main Pod Bank 1, Door 14." Do not mention sender, weight, or timestamps.
   - If the user asks: "Did Amazon arrive today?", reply: "Yes, 1 Amazon package arrived today at 9:15 AM and is ready for pickup in Door 14."
3. CARRIER DOCK RECONCILIATION: When a user mentions a carrier delivered at a certain time but Smiota says In Transit, look at `carrier_reconciliation.status_explanation` from `get_package_timeline` to explain the difference between dock delivery and final locker stocking.
4. PROACTIVE DISAMBIGUATION: If the user asks "Where is my package?" without a tracking number, call `search_packages(status_group='PENDING')`. If they have multiple packages, list them concisely and ask which one they need help with.
```

---

## 5. Backend Implementation Blueprint (Java Spark DAO & Controller)

### `AIPackageDao.java` Interface
```java
public interface AIPackageDao {
    AIPackageListResponse searchPackages(Long customerId, Long tenantId, Long locationId, Long recipientId,
            String statusGroup, String carrier, String storageType, Integer days, Boolean isPerishable);

    AIPackageDetailResponse getPackageDetails(Long customerId, Long tenantId, Long locationId, Long recipientId, String identifier);

    AIPackageTimelineResponse getPackageTimeline(Long customerId, Long tenantId, Long locationId, Long recipientId, String identifier);
}
```

### `AIUserDao.java` Interface
```java
public interface AIUserDao {
    AIUserProfileServicesResponse getUserPreferencesAndServices(Long customerId, Long tenantId, Long locationId, Long userId);
}
```

### Domain Controller Route Definitions
```java
// Route 1: Search & Summaries (AIPackageControllerImpl)
get(new Route("/internal/ai/packages") {
    @Override
    public Object handle(Request request, Response response) {
        // Enforces customer_id, tenant_id, location_id, recipient_id
        return packageService.searchPackages(customerId, tenantId, locationId, recipientId, ...);
    }
});

// Route 2: 360° Package Details (AIPackageControllerImpl)
get(new Route("/internal/ai/packages/:identifier") {
    @Override
    public Object handle(Request request, Response response) {
        String identifier = request.params(":identifier");
        return packageService.getPackageDetails(customerId, tenantId, locationId, recipientId, identifier);
    }
});

// Route 3: Timeline & Chain of Custody (AIPackageControllerImpl)
get(new Route("/internal/ai/packages/:identifier/timeline") {
    @Override
    public Object handle(Request request, Response response) {
        String identifier = request.params(":identifier");
        return packageService.getPackageTimeline(customerId, tenantId, locationId, recipientId, identifier);
    }
});

// Route 4: User Profile & Services (AIUserControllerImpl)
get(new Route("/internal/ai/users/profile-and-services") {
    @Override
    public Object handle(Request request, Response response) {
        return userService.getUserPreferencesAndServices(customerId, tenantId, locationId, userId);
    }
});
```

---

## 6. Agent Tool Definitions (Python Pydantic Schemas for `smiota-ai`)

These Pydantic schemas can be dropped directly into `src/smiota/agents/routing/` or OpenAI/LangChain tool definitions:

```python
from typing import Optional, Literal
from pydantic import BaseModel, Field

class SearchPackagesInput(BaseModel):
    """Tool to search, count, or filter packages for the current user."""
    status_group: Optional[Literal["PENDING", "RELEASED", "OUTBOUND", "ALL"]] = Field(
        default="PENDING",
        description="Filter by lifecycle phase. Use PENDING for items awaiting pickup, RELEASED for past pickups."
    )
    carrier: Optional[str] = Field(
        default=None,
        description="Optional courier name filter (e.g. Amazon, FedEx, UPS, DHL, USPS)."
    )
    storage_type: Optional[Literal["ALL", "LOCKER", "SHELF"]] = Field(
        default="ALL",
        description="Filter by where the package is placed: LOCKER or manual mailroom SHELF."
    )
    days: Optional[int] = Field(
        default=None,
        description="Lookback window in days (e.g., 30 for the past month, 0 for today)."
    )

class GetPackageDetailsInput(BaseModel):
    """Tool to retrieve full 360-degree details for a single package."""
    identifier: str = Field(
        ...,
        description="The carrier tracking number, package UUID, PO number, or pickup passcode."
    )

class GetPackageTimelineInput(BaseModel):
    """Tool to retrieve chain of custody, dock arrival vs intake times, proof of delivery, or failed alerts."""
    identifier: str = Field(
        ...,
        description="The carrier tracking number or package ID."
    )

class GetUserPreferencesAndServicesInput(BaseModel):
    """Tool to check wheelchair accessibility, proxy pickup delegates, notification channels, or day-use lockers."""
    pass
```
