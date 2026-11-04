# SRE Kubernetes Read-Only MCP Server
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN groupadd -g 10001 mcp && \
    useradd -u 10001 -g mcp -s /bin/bash -m mcp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN chown -R mcp:mcp /app
USER 10001:10001

EXPOSE 8080

CMD ["python", "-m", "app.server"]

