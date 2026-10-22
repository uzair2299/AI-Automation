# Smiota Standard Event Catalog

This catalog defines the stable, standardized event names, severity levels, and mandatory structured fields used across the Smiota platform.

---

## 1. HTTP & API Events

| Event Name | Level | Required Fields | Description |
| :--- | :--- | :--- | :--- |
| `http.request.completed` | INFO | `http_method`, `http_route`, `http_status_code`, `duration_ms`, `correlation_id` | Standard request lifecycle completion event |
| `http.request.failed` | ERROR | `http_method`, `http_route`, `http_status_code`, `error_type`, `correlation_id` | Unhandled HTTP server failure (5xx) |
| `http.rate_limited` | WARNING | `http_route`, `correlation_id`, `client_id` | Client request exceeded configured rate limits |

---

## 2. Agent & AI Execution Events

| Event Name | Level | Required Fields | Description |
| :--- | :--- | :--- | :--- |
| `agent.routing.decided` | INFO | `agent_name`, `confidence`, `routing_method`, `matched_intent`, `correlation_id` | Multi-agent router selected target agent |
| `agent.execution.started` | INFO | `agent_name`, `session_id`, `correlation_id` | Agent processing initiated |
| `agent.execution.completed` | INFO | `agent_name`, `session_id`, `duration_ms`, `requires_approval`, `correlation_id` | Agent completed reasoning loop |
| `agent.execution.failed` | ERROR | `agent_name`, `session_id`, `error_type`, `correlation_id` | Agent reasoning loop crashed or raised exception |
| `agent.approval.created` | INFO | `agent_name`, `approval_id`, `action`, `session_id` | Human-in-the-loop approval gate triggered |
| `agent.approval.resolved` | INFO | `approval_id`, `status` (`approved`/`rejected`), `session_id` | Gate resolved by authorized reviewer |

---

## 3. LLM & Provider Events

| Event Name | Level | Required Fields | Description |
| :--- | :--- | :--- | :--- |
| `llm.completion.started` | DEBUG | `model`, `provider`, `correlation_id` | Vertex AI / Gemini request dispatched |
| `llm.completion.completed` | INFO | `model`, `provider`, `duration_ms`, `correlation_id` | Vertex AI / Gemini returned response |
| `llm.completion.failed` | ERROR | `model`, `provider`, `error_type`, `retry_count`, `correlation_id` | Model provider error or timeout |
| `llm.guardrail.triggered` | WARNING | `violation_type`, `action_taken`, `correlation_id` | Input or output safety filter violation |

---

## 4. MCP & External Integration Events

| Event Name | Level | Required Fields | Description |
| :--- | :--- | :--- | :--- |
| `mcp.tool.invoked` | DEBUG | `tool_name`, `access_level`, `correlation_id` | Tool execution initiated by agent |
| `mcp.tool.completed` | INFO | `tool_name`, `duration_ms`, `outcome`, `correlation_id` | Tool executed successfully |
| `mcp.tool.failed` | ERROR | `tool_name`, `error_type`, `correlation_id` | Tool execution returned an error |

---

## 5. Storage & Database Events

| Event Name | Level | Required Fields | Description |
| :--- | :--- | :--- | :--- |
| `chat.session.created` | INFO | `session_id`, `channel`, `correlation_id` | New chat session initialized in DB / Redis |
| `chat.message.appended` | DEBUG | `session_id`, `role`, `message_type`, `correlation_id` | Message turn appended to repository |
| `db.operation.failed` | ERROR | `operation`, `error_type`, `duration_ms`, `correlation_id` | Database query or write failed |
