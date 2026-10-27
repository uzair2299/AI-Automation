"""Vector Store Factory supporting dynamic backend selection."""
from typing import ClassVar

from smiota.core.logging import logger
from smiota.rag.config import RAGConfig
from smiota.rag.vector_store.base import BaseVectorStore
from smiota.rag.vector_store.in_memory_store import InMemoryVectorStore


class VectorStoreFactory:
    """Factory to instantiate the configured vector store backend adapter."""

    _instances: ClassVar[dict[str, BaseVectorStore]] = {}

    @classmethod
    def get_vector_store(
        cls,
        backend: str | None = None,
        config: RAGConfig | None = None,
    ) -> BaseVectorStore:
        """Retrieve or create the vector store instance for the configured backend."""
        cfg = config or RAGConfig()
        selected_backend = (backend or cfg.vector_store_backend).lower().strip()

        if selected_backend in cls._instances:
            return cls._instances[selected_backend]

        if selected_backend in ("memory", "in_memory", "inmemory"):
            logger.info("Initializing InMemoryVectorStore backend")
            instance = InMemoryVectorStore(config=cfg)
            cls._instances[selected_backend] = instance
            return instance

        if selected_backend == "pgvector":
            # Documented migration point for Phase 5
            raise NotImplementedError(
                "Backend 'pgvector' requested, but the PostgreSQL/pgvector adapter is not yet installed. "
                "Ensure pgvector extension is enabled on PostgreSQL, configure DATABASE_URL, and register PgVectorStore."
            )

        raise ValueError(
            f"Unsupported vector store backend '{selected_backend}'. Supported backends: ['memory', 'pgvector']"
        )

    @classmethod
    def reset(cls) -> None:
        """Reset cached instances (useful for test isolation)."""
        cls._instances.clear()
