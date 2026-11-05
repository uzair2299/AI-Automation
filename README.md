# Smiota Platform Monorepo

Unified repository for the **Smiota Core Platform** and **Smiota AI / MCP Ecosystem**.

---

## Architecture Overview

```
smiota/
├── smiota-core/                 # ☕ Java Backend Services (Maven Multi-Module)
│   ├── smiota-common-model/     # Shared DTOs, Enums, and JPA Entities
│   └── smiota-core-api/         # Spring Boot 3 REST API & MCP Data Provider
│
└── smiota-ai/                   # 🐍 Python AI Platform & MCP Tools
    ├── smiota-agent-gateway/    # Multi-agent orchestrator & Chat Gateway (Port 8000)
    ├── rag-service/             # Embeddings & Vector Knowledge Base (Port 8001)
    └── mcp-servers/             # Model Context Protocol Tools (Port 8082)
```

---

## Service Port Mapping

| Service | Technology | Port | Purpose |
| :--- | :--- | :---: | :--- |
| **smiota-core-api** | Java 17 / Spring Boot | `8080` | Core REST APIs, database persistence, DTO provider |
| **smiota-agent-gateway** | Python 3.11 / FastAPI | `8000` | Agent orchestration, WebChat & Teams channels |
| **rag-service** | Python / pgvector | `8001` | Semantic search, vector embeddings & runbooks |
| **smart-locker-mcp** | Python / FastMCP | `8082` | MCP tools for locker telemetry & state inspection |
| **MySQL** | MySQL 8.0 (Container) | `3306` | Shared enterprise locker & package database |
| **PostgreSQL** | pgvector 16 (VM Host Service) | `5432` | Vector store for AI embeddings & chat sessions |
| **Redis** | Redis 7 (VM Host Service) | `6379` | Session caching & rate-limiting |

---

## Quickstart Guide

### 1. Prerequisites
* **Java 17+** (Eclipse Temurin / OpenJDK)
* **Apache Maven 3.8+**
* **Python 3.10+**
* **Docker & Docker Compose**

---

### 2. Local Setup (Windows)

Run the automated PowerShell setup script from the root directory:

```powershell
.\setup-dev.ps1
```
This script will:
1. Validate required software dependencies.
2. Generate your `.env` configuration from `.env.example`.
3. Compile the Java backend (`smiota-core`) using Maven.
4. Initialize the Python virtual environment in `smiota-ai`.

---

### 3. Running with Docker Compose (Recommended)

To start the entire platform (all microservices, databases, and caches):

```bash
docker compose up -d
```

To view logs:
```bash
docker compose logs -f smiota-core-api smiota-agent-gateway
```

To stop all services:
```bash
docker compose down
```

---

### 4. Running Services Individually for Local Development

#### Java Backend (`smiota-core`):
```bash
cd smiota-core
mvn clean install

cd smiota-core-api
mvn spring-boot:run
```

#### Python AI Gateway (`smiota-ai`):
```bash
cd smiota-ai
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

uvicorn smiota-agent-gateway.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 5. Automated Linux VM Deployment

On a Linux VM (Ubuntu / Debian), run:

```bash
chmod +x setup-vm.sh
./setup-vm.sh
```
