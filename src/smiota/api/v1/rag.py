"""RAG Knowledge base ingestion and retrieval API endpoints."""
from fastapi import APIRouter, Depends
from smiota.rag.retriever import KnowledgeRetriever
from smiota.rag.chunking import DocumentChunker
from smiota.rag.embeddings import EmbeddingService
from smiota.rag.vector_store import VectorStoreClient
from smiota.schemas.rag import (
    VectorSearchRequest,
    VectorSearchResponse,
    DocumentIngestionRequest,
    DocumentIngestionResponse,
)
from smiota.schemas.common import APIResponse

router = APIRouter(prefix="/rag", tags=["RAG Knowledge Engine"])

_vector_store = VectorStoreClient()
_embedding_service = EmbeddingService()
_chunker = DocumentChunker()
_retriever = KnowledgeRetriever(vector_store=_vector_store, embedding_service=_embedding_service)


@router.post("/search", response_model=APIResponse[VectorSearchResponse], summary="Semantic search across runbooks")
async def search_knowledge_base(payload: VectorSearchRequest):
    """Retrieve semantically similar runbooks and postmortems."""
    results = await _retriever.retrieve(
        query=payload.query,
        category=payload.category,
        top_k=payload.top_k,
    )
    data = VectorSearchResponse(
        query=payload.query,
        results=results,
        total_found=len(results),
    )
    return APIResponse(data=data)


@router.post("/ingest", response_model=APIResponse[DocumentIngestionResponse], summary="Ingest markdown runbook or postmortem")
async def ingest_document(payload: DocumentIngestionRequest):
    """Chunk and embed a technical runbook into the vector store."""
    chunks = _chunker.split_text(payload.content)
    first_doc_id = ""

    for idx, chunk in enumerate(chunks):
        emb = await _embedding_service.get_embedding(chunk)
        doc_id = await _vector_store.insert_document(
            title=f"{payload.title} (Part {idx+1})" if len(chunks) > 1 else payload.title,
            content=chunk,
            embedding=emb,
            category=payload.category,
            metadata={**payload.metadata, "tags": payload.tags},
        )
        if not first_doc_id:
            first_doc_id = doc_id

    data = DocumentIngestionResponse(
        document_id=first_doc_id,
        chunks_created=len(chunks),
        status="indexed",
    )
    return APIResponse(data=data, message="Document indexed successfully.")
