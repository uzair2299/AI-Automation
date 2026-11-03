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
    VECTOR_STORE_BACKEND: str = "memory"  # "memory" or "qdrant"
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""


settings = RAGServiceSettings()

