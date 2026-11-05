# Smiota Core Business Domains Catalog

This catalog documents the **10 core business domains** discovered through deep analysis of the Smiota Server codebase. Each domain details its business responsibilities, underlying database tables, entities, repositories, service methods, APIs, access permissions, and query data requirements.

---

## 1. Package Intake, Tracking & Mailroom Operations

### Business Purpose
The primary domain of Smiota. Manages the lifecycle of packages from the moment a carrier or courier delivers them to a central mailroom or facility, through internal hub-and-spoke sorting, smart locker deposition, recipient notification, and final proof-of-delivery release.

### Database Tables & Entities
* **Tables**: `package`, `package_status`, `package_status_assignment`, `package_status_log`, `package_edit_log`, `package_release`, `package_release_blobs`, `package_type`, `customer_package_type`, `package_content_types`, `package_advanced_properties`, `sender`, `courier`, `courier_user`.
* **Entities**: `Package`, `PackageStatus` (Enum: -1 to 34), `PackageStatusGroupEnum`, `PackageRelease`, `PackageReleaseBlobs`, `Courier`, `Sender`, `CustomerPackageType`.

### Repositories & Key Services
* **DAOs**: `PackageDao` -> `PackageDaoImpl` (7,169 lines), `BaseDaoImpl`, `DB.java` (853 KB direct SQL).
* **Services & Managers**: `PackageService`, `PackageManagerImpl`, `AbstractPackageManagerImpl`, `BTPackageManagerImpl`, `CleanlyPackageManagerImpl`, `PickUpDeliverManager`.
* **Key Methods**:
  - `DB.getPackagesInStorage(locationId, customerId, userId, false)`
  - `PackageDaoImpl.getPackageStatusHistory(locationId, customerId, uuid)`
  - `PackageDaoImpl.getPackages(customerId, locationId, numericFilterParams, stringFilterParams, paginatedResult)`
  - `PackageManagerImpl.receivePackagesWithTrackingNumber(ctx, ...)`
  - `PackageManagerImpl.releasePackage(ctx, packageId, releaseRequestData)`

### Available APIs & Endpoints
* `GET /mypackagesinstorage`: Recipient's active uncollected packages ready for pickup.
* `GET /mydeliveredpackages`: Recipient's historically collected packages.
* `GET /packagecountbyrecipient`: Active package count for current recipient.
* `GET /api/v1/packages`: Comprehensive filtered package search (Admins/Tenant Admins).
* `GET /api/v1/package/status/history`: Chronological audit trail of all status transitions for a package UUID.
* `GET /api/v1/package/communication/history`: Notification history (SMS, email, app push) for a package.
* `GET /packages/signature`: Retrieves handwritten signature blob for released package.
* `POST /receivepackageswithtrackingnumber`: Check in incoming parcel by tracking number and recipient ID.
* `POST /packages/release/:statusId`: Releases package to recipient or courier with signature/ID photo.

### Business Rules & Edge Cases
* **Ready for Release Logic (`Package.isReadyForRelease()`)**: A package is eligible for recipient collection **only if** `!isOutbound` **AND** either:
  1. `atDestination == true` (explicitly overridden), OR
  2. `lockerId > 0` (deposited in a smart locker), OR
  3. `currentlyAtBuildingId == intendedForBuildingId` (has arrived at the recipient's assigned spoke building).
* If a package is checked in at a central Hub building, it remains in `COURIER_TO_MAILROOM` (5) or `IN_TRANSIT` (6) until transported to the spoke building.
* Packages marked `didntFit == true` cannot fit in physical lockers and are automatically redirected to the mailroom shelf.

### Permitted User Roles
* `RECIPIENT`: Access strictly limited to own packages (`RECIPIENT_ID = ctx.getUser().getId()`).
* `LOCATION_ADMIN`, `SMIOTA_LOCATION_ADMIN`: Scoped to all packages within their assigned location.
* `CUSTOMER_ADMIN`, `SUPER_USER`: Scoped across all customer locations.
* `TENANT_ADMIN`: Scoped to packages addressed to their assigned tenant/company unit.
* `COURIER`: Scoped to packages deposited/retrieved by that courier carrier.

### Data Freshness
* Current status, locker assignment, and mailroom location: **Real-time (live DB record)**.
* Status transitions, recorded times, and past actors: **Historical (from `package_status_log`)**.

---

## 2. Smart Lockers & Hardware Infrastructure (PoD)

### Business Purpose
Manages physical electronic locker units (Points of Distribution / PoD), hardware controllers, door latches, low-level bus addressing, environmental capabilities (ambient, refrigerated, freezer), and real-time operational status.

### Database Tables & Entities
* **Tables**: `locker_unit`, `locker`, `locker_unit_config`, `locker_controller`, `locker_controller_type`, `locker_unit_controller`, `locker_device_address`, `locker_size`, `locker_type`, `status_log`, `lock_codes`, `beacon`.
* **Entities**: `LockerUnit`, `Locker`, `LockerSize`, `LockerType`, `LockerUnitController`, `LockerDeviceAddress`, `LockerEvent`, `LockerSummary`.

### Repositories & Key Services
* **DAOs**: `LockerDao` -> `LockerDaoImpl`, `DB.java`, `DBReportsImpl`.
* **Services & Managers**: `LockerService`, `LockerManager` -> `LockerManagerImpl`.
* **Key Methods**:
  - `DB.getLockerUnitDetails(lockerUnitIds, locationId, customerId)`
  - `DB.checkLockersEligibility(map, lockerIds, apiAction, locationId, customerId)`
  - `DBReportsImpl.getLockerStateReportAsHTML()`, `getLockerStateReportAsCSV()`
  - `LockerManagerImpl.openLocker(ctx, lockerId, packageId)`

### Available APIs & Endpoints
* `GET /integration/api/v1/lockerUnit:lockers`: Live compartment status, dimensions, and occupancy for a PoD.
* `GET /locker/customer/:customerId/location/:locationId/units`: List of all locker units at a site.
* `GET /api/v1/locker/sizes`: Master list of compartment sizes (XS, S, M, L, XL).
* `GET /api/v1/locker/types`: Locker types (Ambient, Refrigerated, Heated).
* `POST /openlocker`: Remotely fires the electric solenoid latch to open a specific compartment.
* `POST /api/v1/updateLockerDeviceAddress/status`: Hardware bus status update from Urban app.
* `GET /audit/locker/summary/...`: Operational uptime, error rates, and compartment occupancy summary.

### Business Rules & Edge Cases
* **Locker Eligibility Check**: A compartment cannot be assigned for deposit if:
  1. `isInErrorState == true` or `statusCode >= 400`
  2. `inactive == true`
  3. `packages.size() > 0` (unless multi-package consolidation is specifically active)
  4. `reserves.size() > 0` (reserved for another recipient)
* **Wheelchair / ADA Accessibility**: If `user.wheelChairAccess == true`, the allocation algorithm strictly restricts compartment selection to lockers flagged `adaCompliant == true` (typically bottom rows 1–3).

### Permitted User Roles
* `LOCATION_ADMIN`, `CUSTOMER_ADMIN`, `SUPER_USER`: Full visibility into locker states, error logs, and door overrides.
* `LOCKER_UNIT`: The kiosk terminal user account performing deposit/retrieval operations.
* `PARTNER_INTEGRATION`: Authorized partner systems querying compartment availability.

### Data Freshness
* Compartment occupancy, latch state, and fault status: **Real-time (live DB + hardware telemetry)**.
* Historical error frequency and recovery events: **Historical (from `status_log`)**.

---

## 3. Orders & Package Groups (IT Asset Provisioning & BOPIS)

### Business Purpose
Coordinates multi-package orders and multi-step equipment workflows. Designed for two specialized operational flows:
1. **IT Flow**: Enterprise asset provisioning where employees deposit broken laptops/devices into lockers (`Employee Deposit`), IT technicians retrieve them (`IT Picked Up`), perform repairs/provisioning, redeposit them (`IT Deposit`), and employees pick up the configured hardware (`Complete`).
2. **Food & Dining / Retail (BOPIS)**: Multi-item customer orders deposited in ambient or refrigerated lockers with partial or complete customer retrieval.

### Database Tables & Entities
* **Tables**: `package_group`, `package_group_package`, `package_group_status`, `package_group_status_log`, `package_group_status_transition`, `package_group_status_transition_log`.
* **Entities**: `PackageGroup`, `PackageGroupStatusEnum` (1: Deposited, 3: Partial Retrieval, 4: Complete/Picked Up, 9: Sent Back, 16: Ready for Deposit, 17: Employee Deposit, 18: IT Picked Up, 19: IT Deposit).

### Repositories & Key Services
* **DAOs**: `PackageDaoImpl`, `DB.java`.
* **Services**: `PackageManagerImpl`, `PackageControllerImpl`.
* **Key Methods**:
  - `PackageDaoImpl.getOrders(...)`
  - `PackageControllerImpl`: `/api/v1/orders`, `/api/v2/order`
  - `PackageManagerImpl.validatePackageGroupStatusTransition(...)`

### Available APIs & Endpoints
* `GET /api/v1/orders`: Filtered query for active or completed orders/IT tickets.
* `GET /api/v2/order/:uuid`: Single order details with all constituent packages.
* `GET /ticketsInLocker`: Specific to IT flow — retrieves tickets currently awaiting IT technician pickup.
* `GET /assignedTickets`: Tickets assigned to a specific user or technician.
* `POST /api/v2/order`: Creates a new multi-package order or IT service ticket.
* `GET /package/group/status/history`: Chronological audit trail of ticket handovers.

### Business Rules & Edge Cases
* State transitions are strictly enforced via `package_group_status_transition`. An order cannot skip steps (e.g., cannot move from `Ready for Deposit` directly to `Complete` without passing through `Deposited` or `IT Picked Up`).
* When `locationProperties.isItFlow == true`, the UI and API adapt status groupings to IT terminology (Tickets, Employee Deposit, IT Pickup).

### Permitted User Roles
* `RECIPIENT`: Can view orders/tickets where they are the designated recipient.
* `LOCATION_ADMIN`, `CUSTOMER_ADMIN`: Full management of orders across the facility.
* `INVENTORY_WORKER` / IT Staff: Access to IT ticket queues.

---

## 4. Day-Use Smart Locks & Lockers

### Business Purpose
Manages shared, flexible storage for offices (hot-desking), gym lockers, or temporary visitor lockers using battery-powered smart locks (`lock`) grouped into day-use pods (`day_use_pod`).

### Database Tables & Entities
* **Tables**: `lock`, `day_use_pod`, `lock_codes`.
* **Entities**: `Lock`, `DayUsePod`.
* **Key Enums**: `RoleEnum.DAY_USE_ADMIN`, `DAY_USE_USER`, `DAY_USE_RESERVER`.

### Repositories & Key Services
* **DAOs**: `DB.java`, `BaseDaoImpl`.
* **Controllers**: `DayUseController` -> `DayUseControllerImpl`.

### Available APIs & Endpoints
* `GET /v1/locks`: List smart locks with filters (`assigned_to`, `podId`, `inactive`, `wheelchair`).
* `PUT /v1/locks/:uuid/reserve/:userId`: Assigns or reserves a day-use smart lock for a specific user.
* `PUT /v1/locks/:uuid/release`: Releases the smart lock, clears user assignment, and resets passcode.
* `GET /v1/locks/:uuid/reserve/history`: Historical audit of users who previously used this lock.
* `GET /v1/locks/util-history`: Utilization metrics and daily occupancy trends for smart locks.

### Business Rules & Edge Cases
* `lock.battery_percentage` tracks battery health; low battery triggers operational maintenance alerts.
* Smart locks support dynamic PIN generation (`passcode`) delivered to the user via app or SMS upon reservation.

### Permitted User Roles
* `DAY_USE_USER`: Can view their currently assigned lock, PIN, and pod location.
* `DAY_USE_ADMIN`, `LOCATION_ADMIN`: Can reassign, force-release, or view utilization across all locks.

---

## 5. Locker Reservations & Compartment Consolidation

### Business Purpose
Enables advance reservation of locker compartments for incoming shipments, scheduled courier drop-offs, and multi-package consolidation (placing multiple parcels for the same recipient into a single locker to maximize capacity).

### Database Tables & Entities
* **Tables**: `reserve`, `reserve_package`, `reserve_status`, `reserve_log`, `reserve_package_log`, `reserve_status_transition`.
* **Entities**: `Reserve`, `ReservePackage`, `ReserveStatusEnum` (HOLD, CONFIRMED, CANCELLED, COMPLETE).
* **Manager**: `ReserveManager` -> `ReserveManagerImpl`, `LockerConsolidateManager`.

### Available APIs & Endpoints
* `POST /v1/reservation`: Creates an advance locker reservation (starts in `HOLD` or `CONFIRMED`).
* `GET /v1/reservation`: Queries active reservations by user, location, or customer.
* `POST /v1/reservation/lockerConsolidate`: Consolidates multiple packages for a single recipient into one door.
* `GET /v1/reservation/transitions`: Valid next states for a reservation.

### Business Rules & Edge Cases
* Expired `HOLD` reservations are automatically cleaned up by `CleanUpReserveLockersJob.java`.
* Consolidation requires that all packages belong to the exact same recipient and location, and fit within the total cubic dimensions of the designated compartment.

---

## 6. Multi-Tenancy, Facilities & Hierarchy

### Business Purpose
Enforces rigid multi-tenant data isolation and models physical campus layouts: Distributors -> Customers -> Locations -> Buildings (Hubs vs Spokes) -> Tenants (Suites/Apartments) -> Users.

### Database Tables & Entities
* **Tables**: `customer`, `location`, `location_properties`, `building`, `delivery_building`, `tenant`, `user_tenants`, `distributor`, `distributor_customer`.
* **Entities**: `Customer`, `Location`, `Building`, `Tenant`, `Distributor`.

### Key Relationships & Data Logic
* **Hub and Spoke Routing**:
  - `building.PACKAGE_HUB = 1` designates a central receiving facility.
  - Packages scanned at a Hub set `buildingId = Hub.ID` and `intendedForBuildingId = Spoke.ID`.
  - The package is routed via `IN_TRANSIT` status to the Spoke building for final pickup.
* **Custom Tenant Terminology**: `location.tenantLabel` allows each property to customize labels (e.g., "Apartment", "Suite", "Department", "Company").

---

## 7. Identity, Access & Role-Based Permissions

### Business Purpose
Authenticates users and enforces authorization scopes across 19 discrete roles and 6 hierarchy levels.

### Key Enums & Roles
* **Levels (`RoleLevelEnum`)**: `SYSTEM` (1), `ADMIN` (2), `MANAGER` (3), `INTERNAL` (4), `WORKER` (5), `REPORTER` (6).
* **Roles (`RoleEnum`)**:
  - `SUPER_USER` (1): Global access across all customers and locations.
  - `CUSTOMER_ADMIN` (2): Enterprise admin across all sites of a single customer.
  - `LOCATION_ADMIN` (3): Scoped to a specific physical location.
  - `RECIPIENT` (4): End recipient; can only see own packages and assigned locks.
  - `LOCKER_UNIT` (5): Kiosk user for PoD terminals.
  - `COURIER` (6): Delivery driver account.
  - `TENANT_ADMIN` (17): Scoped to a company or apartment tenant within a building.
  - `MAINT_ADMIN` (9), `MAINT_WORKER` (10): Maintenance technicians.
  - `INVENTORY_WORKER` (12): Stock room / parts inventory staff.
  - `SHIFT_MANAGER` (18): Shift supervisor managing workers and shift assets.
  - `DAY_USE_*` (20-23): Day-use locker administrators and users.

---

## 8. Multi-Channel Notifications & Communications

### Business Purpose
Dispatches timely pickup alerts, reminder notices, delivery verification codes, and hardware fault notifications across SMS, Email, Push Notification, and Voice.

### Channels & Providers
* **SMS**: Twilio (`package_communication_sms`, `TwilioService`).
* **Transactional Email**: SendGrid / SMTP (`package_communication_email`, `SendGridService`).
* **Push Notifications**: Firebase Cloud Messaging (`package_communication_app`, `FirebaseNotificationService`).
* **Automated Voice Calls**: Twilio Voice (`package_communication_voice`).

### Automated Quartz Notification Jobs
* `NotifyRecipients.java`: Dispatches initial delivery notice with pickup PIN / QR link upon intake/deposit.
* `RemindRecipientsForPendingPackages.java`: Scheduled cron job reminding users of uncollected parcels.
* `NotifyRecipientExpiredPackages.java`: Alerts recipients when packages exceed max holding time.
* `NotifyAdminsOfPendingPackages.java`: Daily summary to mailroom staff of packages awaiting pickup.

---

## 9. Maintenance, Service Tasks & Work Orders

### Business Purpose
Schedules, assigns, and tracks preventative and corrective maintenance across smart locker banks, including latch lubrication, screen calibration, sensor checks, and locker cleaning.

### Database Tables & Entities
* **Tables**: `maint_type`, `maint_frequency`, `maint_location`, `maint_schedule`, `maint_service`, `maint_task`, `maint_service_task`, `maint_task_product`.
* **Entities**: `MaintType`, `MaintFrequencyEnum` (Daily, Weekly, Monthly, Quarterly, Semi-Annual, Annual), `MaintSchedule`, `MaintService`, `MaintTask`.

### Available APIs
* `GET /maintenance/customer/:customerId/location/:locationId/services`: Work orders and service records.
* `GET /maintenance/customer/:customerId/location/:locationId/tasks`: Maintenance checklists.
* `GET /maintenance/customer/:customerId/location/:locationId/reports/services/status`: Service completion reports.

---

## 10. Inventory Management, Spare Parts & Shifts

### Business Purpose
Tracks hardware inventory (spare controller boards, electric latches, antennas, sensors) and manages facility worker shifts and associated physical asset tags.

### Database Tables & Entities
* **Tables**: `product`, `product_inventory`, `product_inventory_status`, `product_inventory_status_log`, `product_package`, `shift`, `shift_asset`.
* **Entities**: `Product`, `ProductInventory`, `ProductInventoryStatusEnum` (ORDERED, RECEIVED_INTO_INVENTORY_ROOM, RELEASED_FROM_INVENTORY_ROOM, RELEASED_TO_SERVICE_ROOM), `Shift`.

### Available APIs
* `GET /inventory/api/v1/products`: Product catalog and minimum stock levels.
* `GET /inventory/api/v1/productInventories`: Serialized physical parts and MAC addresses.
* `GET /admin/inventory/api/v1/report/productInventoryTransactions`: Inventory movement audit report.
* `GET /v1/shifts`: Staff shifts with days of week and assigned shift managers.
* `GET /v1/shifts/filters`: Shift filtering parameters.
