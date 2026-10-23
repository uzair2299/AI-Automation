# Smiota Business Workflows & Lifecycle State Machines

This document outlines the core business workflows, state transitions, and operational execution flows discovered in the Smiota Server codebase.

---

## 1. Package Intake, Routing & Release Lifecycle

```mermaid
stateDiagram-v2
    [*] --> RECEIVED : Courier Delivery to Mailroom
    [*] --> ATTEMPTED_TO_DELIVER : Direct Courier Deposit into PoD Locker
    
    RECEIVED --> COURIER_TO_MAILROOM : Logged at Central Hub
    COURIER_TO_MAILROOM --> IN_TRANSIT : Dispatched to Spoke Building
    IN_TRANSIT --> DELIVERED_TO_BUILDING : Arrived at Spoke Mailroom
    
    DELIVERED_TO_BUILDING --> ATTEMPTED_TO_DELIVER : Deposited into Spoke Locker
    DELIVERED_TO_BUILDING --> RELEASED : Handed Over at Mailroom Counter
    
    ATTEMPTED_TO_DELIVER --> RELEASED : Recipient Collects (PIN/QR Code)
    ATTEMPTED_TO_DELIVER --> HOLD : Locker Fault / Problem Flagged
    HOLD --> ATTEMPTED_TO_DELIVER : Problem Resolved
    
    ATTEMPTED_TO_DELIVER --> SENT_BACK : Exceeded Max Hold Days (Unclaimed)
    DELIVERED_TO_BUILDING --> SENT_BACK : Unclaimed at Mailroom Shelf
    
    RELEASED --> [*] : Completed Handover
    SENT_BACK --> [*] : Returned to Courier/Shipper
```

### Step-by-Step Intake & Processing Logic

1. **Carrier Intake & Scanning**:
   - The courier scans carrier barcodes via mobile terminal or PoD kiosk (`/receivepackageswithtrackingnumber`).
   - The system checks `courier` table or matches tracking pattern (FedEx, UPS, USPS, Amazon).
2. **Recipient & Tenant Matching**:
   - The system attempts exact matching on recipient name, email, or unit number.
   - If not found, fuzzy search evaluates `user` and `tenant` records scoped to `ctx.getUser().getLocationId()`.
3. **Special Handling & Tag Evaluation**:
   - Active tags in `tag` table are evaluated for the recipient:
     - **Vacation Hold**: Package status set to `HOLD` (33); delivery notifications suspended.
     - **Alternate Recipient**: If `alternate_recipient` is designated, notifications route to the proxy recipient.
     - **Alternate Address**: Package flagged for rerouting to another building/location.
     - **Signature Waiver**: If `signature_waived == 1`, mailroom counter staff can bypass physical signature capture.
4. **Deposit vs. Shelf Decision**:
   - If a smart locker is available and the parcel fits dimensions, status becomes `ATTEMPTED_TO_DELIVER` (4).
   - If no locker fits, or all lockers of suitable size are occupied, or parcel is flagged `didntFit == true`, parcel remains in the mailroom shelf at `DELIVERED_TO_BUILDING` (1) or `RECEIVED` (0).
5. **Notification Dispatch**:
   - An entry is created in `package_communication`.
   - `NotifyRecipients.java` dispatches pickup PIN, QR link, and location details via SMS (Twilio), Email (SendGrid), and Push Notification (Firebase).

---

## 2. Hub-and-Spoke Facility Routing Workflow

In large university campuses or corporate facilities, packages arrive at a central receiving warehouse (Hub) and are transported to individual residential halls or office towers (Spokes).

```mermaid
flowchart TD
    A["Package Arrives at Central Warehouse (Building.PACKAGE_HUB = 1)"] --> B["Intake Scan at Hub (/receivepackages)"]
    B --> C["System Identifies Intended Spoke Building from Recipient User Profile"]
    C --> D{"Recipient Assigned to Hub?"}
    D -- Yes --> E["Ready for Pickup at Hub Mailroom"]
    D -- No --> F["Package Status set to IN_TRANSIT (6)"]
    F --> G["Transit Manifest Generated for Internal Drivers"]
    G --> H["Physical Transfer to Spoke Building"]
    H --> I["Arrival Scan at Spoke Facility"]
    I --> J{"Deposit in PoD Locker or Mailroom Shelf?"}
    J -- Locker --> K["Deposited into Locker: ATTEMPTED_TO_DELIVER (4)"]
    J -- Mailroom --> L["Staged on Shelf: DELIVERED_TO_BUILDING (1)"]
    K --> M["Recipient Notified of Spoke Pickup"]
    L --> M
```

### Readiness Evaluation Rule: `Package.isReadyForRelease()`
The application code in `WEB-INF/src/com/smiota/app/domainmodel/Package.java` (lines 401–407) enforces this exact rule:
```java
public boolean isReadyForRelease() {
    if (isOutbound) 
        return false;
    else
        return (this.atDestination) ? true : 
            (getLockerId() > 0 || getCurrentlyAtBuildingId() == getIntendedForBuildingId());
}
```
* If a package is physically at Building 1 (Hub) but intended for Building 5 (Spoke), `getCurrentlyAtBuildingId() != getIntendedForBuildingId()`, so it is **NOT ready for pickup**, unless the operator sets `atDestination = true`.
* The AI chatbot must check this condition before telling a recipient their package is ready for collection!

---

## 3. Smart Locker Auto-Sizing & Deposition Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Courier as Courier / Operator
    participant Kiosk as Smiota Urban Kiosk
    participant Server as Smiota Server Backend
    participant DB as Smiota MySQL DB
    participant Hardware as Locker Controller Board
    actor Recipient as Recipient

    Courier->>Kiosk: Authenticates (Badge / PIN)
    Kiosk->>Server: POST /authenticatecourier
    Server-->>Kiosk: Session Token & Authorized Building
    Courier->>Kiosk: Scans Tracking Number & Selects Recipient
    Kiosk->>Server: Request Compartment Allocation
    Server->>DB: Query available lockers in PoD
    Note over Server,DB: Filters out error states, occupied lockers, and matches ADA if wheelchair user
    Server->>Hardware: Fire Solenoid Latch for Locker #14
    Hardware-->>Kiosk: Door 14 Pops Open
    Courier->>Kiosk: Inserts Package & Closes Door
    Hardware->>Kiosk: Door Closed Sensor Triggered
    Kiosk->>Server: POST /updatelockerstatus (Locker 14: Occupied, Pkg ID)
    Server->>DB: Update package.locker_id = 14, status = 4 (ATTEMPTED_TO_DELIVER)
    Server->>DB: Generate 6-digit Pickup Passcode & QR Token
    Server->>Recipient: Dispatch Multi-Channel Pickup Notification
```

---

## 4. Proof-of-Delivery (POD) & Package Handover Workflow

When releasing a package at an attended counter or mailroom desk:

```mermaid
flowchart TD
    A["Recipient Arrives at Mailroom Counter"] --> B["Operator Scans Tracking Number or Searches Recipient Name"]
    B --> C["System Displays Package Details & Identifies Required Handover Rules"]
    C --> D{"Signature Required?"}
    D -- "Waived by Tag" --> G["Bypass Signature"]
    D -- "Required" --> E["Recipient Signs on Stylus / Touchscreen"]
    E --> F["Signature Stored in PACKAGE_RELEASE_BLOBS.SIGNATURE"]
    F --> G["Operator Checks ID"]
    G --> H["Record ID Type & Number (e.g. Student ID, Driver's License)"]
    H --> I["Optional: Photo of Recipient/ID captured in PACKAGE_RELEASE_BLOBS.ID_PHOTO"]
    I --> J["Operator Clicks Confirm Release (/packages/release/:statusId)"]
    J --> K["Status changes to RELEASED (2) in PACKAGE table"]
    K --> L["Audit Log appended to PACKAGE_STATUS_LOG & PACKAGE_RELEASE"]
```

---

## 5. Enterprise IT Equipment Provisioning Workflow (IT Flow)

For corporate customers using Smiota for IT service management (laptops, peripherals, replacement parts):

```mermaid
stateDiagram-v2
    [*] --> READY_FOR_DEPOSIT : Ticket Created in ITSM
    READY_FOR_DEPOSIT --> EMPLOYEE_DEPOSIT : Employee Drops Device in Locker
    EMPLOYEE_DEPOSIT --> IT_PICKED_UP : IT Technician Retrieves Device
    
    state "IT Repair & Configuration" as WorkState {
        IT_PICKED_UP --> Diagnostics : Hardware Check
        Diagnostics --> Provisioning : OS & Security Image
        Provisioning --> QualityCheck : QA Testing
    }
    
    QualityCheck --> IT_DEPOSIT : IT Technician Drops Ready Device in Locker
    IT_DEPOSIT --> COMPLETE : Employee Collects Ready Device
    COMPLETE --> [*] : Ticket Closed
```

* **Group Status Mapping**:
  - `Ready for Deposit` (`id = 16`)
  - `Employee Deposit` (`id = 17`)
  - `IT Picked Up` (`id = 18`)
  - `IT Deposit` (`id = 19`)
  - `Complete` (`id = 4`)
* **Endpoint Evidence**: Handled via `GET /ticketsInLocker`, `GET /assignedTickets`, and `GET /api/v1/orders?show=...` in `PackageControllerImpl.java` (lines 1266–1287).

---

## 6. Food & Dining / Retail (BOPIS) Workflow

For grocery, campus dining, and retail customers with temperature-sensitive deliveries:

```mermaid
stateDiagram-v2
    [*] --> READY_TO_DEPOSIT : Order Placed
    READY_TO_DEPOSIT --> DEPOSITED : Merchant Deposits in Ambient/Chilled/Freezer Locker
    
    DEPOSITED --> PARTIAL_RETRIEVAL : Customer Picks Up Part of Multi-Bag Order
    PARTIAL_RETRIEVAL --> PICKED_UP : Customer Picks Up Remaining Items
    DEPOSITED --> PICKED_UP : Full Pickup
    
    DEPOSITED --> SENT_BACK : Customer Never Picked Up / Food Expired
    PARTIAL_RETRIEVAL --> SENT_BACK : Remaining Items Expired
    
    PICKED_UP --> [*] : Completed Order
    SENT_BACK --> [*] : Order Discarded / Returned
```

* **Temperature Monitoring**: Refrigerator/Freezer lockers are continuously monitored via `TemperatureEventJob.java`. If temperature rises above `event_definition.max_value`, alerts are immediately dispatched to facility managers.

---

## 7. Automated Reminders & Expiration Workflow

```mermaid
flowchart TD
    A["Package Deposited / Staged (Day 0)"] --> B["Initial Notification Sent to Recipient with Pickup PIN"]
    B --> C{"Package Picked Up?"}
    C -- Yes --> D["Status = RELEASED (2)"]
    C -- No --> E["24-48 Hours Elapsed"]
    E --> F["Quartz Job (RemindRecipientsForPendingPackages) Fires 1st Reminder"]
    F --> G{"Package Picked Up?"}
    G -- Yes --> D
    G -- No --> H["Configured Max Threshold Reached (e.g. 5-7 Days)"]
    H --> I["Quartz Job (NotifyAdminsOfPendingPackages) Alerts Mailroom Staff"]
    I --> J["Quartz Job (NotifyRecipientExpiredPackages) Warns Recipient of Return"]
    J --> K{"Operator Action"}
    K -- "Return to Sender" --> L["Status = SENT_BACK (3), Door Opened / Removed from Shelf"]
    K -- "Extend Grace Period" --> M["Operator Grants Additional Days"]
```

---

## 8. Automated Data Purge Lifecycle

To comply with data privacy policies and optimize database storage:

```mermaid
flowchart TD
    A["Scheduled Quartz Job (UserPurgeJob.java) Runs"] --> B["Reads DATA_PURGE_SETTINGS per Customer"]
    B --> C{"data_purge_settings.enable_data_purge == true?"}
    C -- No --> D["Skip Customer"]
    C -- Yes --> E["Calculates Cutoff Date: NOW minus data_purge_months (default 36)"]
    E --> F["Identifies RELEASED or SENT_BACK Packages older than Cutoff Date"]
    F --> G["Deletes Heavy Blobs in PACKAGE_RELEASE_BLOBS (Signatures & Photos)"]
    G --> H["Soft-Deletes or Removes Purged Records"]
    H --> I["Records Purged Statistics in DATA_PURGE_RESULT and USER_PURGE_RESULTS"]
    I --> J["Dispatches Summary Email to result_email"]
```
