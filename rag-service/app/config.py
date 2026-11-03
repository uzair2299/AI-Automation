"""Configuration settings for Standalone RAG Knowledge Service."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGServiceSettings(BaseSettings):
    """Environment configuration for the RAG service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SERVICE_NAME: str = "smiota-rag-service"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = False

    # Embedding settings
    EMBEDDING_PROVIDER: str = "deterministic"  # "gemini" or "deterministic"
    GEMINI_API_KEY: str = ""
    EMBEDDING_DIMENSION: int = 768

    # Chunking settings
    TARGET_CHUNK_SIZE: int = 250
    CHUNK_OVERLAP: int = 40

    # Vector store settings
    VECTOR_STORE_BACKEND: str = "memory"  # "memory", "pgvector", or "qdrant"
    DATABASE_URL: str = "postgresql+asyncpg://smiota_user:smaiops26devdb@localhost:5432/smiota_ai_dev"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "smiota_user"
    POSTGRES_PASSWORD: str = "smaiops26devdb"
    POSTGRES_DB: str = "smiota_ai_dev"
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""


settings = RAGServiceSettings()

