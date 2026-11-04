"""Unit tests for standalone Smart Locker MCP Server."""
import pytest

from app.server import (
    get_locker_status,
    query_locker_door_status,
    locker_open_compartment,
    package_lookup,
    resident_verify_pin,
    locker_list_compartments,
    locker_diagnose_hardware,
)


@pytest.mark.asyncio
async def test_get_locker_status():
    """Verify top-level locker status reporting."""
    res = await get_locker_status(locker_id="TEST-LOCKER-01")
    assert res["status"] == "ONLINE"
    assert res["locker_id"] == "TEST-LOCKER-01"
    assert res["total_compartments"] >= 1
    assert "temperature_zones" in res


@pytest.mark.asyncio
async def test_query_locker_door_status():
    """Verify compartment door and sensor query."""
    res = await query_locker_door_status(locker_id="TEST-LOCKER-01", compartment_id="C-01")
    assert res["status"] == "success"
    assert res["compartment_id"] == "C-01"
    assert res["door_state"] in ("OPEN", "CLOSED")
    assert "infrared_sensor" in res


@pytest.mark.asyncio
async def test_locker_open_compartment_approval_required():
    """Verify unauthorized opening requires approval."""
    res = await locker_open_compartment(locker_id="LOCKER-01", compartment_id="C-02")
    assert res["status"] == "requires_approval"
    assert "RemediationApprovalRequiredError" in res["error"]


@pytest.mark.asyncio
async def test_locker_open_compartment_with_pin():
    """Verify solenoid unlock with valid PIN."""
    res = await locker_open_compartment(
        locker_id="LOCKER-01", compartment_id="C-02", authorization_pin="482910"
    )
    assert res["status"] == "success"
    assert res["action"] == "solenoid_unlocked"
    assert res["door_state"] == "OPEN"
    assert res["lock_state"] == "UNLOCKED"


@pytest.mark.asyncio
async def test_resident_verify_pin_valid_and_invalid():
    """Verify PIN authentication."""
    valid_res = await resident_verify_pin(pin_code="482910")
    assert valid_res["status"] == "success"
    assert valid_res["verified"] is True
    assert valid_res["compartment_id"] == "C-02"

    invalid_res = await resident_verify_pin(pin_code="000000")
    assert invalid_res["status"] == "error"
    assert invalid_res["verified"] is False


@pytest.mark.asyncio
async def test_package_lookup():
    """Verify package compartment lookup."""
    res = await package_lookup(package_id="PKG-8821")
    assert res["status"] == "success"
    assert res["found"] is True
    assert res["compartment_id"] == "C-02"


@pytest.mark.asyncio
async def test_locker_diagnose_hardware():
    """Verify hardware diagnostics self-test."""
    res = await locker_diagnose_hardware(locker_id="LOCKER-01")
    assert res["status"] == "success"
    assert res["all_systems_operational"] is True
    assert "ups_battery_health" in res["diagnostics"]

