# Production Logging Policy & Schema Guidelines

This document details the operational rules, format specifications, and lifecycle requirements for structured logging across the Smiota platform.

---

## 1. Production JSON Log Schema

All logs in production (`ENVIRONMENT=production` or `ENVIRONMENT=prod`) must be emitted as single-line, parseable JSON records directly to standard output (`stdout`).

### Core JSON Fields

| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `timestamp` | string (ISO-8601) | Precise UTC timestamp with millisecond resolution | `"2026-10-22T07:30:15.123Z"` |
| `level` | string | Log level in uppercase (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) | `"INFO"` |
| `event` | string | Machine-readable, period-delimited event name | `"http.request.completed"` |
| `service` | string | Standard service identifier | `"smiota-ai"` |
| `environment` | string | Deployment environment (`development`, `staging`, `production`) | `"production"` |
| `version` | string | Application semantic version or git commit SHA | `"1.2.0"` |
| `logger` | string | Hierarchical Python logger name | `"smiota.api.middleware"` |
| `message` | string | Human-readable event description | `"HTTP GET /api/v1/health completed in 2.4ms"` |
| `correlation_id` | string | Request / trace correlation ID | `"corr-7f3b89a1c02e"` |
| `duration_ms` | float (optional) | Monotonic operation duration in milliseconds | `24.5` |
| `http_method` | string (optional) | Normalized HTTP verb (`GET`, `POST`, etc.) | `"POST"` |
| `http_route` | string (optional) | Parameterized route path template | `"/api/v1/chat/message"` |
| `http_status_code` | int (optional) | HTTP response status code | `200` |
| `error_type` | string (optional) | Class name or category of error | `"DatabaseConnectionError"` |
| `exception` | string (optional) | Sanitized stack trace (internal logs only) | `"Traceback (most recent call last)..."` |

---

## 2. Retention & Log Volume Controls

1. **Volume Management**:
   - Never log at `INFO` level inside high-frequency inner loops (e.g., token streaming chunks, per-row DB fetch).
   - Health check endpoints (`/health`, `/healthz`, `/ready`) must use quiet logging or log only on status changes / failures to avoid log pollution.
2. **Log Levels by Environment**:
   - `development`: Console formatted string, level `DEBUG` enabled.
   - `staging`: JSON format, level `INFO` default (selective `DEBUG` for test runs).
   - `production`: JSON format, level `INFO` default (`DEBUG` globally forbidden; only enabled selectively via dynamic feature flags).
3. **Retention**:
   - Platform infrastructure (GCP Cloud Logging / Datadog) handles retention policies (typically 30 days hot, 365 days cold archive).
   - The application does not manage file rotation in containerized environments; stdout/stderr are captured by container runtimes.

---

## 3. Correlation ID Lifecycle

1. **Extraction**: Check `X-Correlation-ID` header. Validate:
   - Must match regex: `^[a-zA-Z0-9\-_]{8,64}$`
   - If invalid or missing, generate `corr-<uuid4.hex[:12]>`.
2. **Context Binding**: Use Python's `contextvars.ContextVar` to bind the correlation ID across coroutine transitions.
3. **Propagation**: Include `X-Correlation-ID` in outgoing HTTP requests to downstream internal services (e.g. `smiota-server`, external APIs).
4. **Response**: Always return `X-Correlation-ID` in HTTP response headers for client-side support tracking.
5. **Teardown**: Always reset the `ContextVar` token in a `finally:` block in middleware.
