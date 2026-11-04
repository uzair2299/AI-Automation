# Smiota Smart Locker Hardware & Compartment MCP Server

**Port**: `8082`  
**Protocol**: Model Context Protocol (FastMCP over Streamable-HTTP / SSE)  
**Role**: Provides hardware solenoid actuation, compartment door monitoring, pickup PIN verification, and IoT parcel sensor inspection.

---

## Exposed MCP Tools

1. `get_locker_status(locker_id: str = "LOCKER-01")`: Top-level health, battery status, and compartment availability.
2. `query_locker_door_status(locker_id: str, compartment_id: str)`: Real-time IoT sensor telemetry (door open/closed, solenoid voltage, infrared parcel sensor).
3. `locker_open_compartment(locker_id: str, compartment_id: str, authorization_pin: Optional[str], approval_token: Optional[str])`: Actuates motorized solenoid with verification.
4. `package_lookup(tracking_number: Optional[str], package_id: Optional[str], locker_id: Optional[str])`: Look up package compartment placement, carrier, and holding status.
5. `resident_verify_pin(pin_code: str, locker_id: Optional[str])`: Validate 6-digit pickup PIN or dynamic QR token.
6. `locker_list_compartments(locker_id: str, status_filter: Optional[str])`: List all compartments with sizes, zones, and availability.
7. `locker_diagnose_hardware(locker_id: str)`: Hardware diagnostics for UPS battery, solenoid bus, and optical sensors.

---

## Local Development & Docker

```bash
cd mcp-servers/smart-locker
pip install -r requirements.txt
python -m app.server
```

Or via Docker:
```bash
docker build -t smiota-smart-locker-mcp:latest -f mcp-servers/smart-locker/Dockerfile mcp-servers/smart-locker/
docker run -p 8082:8082 smiota-smart-locker-mcp:latest
```

