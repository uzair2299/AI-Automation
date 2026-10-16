# Smiota AI Platform

Enterprise AI Platform for AIOps, DevSecOps, and Customer AI powered by **Python 3.11/3.12 (Stable LTS)**, **FastAPI**, **Gemini / Vertex AI**, and the **Model Context Protocol (MCP)**.

---

## 🏛️ Architecture Overview

The platform implements a centralized, multi-agent reasoning core connected to internal and external tools through standard MCP servers:

- **Multiple Channels**: MS Teams, VS Code / Antigravity IDE, Smiota Web Chat.
- **Agent Core**: Orchestrator with 5 domain agents (AIOps, Security, Developer, QA, Customer) built on clean, isolated cognitive boundaries.
- **MCP Tool Integration**: Standardized protocol connecting to Observability, CI/CD, SIEM, and IoT Smart Locker hardware.
- **Safety & HITL (Human-in-the-Loop)**: Read-only investigation first; automated remediation requires human approval.
- **Cloud Infrastructure**: Scalable containerized workloads on GCP (GKE / Cloud SQL / Memorystore Redis / Vertex AI).

---

## 📁 Repository Structure

```text
smiota-ai/
├── alembic.ini                     # Database migration configuration
├── alembic/                        # Async SQLAlchemy migration versions
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── deploy/                         # Production Deployment & Infrastructure as Code (IaC)
│   ├── docker/
│   │   ├── Dockerfile.api          # Container image for FastAPI agent core
│   │   └── Dockerfile.worker       # Container image for background automation engine
│   ├── k8s/                        # Kubernetes GKE manifests with Kustomize
│   │   ├── base/                   # Base manifests: deployment, worker, service, hpa, ingress, secrets
│   │   │   ├── configmap.yaml
│   │   │   ├── deployment.yaml
│   │   │   ├── hpa.yaml
│   │   │   ├── ingress.yaml
│   │   │   ├── kustomization.yaml
│   │   │   ├── secret.yaml
│   │   │   ├── service.yaml
│   │   │   └── worker-deployment.yaml
│   │   └── overlays/               # Environment-specific overlays (dev, prod)
│   │       ├── dev/kustomization.yaml
│   │       └── prod/kustomization.yaml
│   └── terraform/                  # Production GCP IaC (GKE, Cloud SQL, Memorystore Redis)
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── scripts/                        # Operational and benchmark utilities
│   ├── run_evals.py                # CLI runner for agent reasoning and safety benchmarks
│   └── seed_runbooks.py            # Knowledge base ingestion for engineering runbooks
├── src/smiota/
│   ├── main.py                     # FastAPI application factory, lifespan, and middlewares
│   ├── core/                       # Shared platform primitives & decoupling layer
│   │   ├── cache.py                # Async Redis cache manager with in-memory fallback
│   │   ├── config.py               # Pydantic BaseSettings loaded from environment
│   │   ├── constants.py            # Global enums, domain names, access levels, limits
│   │   ├── database.py             # Async SQLAlchemy engine, sessionmaker, and pool
│   │   ├── exceptions.py           # Domain exception hierarchy (HITL, Guardrails, MCP)
│   │   ├── logging.py              # Structured JSON logging
│   │   ├── security.py             # JWT token verification and RBAC roles
│   │   └── telemetry.py            # OpenTelemetry tracing and Prometheus metrics
│   ├── api/                        # HTTP & WebSocket routing layer
│   │   ├── deps.py                 # FastAPI dependency injection providers
│   │   ├── middleware/             # Request correlation ID and global exception handlers
│   │   │   ├── correlation.py
│   │   │   └── error_handler.py
│   │   └── v1/
│   │       ├── router.py           # API v1 master router
│   │       ├── chat.py             # Conversational agent chat endpoint
│   │       ├── approvals.py        # HITL remediation approval workflow endpoints
│   │       ├── agents.py           # Domain agent discovery and capability catalog
│   │       ├── health.py           # Kubernetes liveness, readiness, and deep status checks
│   │       ├── rag.py              # Knowledge search and runbook ingestion endpoints
│   │       └── channels/           # Specialized channel adapters
│   │           ├── ide.py          # Antigravity IDE / VS Code extension webhook
│   │           ├── teams.py        # Microsoft Teams Bot webhook adapter
│   │           └── webchat.py      # Smiota Web Chat client gateway
│   ├── agents/                     # Autonomous Multi-Agent reasoning subsystems
│   │   ├── base.py                 # BaseAgent, AgentContext, AgentResult, AgentCapability
│   │   ├── memory.py               # Multi-turn conversation sliding window memory
│   │   ├── orchestrator.py         # Intent classification and multi-agent dispatch
│   │   ├── registry.py             # Decoupled dynamic agent registration catalog
│   │   └── implementations/        # Domain-specific cognitive agents
│   │       ├── aiops/              # SRE: Incident investigation, RCA, runbook recommendations
│   │       │   ├── agent.py
│   │       │   ├── prompts.py
│   │       │   └── tools.py
│   │       ├── security/           # DevSecOps: Threat detection, SIEM alerts, IAM audits
│   │       │   ├── agent.py
│   │       │   ├── prompts.py
│   │       │   └── tools.py
│   │       ├── developer/          # Engineering: PR reviews, IaC validation, PromQL generation
│   │       │   ├── agent.py
│   │       │   ├── prompts.py
│   │       │   └── tools.py
│   │       ├── qa/                 # QA: Test case generation, flakiness analysis, Playwright
│   │       │   ├── agent.py
│   │       │   ├── prompts.py
│   │       │   └── tools.py
│   │       └── customer/           # Customer Support & IoT Smart Locker operations
│   │           ├── agent.py
│   │           ├── prompts.py
│   │           └── tools.py
│   ├── mcp/                        # Model Context Protocol integration layer
│   │   ├── client.py               # Async MCP execution client with latency telemetry
│   │   ├── registry.py             # Central tool registry with Gemini function declarations
│   │   ├── security.py             # @mcp_tool decorator with HITL enforcement gate
│   │   └── servers/                # Domain tool servers
│   │       ├── observability/      # Prometheus, OpenSearch, GKE rollout restart
│   │       │   └── tools.py
│   │       ├── security/           # Wazuh SIEM, Trivy CVE scan, GCP IAM audit
│   │       │   └── tools.py
│   │       ├── devops/             # GitHub PR diff, Terraform plan, CI/CD trigger
│   │       │   └── tools.py
│   │       ├── qa/                 # Playwright test runner, test failure log parser
│   │       │   └── tools.py
│   │       └── customer/           # Smart locker door status, parcel lookup, remote unlock
│   │           └── tools.py
│   ├── llm/                        # Large Language Model gateway
│   │   ├── cost_tracker.py         # FinOps token counting and cost tracking
│   │   ├── guardrails.py           # Prompt injection detection, command filtering, PII redaction
│   │   ├── provider.py             # Vertex AI / Gemini 1.5 completion and embedding client
│   │   └── prompts/                # Base blueprints and routing templates
│   │       ├── base.py
│   │       └── templates.py
│   ├── rag/                        # Retrieval-Augmented Generation (RAG) engine
│   │   ├── chunking.py             # Semantic markdown and technical document chunker
│   │   ├── embeddings.py           # Text embedding service (text-embedding-004)
│   │   ├── retriever.py            # Hybrid search knowledge retriever
│   │   └── vector_store.py         # Vector store client (pgvector / Vertex Search)
│   ├── workflows/                  # Asynchronous automation & background workers
│   │   ├── engine.py               # Workflow daemon and async event loop
│   │   ├── state.py                # Workflow execution context and state machine
│   │   └── tasks/                  # Distributed background tasks
│   │       ├── automated_remediation.py
│   │       ├── incident_postmortem.py
│   │       └── notification.py
│   ├── models/                     # Async SQLAlchemy 2.0 database entities
│   │   ├── base.py                 # Declarative Base with UUID & Timestamp mixins
│   │   ├── approval.py             # HITL remediation approval state entity
│   │   ├── audit.py                # Full audit log of queries, agent reasoning, tool traces
│   │   └── session.py              # Multi-turn chat sessions and message history
│   └── schemas/                    # Pydantic v2 validation contracts & API schemas
│       ├── common.py               # Unified APIResponse, ErrorResponse, and Pagination
│       ├── agents.py               # Agent metadata, capabilities, and routing diagnostics
│       ├── approvals.py            # HITL approval requests and decision models
│       ├── chat.py                 # Chat request/response payloads
│       ├── health.py               # Deep system health response models
│       ├── mcp.py                  # MCP tool definitions and execution envelopes
│       └── rag.py                  # Knowledge ingestion and vector search contracts
└── tests/                          # Test Suites & Benchmark Framework
    ├── conftest.py                 # Pytest async fixtures and mock dependencies
    ├── unit/                       # Unit test suite
    │   ├── test_agents.py          # Agent registration and orchestrator routing
    │   ├── test_guardrails.py      # Prompt injection filtering & PII redaction
    │   ├── test_health.py          # Kubernetes probes & health endpoints
    │   ├── test_mcp_security.py    # MCP tool access levels & HITL token blocking
    │   └── test_rag.py             # Chunking and semantic retrieval
    ├── integration/                # End-to-end integration tests
    │   ├── test_chat_flow.py       # End-to-end chat routing across domain agents
    │   └── test_approvals_flow.py  # HITL approval listing and decision flow
    └── evals/                      # Agent Evaluation Benchmark Framework
        ├── datasets/
        │   └── golden_evals.json   # Golden dataset of domain test queries & expected actions
        └── test_agent_evals.py     # Automated benchmark evaluating routing & safety accuracy
```

---

## 🛠️ Key Engineering Architectural Principles

1. **Scalability**:
   - **Non-blocking Asynchronous I/O**: Every I/O operation (HTTP, database queries, Redis caching, Vertex AI LLM calls, MCP tool execution) uses Python `async`/`await`.
   - **Horizontal Autoscaling (HPA)**: Kubernetes deployment scales from 3 to 25 replicas based on CPU and memory utilization.
   - **Distributed Task Offloading**: Long-running postmortems and remediations are processed by decoupled worker pods (`deploy/docker/Dockerfile.worker`).

2. **Independence (Loose Coupling & Modular Domain Boundaries)**:
   - **Domain Isolation**: Each specialized domain agent (`aiops`, `security`, `developer`, `qa`, `customer`) owns its specific prompts, tool client bindings, and capabilities without tight coupling to the orchestrator.
   - **Model Context Protocol (MCP)**: Tools are encapsulated as standard MCP tool definitions, making tools easily pluggable, testable, and swappable.
   - **Inversion of Control**: FastAPI dependency injection (`api/deps.py`) injects cache, database sessions, and clients rather than relying on global singletons.

3. **Maintainability & Production-Readiness**:
   - **Human-in-the-Loop (HITL) Safety Gates**: Clear distinction between `read_only` tools (executed autonomously) and `remediation` tools (requiring cryptographic approval tokens).
   - **Adversarial Guardrails**: Built-in prompt injection defense, destructive command filtering, and PII/API key sanitization.
   - **Type Safety**: Pydantic v2 validation contracts for all ingress/egress payloads and async SQLAlchemy 2.0 ORM models for data persistence.
   - **Continuous Agent Evaluation (Evals)**: Golden dataset benchmark suite evaluates routing precision and safety policy adherence.

---

## 🚀 Quick Start

### 1. Setup Virtual Environment (Python 3.11 or 3.12 Stable LTS)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -e ".[dev]"
```

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Run FastAPI Development Server
```bash
uvicorn smiota.main:app --reload --port 8000
```

Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Probes: `http://localhost:8000/api/v1/health`
- Detailed System Status: `http://localhost:8000/api/v1/health/status`
- Agent Catalog: `http://localhost:8000/api/v1/agents`

---

## 🧪 Testing & Evaluation

### Run Full Test Suite
```bash
pytest -v
```

### Run Golden Evaluation Benchmark
```bash
python scripts/run_evals.py
```

### Seed Knowledge Base Runbooks
```bash
python scripts/seed_runbooks.py
```
