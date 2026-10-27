"""Knowledge Assistant Agent: Grounded Smiota Product, Hardware, Solution & Integration QA."""
import re
from typing import ClassVar

from smiota.agents.base import AgentContext, AgentResult, BaseAgent
from smiota.core.logging import logger
from smiota.llm.provider import GeminiProvider
from smiota.rag.config import RAGConfig
from smiota.rag.prompts import (
    SMIOTA_KNOWLEDGE_ASSISTANT_SYSTEM_PROMPT,
    build_rag_prompt,
)
from smiota.rag.retrieval.retrieval_service import RetrievalService
from smiota.schemas.agents import AgentCapability


class KnowledgeAssistantAgent(BaseAgent):
    """Public-facing Smiota AI Knowledge Assistant.

    Provides strict retrieval-bounded, zero-hallucination answers regarding
    smart locker products, technical specifications, and system integrations.
    Has zero mutation or tenant-account access tools.
    """

    PRIVATE_DATA_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"\b(where is my (package|parcel|delivery)|my package|my delivery)\b", re.IGNORECASE),
        re.compile(r"\b(my pin|my qr code|locker pin|pickup code|door pin|pickup pin)\b", re.IGNORECASE),
        re.compile(r"\b(open locker|unlock door|open door|door #\d+|locker #\d+)\b", re.IGNORECASE),
        re.compile(r"\b(tenant account|resident account|look up account|resident profile)\b", re.IGNORECASE),
    ]

    CARRIER_TRACKING_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"\b(1z[0-9a-z]{16}|94[0-9]{20}|92[0-9]{20}|tba[0-9]{12})\b", re.IGNORECASE),
        re.compile(r"\b(usps|ups|fedex|dhl|amazon) tracking\b", re.IGNORECASE),
    ]

    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
        llm_provider: GeminiProvider | None = None,
        config: RAGConfig | None = None,
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
        self.retrieval_service = retrieval_service or RetrievalService(config=self.config)
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
                suggested_actions=[
                    "Check SMS or email for PIN code",
                    "Open Smiota Mobile App",
                    "Contact building management",
                ],
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
                suggested_actions=[
                    "Track package on USPS.com",
                    "Track package on UPS.com",
                    "Track package on FedEx.com",
                ],
                metadata={"refusal_type": "carrier_tracking"},
            )

        # 3. Retrieve relevant public knowledge context
        scored_chunks = await self.retrieval_service.retrieve(
            query=query,
            top_k=5,
            enable_mmr=True,
        )

        # 4. Construct prompt with dynamic retrieved chunks
        full_prompt = build_rag_prompt(
            user_message=query,
            retrieved_chunks=scored_chunks,
            system_prompt=self.system_prompt,
        )

        # 5. Synthesize response via LLM
        response_text = await self.llm_provider.generate_completion(
            prompt=full_prompt,
            temperature=0.2,
        )

        logger.info(
            f"KnowledgeAssistant generated answer (chunks: {len(scored_chunks)})",
            extra={
                "event": "agent.knowledge.completed",
                "session_id": context.session_id,
                "chunks_retrieved": len(scored_chunks),
            },
        )

        suggested_actions = [
            "Book a Demo (https://smiota.com/contact/)",
            "Get a Quote (https://smiota.com/get-quote/)",
            "Contact Sales (sales@smiota.com)",
        ]

        return AgentResult(
            agent_name=self.name,
            content=response_text,
            requires_approval=False,
            suggested_actions=suggested_actions,
            metadata={
                "is_grounded": True,
                "retrieved_chunks_count": len(scored_chunks),
                "sources": [
                    c.chunk.metadata.get("canonical_url") or c.chunk.metadata.get("source_url") or c.chunk.title
                    for c in scored_chunks
                ],
            },
        )
