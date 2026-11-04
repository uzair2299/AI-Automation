"""RAG Knowledge base ingestion and retrieval API endpoints (proxied to standalone RAG service)."""
from fastapi import APIRouter
from smiota.rag_client.client import RAGServiceClient
from smiota.schemas.rag import (
    VectorSearchRequest,
    VectorSearchResponse,
    DocumentSearchResult,
    DocumentIngestionRequest,
    DocumentIngestionResponse,
)
from smiota.schemas.common import APIResponse

router = APIRouter(prefix="/rag", tags=["RAG Knowledge Engine"])
_rag_client = RAGServiceClient()


@router.post("/search", response_model=APIResponse[VectorSearchResponse], summary="Semantic search across knowledge base")
async def search_knowledge_base(payload: VectorSearchRequest):
    """Retrieve semantically similar runbooks and knowledge documents via standalone RAG service."""
    scored_chunks = await _rag_client.search(
        query=payload.query,
        category=payload.category,
        top_k=payload.top_k,
    )
    results = [
        DocumentSearchResult(
            document_id=c.chunk.document_id,
            title=c.chunk.title,
            content=c.chunk.text,
            score=c.score,
            category=c.chunk.category,
            metadata=c.chunk.metadata,
        )
        for c in scored_chunks
    ]
    data = VectorSearchResponse(
        query=payload.query,
        results=results,
        total_found=len(results),
    )
    return APIResponse(data=data)


@router.post("/ingest", response_model=APIResponse[DocumentIngestionResponse], summary="Ingest markdown runbook or document")
async def ingest_document(payload: DocumentIngestionRequest):
    """Ingest a technical runbook or document into the standalone RAG service."""
    res = await _rag_client.ingest(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        tags=payload.tags,
        metadata=payload.metadata,
    )
    inner = res.get("data", res)
    data = DocumentIngestionResponse(
        document_id=inner.get("document_id", "doc-1"),
        chunks_created=inner.get("chunks_created", 1),
        status="indexed",
    )
    return APIResponse(data=data)
