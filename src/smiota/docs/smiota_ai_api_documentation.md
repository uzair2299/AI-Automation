# Smiota Internal AI Service: API Reference & Payload Documentation

This document provides complete technical documentation for the internal AI endpoints exposed by `smiota-server` (`com.smiota.app.ai`). 

These endpoints are engineered with **strict Multi-Tenant Customer & Tenant isolation**, providing secure service-to-service communication with the Smiota AI Agent core (`smiota-ai`), webchat channels, mobile backends, and IVR voice systems.

---

## Table of Contents
1. [Multi-Tenant Isolation & Security Architecture](#1-multi-tenant-isolation--security-architecture)
   - [Base URL & Protocol](#base-url--protocol)
   - [Authentication Headers](#authentication-headers)
   - [Customer & Tenant Context Resolution Matrix](#customer--tenant-context-resolution-matrix)
   - [Defense-in-Depth Isolation Guarantees](#defense-in-depth-isolation-guarantees)
   - [Standard Error Payload Format](#standard-error-payload-format)
2. [Package Domain Endpoints](#2-package-domain-endpoints)
   - [1. Search & Summaries (`GET /internal/ai/packages`)](#1-search--summaries-get-internalaipackages)
   - [2. 360° Package Details (`GET /internal/ai/packages/{identifier}`)](#2-360-package-details-get-internalaipackagesidentifier)
   - [3. Chain of Custody & Audit Timeline (`GET /internal/ai/packages/{identifier}/timeline`)](#3-chain-of-custody--audit-timeline-get-internalaipackagesidentifiertimeline)
3. [User & Services Domain Endpoints](#3-user--services-domain-endpoints)
   - [4. User Profile, ADA & Day-Use Pods (`GET /internal/ai/users/profile-and-services`)](#4-user-profile-ada--day-use-pods-get-internalaiusersprofile-and-services)
4. [Authentication Exchange Endpoint](#4-authentication-exchange-endpoint)
   - [5. Auth Token Exchange (`POST /internal/ai/auth/exchange`)](#5-auth-token-exchange-post-internalaiauthexchange)
5. [Complete Status Code Reference](#5-complete-status-code-reference)
6. [LLM Tool Calling & Extraction Quick Reference](#6-llm-tool-calling--extraction-quick-reference)

---

## 1. Multi-Tenant Isolation & Security Architecture

### Base URL & Protocol
* **Internal Network Base URL**: `http://127.0.0.1:8080` (or Docker service hostname `http://smiota-server:8080`)
* **Transport**: HTTP/1.1 or HTTP/2
* **Data Format**: `application/json; charset=UTF-8`

### Authentication Headers
All internal AI routes require authentication via a shared internal service secret:

| Header Name | Type | Description |
|---|---|---|
| `X-Internal-Service-Key` | String | Configured internal service shared token (e.g., `smiota-internal-ai-secret-key-production`). |
| `Authorization` | String | Alternative Bearer token format: `Bearer <INTERNAL_SERVICE_TOKEN>`. |

### Customer & Tenant Context Resolution Matrix
To prevent cross-tenant or cross-customer data leakage, every endpoint enforces boundaries at the database SQL layer. Context can be supplied either via an authenticated session token or explicit boundary headers/parameters:

| Context Dimension | Header | Query Parameter | Resolution via Session Token |
|---|---|---|---|
| **Customer Boundary** | `X-Customer-Id` | `customer_id` | Automatically resolved from `USER.customer_id` |
| **Tenant Boundary** | `X-Tenant-Id` | `tenant_id` | Automatically resolved from `USER.tenant_id` |
| **Location Boundary** | `X-Location-Id` | `location_id` | Automatically resolved from `USER.location_id` |
| **User / Recipient** | `X-User-Id` | `user_id` | Automatically resolved from `USER_SESSION.user_id` |
| **Session Token** | `X-Auth-Token` | `token` | Full profile resolved via `POST /internal/ai/auth/exchange` |

### Defense-in-Depth Isolation Guarantees
1. **Mandatory Scoping Guardrail**: All package search and listing queries require a verified `CUSTOMER_ID` or `RECIPIENT_ID`. Requests lacking both customer and user context are rejected immediately with `400 Bad Request` (`CUSTOMER_CONTEXT_REQUIRED`).
2. **Strict SQL Isolation**:
   - `package`: Enforces `p.CUSTOMER_ID = ?` and `(p.tenant_id = ? OR p.tenant_id IS NULL)`.
   - `user`: Enforces `u.CUSTOMER_ID = ?` and `(u.TENANT_ID = ? OR u.TENANT_ID IS NULL)`.
   - Sub-queries for chain of custody, signatures, proof of delivery, and notifications are only queried after verifying package ownership.
3. **Cross-Tenant Blocking**: An identifier (e.g. tracking number or package ID) belonging to Customer A cannot be viewed or located by Customer B or an unauthorized Tenant, returning `404 Not Found`.

### Standard Error Payload Format
```json
{
  "error_code": "CUSTOMER_CONTEXT_REQUIRED",
  "message": "Customer ID or User Context is required to enforce tenant isolation."
}
```

---

## 2. Package Domain Endpoints

### 1. Search & Summaries (`GET /internal/ai/packages`)

Retrieves packages matching multi-dimensional filters, along with aggregated counts broken down by storage mechanism (Locker vs. Shelf), perishable status, and urgent priority mail. Results are strictly filtered to the caller's Customer and Tenant boundaries.

#### Request Parameters (Query String & Headers)
| Parameter | Location | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `customer_id` | Query / Header (`X-Customer-Id`) | Long | Yes* | `null` | Customer enterprise boundary (*auto-resolved if token/user_id is passed). |
| `tenant_id` | Query / Header (`X-Tenant-Id`) | Long | No | `null` | Tenant organization boundary under the customer. |
| `location_id` | Query / Header (`X-Location-Id`) | Long | No | `null` | Facility or campus location ID. |
| `user_id` | Query / Header (`X-User-Id`) | Long | No | `null` | Recipient user ID. |
| `status_group` | Query | String | No | `PENDING` | `PENDING` (awaiting pickup), `RELEASED` (history), `OUTBOUND` (returns), `ALL`. |
| `carrier` | Query | String | No | `null` | Substring carrier search (e.g., `Amazon`, `FedEx`, `UPS`, `DHL`, `USPS`). |
| `storage_type` | Query | String | No | `ALL` | `LOCKER` (in smart locker), `SHELF` (mailroom shelf/counter), `ALL`. |
| `days` | Query | Integer | No | `null` | Lookback window: `0` for today, `30` for past month, `90` for past quarter. |
| `is_perishable` | Query | Boolean | No | `null` | Filter by cold-storage / perishable tag (`true` or `false`). |

#### Request Example (Scoped by Token)
```http
GET /internal/ai/packages?status_group=PENDING&carrier=Amazon HTTP/1.1
Host: 127.0.0.1:8080
X-Internal-Service-Key: smiota-internal-ai-secret-key-production
X-Auth-Token: 8e312a76-2f04-4b5b-9d41-3b7c8e90a12f
Accept: application/json
```

#### Request Example (Explicit Customer & Tenant Headers)
```bash
curl -X GET "http://127.0.0.1:8080/internal/ai/packages?status_group=PENDING&carrier=Amazon" \
  -H "X-Internal-Service-Key: smiota-internal-ai-secret-key-production" \
  -H "X-Customer-Id: 100" \
  -H "X-Tenant-Id: 12" \
  -H "X-User-Id: 4021"
```

#### Success Response (`200 OK`)
```json
{
  "total_count": 2,
  "summary": {
    "in_locker": 1,
    "on_shelf": 1,
    "perishable_count": 0,
    "urgent_count": 1
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
      "is_priority_mail": true
    },
    {
      "id": 10518,
      "tracking_number": "TBA092148912000",
      "carrier": "Amazon",
      "status": "READY_FOR_PICKUP",
      "storage_type": "SHELF",
      "building_name": "East Campus Commons",
      "locker_bank": null,
      "locker_name": null,
      "received_time": "2026-10-23T11:45:00Z",
      "expiration_time": "2026-10-30T18:00:00Z",
      "is_perishable": false,
      "didnt_fit": true,
      "is_priority_mail": false
    }
  ]
}
```

---

### 2. 360° Package Details (`GET /internal/ai/packages/{identifier}`)

Unified single-package inspection endpoint. Resolves packages across multiple identifier formats (carrier tracking number, package UUID, PO number, external ERP ID, release passcode, or database ID) while guaranteeing strict Customer and Tenant isolation.

#### Request Parameters
| Parameter | Location | Type | Required | Description |
|---|---|---|---|---|
| `identifier` | Path | String | Yes | Tracking number (e.g. `1Z9999999999999999`), UUID, PO number (`PO-88421`), or passcode. |
| `X-Customer-Id` | Header | Long | No* | Scopes lookup to specified Customer ID (*auto-resolved from token or user ID). |
| `X-Tenant-Id` | Header | Long | No | Scopes lookup to specified Tenant ID. |
| `X-User-Id` | Header | Long | No | Scopes lookup to recipient user. |

#### Request Example
```http
GET /internal/ai/packages/1Z9999999999999999 HTTP/1.1
Host: 127.0.0.1:8080
X-Internal-Service-Key: smiota-internal-ai-secret-key-production
X-Customer-Id: 100
X-Tenant-Id: 12
X-User-Id: 4021
Accept: application/json
```

```bash
curl -X GET "http://127.0.0.1:8080/internal/ai/packages/1Z9999999999999999" \
  -H "X-Internal-Service-Key: smiota-internal-ai-secret-key-production" \
  -H "X-Customer-Id: 100" \
  -H "X-Tenant-Id: 12" \
  -H "X-User-Id: 4021"
```

#### Success Response (`200 OK`)
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
      "length_in": 14.50,
      "width_in": 10.00,
      "height_in": 8.00
    },
    "didnt_fit": false,
    "is_perishable": false,
    "is_priority_mail": false,
    "package_type": "Standard Box",
    "number_of_subitems": 1
  },
  "origin_info": {
    "sender_name": "Amazon Fulfillment Services",
    "sender_company": "Amazon.com, Inc.",
    "has_label_photo": true,
    "ocr_text_preview": "SHIP TO: ALEX JOHNSON APARTMENT 4B EAST CAMPUS COMMONS..."
  }
}
```

#### Cross-Tenant Rejection (`404 Not Found`)
If the package exists under Customer 200, but is requested with Customer 100 or Tenant 99, the server immediately rejects access:
```json
{
  "error_code": "PACKAGE_NOT_FOUND",
  "message": "Package [1Z9999999999999999] was not found for the specified customer/tenant."
}
```

---

### 3. Chain of Custody & Audit Timeline (`GET /internal/ai/packages/{identifier}/timeline`)

Returns the chronological audit trail of a parcel since arrival, carrier dock vs. intake reconciliation, staff handling logs, proof-of-delivery (signatures/photo ID), and alert delivery logs.

#### Request Example
```http
GET /internal/ai/packages/1Z9999999999999999/timeline HTTP/1.1
Host: 127.0.0.1:8080
X-Internal-Service-Key: smiota-internal-ai-secret-key-production
X-Customer-Id: 100
X-Tenant-Id: 12
X-User-Id: 4021
Accept: application/json
```

```bash
curl -X GET "http://127.0.0.1:8080/internal/ai/packages/1Z9999999999999999/timeline" \
  -H "X-Internal-Service-Key: smiota-internal-ai-secret-key-production" \
  -H "X-Customer-Id: 100" \
  -H "X-Tenant-Id: 12" \
  -H "X-User-Id: 4021"
```

#### Success Response (`200 OK`)
```json
{
  "tracking_number": "1Z9999999999999999",
  "status": "READY_FOR_PICKUP",
  "carrier_reconciliation": {
    "carrier_reported_dock_arrival": "2026-10-23T09:00:00Z",
    "smiota_central_intake_scan": "2026-10-23T09:15:00Z",
    "building_transit_arrival": "2026-10-23T10:05:00Z",
    "locker_deposit_time": "2026-10-23T10:20:00Z",
    "status_explanation": "Package was scanned into Smiota at 2026-10-23T09:15:00Z and is currently stored in East Campus Commons (LOCKER)."
  },
  "chain_of_custody": [
    {
      "timestamp": "2026-10-23T09:15:00Z",
      "action": "Status updated to RECEIVED_AT_DOCK",
      "handled_by": "Marcus Vance",
      "location": "Central Sorting"
    },
    {
      "timestamp": "2026-10-23T09:45:00Z",
      "action": "Intra-Campus Transit / Building Hand-off",
      "handled_by": "Campus Courier Van 2",
      "location": "East Campus Commons - Route Transit"
    },
    {
      "timestamp": "2026-10-23T10:20:00Z",
      "action": "Status updated to READY_FOR_PICKUP",
      "handled_by": "Elena Rostova",
      "location": "East Campus Commons - Door 14"
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
      "destination": "+1 (555) 019-4820",
      "error_message": null
    },
    {
      "channel": "EMAIL",
      "dispatched_at": "2026-10-23T10:21:00Z",
      "status": "DELIVERED",
      "destination": "alex.johnson@campus.edu",
      "error_message": null
    }
  ],
  "exceptions_and_notes": {
    "has_problem_flag": false,
    "problem_reason": null,
    "staff_intake_notes": "Box in good condition upon intake."
  }
}
```

---

## 3. User & Services Domain Endpoints

### 4. User Profile, ADA & Day-Use Pods (`GET /internal/ai/users/profile-and-services`)

Retrieves user accessibility profile (ADA wheelchair bottom-tier enforcement), proxy delegation authorization, communication channel preferences, and active day-use personal storage reservations with Customer and Tenant boundaries enforced.

#### Request Parameters
| Parameter | Location | Type | Required | Description |
|---|---|---|---|---|
| `X-User-Id` / `user_id` | Header / Query | Long | Yes* | User ID to retrieve profile for (*auto-resolved if token is supplied). |
| `X-Customer-Id` / `customer_id` | Header / Query | Long | No | Customer boundary verification. |
| `X-Tenant-Id` / `tenant_id` | Header / Query | Long | No | Tenant boundary verification. |
| `X-Location-Id` / `location_id` | Header / Query | Long | No | Location ID verification. |

#### Request Example
```http
GET /internal/ai/users/profile-and-services HTTP/1.1
Host: 127.0.0.1:8080
X-Internal-Service-Key: smiota-internal-ai-secret-key-production
X-Customer-Id: 100
X-Tenant-Id: 12
X-User-Id: 4021
Accept: application/json
```

```bash
curl -X GET "http://127.0.0.1:8080/internal/ai/users/profile-and-services" \
  -H "X-Internal-Service-Key: smiota-internal-ai-secret-key-production" \
  -H "X-Customer-Id: 100" \
  -H "X-Tenant-Id: 12" \
  -H "X-User-Id: 4021"
```

#### Success Response (`200 OK`)
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
    "delegate_name": "Jordan Smith",
    "delegate_email": "jordan.smith@campus.edu",
    "alternate_recipients": [
      "Jordan Smith"
    ],
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
        "reservation_id": "res-88192",
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

## 4. Authentication Exchange Endpoint

### 5. Auth Token Exchange (`POST /internal/ai/auth/exchange`)

Exchanges a client session token or authentication code for the authenticated user profile with verified Customer, Tenant, and Location IDs.

#### Request Example
```http
POST /internal/ai/auth/exchange HTTP/1.1
Host: 127.0.0.1:8080
X-Internal-Service-Key: smiota-internal-ai-secret-key-production
Content-Type: application/json

{
  "code": "8e312a76-2f04-4b5b-9d41-3b7c8e90a12f"
}
```

```bash
curl -X POST "http://127.0.0.1:8080/internal/ai/auth/exchange" \
  -H "X-Internal-Service-Key: smiota-internal-ai-secret-key-production" \
  -H "Content-Type: application/json" \
  -d '{"code": "8e312a76-2f04-4b5b-9d41-3b7c8e90a12f"}'
```

#### Success Response (`200 OK`)
```json
{
  "valid": true,
  "id": 4021,
  "uuid": "u-4021-98a2-11ef",
  "firstName": "Alex",
  "lastName": "Johnson",
  "recipientName": "Alex Johnson",
  "email": "alex.johnson@campus.edu",
  "phone": "+1 (555) 019-4820",
  "customerId": 100,
  "tenantId": 12,
  "tenantName": "University Housing",
  "locationId": 5,
  "locationName": "Main Campus",
  "buildingId": 14,
  "buildingName": "East Campus Commons",
  "unitNo": "Apartment 4B",
  "passcode": "482910",
  "inactive": false,
  "roles": [
    "recipient",
    "resident"
  ]
}
```

---

## 5. Complete Status Code Reference

| HTTP Code | Error Code | Reason & Troubleshooting |
|---|---|---|
| `200 OK` | `null` | Success. The request returned the requested domain payload within the verified tenant boundary. |
| `400 Bad Request` | `CUSTOMER_CONTEXT_REQUIRED` | Missing required Customer or User context. Supply `X-Customer-Id` or `X-Auth-Token`. |
| `400 Bad Request` | `MISSING_IDENTIFIER` | Path identifier (tracking number or package ID) was empty. |
| `400 Bad Request` | `MISSING_USER_CONTEXT` | User ID or session token is required to retrieve profile services. |
| `401 Unauthorized` | `UNAUTHORIZED_SERVICE` | `X-Internal-Service-Key` or Bearer token is missing or invalid. |
| `404 Not Found` | `PACKAGE_NOT_FOUND` | Package not found, or belongs to a different Customer/Tenant. |
| `404 Not Found` | `USER_NOT_FOUND` | User profile not found within the specified Customer/Tenant boundary. |
| `500 Internal Error` | `INTERNAL_ERROR` | Unhandled database SQL error. Check server logs for full stack trace. |

---

## 6. LLM Tool Calling & Extraction Quick Reference

When wiring these endpoints into LLM tool-calling engines (`smiota-ai`), the multi-tenant context (`customer_id`, `tenant_id`, `location_id`, `user_id`) is automatically injected into each tool call by the agent session context:

```
User: "What is my pickup code for package 1Z9999999999999999?"
  │
  ▼ Autonomous Tool Call (with Multi-Tenant Scoping Injected):
get_package_details(identifier="1Z9999999999999999", customer_id=100, tenant_id=12, user_id=4021)
  │
  ▼ Backend executes parameterized SQL with Customer & Tenant isolation
  │
  ▼ Rich 360° JSON Payload returned
  │
  ▼ LLM Selective Extraction:
Extracts: { passcode: "482910", locker_door_name: "Door 14", locker_bank: "Main Pod Bank 1" }
  │
  ▼ Natural Agent Response:
"Your pickup code is 482910. Your package is waiting in Main Pod Bank 1, Door 14."
```
