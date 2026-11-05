# Smiota RAG Knowledge Service (Standalone REST Service)

**Port**: `8001`  
**Protocol**: Standard HTTP REST (JSON)  
**Role**: Provides decoupled semantic search, chunking, and document ingestion for technical runbooks, hardware specifications, and incident postmortems.

> ⚠️ **Design Principle**: This service is a lightweight, pure REST microservice, **NOT an MCP server**. This allows rapid, horizontal scaling, independent database storage, and low latency semantic retrieval.

---

## API Endpoints

### 1. Health Check
`GET /health`

**Response:**
```json
{
  "status": "ok",
  "service": "smiota-rag-service",
  "indexed_chunks": 42,
  "version": "1.0.0"
}
```

### 2. Semantic Search
`POST /api/v1/rag/search`

**Request Body:**
```json
{
  "query": "How do refrigerated lockers control temperature?",
  "top_k": 3,
  "category": "hardware"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "query": "How do refrigerated lockers control temperature?",
    "results": [
      {
        "document_id": "84d5...",
        "similarity_score": 0.892,
        "document": {
          "title": "Smiota Refrigerated & Cold Storage Lockers",
          "category": "hardware",
          "content": "Smiota refrigerated smart lockers maintain strict temperature control between 34°F and 40°F...",
          "metadata": {},
          "tags": []
        }
      }
    ],
    "total_found": 1
  },
  "message": "Search completed successfully."
}
```

### 3. Document Ingestion
`POST /api/v1/rag/ingest`

**Request Body:**
```json
{
  "title": "CrashLoopBackOff RCA Guide",
  "content": "Detailed steps to troubleshoot CrashLoopBackOff...",
  "category": "runbook",
  "tags": ["kubernetes", "sre", "crashloop"],
  "metadata": {"author": "SRE Team"}
}
```

---

## Local Development & Docker

### Run with Python:
```bash
cd rag-service
pip install -e ../packages/common
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Run with Docker:
```bash
docker build -t smiota-rag-service:latest -f rag-service/Dockerfile .
docker run -p 8001:8001 smiota-rag-service:latest
```

