"""Configuration settings for Smart Locker MCP Server."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class SmartLockerSettings(BaseSettings):
    """Configuration for Smart Locker MCP Server."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SERVER_NAME: str = "smart-locker-mcp"
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8082
    MCP_TRANSPORT: str = "streamable-http"  # streamable-http, sse, stdio

    # Controller API & Hardware integration
    SMIOTA_CONTROLLER_URL: str = "https://controller.int.smiotaapps.com"
    SMIOTA_API_KEY: str = ""
    REQUEST_TIMEOUT_SECONDS: float = 10.0

    # Operational safety parameters
    AUTO_LOCK_TIMEOUT_SECONDS: int = 45
    MAX_OVERRIDE_DURATION_SECONDS: int = 300


settings = SmartLockerSettings()

