"""Text chunking utilities for RAG ingestion."""
import re
from typing import List


class DocumentChunker:
    """Splits technical documents and manuals into coherent chunks."""

    def __init__(self, target_chunk_size: int = 250, overlap: int = 40):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        """Split text by paragraphs and sentences respecting maximum word count."""
        cleaned = text.strip()
        if not cleaned:
            return []

        # Split into paragraphs first
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_words = 0

        for p in paragraphs:
            words = p.split()
            word_count = len(words)

            if current_words + word_count <= self.target_chunk_size:
                current_chunk.append(p)
                current_words += word_count
            else:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                # Start new chunk
                current_chunk = [p]
                current_words = word_count

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks if chunks else [cleaned]

