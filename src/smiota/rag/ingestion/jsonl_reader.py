"""Streaming line-by-line JSONL reader and configurable record normalizer."""
import json
from collections.abc import Generator
from pathlib import Path
from typing import Any

from smiota.core.logging import logger
from smiota.rag.config import RAGConfig
from smiota.rag.models import RawRecord


def read_jsonl_stream(
    file_path: str | Path,
    encoding: str = "utf-8",
    skip_invalid: bool = True,
) -> Generator[tuple[int, dict[str, Any] | None, str | None], None, None]:
    """Stream records line-by-line from a JSONL file without loading the whole file into RAM.

    Yields:
        tuple of (line_number, parsed_dict, error_message)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSONL input file not found at path: {path.resolve()}")

    with open(path, encoding=encoding) as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    err = f"Line {line_number} is valid JSON but not an object/dictionary (got {type(record).__name__})"
                    if not skip_invalid:
                        raise ValueError(err)
                    yield (line_number, None, err)
                    continue

                yield (line_number, record, None)
            except json.JSONDecodeError as exc:
                err = f"Malformed JSON on line {line_number}: {exc}"
                logger.warning(err, extra={"event": "rag.jsonl.malformed_line", "line_number": line_number})
                if not skip_invalid:
                    raise ValueError(err) from exc
                yield (line_number, None, err)


class RecordNormalizer:
    """Validates records, extracts candidate text fields, and preserves source metadata."""

    def __init__(self, config: RAGConfig | None = None):
        self.config = config or RAGConfig()

    def normalize(self, raw_data: dict[str, Any], line_number: int = 1) -> RawRecord | None:
        """Extract text, identifier, title, category, and metadata from arbitrary record schemas."""
        if not raw_data:
            return None

        # 1. Extract source ID (check configured id_field, common synonyms, or line fallback)
        source_id = str(
            raw_data.get(self.config.id_field)
            or raw_data.get("document_id")
            or raw_data.get("source_url")
            or raw_data.get("url")
            or raw_data.get("doc_id")
            or raw_data.get("_id")
            or f"rec-{line_number}"
        ).strip()

        # 2. Extract title
        title = str(
            raw_data.get(self.config.title_field)
            or raw_data.get("page_title")
            or raw_data.get("main_heading")
            or raw_data.get("name")
            or raw_data.get("headline")
            or f"Document {source_id}"
        ).strip()

        # 3. Extract category
        category = str(
            raw_data.get(self.config.category_field)
            or raw_data.get("type")
            or raw_data.get("tag")
            or self.config.default_category
        ).strip()

        # 4. Extract candidate text from configured text fields
        extracted_text = ""
        for field_name in self.config.text_fields:
            val = raw_data.get(field_name)
            if val and isinstance(val, str) and val.strip():
                extracted_text = val.strip()
                break
            if val and isinstance(val, list):
                # Handle list of paragraphs / messages
                joined = "\n\n".join(str(item).strip() for item in val if str(item).strip())
                if joined:
                    extracted_text = joined
                    break

        if not extracted_text:
            return None

        # 5. Preserve remaining fields as metadata
        reserved_keys = {
            self.config.id_field,
            "document_id",
            "doc_id",
            "_id",
            self.config.title_field,
            "name",
            self.config.category_field,
            "type",
            *self.config.text_fields,
        }
        metadata = {k: v for k, v in raw_data.items() if k not in reserved_keys}
        metadata["line_number"] = line_number

        return RawRecord(
            source_id=source_id,
            title=title,
            category=category,
            extracted_text=extracted_text,
            metadata=metadata,
        )
