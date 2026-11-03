"""Configuration settings for Observability MCP Server."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class ObservabilitySettings(BaseSettings):
    """Configuration for Observability MCP Server."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SERVER_NAME: str = "smiota-observability-mcp"
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8081
    MCP_TRANSPORT: str = "streamable-http"  # streamable-http, sse, stdio

    # Prometheus
    PROMETHEUS_URL: str = "https://prometheus.int.smiotaapps.com"
    PROMETHEUS_TIMEOUT_SECONDS: float = 8.0

    # OpenSearch
    OPENSEARCH_URL: str = "https://opensearch.int.smiotaapps.com:9200"
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASSWORD: str = ""
    OPENSEARCH_INDEX_PATTERN: str = "app-logs-*"


settings = ObservabilitySettings()

