# ==============================================================================
# Smiota RAG Knowledge Service - Standalone REST API (Port 8001)
# ==============================================================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install shared internal common package
COPY packages/common /tmp/packages/common
RUN pip install --no-cache-dir /tmp/packages/common

# Install service dependencies
COPY rag-service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source code and knowledge data
COPY rag-service/app/ ./app/
COPY rag-service/data/ ./data/

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
