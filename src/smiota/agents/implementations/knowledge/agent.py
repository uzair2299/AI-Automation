"""Knowledge Assistant Agent: Grounded Smiota Product, Hardware, Solution & Integration QA."""

import re
import time
from typing import Any, ClassVar

from smiota.agents.base import AgentContext, AgentResult, BaseAgent
from smiota.core.logging import logger
from smiota.llm.provider import GeminiProvider
from smiota.rag_client.client import RAGServiceClient
from smiota.rag_client.config import RAGConfig
from smiota.rag_client.prompts import (
    SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT,
    build_rag_prompt,
)
from smiota.schemas.agents import AgentCapability


class KnowledgeAssistantAgent(BaseAgent):
    """Public-facing Smiota AI Knowledge Assistant.

    Provides strict retrieval-bounded, zero-hallucination answers regarding
    smart locker products, technical specifications, and system integrations.
    Has zero mutation or tenant-account access tools.
    """

    PRIVATE_DATA_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(
            r"\b(where is my (package|parcel|delivery)|my package|my delivery)\b", re.IGNORECASE
        ),
        re.compile(
            r"\b(my pin|my qr code|locker pin|pickup code|door pin|pickup pin)\b", re.IGNORECASE
        ),
        re.compile(r"\b(open locker|unlock door|open door|door #\d+|locker #\d+)\b", re.IGNORECASE),
        re.compile(
            r"\b(tenant account|resident account|look up account|resident profile)\b", re.IGNORECASE
        ),
    ]

    CARRIER_TRACKING_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"\b(1z[0-9a-z]{16}|94[0-9]{20}|92[0-9]{20}|tba[0-9]{12})\b", re.IGNORECASE),
        re.compile(r"\b(usps|ups|fedex|dhl|amazon) tracking\b", re.IGNORECASE),
    ]

    def __init__(
        self,
        retrieval_service: Any | None = None,
        llm_provider: GeminiProvider | None = None,
        config: RAGConfig | None = None,
        rag_client: RAGServiceClient | None = None,
    ):
        super().__init__(
            name="KnowledgeAssistant",
            description=(
                "Official Smiota AI Knowledge Assistant for smart locker solutions, "
                "hardware specifications, and enterprise integrations."
            ),
            domain="knowledge",
            capabilities=[
                AgentCapability(
                    name="public_knowledge_qa",
                    description="Answer queries using verified Smiota public documentation with citations",
                ),
            ],
            system_prompt=SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT,
            bound_tools=[],  # Strictly read-only, ZERO execution tools
        )
        self.config = config or RAGConfig()
        self.retrieval_service = retrieval_service
        self.rag_client = rag_client or RAGServiceClient()
        self.llm_provider = llm_provider or GeminiProvider()

    def _is_private_data_query(self, query: str) -> bool:
        """Detect attempts to query live resident/package/door controls."""
        return any(pattern.search(query) for pattern in self.PRIVATE_DATA_PATTERNS)

    def _is_carrier_tracking_query(self, query: str) -> bool:
        """Detect live external carrier tracking queries."""
        return any(pattern.search(query) for pattern in self.CARRIER_TRACKING_PATTERNS)

    async def process(self, query: str, context: AgentContext) -> AgentResult:
        """Execute grounded retrieval and answer synthesis within scope boundaries."""
        logger.info(
            f"KnowledgeAssistant processing query: '{query[:60]}...'",
            extra={
                "event": "agent.knowledge.started",
                "session_id": context.session_id,
                "user_id": context.user_id,
                "channel": context.channel,
            },
        )

        # 1. Scope Enforcement: Refuse private authenticated tenant data
        if self._is_private_data_query(query):
            logger.info(
                "Triggered private tenant data refusal protocol",
                extra={"event": "agent.knowledge.refusal", "reason": "private_resident_data"},
            )
            return AgentResult(
                agent_name=self.name,
                content=(
                    "For security and privacy reasons, I cannot access live tenant accounts, "
                    "locker door controls, or package PIN codes. Please check the SMS or email notification "
                    "sent directly to your phone, or open the Smiota mobile app to retrieve your pickup code. "
                    "If you require property-level assistance, please contact your building management or mailroom staff."
                ),
                requires_approval=False,
                # Suggested action pills (commented out for webchat channel)
                suggested_actions=(
                    []
                    if context.channel == "webchat"
                    else [
                        "Check SMS or email for PIN code",
                        "Open Smiota Mobile App",
                        "Contact building management",
                    ]
                ),
                metadata={"refusal_type": "private_resident_data"},
            )

        # 2. Scope Enforcement: Refuse live external carrier tracking
        if self._is_carrier_tracking_query(query):
            logger.info(
                "Triggered carrier tracking refusal protocol",
                extra={"event": "agent.knowledge.refusal", "reason": "carrier_tracking"},
            )
            return AgentResult(
                agent_name=self.name,
                content=(
                    "I do not have access to live carrier tracking networks. Smiota lockers integrate "
                    "with all major carriers (USPS, FedEx, UPS, DHL, Amazon) for secure drop-off, but "
                    "real-time package transit must be checked directly through the shipping carrier's website."
                ),
                requires_approval=False,
                # Suggested action pills (commented out for webchat channel)
                suggested_actions=(
                    []
                    if context.channel == "webchat"
                    else [
                        "Track package on USPS.com",
                        "Track package on UPS.com",
                        "Track package on FedEx.com",
                    ]
                ),
                metadata={"refusal_type": "carrier_tracking"},
            )

        # 3. Retrieve relevant public knowledge context via RAG Service
        start_rag = time.perf_counter()
        rag_url = getattr(self.rag_client, "service_url", "http://rag-service:8001")
        logger.info(
            f"[TRACE - Step 1: RAG Search] Querying RAG Service ({rag_url}) for: '{query}'",
            extra={"event": "rag.search.started", "query": query},
        )
        scored_chunks = await self.rag_client.search(
            query=query,
            top_k=5,
        )
        if not scored_chunks and self.retrieval_service:
            scored_chunks = await self.retrieval_service.retrieve(
                query=query,
                top_k=5,
                enable_mmr=True,
            )
        rag_latency_ms = (time.perf_counter() - start_rag) * 1000

        detailed_sources = []
        for idx, sc in enumerate(scored_chunks, start=1):
            meta = sc.chunk.metadata or {}
            canonical = meta.get("canonical_url") or meta.get("source_url") or ""
            detailed_sources.append({
                "rank": idx,
                "title": sc.chunk.title,
                "score": round(float(sc.score), 4),
                "url": canonical,
                "category": sc.chunk.category,
            })

        if scored_chunks:
            logger.info(
                f"[TRACE - Step 1: RAG Search] Found {len(scored_chunks)} matching chunks in {rag_latency_ms:.1f}ms:",
                extra={
                    "event": "rag.search.completed",
                    "chunks_count": len(scored_chunks),
                    "duration_ms": rag_latency_ms,
                },
            )
            for s in detailed_sources:
                logger.info(f"  -> Match #{s['rank']}: score={s['score']:.4f} | title='{s['title']}' | url={s['url']}")
        else:
            logger.warning(
                f"[TRACE - Step 1: RAG Search] 0 chunks matched in {rag_latency_ms:.1f}ms for query: '{query}'. Proceeding with baseline LLM generation.",
                extra={"event": "rag.search.empty", "duration_ms": rag_latency_ms},
            )

        # 4. Construct prompt with dynamic retrieved chunks
        full_prompt = build_rag_prompt(
            user_message=query,
            retrieved_chunks=scored_chunks,
            system_prompt=self.system_prompt,
        )

        # 5. Synthesize response via LLM
        start_llm = time.perf_counter()
        logger.info(
            f"[TRACE - Step 2: LLM Synthesis] Prompting Gemini with {len(scored_chunks)} RAG chunks...",
            extra={"event": "llm.generation.started", "chunks_provided": len(scored_chunks)},
        )
        response_text = await self.llm_provider.generate_completion(
            prompt=full_prompt,
            temperature=0.2,
        )
        llm_latency_ms = (time.perf_counter() - start_llm) * 1000

        is_grounded = len(scored_chunks) > 0
        source_type = "rag_grounded" if is_grounded else "llm_direct"

        logger.info(
            f"[TRACE - Step 3: Response Ready] Mode={source_type} | Chunks={len(scored_chunks)} | "
            f"Latency: RAG={rag_latency_ms:.1f}ms, LLM={llm_latency_ms:.1f}ms | Length={len(response_text)} chars",
            extra={
                "event": "agent.knowledge.completed",
                "session_id": context.session_id,
                "source_type": source_type,
                "chunks_retrieved": len(scored_chunks),
                "rag_latency_ms": rag_latency_ms,
                "llm_latency_ms": llm_latency_ms,
            },
        )

        suggested_actions = (
            []
            if context.channel == "webchat"
            else [
                "Book a Demo (https://smiota.com/contact/)",
                "Get a Quote (https://smiota.com/get-quote/)",
                "Contact Sales (sales@smiota.com)",
            ]
        )

        return AgentResult(
            agent_name=self.name,
            content=response_text,
            requires_approval=False,
            suggested_actions=suggested_actions,
            metadata={
                "source_type": source_type,
                "is_grounded": is_grounded,
                "retrieved_chunks_count": len(scored_chunks),
                "sources": [s["url"] or s["title"] for s in detailed_sources],
                "detailed_sources": detailed_sources,
                "rag_service_url": rag_url,
                "rag_latency_ms": round(rag_latency_ms, 1),
                "llm_latency_ms": round(llm_latency_ms, 1),
                "provenance": {
                    "source_type": source_type,
                    "is_grounded": is_grounded,
                    "retrieved_chunks_count": len(scored_chunks),
                    "detailed_sources": detailed_sources,
                    "rag_latency_ms": round(rag_latency_ms, 1),
                    "llm_latency_ms": round(llm_latency_ms, 1),
                },
            },
        )
