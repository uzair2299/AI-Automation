# Smiota Agent Gateway (`smiota-agent-gateway`)

Unified AI & API Gateway for the Smiota AI Platform running on port `8000`.

## Architecture & Responsibilities

1. **Omnichannel Ingress Gateway**: Handles WebChat (`/api/v1/channels/webchat`), Microsoft Teams (`/api/v1/channels/teams`), and IDE extensions (`/api/v1/channels/ide`).
2. **Real-Time Streaming**: Bi-directional WebSocket server at `/api/v1/chat/ws/{session_id}` for token streaming.
3. **Multi-Agent Orchestrator**: Intent classification and semantic routing across domain-specific agents (Customer, Knowledge, SRE/Observability, DevOps, QA, Security).
4. **MCP Client Aggregator**: Central client managing connections to external MCP tool servers:
   - Kubernetes SRE MCP (`:8080`)
   - Observability MCP (`:8081`)
   - Smart Locker MCP (`:8082`)
5. **RAG Client**: Vector search & document retrieval via `rag-service` (`:8001`).
6. **Security & Human-in-the-Loop (HITL)**: Action verification gate at `/api/v1/approvals` for state-mutating hardware and infrastructure commands.

## Local Execution

```bash
uvicorn smiota.main:app --host 0.0.0.0 --port 8000 --reload
```

