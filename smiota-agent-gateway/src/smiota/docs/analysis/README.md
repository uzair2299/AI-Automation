# Smiota Server — Codebase Discovery & AI Chatbot Capability Analysis

## Executive Summary

**Smiota Server** is an enterprise-grade smart locker and package delivery management platform deployed across commercial offices, residential communities, universities, retail (BOPIS — Buy Online, Pick Up In Store), and multi-tenant campuses. 

At its functional core, Smiota automates and coordinates the physical custody transfer of parcels, dry/refrigerated goods, and shared or provisioned equipment through three primary delivery channels:
1. **Physical Smart Lockers (PoDs)**: Hardware locker banks containing automated compartments (XS to XL sizes, ambient, chilled, or frozen) controlled via IoT controller boards, Bluetooth Low Energy (BLE) beacons, and touchscreen kiosks running the Smiota Urban Android application.
2. **Attended Mailrooms & Hubs**: Manual check-in and pickup counters with barcode/OCR scanning, routing between central hubs and spoke buildings, proof-of-delivery (POD) capture (signatures, ID photos), and automated recipient notifications.
3. **Day-Use Smart Locks & IT Provisioning**: Self-service lockers for temporary employee/visitor storage (hot-desking, gym lockers) and enterprise IT device drop-off/repair workflows.

### Chatbot Discovery Findings at a Glance

* **Total Database Tables**: 173 tables across migrations `v1` to `v223` (consolidated in `consolidated_schema.sql`).
* **Active Architectural Framework**: Java 8+, Google Guice (dependency injection), Spark Java (REST framework on embedded Jetty/Tomcat), C3P0 JDBC connection pooling, Quartz Scheduler (36 background/cron jobs).
* **Supported User Roles**: 19 discrete roles across 6 hierarchy levels (`SUPER_USER`, `CUSTOMER_ADMIN`, `LOCATION_ADMIN`, `TENANT_ADMIN`, `RECIPIENT`, `LOCKER_UNIT`, `COURIER`, `MAINT_ADMIN`, `MAINT_WORKER`, `INVENTORY_WORKER`, `DAY_USE_*`, `SHIFT_MANAGER`, etc.).
* **Primary Query Domains for AI Chatbot**:
  - **Package & Parcel Tracking**: 100% answerable for current status, locker assignment, mailroom location, pickup passcodes, delivery history, and courier tracking numbers.
  - **Locker Availability & Telemetry**: Current PoD occupancy, compartment size availability, temperature logs, and hardware fault status.
  - **Proof of Delivery & Handover**: Signatures, ID verification types/numbers, handover timestamps, and releasing personnel.
  - **Recipient & Notification Preferences**: Delegate users, alternate recipients, vacation/hold tags, SMS/email opt-outs, and uncollected package reminders.
  - **Day-Use Smart Locks & Reservations**: Battery percentage, passcode, user assignment, wheelchair accessibility, and reservation state.
  - **Operational & SLA Analytics**: Intake/release counts by hour/day, SLA breaches, overdue uncollected packages, and courier reconciliation metrics.

---

## Repository Coverage Checklist

| Repository Area | Path | Examination Status | Key Artifacts Analyzed |
| :--- | :--- | :---: | :--- |
| **Database Migrations** | `WEB-INF/db/mysql_migration/` | **Complete (100%)** | 220 migration files (`v26.sql` to `v223.sql`, `mysql.ddl`, seed scripts) |
| **Stored Routines** | `WEB-INF/db/procedure/`, `function/` | **Complete (100%)** | `init_package_status_for_customer_location.sql`, `GetUpdatedTenantsUsers.sql`, `get_maint_location_schedule_status.sql`, `GetUserRoleNames.sql` |
| **Consolidated Schema** | `consolidated_schema.sql` | **Complete (100%)** | 4,110 lines of verified DDL covering all 173 production tables |
| **Domain Models** | `WEB-INF/src/com/smiota/app/domainmodel/` | **Complete (100%)** | 90 Java classes (`Package`, `Locker`, `User`, `Tenant`, `Location`, `Building`, `Reserve`, `Shift`, etc.) |
| **Data Access Objects** | `WEB-INF/src/com/smiota/app/database/`, `*DaoImpl.java` | **Complete (100%)** | `DB.java` (853 KB direct SQL), `BaseDaoImpl.java`, `PackageDaoImpl.java` (7,169 lines), `LockerDaoImpl.java`, `UserDaoImpl.java`, `AdminDaoImpl.java`, etc. |
| **Service Layer** | `WEB-INF/src/com/smiota/app/service/`, `*ServiceImpl.java`, `*ManagerImpl.java` | **Complete (100%)** | `PackageManagerImpl.java`, `LockerManagerImpl.java`, `UserManagerImpl.java`, `NotificationService.java`, `AuthManagerImpl.java`, `ResManManagerImpl.java`, `AuditServiceImpl.java` |
| **REST Controllers & APIs** | `WEB-INF/src/com/smiota/app/MainApplication.java`, `*ControllerImpl.java` | **Complete (100%)** | `MainApplication.java` (6,675 lines, 120+ routes), `PackageControllerImpl.java` (4,355 lines), `LockerControllerImpl.java`, `UserControllerImpl.java`, `AdminControllerImpl.java`, etc. |
| **Async & Scheduled Jobs** | `WEB-INF/src/com/smiota/app/job/` | **Complete (100%)** | 36 Quartz jobs (`Scheduler.java`, `NotifyRecipients.java`, `RemindRecipientsForPendingPackages.java`, `OccupancyReportsJob.java`, etc.) |
| **Reporting Subsystem** | `WEB-INF/src/com/smiota/app/database/impl/DBReportsImpl.java`, `report/` | **Complete (100%)** | CSV & HTML report generators for Packages, Occupancy, Locker State, Courier Reconciliation, POD, and SLA |
| **Web UI Views** | `views/app/` | **Complete (100%)** | 60+ JSP/HTML views (`wheresMyPackage.jsp`, `packages.jsp`, `lockerunits.jsp`, `SLAReport.jsp`, `podReport.jsp`, `dashboard.jsp`) |
| **Third-Party Integrations** | `WEB-INF/src/com/smiota/app/integration/`, `com/smiota/external/` | **Complete (100%)** | Twilio (SMS/Voice), SendGrid/SMTP (Email), Firebase (FCM), AfterShip, Entrata, ResMan, SCIM 2.0, SAML 2.0, Google Directory, Tesla Robotaxi |
| **Unit & Integration Tests** | `test/`, `unittests/` | **Examined** | 26 test classes revealing business rules, SLA calculations, and edge cases |

---

## Detailed Discovery Documents Index

The detailed findings of this codebase investigation are organized into dedicated reference documents:

1. **[Database Schema Reference](file:///d:/repos/smiota-server/analysis/database-schema.md)**
   Comprehensive entity-relationship catalog, 173 database tables, column types, primary/foreign keys, implicit joins, soft-delete flags, audit timestamps, and Mermaid ER diagrams for the primary domains.
2. **[Core Business Domains](file:///d:/repos/smiota-server/analysis/core-domains.md)**
   In-depth documentation of all 10 discovered business domains: Packages & Mailroom, Smart Lockers (PoDs), Day-Use Smart Locks, Reservations & Consolidation, Multi-Tenancy Hierarchy, User Management & Authentication, Maintenance Management, Inventory & Spare Parts, Shifts & Staffing, and Tags & Redirection.
3. **[Business Workflows & Lifecycle State Machines](file:///d:/repos/smiota-server/analysis/business-workflows.md)**
   End-to-end operational workflows: Package Hub-and-Spoke intake and transit, Smart Locker auto-sizing and deposit, Recipient notification and PIN verification, Proof-of-Delivery handover, IT Asset Provisioning lifecycle, Food & Dining (BOPIS) flow, and Data Purge routines.
4. **[Security, Multi-Tenancy & Access Control](file:///d:/repos/smiota-server/analysis/security-and-access-control.md)**
   Tenant isolation model, session management, RBAC matrix across all 19 roles, field-level sensitivity classifications (passcodes, PINs, signatures, PII), and identified authorization vulnerabilities.
5. **[Comprehensive Chatbot Query Catalog](file:///d:/repos/smiota-server/analysis/chatbot-query-catalog.md)**
   Exhaustive catalog of real user queries organized by Persona (Recipient, Mailroom Operator, Location Admin, Customer Admin, Maintenance Tech, Support) and Query Intent (Direct Retrieval, Filtering, Aggregation, History, Operational Exceptions).
6. **[Query Capability Matrix](file:///d:/repos/smiota-server/analysis/query-capability-matrix.md)**
   13-column matrix mapping natural-language questions to required tables, fields, join paths, data access endpoints, freshness, business logic rules, and implementation status.
7. **[AI Architecture & Implementation Roadmap](file:///d:/repos/smiota-server/analysis/architecture-and-roadmap.md)**
   Target AI chatbot architecture combining LLM function calling, controlled read-only database query layer, row-level tenant security enforcement, high-priority intent traces, and a phased implementation roadmap from MVP to Enterprise.
