"""Semantic & Embedding Intent Router powered by Gemini & Vertex AI."""

import json
import math
import re
from typing import Optional

from smiota.agents.base import AgentContext
from smiota.agents.registry import AgentRegistry
from smiota.agents.routing.base import BaseIntentRouter
from smiota.agents.routing.schema import RouteDecision
from smiota.core.logging import logger
from smiota.llm.provider import GeminiProvider

# Domain descriptions guiding zero-shot semantic classification
DOMAIN_DESCRIPTIONS: dict[str, str] = {
    "knowledge_assistant": (
        "Official Smiota smart locker product solutions, technical hardware specifications (NEMA 4, dimensions, touchscreen), "
        "locker models (refrigerated, outdoor, indoor, day-use), system integrations (Yardi, RealPage, Entrata, Koha, etc.), "
        "capabilities, benefits, pricing/demo inquiries, and company documentation. "
        "Handles queries like 'why choose Smiota package management system', 'tell me about refrigerated lockers', "
        "'what integrations do you support', 'specifications of smart lockers'."
    ),
    "customer": (
        "Live resident & customer locker pickup operations: finding where a package is stored, retrieving pickup PIN codes "
        "or QR codes, reporting open or jammed compartment doors, unlocking locker doors, and checking parcel delivery status."
    ),
    "aiops": (
        "Infrastructure operations, Kubernetes (k8s) pods, Prometheus metrics, crashloops, OOMKilled, deployment rollouts, "
        "service latency, 5xx errors, GKE cluster diagnostics, SRE incident response."
    ),
    "security": (
        "Security vulnerabilities, CVE alerts, Wazuh SIEM events, suspicious SSH logins, brute-force attempts, IAM roles, "
        "service account permissions, firewall policies, audit compliance."
    ),
    "developer": (
        "Software engineering, GitHub pull requests, code reviews, Terraform IaC, CI/CD build pipelines, git diffs, commits."
    ),
    "qa": (
        "Automated test suites, Playwright, Selenium, end-to-end (E2E) testing, regression tests, flaky test diagnosis."
    ),
}

# Domain prototype anchors for vector embedding similarity
DOMAIN_ANCHORS: dict[str, list[str]] = {
    "knowledge_assistant": [
        "why choose smiota package management system",
        "what are the specifications and dimensions of smiota smart lockers",
        "does smiota integrate with yardi realpage or entrata property management",
        "tell me about refrigerated cold storage smart lockers for groceries",
        "what are the benefits features and pricing of smiota lockers",
        "how does smiota package delivery automation work and how to book a demo",
    ],
    "customer": [
        "where is my package in the locker compartment",
        "i need to pick up my parcel and retrieve my pin code",
        "the locker compartment door is stuck and will not open",
        "can you unlock compartment 4 for my package delivery",
        "what is my pickup code for the locker",
    ],
    "aiops": [
        "kubernetes pods are crash looping with oomkilled in production",
        "check prometheus metrics for high cpu and memory utilization",
        "investigate 504 gateway timeout errors and service latency",
        "gke cluster deployment rollout failed",
    ],
    "security": [
        "cve vulnerability detected in container image",
        "wazuh siem alert for suspicious brute force ssh login",
        "revoke compromised service account credentials",
    ],
    "developer": [
        "review pull request diff and terraform plan",
        "merge github pr and check github actions pipeline",
    ],
    "qa": [
        "playwright automated end to end test failed on checkout flow",
        "investigate flaky regression test in automated test suite",
    ],
}


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)


class SemanticRouter(BaseIntentRouter):
    """Uses Gemini / Vertex AI semantic reasoning and vector embeddings to classify user intent

    for queries that cannot be resolved with high confidence by fast rule patterns alone.
    """

    def __init__(self, provider: Optional[GeminiProvider] = None):
        self.provider = provider or GeminiProvider()
        self._anchor_embeddings: dict[str, list[list[float]]] = {}
        self._embeddings_initialized = False

    async def _init_anchor_embeddings(self) -> None:
        """Lazily initialize vector embeddings for domain anchors."""
        if self._embeddings_initialized:
            return
        self._embeddings_initialized = True
        try:
            for domain, anchors in DOMAIN_ANCHORS.items():
                domain_embs = []
                for anchor in anchors:
                    emb = await self.provider.generate_embedding(anchor)
                    if emb and any(v != 0.0 for v in emb):
                        domain_embs.append(emb)
                if domain_embs:
                    self._anchor_embeddings[domain] = domain_embs
        except Exception as e:
            logger.debug(f"Anchor embedding pre-computation skipped: {e}")

    async def _classify_via_embeddings(
        self, query: str, candidate_domains: set[str]
    ) -> Optional[RouteDecision]:
        """Classify query using cosine similarity against domain anchor embeddings."""
        try:
            await self._init_anchor_embeddings()
            if not self._anchor_embeddings:
                return None

            query_emb = await self.provider.generate_embedding(query)
            if not query_emb or not any(v != 0.0 for v in query_emb):
                return None

            best_domain = None
            best_sim = -1.0

            for domain, anchor_vectors in self._anchor_embeddings.items():
                if domain not in candidate_domains:
                    continue
                sims = [_cosine_similarity(query_emb, a_emb) for a_emb in anchor_vectors]
                if sims:
                    top_sim = max(sims)
                    if top_sim > best_sim:
                        best_sim = top_sim
                        best_domain = domain

            if best_domain and best_sim >= 0.82:
                logger.info(
                    f"Embedding similarity matched [{best_domain}] (similarity: {best_sim:.3f})"
                )
                return RouteDecision(
                    agent_name=best_domain,
                    confidence=min(best_sim, 0.97),
                    matched_intent=f"{best_domain}_semantic_match",
                    routing_method="embedding_similarity",
                    reasoning=f"High cosine similarity ({best_sim:.2f}) to domain anchor embeddings",
                )
        except Exception as e:
            logger.debug(f"Embedding routing check skipped: {e}")
        return None

    def _canonicalize_agent_name(self, raw_name: str) -> str:
        """Map raw LLM output or domain name to registered agent identifier."""
        name = raw_name.lower().strip()
        if "knowledge" in name:
            return "knowledge_assistant"
        if "customer" in name:
            return "customer"
        if "aiops" in name or "sre" in name:
            return "aiops"
        if "security" in name:
            return "security"
        if "developer" in name or "devops" in name:
            return "developer"
        if "qa" in name or "test" in name:
            return "qa"
        return name

    async def classify(self, query: str, context: AgentContext) -> RouteDecision:
        """Classifies intent using vector embeddings and Gemini Flash semantic reasoning."""
        channel = (context.channel or "webchat").lower()

        # Build candidate agents dynamically from registry
        all_agents = AgentRegistry.list_agents()
        if channel == "webchat":
            # Guardrail: In webchat, candidates are customer, knowledge assistant, aiops, and security
            valid_webchat = {
                "customer",
                "knowledgeassistant",
                "knowledge_assistant",
                "knowledge",
                "aiops",
                "security",
            }
            candidate_agents = [
                a
                for a in all_agents
                if a["name"].lower() in valid_webchat
                or a.get("domain", "").lower() in valid_webchat
            ]
        else:
            candidate_agents = all_agents

        candidate_domains = {self._canonicalize_agent_name(a["name"]) for a in candidate_agents}
        candidate_domains.update(
            {self._canonicalize_agent_name(a.get("domain", "")) for a in candidate_agents}
        )

        # 1. Fast Vector Embedding Similarity Check
        embedding_decision = await self._classify_via_embeddings(query, candidate_domains)
        if embedding_decision:
            return embedding_decision

        # 2. LLM Semantic Routing with Gemini Flash
        agents_description = "\n".join(
            f"- {self._canonicalize_agent_name(a['name'])}: {DOMAIN_DESCRIPTIONS.get(self._canonicalize_agent_name(a['name']), a.get('description', ''))}"
            for a in candidate_agents
        )

        prompt = f"""You are the intent router for the Smiota platform.
Your task is to classify the user query into the single most appropriate agent domain.

Available Candidate Agents:
{agents_description}

User Channel: {channel}
User Query: "{query}"

Classification Rules:
- If the user asks about Smiota smart locker solutions, hardware specs, locker models (refrigerated, outdoor), pricing, demo, why choose Smiota, or integrations (Yardi, RealPage, Koha), choose 'knowledge_assistant'.
- If the user is asking about their personal package delivery, locker PIN, opening a compartment door, or parcel status, choose 'customer'.
- If the user is asking about Kubernetes, pods, Prometheus metrics, crashloops, or system outages, choose 'aiops'.
- If the user is asking about CVEs, Wazuh alerts, security compliance, or authentication threats, choose 'security'.

Respond strictly in valid JSON format with no markdown blocks:
{{
  "agent": "<agent_name_in_lowercase>",
  "confidence": <float between 0.0 and 1.0>,
  "intent": "<short_snake_case_intent_name>",
  "reasoning": "<one sentence explanation>"
}}
"""
        try:
            raw_response = await self.provider.generate_completion(
                prompt=prompt,
                temperature=0.0,
            )

            # Strip markdown ```json ``` markers if present
            cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw_response).strip()
            data = json.loads(cleaned)

            raw_agent = str(data.get("agent", "")).lower().strip()
            agent_name = self._canonicalize_agent_name(raw_agent)
            confidence = float(data.get("confidence", 0.90))
            intent = str(data.get("intent", "semantic_classified"))
            reasoning = str(data.get("reasoning", "Classified by Gemini semantic router"))

            # Validate that canonical agent exists in candidates
            if agent_name in candidate_domains:
                return RouteDecision(
                    agent_name=agent_name,
                    confidence=min(max(confidence, 0.0), 1.0),
                    matched_intent=intent,
                    routing_method="gemini_semantic",
                    reasoning=reasoning,
                )
        except Exception as e:
            logger.warning(f"SemanticRouter call failed: {e}. Falling back to default.")

        # Fallback if LLM classification fails
        fallback_agent = "customer" if channel == "webchat" else "aiops"
        return RouteDecision(
            agent_name=fallback_agent,
            confidence=0.50,
            matched_intent="semantic_fallback",
            routing_method="fallback",
            reasoning="Semantic classification unavailable or timed out; selected channel default",
        )
