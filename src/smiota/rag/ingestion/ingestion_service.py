import json
import time
from pathlib import Path

from smiota.core.logging import logger
from smiota.rag.chunking.chunking_service import ChunkingService
from smiota.rag.config import RAGConfig
from smiota.rag.embeddings.base import BaseEmbeddingService
from smiota.rag.embeddings.embedding_service import EmbeddingService
from smiota.rag.ingestion.jsonl_reader import RecordNormalizer, read_jsonl_stream
from smiota.rag.models import DocumentChunk, IngestionStats, RawRecord
from smiota.rag.vector_store.base import BaseVectorStore


class IngestionService:
    """Orchestrates streaming knowledge ingestion from files or full directories."""

    def __init__(
        self,
        vector_store: BaseVectorStore | None = None,
        embedding_service: BaseEmbeddingService | None = None,
        chunking_service: ChunkingService | None = None,
        normalizer: RecordNormalizer | None = None,
        config: RAGConfig | None = None,
    ):
        self.config = config or RAGConfig()
        if vector_store is None:
            from smiota.rag.vector_store.factory import VectorStoreFactory

            self.vector_store = VectorStoreFactory.get_vector_store(config=self.config)
        else:
            self.vector_store = vector_store
        self.embedding_service = embedding_service or EmbeddingService(config=self.config)
        self.chunking_service = chunking_service or ChunkingService(config=self.config)
        self.normalizer = normalizer or RecordNormalizer(config=self.config)

    async def ingest_directory(
        self,
        directory_path: str | Path | None = None,
        recursive: bool = True,
        skip_invalid: bool = True,
    ) -> IngestionStats:
        """Scan a knowledge directory for supported files (.jsonl, .json, .txt, .md) and ingest them.

        Args:
            directory_path: Directory path to scan (defaults to config.knowledge_dir).
            recursive: If True, recursively scan all subdirectories.
            skip_invalid: If True, record errors on malformed files and continue.

        Returns:
            IngestionStats: Combined ingestion metrics across all processed files.
        """
        dir_path = Path(directory_path or self.config.knowledge_dir)
        if not dir_path.exists():
            raise FileNotFoundError(f"Knowledge directory not found: {dir_path.resolve()}")

        combined_stats = IngestionStats()
        start_time = time.monotonic()

        pattern = "**/*" if recursive else "*"
        matched_files = sorted(
            p
            for p in dir_path.glob(pattern)
            if p.is_file() and p.suffix.lower() in self.config.supported_extensions
        )

        logger.info(
            f"Scanning knowledge directory '{dir_path}': found {len(matched_files)} matching files",
            extra={
                "event": "rag.ingestion.directory_scan",
                "directory": str(dir_path),
                "matched_count": len(matched_files),
            },
        )

        for file_path in matched_files:
            file_stats = await self._ingest_single_file(file_path, skip_invalid=skip_invalid)
            combined_stats.total_records_read += file_stats.total_records_read
            combined_stats.valid_records += file_stats.valid_records
            combined_stats.invalid_records += file_stats.invalid_records
            combined_stats.chunks_created += file_stats.chunks_created
            combined_stats.chunks_embedded += file_stats.chunks_embedded
            combined_stats.chunks_upserted += file_stats.chunks_upserted
            combined_stats.duplicate_chunks_skipped += file_stats.duplicate_chunks_skipped
            combined_stats.errors.extend(file_stats.errors)

        combined_stats.duration_seconds = round(time.monotonic() - start_time, 2)
        return combined_stats

    async def ingest_file(
        self,
        file_path: str | Path,
        skip_invalid: bool = True,
    ) -> IngestionStats:
        """Ingest a single file or directory into the vector store.

        If `file_path` is a directory, delegates to `ingest_directory`.
        Supports .jsonl (streaming), .json (array or object), .txt, and .md files.
        """
        path = Path(file_path)
        if path.is_dir():
            return await self.ingest_directory(directory_path=path, skip_invalid=skip_invalid)

        return await self._ingest_single_file(path, skip_invalid=skip_invalid)

    async def _ingest_single_file(
        self,
        file_path: Path,
        skip_invalid: bool = True,
    ) -> IngestionStats:
        """Process an individual knowledge file based on its extension."""
        stats = IngestionStats()
        start_time = time.monotonic()
        ext = file_path.suffix.lower()

        logger.info(
            f"Starting ingestion for '{file_path.name}' (type: {ext})",
            extra={
                "event": "rag.ingestion.file_started",
                "file_path": str(file_path),
                "extension": ext,
            },
        )

        chunk_buffer: list[DocumentChunk] = []

        try:
            if ext == ".jsonl":
                for line_no, raw_data, err in read_jsonl_stream(file_path, skip_invalid=skip_invalid):
                    stats.total_records_read += 1
                    if err or raw_data is None:
                        stats.invalid_records += 1
                        if err:
                            stats.errors.append(err)
                        continue

                    record = self.normalizer.normalize(raw_data, line_number=line_no)
                    if not record:
                        stats.invalid_records += 1
                        stats.errors.append(f"Line {line_no}: Missing or empty text fields")
                        continue

                    stats.valid_records += 1
                    doc_chunks = self.chunking_service.split_record(record)
                    stats.chunks_created += len(doc_chunks)
                    chunk_buffer.extend(doc_chunks)

                    if len(chunk_buffer) >= self.config.embedding_batch_size:
                        await self._flush_chunk_batch(chunk_buffer, stats)
                        chunk_buffer.clear()

            elif ext == ".json":
                data = json.loads(file_path.read_text(encoding="utf-8"))
                records_list = data if isinstance(data, list) else [data]
                for idx, item in enumerate(records_list, start=1):
                    stats.total_records_read += 1
                    if not isinstance(item, dict):
                        stats.invalid_records += 1
                        continue
                    record = self.normalizer.normalize(item, line_number=idx)
                    if not record:
                        stats.invalid_records += 1
                        continue
                    stats.valid_records += 1
                    doc_chunks = self.chunking_service.split_record(record)
                    stats.chunks_created += len(doc_chunks)
                    chunk_buffer.extend(doc_chunks)

                    if len(chunk_buffer) >= self.config.embedding_batch_size:
                        await self._flush_chunk_batch(chunk_buffer, stats)
                        chunk_buffer.clear()

            elif ext in {".txt", ".md"}:
                stats.total_records_read += 1
                content = file_path.read_text(encoding="utf-8").strip()
                if not content:
                    stats.invalid_records += 1
                else:
                    stats.valid_records += 1
                    title = file_path.stem.replace("_", " ").replace("-", " ").title()
                    if ext == ".md":
                        for line in content.splitlines():
                            if line.startswith("# "):
                                title = line.lstrip("# ").strip()
                                break
                    record = RawRecord(
                        source_id=f"doc-{file_path.stem}",
                        title=title,
                        category=file_path.parent.name if file_path.parent.name else self.config.default_category,
                        extracted_text=content,
                        metadata={"source_file": str(file_path), "extension": ext},
                    )
                    doc_chunks = self.chunking_service.split_record(record)
                    stats.chunks_created += len(doc_chunks)
                    chunk_buffer.extend(doc_chunks)

            # Flush any remaining chunks
            if chunk_buffer:
                await self._flush_chunk_batch(chunk_buffer, stats)
                chunk_buffer.clear()

        except Exception as exc:
            logger.error(
                f"Ingestion failed for '{file_path.name}': {exc}",
                extra={"event": "rag.ingestion.failed", "file": str(file_path), "error_type": type(exc).__name__},
            )
            stats.errors.append(str(exc))
            if not skip_invalid:
                raise

        finally:
            stats.duration_seconds = round(time.monotonic() - start_time, 2)
            logger.info(
                f"Ingestion finished for '{file_path.name}': {stats.valid_records} valid, {stats.chunks_upserted} indexed",
                extra={
                    "event": "rag.ingestion.completed",
                    "file": str(file_path),
                    "valid_records": stats.valid_records,
                    "chunks_upserted": stats.chunks_upserted,
                },
            )

        return stats

    async def _flush_chunk_batch(
        self,
        batch: list[DocumentChunk],
        stats: IngestionStats,
    ) -> None:
        """Embed and upsert a batch of document chunks."""
        if not batch:
            return

        texts_to_embed = [c.text for c in batch]
        embeddings = await self.embedding_service.embed_texts(texts_to_embed)
        stats.chunks_embedded += len(embeddings)

        for chunk, emb in zip(batch, embeddings, strict=False):
            chunk.embedding = emb

        upserted = await self.vector_store.upsert(batch)
        stats.chunks_upserted += upserted
        stats.duplicate_chunks_skipped += len(batch) - upserted
