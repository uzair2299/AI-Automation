"""Core Smiota Smart Locker Database Schema for Live Text-to-SQL & Chat Agents.

Extracted directly from consolidated_schema.sql for the primary customer, resident,
package, and physical locker compartment operations.
"""

CORE_CUSTOMER_SCHEMA_PROMPT = """
=== SMIOTA CORE RELATIONAL DATABASE SCHEMA ===
Database Engine: MySQL 8.x

1. TABLE: `package`
   Primary entity storing parcel deliveries and pickup records.
   Columns:
   - `ID` (bigint, PK, AUTO_INCREMENT): Unique package identifier.
   - `tracking_number` (varchar(750)): Courier tracking ID or carrier barcode.
   - `PASSCODE` (varchar(100)): 6-digit PIN used by resident on kiosk to unlock locker.
   - `RECIPIENT_ID` (bigint, FK -> user.ID): Resident / recipient of package.
   - `LOCKER_ID` (bigint, FK -> locker.ID): Assigned physical locker compartment.
   - `CUSTOMER_ID` (bigint, FK -> customer.ID): Smiota customer account / tenant organization.
   - `LOCATION_ID` (bigint, FK -> location.ID): Campus or property facility location.
   - `currently_at_building_id` (bigint, FK -> building.ID): Building where package is physically stored.
   - `STATUS` (int): Delivery status code (e.g. deposited, ready, picked up, expired).
   - `COURIER` (varchar(1000)): Name of carrier (FedEx, UPS, Amazon, DHL, USPS).
   - `RECEIVED_TIME` (timestamp): Timestamp when carrier deposited package into locker.
   - `EXPIRATION_TIME` (timestamp): Timestamp when pickup window expires.
   - `status_change_time` (timestamp): Timestamp of last status update.
   - `is_deleted` (bit(1)): Soft-delete flag (0 = active, 1 = deleted).

2. TABLE: `locker`
   Represents individual physical smart locker doors / compartments.
   Columns:
   - `ID` (bigint, PK, AUTO_INCREMENT): Compartment ID.
   - `NAME` (varchar(255)): Compartment door number/label (e.g. "101", "B-14").
   - `SIZE` (int, FK -> locker_size.ID): Compartment dimensions (Small, Medium, Large).
   - `CUSTOMER_ID` (bigint, FK -> customer.ID): Customer property ID.
   - `IS_GATE_OPEN` (tinyint(1)): Door sensor (1 = open, 0 = closed).
   - `IS_IN_ERROR_STATE` (tinyint(1)): Hardware fault / jam flag (1 = error, 0 = normal).
   - `ERROR_MESSAGE` (varchar(1000)): Hardware fault diagnostics.
   - `STATUS_CODE` (varchar(64)): Operational status.
   - `INACTIVE` (tinyint(1)): 0 = active in service, 1 = disabled.

3. TABLE: `user`
   Residents, apartment occupants, and building recipients.
   Columns:
   - `ID` (bigint, PK, AUTO_INCREMENT): Resident user ID.
   - `FIRST_NAME` (varchar(60)): Resident first name.
   - `LAST_NAME` (varchar(60)): Resident last name.
   - `EMAIL` (varchar(255)): Resident email address.
   - `PHONE` (varchar(256)): Registered mobile phone number.
   - `UNIT_NO` (varchar(25)): Apartment / suite / office unit number.
   - `BUILDING_ID` (bigint, FK -> building.ID): Residential building.
   - `LOCATION_ID` (bigint, FK -> location.ID): Facility location.
   - `CUSTOMER_ID` (bigint, FK -> customer.ID): Property management customer ID.
   - `INACTIVE` (tinyint(1)): 0 = active resident, 1 = moved out.

4. TABLE: `building`
   Physical apartment buildings or office towers.
   Columns:
   - `ID` (bigint, PK, AUTO_INCREMENT): Building ID.
   - `NAME` (varchar(255)): Building name (e.g. "East Tower", "Building 3").
   - `ADDRESS_LINE1` (varchar(100)): Street address.
   - `CITY` (varchar(100)), `POST_CODE` (varchar(10)).
   - `LOCATION_ID` (bigint, FK -> location.ID): Associated facility.
   - `OFFICE_HOURS` (varchar(1000)): Building concierge and pickup operating hours.

5. TABLE: `location`
   High-level property, campus, or residential community.
   Columns:
   - `ID` (bigint, PK, AUTO_INCREMENT): Location ID.
   - `NAME` (varchar(255)): Location name (e.g. "Sunset Apartments").
   - `timezone` (varchar(100)): Local timezone (e.g. "America/New_York").
   - `SUPPORT_EMAIL` (varchar(50)), `SUPPORT_PHONE` (varchar(20)).

6. TABLE: `courier`
   Shipping carriers and delivery companies.
   Columns:
   - `ID` (int, PK, AUTO_INCREMENT): Courier ID.
   - `NAME` (varchar(200)): Internal courier identifier.
   - `DISPLAY_NAME` (varchar(255)): Public carrier name (e.g. "FedEx Express").

JOIN PATHS FOR COMMON QUERIES:
- Find package with locker door & building:
  SELECT p.tracking_number, p.PASSCODE as pin, p.STATUS, l.NAME as compartment, b.NAME as building, p.RECEIVED_TIME
  FROM package p
  LEFT JOIN locker l ON p.LOCKER_ID = l.ID
  LEFT JOIN building b ON p.currently_at_building_id = b.ID
  WHERE p.tracking_number = :tracking_number AND p.is_deleted = 0;

- Find resident packages by phone or email:
  SELECT p.tracking_number, p.PASSCODE as pin, l.NAME as compartment, b.NAME as building
  FROM package p
  JOIN user u ON p.RECIPIENT_ID = u.ID
  LEFT JOIN locker l ON p.LOCKER_ID = l.ID
  LEFT JOIN building b ON p.currently_at_building_id = b.ID
  WHERE (u.PHONE = :contact OR u.EMAIL = :contact) AND p.is_deleted = 0;
"""
