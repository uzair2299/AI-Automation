"""Structural text and markdown chunking service with token boundary awareness."""
import hashlib
import re
from typing import Any

from smiota.rag.config import RAGConfig
from smiota.rag.models import DocumentChunk, RawRecord


class ChunkingService:
    """Splits technical documents, runbooks, and records into token-bounded, coherent chunks."""

    def __init__(self, config: RAGConfig | None = None):
        self.config = config or RAGConfig()

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count using whitespace and punctuation tokens (~4 chars per token)."""
        if not text:
            return 0
        words = len(re.findall(r"\w+|[^\w\s]", text))
        char_est = len(text) // 4
        return max(1, (words + char_est) // 2)

    def split_record(self, record: RawRecord) -> list[DocumentChunk]:
        """Split a normalized RawRecord into DocumentChunk instances."""
        return self.split_text(
            text=record.extracted_text,
            document_id=record.source_id,
            title=record.title,
            category=record.category,
            metadata=record.metadata,
        )

    def split_text(
        self,
        text: str,
        document_id: str = "doc",
        title: str = "",
        category: str = "general",
        metadata: dict[str, Any] | None = None,
    ) -> list[DocumentChunk]:
        """Chunk text using markdown headers, paragraphs, and sentence boundaries."""
        clean_text = text.strip()
        if not clean_text:
            return []

        meta = dict(metadata or {})
        total_tokens = self.estimate_tokens(clean_text)
        has_headers = bool(re.search(r"(?:\n|^)#{1,3}\s", clean_text))

        # Preserve short, self-contained records intact if below target chunk size and without explicit headers
        if total_tokens <= self.config.target_chunk_size and not has_headers:
            chunk_hash = hashlib.sha256(f"{document_id}:0:{clean_text}".encode()).hexdigest()
            return [
                DocumentChunk(
                    chunk_id=f"{document_id}-chk-0",
                    document_id=document_id,
                    title=title,
                    category=category,
                    text=clean_text,
                    chunk_index=0,
                    token_count=total_tokens,
                    content_hash=chunk_hash,
                    metadata=meta,
                )
            ]

        # 1. Primary split: Markdown headers (#, ##, ###)
        sections = re.split(r"(?=(?:\n|^)#{1,3}\s)", clean_text)
        atomic_blocks: list[str] = []

        for section in sections:
            sec_clean = section.strip()
            if not sec_clean:
                continue

            sec_tokens = self.estimate_tokens(sec_clean)
            if sec_tokens <= self.config.target_chunk_size:
                atomic_blocks.append(sec_clean)
            else:
                # 2. Secondary split: Paragraph boundaries (\n\n)
                paragraphs = sec_clean.split("\n\n")
                for para in paragraphs:
                    p_clean = para.strip()
                    if not p_clean:
                        continue

                    p_tokens = self.estimate_tokens(p_clean)
                    if p_tokens <= self.config.target_chunk_size:
                        atomic_blocks.append(p_clean)
                    else:
                        # 3. Tertiary split: Sentence boundaries
                        sentences = re.split(r"(?<=[.!?])\s+", p_clean)
                        current_sent_block = ""
                        for sent in sentences:
                            s_clean = sent.strip()
                            if not s_clean:
                                continue
                            candidate = f"{current_sent_block} {s_clean}".strip() if current_sent_block else s_clean
                            if self.estimate_tokens(candidate) <= self.config.target_chunk_size:
                                current_sent_block = candidate
                            else:
                                if current_sent_block:
                                    atomic_blocks.append(current_sent_block)
                                current_sent_block = s_clean
                        if current_sent_block:
                            atomic_blocks.append(current_sent_block)

        # 4. Assemble atomic blocks into target chunks respecting overlap
        chunks: list[DocumentChunk] = []
        current_text = ""
        chunk_idx = 0

        for block in atomic_blocks:
            candidate = f"{current_text}\n\n{block}".strip() if current_text else block
            cand_tokens = self.estimate_tokens(candidate)

            if cand_tokens <= self.config.target_chunk_size:
                current_text = candidate
            else:
                if current_text:
                    # Finalize current chunk
                    chunk_tokens = self.estimate_tokens(current_text)
                    chunk_hash = hashlib.sha256(f"{document_id}:{chunk_idx}:{current_text}".encode()).hexdigest()
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{document_id}-chk-{chunk_idx}",
                            document_id=document_id,
                            title=title,
                            category=category,
                            text=current_text,
                            chunk_index=chunk_idx,
                            token_count=chunk_tokens,
                            content_hash=chunk_hash,
                            metadata=meta,
                        )
                    )
                    chunk_idx += 1

                    # Compute overlap text from tail of current_text
                    overlap_words = current_text.split()[-self.config.chunk_overlap :]
                    overlap_prefix = " ".join(overlap_words)
                    current_text = f"{overlap_prefix}\n\n{block}".strip() if overlap_prefix else block
                else:
                    current_text = block

        if current_text:
            chunk_tokens = self.estimate_tokens(current_text)
            chunk_hash = hashlib.sha256(f"{document_id}:{chunk_idx}:{current_text}".encode()).hexdigest()
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{document_id}-chk-{chunk_idx}",
                    document_id=document_id,
                    title=title,
                    category=category,
                    text=current_text,
                    chunk_index=chunk_idx,
                    token_count=chunk_tokens,
                    content_hash=chunk_hash,
                    metadata=meta,
                )
            )

        return chunks


class DocumentChunker:
    """Document and runbook chunking utilities preserving full backward compatibility."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        """Split text by markdown headers or paragraph boundaries."""
        sections = re.split(r"(?=(?:\n|^)#{1,3}\s)", text)
        chunks: list[str] = []

        for section in sections:
            clean = section.strip()
            if not clean:
                continue

            if len(clean) <= self.chunk_size:
                chunks.append(clean)
            else:
                paragraphs = clean.split("\n\n")
                current_chunk = ""
                for p in paragraphs:
                    if len(current_chunk) + len(p) <= self.chunk_size:
                        current_chunk += "\n\n" + p if current_chunk else p
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = p
                if current_chunk:
                    chunks.append(current_chunk)

        return chunks if chunks else [text]
