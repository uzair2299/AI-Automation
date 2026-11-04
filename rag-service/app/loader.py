"""Knowledge loader for streaming real website content JSONL into vector storage."""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from app.chunking import DocumentChunker
    from app.embeddings import EmbeddingService
except ImportError:
    from .chunking import DocumentChunker
    from .embeddings import EmbeddingService

logger = logging.getLogger("rag-service.loader")

_BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_SEARCH_PATHS = [
    _BASE_DIR / "data" / "knowledge" / "public" / "website_content.jsonl",
    Path("/app/data/knowledge/public/website_content.jsonl"),
    Path("rag-service/data/knowledge/public/website_content.jsonl"),
    Path("data/knowledge/public/website_content.jsonl"),
]


def find_knowledge_file() -> Optional[Path]:
    """Locate the website_content.jsonl file across standard Docker and local paths."""
    for p in KNOWLEDGE_SEARCH_PATHS:
        if p.exists() and p.is_file():
            return p
    return None


def infer_category(url: str, title: str) -> str:
    """Infer functional category from URL path or title."""
    lower_url = (url or "").lower()
    lower_title = (title or "").lower()

    if "locker" in lower_url or "hardware" in lower_url or "hardware" in lower_title:
        return "hardware"
    if "mailroom" in lower_url or "software" in lower_url:
        return "software"
    if "retail" in lower_url or "bopis" in lower_url:
        return "retail"
    if "multifamily" in lower_url or "apartment" in lower_url or "apartments" in lower_title:
        return "multifamily"
    if "university" in lower_url or "campus" in lower_url or "student" in lower_url:
        return "education"
    if "healthcare" in lower_url or "refrigerated" in lower_url or "temperature" in lower_url:
        return "healthcare"
    return "general"


async def load_real_knowledge_base(
    vector_store: Any,
    embedding_service: EmbeddingService,
    chunker: DocumentChunker,
    file_path: Optional[Path] = None,
    batch_size: int = 50,
) -> Dict[str, Any]:
    """Ingest, chunk, embed, and store real Smiota website knowledge into vector store."""
    target_file = file_path or find_knowledge_file()
    if not target_file:
        logger.warning(
            "Could not locate website_content.jsonl in search paths: %s",
            [str(p) for p in KNOWLEDGE_SEARCH_PATHS],
        )
        return {"status": "not_found", "chunks_indexed": 0, "pages_processed": 0}

    logger.info("Starting ingestion of real knowledge from: %s", target_file)

    pages_processed = 0
    total_chunks = 0
    docs_batch: List[Dict[str, Any]] = []

    with open(target_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except Exception:
                continue

            pages_processed += 1
            title = (
                record.get("page_title")
                or record.get("main_heading")
                or "Smiota Smart Locker Knowledge"
            ).strip()

            content = (record.get("content_markdown") or "").strip()
            meta_desc = (record.get("meta_description") or "").strip()
            headings = record.get("headings") or []

            # If content is short, enrich with meta description and headings
            if len(content.split()) < 30:
                parts = []
                if content:
                    parts.append(content)
                if meta_desc and meta_desc != content:
                    parts.append(meta_desc)
                if headings:
                    clean_headings = [h.replace("H1: ", "").replace("H2: ", "").replace("H3: ", "").replace("H4: ", "") for h in headings[:6]]
                    parts.append("Topics covered: " + ", ".join(clean_headings))
                content = "\n\n".join(parts)

            if not content.strip():
                continue

            url = record.get("source_url") or record.get("canonical_url") or ""
            category = infer_category(url, title)
            chunks = chunker.split_text(content)

            for idx, chunk_text in enumerate(chunks):
                emb = await embedding_service.get_embedding(chunk_text)
                chunk_title = f"{title} (Part {idx+1})" if len(chunks) > 1 else title
                docs_batch.append(
                    {
                        "title": chunk_title,
                        "category": category,
                        "content": chunk_text,
                        "metadata": {
                            "source_url": url,
                            "original_title": title,
                            "chunk_index": idx,
                            "total_chunks": len(chunks),
                        },
                        "tags": [category, "website", "smiota"],
                        "embedding": emb,
                    }
                )

                if len(docs_batch) >= batch_size:
                    await vector_store.insert_documents_batch(docs_batch)
                    total_chunks += len(docs_batch)
                    docs_batch = []

    if docs_batch:
        await vector_store.insert_documents_batch(docs_batch)
        total_chunks += len(docs_batch)

    logger.info(
        "Successfully indexed real knowledge base: %d pages processed, %d chunks stored.",
        pages_processed,
        total_chunks,
    )
    return {
        "status": "success",
        "file": str(target_file),
        "pages_processed": pages_processed,
        "chunks_indexed": total_chunks,
    }
