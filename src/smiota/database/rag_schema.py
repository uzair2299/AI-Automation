"""RAG & Enterprise Smiota Schema Registry.

Categorizes the remaining 160+ database tables across enterprise domains:
- IoT Hardware Telemetry & Alarms
- Configuration & Feature Properties
- Maintenance & Preventative Schedules
- Auditing, HTTP Logs & Data Purge
- Identity, SAML & SCIM Integration
"""

from typing import Dict, List

RAG_ENTERPRISE_DOMAINS: Dict[str, Dict[str, str]] = {
    "telemetry_and_hardware_alarms": {
        "event": "Core catalog of hardware, lock, and system event definitions.",
        "event_definition": "Threshold rules (max_value, min_value, duration) for triggering sensor alerts.",
        "event_definition_log": "Audit logs of tripped sensor events, door jams, temperature violations, battery drops.",
        "locker_unit_controller": "Microcontroller boards controlling banks of solenoids and sensors.",
        "locker_device_address": "RS485 / CAN bus hardware addresses for locker modules.",
        "locker_device_type": "Hardware sensor classifications (optical, magnetic, vibration, temperature).",
        "beacon": "Bluetooth Low Energy (BLE) beacons mounted on lockers for resident mobile app proximity.",
        "beacon_global": "Master UUID registry for Bluetooth beacons.",
    },
    "maintenance_and_tasks": {
        "maint_schedule": "Recurring maintenance schedules for technicians.",
        "maint_frequency": "Frequency intervals (daily, weekly, monthly, quarterly).",
        "maint_service": "Service tickets and work orders for hardware repairs.",
        "maint_service_task": "Checklist tasks assigned to field engineers (replace latch, clean optical sensor).",
        "shift": "Technician operational shifts and schedule assignments.",
    },
    "configuration_and_feature_flags": {
        "config_props": "Master property keys for system-wide feature toggles.",
        "config_values": "Customer-specific and location-specific overrides for feature properties.",
        "customer_package_type": "Rules for special packages (e.g. dry cleaning, oversized, refrigerated).",
        "label_template_configs": "Barcode and QR print layout settings for parcel labels.",
        "auth_config": "SAML 2.0 / Okta / Azure AD IdP integration settings per customer.",
    },
    "auditing_and_data_compliance": {
        "admin_dashboard_log": "Audit trail of admin user actions in the Smiota management portal.",
        "api_result": "Historical log of inbound/outbound HTTP API transactions and response codes.",
        "data_purge_settings": "Retention rules for automated data purging (e.g. purge packages older than 36 months).",
        "data_purge_result": "Execution logs, record counts, and errors for data purge batch runs.",
        "package_edit_log": "Audit trail tracking manual modifications to package records.",
    },
    "identity_and_enterprise_directory": {
        "account": "User login accounts, password expiration timestamps, and failed login retries.",
        "role": "Role-based access control (Admin, SuperAdmin, Technician, PropertyManager).",
        "scim_user": "SCIM synchronized resident profiles from building HR/identity systems.",
        "scim_group": "Active Directory / Okta groups mapped to Smiota locker permissions.",
        "security_card": "RFID / NFC physical keycard badges assigned to staff.",
    },
}


def search_rag_schema(query: str, top_k: int = 5) -> List[str]:
    """Retrieve relevant domain tables matching query terms."""
    q = query.lower()
    matches = []
    for domain, tables in RAG_ENTERPRISE_DOMAINS.items():
        for table_name, desc in tables.items():
            if any(term in table_name for term in q.split()) or any(term in desc.lower() for term in q.split()):
                matches.append(f"Table `{table_name}` ({domain}): {desc}")
                if len(matches) >= top_k:
                    return matches
    return matches
