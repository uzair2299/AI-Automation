"""RAG Source Reference Processing, Validation, and Deduplication Service."""
from __future__ import annotations

import logging
import re
from typing import Any, Iterable, List, Optional
from urllib.parse import urlparse

from core.config import get_settings
from rag_client.models import DocumentChunk, ScoredChunk
from schemas.chat import SourceReference

logger = logging.getLogger("smiota.services.source_processor")

# Patterns for identifying source document types from URL or title
PDF_PATTERN = re.compile(r"\.pdf($|\?|#)", re.IGNORECASE)
RUNBOOK_PATTERN = re.compile(r"(runbook|postmortem|troubleshoot|rca|incident)", re.IGNORECASE)
DOCS_PATTERN = re.compile(r"(docs|documentation|internal|architecture|spec)", re.IGNORECASE)
PART_SUFFIX_PATTERN = re.compile(
    r"(\s*[-–—:]\s*|\s+)?(\(|\[)?part\s+\d+(\)|\])?\s*$", re.IGNORECASE
)


class SourceProcessor:
    """Validates, sanitizes, deduplicates, and limits RAG source citations."""

    def __init__(
        self,
        default_max_sources: int = 5,
        max_displayed_sources: Optional[int] = None,
        allowed_domains: Optional[List[str]] = None,
        min_relevance_threshold: Optional[float] = None,
        enabled: Optional[bool] = None,
    ):
        settings = get_settings()
        self._max_sources = (
            max_displayed_sources
            if max_displayed_sources is not None
            else getattr(settings, "RAG_MAX_DISPLAYED_SOURCES", default_max_sources)
        )
        self.default_max_sources = self._max_sources
        self.allowed_domains = (
            allowed_domains
            if allowed_domains is not None
            else getattr(
                settings,
                "RAG_ALLOWED_SOURCE_DOMAINS",
                ["smiota.com", "dev.smiotaapps.com", "smiotaapps.com"],
            )
        )
        self.min_relevance_threshold = (
            min_relevance_threshold
            if min_relevance_threshold is not None
            else getattr(settings, "RAG_MIN_RELEVANCE_THRESHOLD", None)
        )
        self.enabled = (
            enabled
            if enabled is not None
            else getattr(settings, "RAG_SOURCES_ENABLED", True)
        )

    @property
    def max_displayed_sources(self) -> int:
        """Alias for default_max_sources."""
        return self._max_sources

    @max_displayed_sources.setter
    def max_displayed_sources(self, value: int) -> None:
        self._max_sources = value
        self.default_max_sources = value

    def is_safe_url(self, url: str) -> bool:
        """Validate URL scheme and ensure no private IPs or local paths are exposed."""
        if not url or not isinstance(url, str):
            return False

        trimmed = url.strip()
        if not trimmed:
            return False

        try:
            parsed = urlparse(trimmed)
        except Exception:
            return False

        # Only allow standard http and https protocols
        if parsed.scheme.lower() not in ("http", "https"):
            return False

        hostname = (parsed.hostname or "").lower().strip()
        if not hostname:
            return False

        # Block localhost, loopbacks, internal containers, and raw private IP addresses
        if hostname in ("localhost", "127.0.0.1", "0.0.0.0", "::1", "rag-service"):
            return False
        if hostname.endswith(".local") or hostname.endswith(".internal"):
            return False

        # Check against allowed domain whitelist if configured
        if self.allowed_domains:
            domain_match = any(
                hostname == d.lower() or hostname.endswith("." + d.lower())
                for d in self.allowed_domains
            )
            if not domain_match:
                return False

        return True

    is_valid_url = is_safe_url

    def sanitize_title(
        self,
        raw_title: Optional[str],
        url: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> str:
        """Clean up document titles, stripping chunk suffixes and fallback cleanly."""
        title = (raw_title or "").strip()
        if title:
            # Strip '(Part 1)', '(Part 2)', etc.
            title = PART_SUFFIX_PATTERN.sub("", title).strip()

        if title:
            return title

        # Fallback: derive readable title from URL path
        if url:
            try:
                parsed = urlparse(url)
                path_parts = [p for p in parsed.path.strip("/").split("/") if p]
                if path_parts:
                    slug = path_parts[-1].replace("-", " ").replace("_", " ")
                    if slug:
                        return slug.title()
            except Exception:
                pass

        # Fallback: derive readable title from document_id
        if document_id:
            cleaned_id = str(document_id).replace("-", " ").replace("_", " ").strip()
            if cleaned_id:
                return cleaned_id.title()

        return "Smiota Documentation"

    clean_title = sanitize_title

    def infer_source_type(
        self,
        url: str,
        title: Optional[str] = None,
        category: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        """Infer user-facing source type (website, pdf, runbook, internal_docs)."""
        meta = metadata or {}
        explicit_type = (
            meta.get("source_type")
            or meta.get("type")
            or kwargs.get("source_type")
        )
        if explicit_type and str(explicit_type).lower() in (
            "website",
            "pdf",
            "runbook",
            "internal_docs",
        ):
            return str(explicit_type).lower()

        cat_str = str(
            category or meta.get("category") or kwargs.get("category") or title or ""
        ).lower()
        if "runbook" in cat_str or "postmortem" in cat_str:
            return "runbook"

        if PDF_PATTERN.search(url) or "pdf" in cat_str:
            return "pdf"

        if RUNBOOK_PATTERN.search(url) or RUNBOOK_PATTERN.search(cat_str):
            return "runbook"

        if DOCS_PATTERN.search(url) or "spec" in cat_str:
            return "internal_docs"

        return "website"

    def extract_domain(self, url: str) -> str:
        """Extract clean hostname from URL."""
        if not url:
            return "smiota.com"
        try:
            parsed = urlparse(url)
            host = parsed.hostname or ""
            if host.startswith("www."):
                host = host[4:]
            return host.lower() or "smiota.com"
        except Exception:
            return "smiota.com"

    def process_sources(
        self,
        chunks: Iterable[Any],
        max_sources: Optional[int] = None,
        min_relevance: Optional[float] = None,
        allowed_domains: Optional[List[str]] = None,
    ) -> List[SourceReference]:
        """Validate, deduplicate, filter, and format source references from retrieved chunks."""
        if not self.enabled:
            return []

        effective_max = max_sources if max_sources is not None else self.default_max_sources
        effective_threshold = (
            min_relevance if min_relevance is not None else self.min_relevance_threshold
        )
        if allowed_domains is not None:
            self.allowed_domains = allowed_domains

        candidates: List[dict[str, Any]] = []

        for item in chunks:
            # Handle ScoredChunk, DocumentChunk, dict, or object with chunk attribute
            chunk_obj = getattr(item, "chunk", item)
            score = item.get("score") if isinstance(item, dict) else getattr(item, "score", None)

            # Filter by relevance score threshold if defined
            if effective_threshold is not None and score is not None:
                if float(score) < effective_threshold:
                    continue

            # Extract metadata and document properties
            metadata: dict[str, Any] = getattr(chunk_obj, "metadata", {}) or {}
            if isinstance(chunk_obj, dict):
                metadata = chunk_obj.get("metadata", {}) or chunk_obj

            raw_title = (
                getattr(chunk_obj, "title", None)
                or metadata.get("original_title")
                or metadata.get("page_title")
                or (chunk_obj.get("title") if isinstance(chunk_obj, dict) else None)
            )

            raw_url = (
                metadata.get("canonical_url")
                or metadata.get("source_url")
                or metadata.get("url")
                or (chunk_obj.get("canonical_url") or chunk_obj.get("url") if isinstance(chunk_obj, dict) else None)
                or ""
            )

            doc_id = (
                getattr(chunk_obj, "document_id", None)
                or getattr(chunk_obj, "chunk_id", None)
                or metadata.get("document_id")
                or (chunk_obj.get("document_id") or chunk_obj.get("id") if isinstance(chunk_obj, dict) else None)
            )

            category = (
                getattr(chunk_obj, "category", None)
                or metadata.get("category")
                or (chunk_obj.get("category") if isinstance(chunk_obj, dict) else None)
            )

            # Validate and filter URL
            clean_url = str(raw_url).strip()
            if not self.is_safe_url(clean_url):
                logger.debug("Excluded unsafe or non-whitelisted source URL: '%s'", clean_url)
                continue

            clean_title = self.sanitize_title(raw_title, url=clean_url, document_id=doc_id)
            source_type = self.infer_source_type(clean_url, category=category, metadata=metadata)
            domain = self.extract_domain(clean_url)

            candidates.append(
                {
                    "title": clean_title,
                    "url": clean_url,
                    "source_type": source_type,
                    "document_id": str(doc_id) if doc_id else None,
                    "domain": domain,
                    "score": round(float(score), 4) if score is not None else None,
                }
            )

        # Deduplicate sources preserving highest score and earliest occurrence
        deduped_map: dict[str, dict[str, Any]] = {}

        for cand in candidates:
            # Normalize URL for deduplication (strip trailing slash, lowercase scheme/host)
            parsed = urlparse(cand["url"])
            normalized_key = (
                f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{parsed.path.rstrip('/')}"
            )

            if normalized_key in deduped_map:
                prev = deduped_map[normalized_key]
                cand_score = cand.get("score")
                prev_score = prev.get("score")
                if cand_score is not None:
                    if prev_score is None or cand_score > prev_score:
                        prev["score"] = cand_score
                if not prev.get("document_id") and cand.get("document_id"):
                    prev["document_id"] = cand.get("document_id")
            else:
                deduped_map[normalized_key] = cand

        deduped: List[SourceReference] = [
            SourceReference(
                title=item["title"],
                url=item["url"],
                source_type=item["source_type"],
                document_id=item["document_id"],
                domain=item["domain"],
                score=item["score"],
            )
            for item in deduped_map.values()
        ]

        return deduped[:effective_max]


_default_source_processor: Optional[SourceProcessor] = None


def get_source_processor() -> SourceProcessor:
    """Singleton provider for SourceProcessor service."""
    global _default_source_processor
    if _default_source_processor is None:
        _default_source_processor = SourceProcessor()
    return _default_source_processor
