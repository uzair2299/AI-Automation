"""Document and runbook chunking utilities."""
import re
from typing import Optional


class DocumentChunker:
    """Splits technical markdown runbooks, postmortems, and articles into coherent chunks."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        """Split text by markdown headers or paragraph boundaries."""
        # Split by markdown headers (#, ##, ###)
        sections = re.split(r"(?=(?:\n|^)#{1,3}\s)", text)
        chunks: list[str] = []

        for section in sections:
            clean = section.strip()
            if not clean:
                continue

            if len(clean) <= self.chunk_size:
                chunks.append(clean)
            else:
                # Fallback to paragraph splitting
                paragraphs = clean.split("\n\n")
                current_chunk = ""
                for p in paragraphs:
                    if len(current_chunk) + len(p) <= self.chunk_size:
                        current_chunk += ("\n\n" + p if current_chunk else p)
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = p
                if current_chunk:
                    chunks.append(current_chunk)

        return chunks if chunks else [text]
