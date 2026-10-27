"""Application settings and environment profiling (Development, Staging, Production, Test)."""
import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from smiota.core.constants import Environment


class BaseAppSettings(BaseSettings):
    """Common baseline settings shared across all execution profiles."""

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{os.getenv('ENVIRONMENT', os.getenv('APP_ENV', 'development')).lower()}"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General Platform Identifiers
    PROJECT_NAME: str = "Smiota AI Platform"
    API_V1_PREFIX: str = "/api/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = Environment.DEVELOPMENT
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API Documentation & Ingress
    ENABLE_SWAGGER: bool = True
    CORS_ORIGINS: list[str] = ["*"]

    # GCP & Vertex AI Configuration
    GCP_PROJECT_ID: str = "vertex-ai-510710"
    GCP_REGION: str = "global"
    GEMINI_MODEL: str = "gemini-3.7-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

    # Database, Cache & Message Broker
    DATABASE_URL: str = "postgresql+asyncpg://smiota_user:password@localhost:5432/smiota_ai"
    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://SMIOTA:Password-1@shortline.proxy.rlwy.net:45560/"
    RABBITMQ_EXCHANGE: str = "smiota.events"

    # Web Chat & Concierge Customization (Configurable via Environment)
    WEBCHAT_ASSISTANT_NAME: str = "Smiota Assistant"
    WEBCHAT_SUBTITLE: str = "Smart Locker & Parcel Concierge"
    WEBCHAT_WELCOME_TITLE: str = "Welcome to Smiota!"
    WEBCHAT_WELCOME_MESSAGE: str = "Hi there! Welcome to Smiota. How can I help you today?"

    # Security & Auth
    JWT_SECRET_KEY: str = "smiota-dev-secret-key-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "smiota-ai"
    JWT_AUDIENCE: str = "smiota-chat"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SMIOTA_SERVER_BASE_URL: str = "https://dev.smiotaapps.com/smiota"
    SMIOTA_BACKEND_URL: str = "https://dev.smiotaapps.com/smiota"
    SMIOTA_INTERNAL_EXCHANGE_ENDPOINT: str = "/internal/ai/auth/exchange"
    SMIOTA_SERVICE_TOKEN: str = "smsec_fc7308bef9f566733226ff8db7601fe7dc138e6f12831b9978bb307973604f3e"
    SMIOTA_BACKEND_TIMEOUT_SECONDS: float = 10.0
    SMIOTA_AUTH_DUMMY_MODE: bool = False

    # Microsoft Teams & Bot Framework Connector
    MICROSOFT_APP_ID: Optional[str] = "c93bfc04-2bf6-4c89-b04f-5d4ef6aa734a"
    MICROSOFT_APP_PASSWORD: Optional[str] = None
    TEAMS_APP_ID: Optional[str] = "d6c463d0-d6a3-4704-bd53-f5fcb06256a2"

    # Chat Session Persistence & Storage Provider
    CHAT_STORAGE_BACKEND: str = "memory"  # Options: 'memory', 'redis', 'postgres'
    CHAT_SESSION_TTL_HOURS: int = 24
    CHAT_SESSION_MAX_TURNS: int = 20


    # Model Context Protocol & Safety Gates
    MCP_READ_ONLY_DEFAULT: bool = True
    REQUIRE_HUMAN_APPROVAL_FOR_REMEDIATION: bool = True

    # Observability & Metrics
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    ENABLE_PROMETHEUS_METRICS: bool = True


class DevelopmentSettings(BaseAppSettings):
    """Profile: Local Development environment."""
    ENVIRONMENT: str = Environment.DEVELOPMENT
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    ENABLE_SWAGGER: bool = True
    CORS_ORIGINS: list[str] = ["*"]
    GCP_PROJECT_ID: str = "smiota-cloud-dev"


class StagingSettings(BaseAppSettings):
    """Profile: Staging / Pre-Production environment."""
    ENVIRONMENT: str = Environment.STAGING
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENABLE_SWAGGER: bool = True
    CORS_ORIGINS: list[str] = [
        "https://staging.smiota.com",
        "https://staging-portal.smiota.com",
        "http://localhost:3000",
        "http://localhost:4200",
    ]
    GCP_PROJECT_ID: str = "smiota-cloud-staging"


class ProductionSettings(BaseAppSettings):
    """Profile: Production environment (Hardened security, strict CORS)."""
    ENVIRONMENT: str = Environment.PRODUCTION
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENABLE_SWAGGER: bool = False  # Disabled in production to prevent public schema exposure
    CORS_ORIGINS: list[str] = [
        "https://app.smiota.com",
        "https://portal.smiota.com",
        "https://smiota.com",
    ]
    GCP_PROJECT_ID: str = "smiota-cloud-prod"
    REQUIRE_HUMAN_APPROVAL_FOR_REMEDIATION: bool = True


class TestSettings(BaseAppSettings):
    """Profile: Automated Test suite (Fast in-memory fallbacks)."""
    ENVIRONMENT: str = Environment.TEST
    DEBUG: bool = True
    LOG_LEVEL: str = "WARNING"
    ENABLE_SWAGGER: bool = True
    CORS_ORIGINS: list[str] = ["*"]
    GCP_PROJECT_ID: str = "smiota-cloud-test"
    SMIOTA_AUTH_DUMMY_MODE: bool = False
    REQUIRE_HUMAN_APPROVAL_FOR_REMEDIATION: bool = True



# Type alias for backward compatibility across the codebase
Settings = BaseAppSettings


@lru_cache
def get_settings() -> BaseAppSettings:
    """Factory creating the appropriate Settings profile based on ENVIRONMENT."""
    env_str = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development")).strip().lower()

    if env_str in ("prod", "production"):
        return ProductionSettings()
    elif env_str in ("stage", "staging"):
        return StagingSettings()
    elif env_str in ("test", "testing"):
        return TestSettings()
    else:
        return DevelopmentSettings()


# Export default global settings instance
settings = get_settings()

