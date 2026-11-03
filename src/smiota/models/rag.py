"""SQLAlchemy entity for RAG document chunks and embeddings."""
from typing import Any, Optional
from sqlalchemy import String, Text, JSON, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import UserDefinedType

from smiota.models.base import Base


class PGVectorType(UserDefinedType):
    """Custom SQLAlchemy type representing PostgreSQL pgvector 'vector(N)' column."""

    def __init__(self, dimension: int = 768):
        self.dimension = dimension

    def get_col_spec(self, **kw: Any) -> str:
        return f"vector({self.dimension})"


class RAGDocument(Base):
    """Stores knowledge chunks and vector embeddings for semantic search in pgvector."""

    __tablename__ = "rag_documents"

    document_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="general", nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    doc_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    embedding: Mapped[Optional[Any]] = mapped_column(PGVectorType(768), nullable=True)
