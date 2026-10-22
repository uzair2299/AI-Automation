"""High-speed, zero-latency rule and regex intent router."""
import re
from typing import Optional
from smiota.agents.base import AgentContext
from smiota.agents.routing.base import BaseIntentRouter
from smiota.agents.routing.schema import RouteDecision
from smiota.core.logging import logger


GREETINGS = {"hi", "hello", "hey", "good morning", "good evening", "greetings"}


class RuleBasedRouter(BaseIntentRouter):
    """Classifies user queries using compiled regex patterns, weighted keyword dictionaries,

    and channel guardrails. Runs in < 1 millisecond.
    """

    GREETINGS = GREETINGS

    # High-certainty domain identifiers
    CUSTOMER_REGEX = re.compile(r"\b(sm|pkg)-[a-z0-9]+\b|\bpickup code\b|\bcompartment \d+\b", re.IGNORECASE)
    SECURITY_REGEX = re.compile(r"\bcve-\d{4}-\d+\b|\bbrute-force\b|\bwazuh\b|\bsiem\b", re.IGNORECASE)
    AIOPS_REGEX = re.compile(r"\boomkilled\b|\bgke pod\b|\breadiness probe\b|\bpromql\b", re.IGNORECASE)

    # Keyword dictionaries for domain classification
    SECURITY_KEYWORDS = [
        "security", "cve", "vulnerability", "iam", "wazuh", "threat", "siem",
        "service account", "revoke", "quarantine", "credential", "brute-force",
        "ssh login", "firewall", "audit", "exploit",
    ]

    QA_KEYWORDS = [
        "playwright", "selenium", "flaky", "regression", "test", "testrunner",
        "cypress", "end-to-end", "e2e", "assertion",
    ]

    CUSTOMER_KEYWORDS = [
        "locker", "customer", "ticket", "package", "door", "pickup", "dropoff",
        "parcel", "compartment", "track", "tracking", "sm-", "pkg-", "pin",
        "resident", "unlock", "delivery", "box", "deliveries",
    ]

    AIOPS_KEYWORDS = [
        "cpu", "memory", "oom", "restart", "metric", "prometheus", "opensearch",
        "grafana", "gke", "pod", "incident", "rca", "crash", "probe", "readiness",
        "k8s", "kubernetes", "latency", "alert",
    ]

    DEVELOPER_KEYWORDS = [
        "pr", "pull request", "terraform", "code", "github", "promql", "ci/cd",
        "pipeline", "diff", "commit", "git", "merge", "repo", "repository",
    ]

    # Conversational continuity tokens
    CONTINUITY_WORDS = {
        "yes", "no", "open", "retry", "ok", "okay", "sure", "thanks", "thank you",
        "again", "code", "pin", "where", "how", "what", "please", "help",
    }

    @classmethod
    def _is_greeting(cls, q: str) -> bool:
        """Check if query is a greeting.
        Matches exact greetings or short greetings with punctuation/fillers (e.g., 'hello!', 'hey there').
        """
        clean = re.sub(r"[^\w\s]", "", q).strip().lower()
        if clean in cls.GREETINGS:
            return True
        tokens = clean.split()
        if len(tokens) <= 3 and any(clean == g or clean.startswith(g + " ") for g in cls.GREETINGS):
            return True
        return False

    async def classify(self, query: str, context: AgentContext) -> RouteDecision:
        """Classify user query based on channel, rules, and conversation continuity."""
        q = query.lower().strip()
        channel = (context.channel or "webchat").lower()

        # 1. Greetings classification check (Immediate high confidence < 1ms)
        if self._is_greeting(q):
            target_agent = "customer" if channel == "webchat" else "aiops"
            return RouteDecision(
                agent_name=target_agent,
                confidence=0.98,
                matched_intent="greeting",
                routing_method="rule_greeting",
                reasoning=f"Matched standard greeting intent in {channel} channel",
            )

        # 2. Multi-turn continuity check: Short queries in active conversations
        continuity_decision = self._check_continuity(q, context)
        if continuity_decision:
            return continuity_decision

        # 3. Channel-specific routing logic
        if channel == "webchat":
            return self._classify_webchat(q)

        # 4. General internal routing (Slack, Teams, Eval, API)
        return self._classify_internal(q)

    def _check_continuity(self, q: str, context: AgentContext) -> Optional[RouteDecision]:
        """Detect follow-up messages (e.g. 'open it again', 'yes', 'retry') in active conversations."""
        tokens = set(re.findall(r"\b\w+\b", q))
        # If very short query (< 5 words) and mostly composed of conversational continuity tokens
        if len(tokens) <= 4 and tokens.intersection(self.CONTINUITY_WORDS):
            history = context.conversation_history
            if history:
                # Find the most recent assistant message to infer context
                channel_default = "customer" if context.channel == "webchat" else "aiops"
                return RouteDecision(
                    agent_name=channel_default,
                    confidence=0.88,
                    matched_intent="conversation_continuity",
                    routing_method="context_continuity",
                    reasoning=f"Short follow-up query '{q}' continuing active conversation session",
                )
        return None

    @classmethod
    def _match_keywords(cls, q: str, keywords: list[str]) -> list[str]:
        """Match keywords with word boundaries to avoid false substring hits (e.g. 'pin' in 'looping')."""
        matches = []
        for kw in keywords:
            if " " in kw or "-" in kw:
                if kw in q:
                    matches.append(kw)
            else:
                pattern = r"\b" + re.escape(kw) + r"(?:s|es|ed|ing)?\b"
                if re.search(pattern, q):
                    matches.append(kw)
        return matches

    def _classify_webchat(self, q: str) -> RouteDecision:
        """Webchat channel classification (prioritizes customer locker support,
        with support for operational security & incident queries).
        """
        # Check standard greeting intent
        if self._is_greeting(q):
            return RouteDecision(
                agent_name="customer",
                confidence=0.98,
                matched_intent="greeting",
                routing_method="rule_greeting",
                reasoning="Matched standard greeting in webchat channel",
            )

        # Strong regex matches
        if self.CUSTOMER_REGEX.search(q):
            return RouteDecision(
                agent_name="customer",
                confidence=0.98,
                matched_intent="customer_locker_identifier",
                routing_method="rule_pattern",
                reasoning="Matched exact locker or package identifier regex",
            )

        # Check security keywords (e.g. admin or staff testing in webchat)
        sec_matches = self._match_keywords(q, self.SECURITY_KEYWORDS)
        if sec_matches or self.SECURITY_REGEX.search(q):
            confidence = 0.95 if len(sec_matches) >= 2 or self.SECURITY_REGEX.search(q) else 0.88
            return RouteDecision(
                agent_name="security",
                confidence=confidence,
                matched_intent="security_compliance",
                routing_method="rule_pattern",
                reasoning=f"Matched security keywords: {sec_matches}",
            )

        # Check AIOps keywords (e.g. pod restarts, high CPU)
        aiops_matches = self._match_keywords(q, self.AIOPS_KEYWORDS)
        if aiops_matches or self.AIOPS_REGEX.search(q):
            confidence = 0.95 if len(aiops_matches) >= 2 or self.AIOPS_REGEX.search(q) else 0.88
            return RouteDecision(
                agent_name="aiops",
                confidence=confidence,
                matched_intent="aiops_sre",
                routing_method="rule_pattern",
                reasoning=f"Matched AIOps keywords: {aiops_matches}",
            )

        # Check Customer keywords
        cust_matches = self._match_keywords(q, self.CUSTOMER_KEYWORDS)
        if cust_matches:
            confidence = 0.95 if len(cust_matches) >= 2 else 0.88
            return RouteDecision(
                agent_name="customer",
                confidence=confidence,
                matched_intent="customer_locker",
                routing_method="rule_pattern",
                reasoning=f"Matched customer keywords: {cust_matches}",
            )

        # Default webchat fallback is customer assistant
        return RouteDecision(
            agent_name="customer",
            confidence=0.65,
            matched_intent="customer_fallback",
            routing_method="channel_default",
            reasoning="Default concierge agent for webchat channel",
        )

    def _classify_internal(self, q: str) -> RouteDecision:
        """Internal enterprise channels (Slack, Teams, Eval, API)."""
        # 0. Check standard greeting intent
        if self._is_greeting(q):
            return RouteDecision(
                agent_name="aiops",
                confidence=0.98,
                matched_intent="greeting",
                routing_method="rule_greeting",
                reasoning="Matched standard greeting in internal channel",
            )

        # 1. Security & Compliance
        sec_matches = self._match_keywords(q, self.SECURITY_KEYWORDS)
        if sec_matches or self.SECURITY_REGEX.search(q):
            confidence = 0.95 if (len(sec_matches) >= 2 or self.SECURITY_REGEX.search(q)) else 0.88
            return RouteDecision(
                agent_name="security",
                confidence=confidence,
                matched_intent="security_compliance",
                routing_method="rule_pattern",
                reasoning=f"Matched security keywords: {sec_matches}",
            )

        # 2. QA & Automated Testing
        qa_matches = self._match_keywords(q, self.QA_KEYWORDS)
        if qa_matches:
            confidence = 0.95 if len(qa_matches) >= 2 else 0.88
            return RouteDecision(
                agent_name="qa",
                confidence=confidence,
                matched_intent="qa_testing",
                routing_method="rule_pattern",
                reasoning=f"Matched QA keywords: {qa_matches}",
            )

        # 3. Customer & Smart Locker
        cust_matches = self._match_keywords(q, self.CUSTOMER_KEYWORDS)
        if cust_matches or self.CUSTOMER_REGEX.search(q):
            confidence = 0.95 if (len(cust_matches) >= 2 or self.CUSTOMER_REGEX.search(q)) else 0.88
            return RouteDecision(
                agent_name="customer",
                confidence=confidence,
                matched_intent="customer_locker",
                routing_method="rule_pattern",
                reasoning=f"Matched customer keywords: {cust_matches}",
            )

        # 4. SRE & AIOps
        aiops_matches = self._match_keywords(q, self.AIOPS_KEYWORDS)
        if aiops_matches or self.AIOPS_REGEX.search(q):
            confidence = 0.95 if (len(aiops_matches) >= 2 or self.AIOPS_REGEX.search(q)) else 0.88
            return RouteDecision(
                agent_name="aiops",
                confidence=confidence,
                matched_intent="aiops_sre",
                routing_method="rule_pattern",
                reasoning=f"Matched AIOps keywords: {aiops_matches}",
            )

        # 5. Developer & DevOps
        dev_matches = self._match_keywords(q, self.DEVELOPER_KEYWORDS)
        if dev_matches:
            confidence = 0.95 if len(dev_matches) >= 2 else 0.88
            return RouteDecision(
                agent_name="developer",
                confidence=confidence,
                matched_intent="developer_devops",
                routing_method="rule_pattern",
                reasoning=f"Matched developer keywords: {dev_matches}",
            )

        # Default fallback for internal channels
        return RouteDecision(
            agent_name="aiops",
            confidence=0.40,
            matched_intent="general_fallback",
            routing_method="fallback",
            reasoning="No specific keyword matched; fallback to default AIOps agent",
        )
