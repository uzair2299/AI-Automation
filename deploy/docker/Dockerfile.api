# ==============================================================================
# Smiota Agent Core Gateway - API Service Dockerfile
# ==============================================================================
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/smiota-agent-gateway

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install shared internal common package
COPY packages/common /tmp/packages/common
RUN pip install --no-cache-dir /tmp/packages/common

COPY pyproject.toml README.md ./
COPY smiota-agent-gateway/ ./smiota-agent-gateway/

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD uvicorn main:app --app-dir /app/smiota-agent-gateway --host 0.0.0.0 --port 8000 --workers 2
