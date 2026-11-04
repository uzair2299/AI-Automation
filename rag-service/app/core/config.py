"""Configuration settings for Standalone RAG Knowledge Service."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent.parent  # rag-service/
_env = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "dev")).lower()

# Map aliases so both short and long names resolve to the right file
_alias_map = {
    "dev": ["dev", "development"],
    "development": ["dev", "development"],
    "prod": ["prod", "production"],
    "production": ["prod", "production"],
    "staging": ["staging", "stage"],
    "stage": ["staging", "stage"],
    "local": ["local"],
}
_aliases = _alias_map.get(_env, [_env])

# Build list of env files in order of increasing priority (later overrides earlier):
# Root project fallbacks first, then rag-service specific configuration files.
_candidates = [Path(".env")]
for a in _aliases:
    _candidates.append(Path(f".env.{a}"))

_candidates.append(_BASE_DIR / ".env")
for a in _aliases:
    _candidates.append(_BASE_DIR / f".env.{a}")

if os.getenv("ENV_FILE"):
    _candidates.append(Path(os.getenv("ENV_FILE")))

# Keep unique existing files preserving order
_seen = set()
_env_files_list = []
for p in _candidates:
    p_str = str(p.resolve()) if p.exists() else None
    if p_str and p_str not in _seen:
        _seen.add(p_str)
        _env_files_list.append(p_str)

_env_files = tuple(_env_files_list) or (".env",)


class RAGServiceSettings(BaseSettings):
    """Environment configuration for the RAG service."""

    model_config = SettingsConfigDict(
        env_file=_env_files,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    SERVICE_NAME: str = "smiota-rag-service"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Embedding settings
    EMBEDDING_PROVIDER: str = "deterministic"  # "gemini" or "deterministic"
    GEMINI_API_KEY: str = ""
    EMBEDDING_DIMENSION: int = 768

    # GCP & Vertex AI settings
    GCP_PROJECT_ID: str = "project-smiota-psi-1"
    GCP_REGION: str = "global"
    GEMINI_MODEL: str = "gemini-3.7-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # Chunking settings
    TARGET_CHUNK_SIZE: int = 250
    CHUNK_OVERLAP: int = 40

    # Vector store settings
    VECTOR_STORE_BACKEND: str = "memory"  # "memory", "pgvector", or "qdrant"
    DATABASE_URL: str = "postgresql+asyncpg://smiota_user:password@localhost:5432/smiota_ai_dev"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "smiota_user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "smiota_ai_dev"
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""

    # Seeding settings
    SEED_MAX_PAGES: int = 50


settings = RAGServiceSettings()
