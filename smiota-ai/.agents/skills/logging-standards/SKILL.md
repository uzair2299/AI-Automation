---
name: logging-standards
description: Enforces production-grade logging, structured observability, correlation IDs, exception handling, security redaction, and consistent event naming across FastAPI services, agents, MCP tools, background tasks, and database operations.
---

# Logging Standards Skill

## 1. Objective

Ensure all application code produces consistent, structured, searchable, secure, and actionable logs suitable for production troubleshooting and incident investigation.

These standards apply to:
- FastAPI routes, middleware, dependencies, and exception handlers.
- Facades, services, repositories, and database integrations.
- LLM providers, agent execution, tools, and MCP calls.
- Background tasks, scheduled jobs, and message consumers.
- Authentication, authorization, validation, and external API integrations.

## 2. Mandatory Principles

1. Use Python's standard `logging` API through the centralized application logging configuration.
2. Emit structured JSON logs in production.
3. Include a request or correlation ID wherever a request context exists.
4. Propagate correlation IDs across downstream HTTP calls, agents, MCP tools, and background jobs when applicable.
5. Never log secrets, access tokens, passwords, API keys, session cookies, or sensitive customer data.
6. Use stable event names and structured fields rather than embedding everything in free-text messages.
7. Log exceptions once at the appropriate handling boundary. Avoid logging and re-raising the same exception at every layer.
8. Never swallow exceptions silently.
9. Never use `print()` for application logging.
10. Keep logging non-blocking where practical and avoid unnecessary high-volume logs.
11. Never log prompts, model responses, or database results by default if they may contain confidential information.
12. Do not let logging failures expose sensitive information or unnecessarily interrupt request processing.

## 3. Log Levels

### DEBUG
Use for temporary, detailed diagnostics and development troubleshooting.

Examples:
- Sanitized decision-path details.
- Retry attempt number.
- Non-sensitive internal state transitions.

Do not enable verbose DEBUG logging globally in production.

### INFO
Use for meaningful application lifecycle and business-process milestones.

Examples:
- `application.started`
- `http.request.completed`
- `agent.execution.completed`
- `mcp.tool.completed`
- `chat.session.created`

Do not log every function call or every intermediate variable.

### WARNING
Use when an operation is degraded or unexpected but the application can continue.

Examples:
- Retryable provider failure.
- Request rate limit approaching a configured threshold.
- Optional integration unavailable.
- Invalid external input rejected, where the event is operationally useful.

Avoid flooding logs for routine client errors or repeated expected failures.

### ERROR
Use when an operation fails and requires investigation, but the process can continue.

Examples:
- Database operation failed.
- External service request exhausted retries.
- Agent execution failed.
- Unexpected application exception returned as HTTP 500.

### CRITICAL
Reserve for severe failures that threaten service availability or essential functionality.

Examples:
- Required application initialization failed.
- An essential dependency makes the service unable to operate.
- A critical integrity or availability condition is detected.

Do not use CRITICAL for ordinary request failures.

## 4. Structured JSON Schema

Production log records should contain these fields where applicable:

- `timestamp`: UTC timestamp in ISO 8601 format.
- `level`: Log severity.
- `event`: Stable, machine-readable event name.
- `service`: Service identifier, such as `smiota-ai`.
- `environment`: `development`, `stage`, or `production`.
- `version`: Application release or build version.
- `logger`: Python logger name.
- `message`: Short, human-readable summary.
- `correlation_id`: Request or distributed trace correlation identifier.
- `trace_id`: Distributed tracing identifier when tracing is configured.
- `span_id`: Active span identifier when tracing is configured.
- `http_method`: HTTP method, if applicable.
- `http_route`: Route template, not a raw URL containing sensitive parameters.
- `http_status_code`: HTTP response status, if applicable.
- `duration_ms`: Operation duration in milliseconds.
- `error_type`: Exception class or sanitized error category, if applicable.

Optional fields must be omitted when unavailable. Do not fabricate IDs or use customer-controlled values as trusted identifiers.

Use consistent field names across all services.

## 5. Correlation ID Rules

- Accept an incoming correlation ID only after validating its format and length.
- Generate a cryptographically random or UUID-based ID if the incoming ID is absent or invalid.
- Store the ID in request-scoped context, not mutable global state.
- Return the correlation ID in the HTTP response header.
- Include it in all request-related log records.
- Propagate it to downstream calls through an approved header.
- For asynchronous tasks, explicitly capture and propagate the correlation context.
- Keep correlation IDs separate from authentication tokens, session identifiers, and customer identities.
- Never trust a correlation ID as proof of identity or authorization.

Use `contextvars` or an equivalent context-aware mechanism. Reset context reliably after each request.

## 6. HTTP Request Logging

Log one completion event for each request that reaches the application logging middleware.

Record:
- HTTP method.
- Route template when available.
- Status code.
- Duration.
- Correlation ID.
- Client classification when useful and privacy-approved.

Do not record by default:
- Request or response bodies.
- Authorization headers.
- Cookies.
- Query-string values.
- Raw tracking numbers or parcel identifiers.
- Full IP addresses unless explicitly approved by the security and privacy policy.

Health-check and metrics endpoints may use reduced logging to prevent noise.

Use monotonic time for duration measurement.

Expected 4xx responses should not automatically be treated as application errors. Server-side 5xx responses should be observable as errors without duplicating exception logs.

## 7. Exception Handling

- Use centralized FastAPI exception handlers for consistent HTTP error responses.
- Log unexpected exceptions with `logger.exception()` at the boundary responsible for handling the failure.
- Include the correlation ID and a stable event name.
- Keep stack traces in protected internal logs, not client responses.
- Return sanitized error messages to callers.
- Preserve exception chaining with `raise ... from exc` where appropriate.
- Do not log the same exception at every architectural layer.
- Do not convert all exceptions into successful responses.
- Do not expose SQL, filesystem paths, provider credentials, internal prompts, or stack traces to clients.

Expected business exceptions should generally be handled without ERROR-level stack traces unless operational policy requires them.

## 8. Security and Privacy

Always redact or exclude:
- Passwords and password hashes.
- API keys and cloud credentials.
- JWTs, bearer tokens, refresh tokens, and authorization headers.
- Session cookies and bootstrap codes.
- Private keys and database connection strings.
- Sensitive personal information.
- Full customer messages, parcel details, or LLM prompts unless an explicitly approved policy permits limited logging.

Prefer allowlisted structured fields over unrestricted dictionary logging.

Sanitize untrusted strings to prevent log injection through newlines, control characters, or oversized values.

Redaction must occur before data reaches the log sink. Do not rely only on dashboards to hide sensitive fields.

Never use a complete request object, environment configuration, exception payload, or database row as a logging field.

## 9. Database and External Service Logging

For database operations, record:
- Operation category.
- Duration.
- Success or failure.
- Sanitized error category.
- Correlation ID.

Do not log SQL bind values, credentials, full result sets, or customer records.

For external HTTP and MCP calls, record:
- Provider or tool name.
- Operation name.
- Duration.
- Outcome.
- Retry count.
- Sanitized status or error category.

Do not log complete URLs when query parameters may contain sensitive values.

Do not log full prompts, tool arguments, or tool results by default. Use approved allowlisted metadata.

## 10. LLM and Agent Logging

For agent and LLM execution, record:
- Agent name.
- Provider and model identifier.
- Operation or workflow name.
- Outcome.
- Duration.
- Retry count.
- Token usage and cost estimates only when supplied by trusted provider metadata.
- Correlation or trace identifiers.

Do not log private chain-of-thought, hidden reasoning, credentials, raw prompts, full customer messages, or unredacted tool outputs.

Record safe operational summaries rather than internal reasoning.

Distinguish provider failures, rate limits, timeouts, invalid model responses, and policy refusals using stable event categories.

## 11. Performance and Volume Controls

- Avoid expensive serialization when the log level is disabled.
- Do not emit per-token or per-chunk INFO logs.
- Sample high-volume successful operations when appropriate and approved.
- Preserve security-relevant events and error visibility when sampling.
- Use bounded field lengths and avoid unbounded payloads.
- Prefer asynchronous or buffered log shipping where appropriate.
- Ensure log rotation, retention, access control, and alerting are configured by the deployment platform.
- Do not use customer IDs, correlation IDs, session IDs, or tracking numbers as metric labels.

## 12. Prohibited Patterns

Never introduce patterns such as:

- `print(exception)`
- `logger.info(request.headers)`
- `logger.info(request.json())`
- `logger.info(os.environ)`
- `logger.exception(...)` followed by an unconditional duplicate log at every caller.
- Bare `except: pass`
- Logging raw JWTs, SQL parameters, prompts, or customer payloads.
- Using mutable module-level variables to store the current request ID.
- Building log event names dynamically from arbitrary user input.

## 13. Implementation Requirements

When modifying code:

1. Inspect the existing logging configuration, middleware, correlation ID implementation, exception handlers, and tracing setup first.
2. Reuse the existing architecture and naming conventions.
3. Do not create competing logging configurations or multiple request-ID middleware implementations.
4. Add structured logging through a shared logging utility where needed.
5. Ensure request context is reset safely.
6. Add tests for correlation propagation, JSON formatting, redaction, exception behavior, and concurrent requests.
7. Verify that secrets and customer payloads do not appear in captured logs.
8. Update configuration documentation and deployment settings.
9. Run the relevant test suite and report any remaining gaps.

## 14. Definition of Done

Logging changes are complete only when:

- Structured production logging is enabled.
- Required fields are present where applicable.
- Correlation IDs work across concurrent requests.
- Exceptions are logged at the correct boundary.
- Sensitive data is redacted before emission.
- Downstream and asynchronous operations preserve correlation context where applicable.
- Log output is valid, searchable JSON in production.
- Tests cover both expected behavior and security-sensitive edge cases.
- No duplicate middleware, unbounded payload logging, or uncontrolled DEBUG output is introduced.

If a requirement cannot be satisfied safely with the current implementation, document the limitation and propose a concrete remediation rather than silently weakening the standard.
