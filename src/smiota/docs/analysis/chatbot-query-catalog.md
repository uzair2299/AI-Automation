# Smiota Chatbot Comprehensive User Query Catalog

This catalog outlines all meaningful natural-language queries that an AI chatbot can answer using existing Smiota application data, business logic, stored procedures, APIs, and documentation.

The queries are organized by **User Persona** and categorized across the six fundamental query archetypes:
* **A. Direct Data Retrieval** (Single record lookup)
* **B. Lists and Filtering** (Multi-record search with criteria)
* **C. Aggregation and Analytics** (Counts, sums, averages, metrics)
* **D. History and Audit** (Chronological transitions, timestamps, actors)
* **E. Relationships and Context** (Cross-entity associations)
* **F. Operational and Exceptions** (Delays, hardware errors, uncollected items)

---

## Persona 1: End Customer / Package Recipient (`RoleEnum.RECIPIENT`)

*Access strictly scoped to packages, smart locks, and preferences where `user_id = ctx.getUser().getId()`.*

### A. Direct Data Retrieval
1. **"Where is my package?"**
   * *Synonyms*: "What is the status of my parcel?", "Has my delivery arrived?", "Is my package ready for collection?", "Did my Amazon box get delivered?"
   * *Chatbot Answerability*: **Completely Supported**.
   * *Data Retrieved*: Status (`ATTEMPTED_TO_DELIVER`, `DELIVERED_TO_BUILDING`, `RECEIVED`, `RELEASED`), current building name, PoD locker unit name, locker compartment number (or mailroom shelf).
2. **"What is my pickup code?"**
   * *Synonyms*: "Can you give me my locker PIN?", "I lost my passcode", "What is my collection code?"
   * *Chatbot Answerability*: **Completely Supported** (with strict user verification).
   * *Data Retrieved*: `package.passcode` or `user.passcode`.
3. **"When was my package delivered?"**
   * *Synonyms*: "At what time was my parcel checked in?", "When did it arrive at the mailroom?"
   * *Chatbot Answerability*: **Completely Supported**.
   * *Data Retrieved*: `package.received_time` or `package.status_change_time` converted to location timezone.
4. **"Who delivered my package?"**
   * *Synonyms*: "Which carrier brought my box?", "Was it FedEx or UPS?"
   * *Chatbot Answerability*: **Completely Supported**.
   * *Data Retrieved*: `courier.NAME` or `package.COURIER`.
5. **"Who signed for my package?"**
   * *Synonyms*: "Who picked up my delivery?", "Did my roommate sign for this?"
   * *Chatbot Answerability*: **Completely Supported**.
   * *Data Retrieved*: `package_release.RELEASE_TO_NAME`, `package_release.TIME_RELEASED`.

### B. Lists and Filtering
6. **"Show all my packages currently waiting for pickup."**
   * *Synonyms*: "What do I have in the lockers right now?", "Which parcels haven't I picked up yet?"
   * *Chatbot Answerability*: **Completely Supported**.
   * *Data Retrieved*: List from `/mypackagesinstorage` (`status` in 0, 1, 4; `isReadyForRelease() == true`).
7. **"Show my package delivery history for the past 30 days."**
   * *Synonyms*: "List my past packages", "Show my delivered parcels"
   * *Chatbot Answerability*: **Completely Supported**.
   * *Data Retrieved*: List from `/mydeliveredpackages` filtered by date range.
8. **"Do I have any packages in the mailroom vs. the lockers?"**
   * *Synonyms*: "Are my packages at the front desk or in the PoD?", "Where do I go to get my stuff?"
   * *Chatbot Answerability*: **Completely Supported**.
   * *Data Retrieved*: Partitioned list based on `locker_id > 0` vs `locker_id IS NULL`.

### C. Aggregation and Analytics
9. **"How many packages do I have waiting for me?"**
   * *Synonyms*: "What's my package count?", "How many parcels do I have in storage?"
   * *Chatbot Answerability*: **Completely Supported**.
   * *Data Retrieved*: Count from `/packagecountbyrecipient`.

### D. History and Audit
10. **"What happened to my package after it was delivered?"**
    * *Synonyms*: "Show tracking history for my parcel", "Why did it move from the mailroom to the locker?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: Chronological steps from `package_status_log` (`RECORDED_TIME`, `STATUS_NAME`, `BUILDING_NAME`).

### E. Relationships and Context
11. **"Which building or mailroom is assigned to my apartment/office?"**
    * *Synonyms*: "Where is my mail center?", "What building do my packages go to?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: `building.NAME`, `building.ADDRESS_LINE1` from `user.building_id`.
12. **"Who is listed as my notification delegate?"**
    * *Synonyms*: "Is my assistant/roommate getting my package alerts?", "Who else gets notified when my box arrives?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: `user.delegates_notifications_to_user_named` from `user.delegates_notifications_to_user_id`.

### F. Operational and Exceptions
13. **"Why can't I pick up my package from the locker?"**
    * *Synonyms*: "Why is the locker not opening?", "Is the locker broken?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: Checks `locker.is_in_error_state`, `locker.status_code`, and whether passcode expired.
14. **"Why does tracking say delivered, but Smiota says awaiting delivery?"**
    * *Synonyms*: "Carrier says delivered but I don't have a code", "Why is my package in transit?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: Explains Hub-and-Spoke model: Package arrived at central campus Hub and is currently `IN_TRANSIT` (6) to the recipient's assigned building.

---

## Persona 2: Mailroom Operator / Facility Staff (`RoleEnum.LOCATION_ADMIN`, `SMIOTA_LOCATION_ADMIN`)

*Access scoped to all packages, lockers, recipients, and hardware within their assigned `location_id`.*

### A. Direct Data Retrieval
15. **"Find package with tracking number 1Z9999999999999999."**
    * *Synonyms*: "Lookup barcode...", "Who does tracking 1Z... belong to?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: Recipient name, apartment/unit, current status, building, locker number, check-in timestamp.
16. **"Which locker compartment is package #4508 stored in?"**
    * *Synonyms*: "What door has tracking #...?", "Where is package 4508 deposited?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: `locker_unit.NAME`, `locker.NAME`, `locker.SIZE`.

### B. Lists and Filtering
17. **"Show all packages received today that are still sitting on the mailroom shelves."**
    * *Synonyms*: "What packages need to be stocked into lockers?", "Show shelf packages for today."
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: `/api/v1/packages?show=2&fromdate=TODAY&statusId=0,1`.
18. **"List all packages currently in transit between Hub and Spoke buildings."**
    * *Synonyms*: "What packages are on the transfer truck?", "Show in-transit parcels."
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: `/api/v1/packages?statusId=6`.
19. **"Which packages couldn't fit into lockers today?"**
    * *Synonyms*: "Show oversize packages", "List didntFit parcels."
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: `package.didnt_fit = 1` for current location.

### C. Aggregation and Analytics
20. **"How many total packages were received today vs. released today?"**
    * *Synonyms*: "Today's mailroom intake count", "Today's package turnover"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: Aggregated counts from `/packagescountbyhour` or `/api/v1/packages`.
21. **"What is the current locker occupancy rate across the facility?"**
    * *Synonyms*: "How full are our PoDs?", "What percentage of lockers are occupied?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: `/occupancyreport` or `DBReportsImpl.getLockerStateReportAsHTML()` (Total, Available, Occupied, Error).
22. **"How many Medium and Large lockers are currently available in Building A?"**
    * *Synonyms*: "Do we have empty large lockers for delivery?", "Show free compartment counts by size."
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: Query `locker` joined with `locker_unit` where `building_id = :bId` and `packages.size() == 0` and `is_in_error_state == 0`.

### D. History and Audit
23. **"Who checked in package #8129 and who released it?"**
    * *Synonyms*: "Show staff audit for tracking 1Z...", "Which operator processed this parcel?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: `package.received_by_user_id` -> `user.NAME`, `package_release.RELEASED_BY_USER_ID` -> `user.NAME`.
24. **"Show the proof-of-delivery signature and timestamp for package #8129."**
    * *Synonyms*: "Did the student sign for this box?", "Pull the signature record."
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: `package_release.RELEASE_TO_NAME`, `TIME_RELEASED`, and signature confirmation via `/packages/signature`.

### E. Relationships and Context
25. **"Which recipient is assigned to Suite 402?"**
    * *Synonyms*: "Who lives in unit 402?", "List tenants in Suite 402."
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: Query `user` joined with `tenant` where `unit = '402'`.

### F. Operational and Exceptions
26. **"Which packages have been sitting uncollected in lockers for more than 5 days?"**
    * *Synonyms*: "Show overdue packages", "Which parcels have expired?", "List stagnant locker items."
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: Query `package` where `status = 4` and `received_time <= NOW() - 5 DAYS` or `hours_in_storage > 120`.
27. **"Which locker doors are currently reporting hardware errors or sensor faults?"**
    * *Synonyms*: "Show broken lockers", "Are any doors stuck open?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: Query `locker` where `is_in_error_state = 1` or `status_code >= 400` or `is_open = 1`.
28. **"Did our delivery SLA get breached for priority parcels today?"**
    * *Synonyms*: "Show SLA report", "Were priority packages delivered within the 2-hour window?"
    * *Chatbot Answerability*: **Completely Supported**.
    * *Data Retrieved*: `/api/v1/report/sla` evaluating `PackageUtil.verifySLAForPriorityPackage(...)`.

---

## Persona 3: Organization / Customer Administrator (`RoleEnum.CUSTOMER_ADMIN`, `SUPER_USER`)

*Access scoped across all campuses, locations, and buildings for the customer.*

### A. Direct Data Retrieval
29. **"Show location details and active settings for the Downtown Campus."**
    * *Data Retrieved*: `location` address, timezone, `location_properties` (BOPIS enabled, IT flow enabled, passcode expiration window).

### B. Lists and Filtering
30. **"List all active couriers delivering across our locations."**
    * *Data Retrieved*: `/v1/couriers` (Carrier name, driver count, integration status).
31. **"Show all users whose accounts are pending approval."**
    * *Data Retrieved*: `/users/pendingApproval` (Self-registered users awaiting administrative verification).

### C. Aggregation and Analytics
32. **"What was the total monthly package volume across all our locations for September?"**
    * *Data Retrieved*: `/monthlyreport` aggregated by location and carrier.
33. **"Show courier reconciliation counts: how many packages did FedEx deliver vs. UPS this month?"**
    * *Data Retrieved*: `/courierreconcilereport` (Intake breakdown by carrier).

### D. History and Audit
34. **"When was the last data purge run, and how many records were cleaned up?"**
    * *Data Retrieved*: `data_purge_result` (timestamp, customer ID, number of purged packages).

### E. Operational and Exceptions
35. **"Which locations currently have an error rate exceeding 5% on their smart lockers?"**
    * *Data Retrieved*: `DBReportsImpl.getLockerStateReportEmailBody(5)` comparing error doors to total doors per site.

---

## Persona 4: Day-Use Smart Lock User & Facility Admin (`DAY_USE_USER`, `DAY_USE_ADMIN`)

*Access scoped to shared day-use smart lockers and smart lock hardware.*

### A. Direct Data Retrieval
36. **"Which day-use locker is currently assigned to me?"**
    * *Data Retrieved*: `lock.label`, `day_use_pod.name`, `lock.passcode`, `lock.is_wheelchair_accessible`.
37. **"What is the unlock PIN for my assigned gym/office locker?"**
    * *Data Retrieved*: `lock.passcode`.

### B. Lists and Filtering
38. **"Show all available day-use lockers in Building 3, Floor 2."**
    * *Data Retrieved*: `/v1/locks?assignedToUserId=-1&inactive=false`.

### C. Aggregation and Analytics
39. **"What is the daily utilization rate of our day-use smart lockers this week?"**
    * *Data Retrieved*: `/v1/locks/util-history`.

### D. Operational and Exceptions
40. **"Which smart locks have low battery levels below 20%?"**
    * *Data Retrieved*: Query `lock` where `battery_percentage < 20`.

---

## Persona 5: Maintenance Technician & Facility Engineer (`MAINT_WORKER`, `MAINT_ADMIN`)

*Access scoped to locker maintenance work orders, schedules, and checklists.*

### A. Direct Data Retrieval
41. **"What maintenance tasks are scheduled for Locker Bank B today?"**
    * *Data Retrieved*: `/maintenance/.../tasks` (Cleaning, solenoid latch inspection, firmware check).
42. **"What is the status of Service Order #104?"**
    * *Data Retrieved*: `/maintenance/.../services` (Scheduled, In Progress, Completed, Passed/Failed).

### B. History and Audit
43. **"When was the last time the cooling unit in the Refrigerated Locker was inspected?"**
    * *Data Retrieved*: `maint_service` joined with `maint_service_task` where `maint_type` = 'Refrigeration Inspection'.

### C. Operational and Exceptions
44. **"Have there been any temperature threshold alerts triggered for refrigerated lockers in the last 24 hours?"**
    * *Data Retrieved*: `/api/v1/lockertemperaturealerts` from `event_definition_log`.

---

## Persona 6: Inventory & Shift Manager (`INVENTORY_WORKER`, `SHIFT_MANAGER`)

*Access scoped to spare parts inventory, stock levels, and shift staffing.*

### A. Direct Data Retrieval
45. **"How many replacement electronic door latches do we have in stock?"**
    * *Data Retrieved*: `/inventory/api/v1/products` joined with `product_inventory` where `status_id = 2` (RECEIVED_INTO_INVENTORY_ROOM).
46. **"Who is the shift manager on duty for the Central Mailroom right now?"**
    * *Data Retrieved*: `/v1/shifts` matching current day of week and current local time.

### B. Operational and Exceptions
47. **"Are any maintenance parts currently below their minimum threshold?"**
    * *Data Retrieved*: Quartz job `NotifyAdminsOfSubParProducts.java` comparing on-hand serialized inventory to product min stock levels.
48. **"Which physical asset tags are currently logged for Shift #4?"**
    * *Data Retrieved*: Query `shift_asset` joined with `shift`.
