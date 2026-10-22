"""High-speed, zero-latency rule and regex intent router."""
import re
from typing import Optional
from smiota.agents.base import AgentContext
from smiota.agents.routing.base import BaseIntentRouter
from smiota.agents.routing.schema import RouteDecision
from smiota.core.logging import logger


GREETINGS = {"hi", "hello", "hey", "good morning", "good evening", "greetings"}

INFORMATIONAL_CATEGORIES = {
    "how_to": [
        "how to",
        "how do i",
        "how can i",
        "how does",
        "how do you",
        "how should i",
    ],
    "definitions": [
        "what is",
        "what are",
        "what does",
        "what do you mean by",
        "define",
    ],
    "explanations": [
        "why does",
        "why is",
        "why do",
        "why can't",
        "why cant",
        "explain",
        "tell me about",
    ],
    "instructions": [
        "what steps",
        "what should i do",
        "guide me",
        "show me how",
    ],
    "general_knowledge": [
        "can you explain",
        "could you explain",
        "help me understand",
        "i want to know",
    ],
    "process_policy": [
        "what is the process",
        "what is the policy",
        "what are the requirements",
        "how does the process work",
    ],
    "capabilities": [
        "does smiota",
        "can smiota",
        "is it possible to",
        "do you support",
    ],
    "troubleshooting": [
        "why am i unable to",
        "why is my locker",
        "what causes",
        "what should i do if",
    ],
}

INFORMATIONAL_PREFIXES = [
    # How-to
    "how to",
    "how do i",
    "how can i",
    "how does",
    "how do you",
    "how should i",
    # Definitions
    "what is",
    "what are",
    "what does",
    "what do you mean by",
    "define",
    # Explanations
    "why does",
    "why is",
    "why do",
    "why can't",
    "explain",
    "tell me about",
    # Instructions
    "what steps",
    "what should i do",
    "guide me",
    "show me how",
    # General knowledge
    "can you explain",
    "could you explain",
    "help me understand",
    "i want to know",
    # Process and policy
    "what is the process",
    "what is the policy",
    "what are the requirements",
    "how does the process work",
    # Capabilities
    "does smiota",
    "can smiota",
    "is it possible to",
    "do you support",
    # Troubleshooting
    "what causes",
    "what should i do if",
    "why am i unable to",
    "why is my locker",
]


class RuleBasedRouter(BaseIntentRouter):
    """Classifies user queries using compiled regex patterns, weighted keyword dictionaries,

    and channel guardrails. Runs in < 1 millisecond.
    """

    GREETINGS = GREETINGS
    INFORMATIONAL_PREFIXES = INFORMATIONAL_PREFIXES
    INFORMATIONAL_CATEGORIES = INFORMATIONAL_CATEGORIES

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

    @classmethod
    def _match_informational(cls, q: str) -> Optional[tuple[str, str]]:
        """Check if query matches any informational prefix pattern.

        Returns tuple of (matched_prefix, category) or None.
        """
        q_norm = q.lower().strip()
        q_clean = re.sub(r"[’']", "'", q_norm)
        q_no_punct = re.sub(r"[^\w\s]", " ", q_norm).strip()
        q_no_punct = " ".join(q_no_punct.split())

        sorted_prefixes = sorted(cls.INFORMATIONAL_PREFIXES, key=len, reverse=True)

        for prefix in sorted_prefixes:
            p_norm = prefix.lower().strip()
            p_no_punct = re.sub(r"[^\w\s]", " ", p_norm).strip()
            p_no_punct = " ".join(p_no_punct.split())

            if q_norm.startswith(p_norm) or q_clean.startswith(p_norm) or q_no_punct.startswith(p_no_punct):
                category = "general"
                for cat, prefixes in cls.INFORMATIONAL_CATEGORIES.items():
                    if prefix in prefixes:
                        category = cat
                        break
                return (prefix, category)

        return None

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
        # 1. Check standard greeting intent
        if self._is_greeting(q):
            return RouteDecision(
                agent_name="customer",
                confidence=0.98,
                matched_intent="greeting",
                routing_method="rule_greeting",
                reasoning="Matched standard greeting in webchat channel",
            )

        # 2. Check Informational questions in webchat (How-to, Definitions, Policies, Instructions, Capabilities, etc.)
        info_match = self._match_informational(q)
        if info_match:
            # Check if specifically asks about security
            sec_matches = self._match_keywords(q, self.SECURITY_KEYWORDS)
            if sec_matches or self.SECURITY_REGEX.search(q):
                return RouteDecision(
                    agent_name="security",
                    confidence=0.95,
                    matched_intent="informational",
                    routing_method="rule_informational",
                    reasoning=f"Matched informational prefix '{info_match[0]}' ({info_match[1]}) with security keywords: {sec_matches}",
                    metadata={"is_informational": True, "category": info_match[1], "matched_prefix": info_match[0], "domain": "security"},
                )
            # Check if specifically asks about AIOps
            aiops_matches = self._match_keywords(q, self.AIOPS_KEYWORDS)
            if aiops_matches or self.AIOPS_REGEX.search(q):
                return RouteDecision(
                    agent_name="aiops",
                    confidence=0.95,
                    matched_intent="informational",
                    routing_method="rule_informational",
                    reasoning=f"Matched informational prefix '{info_match[0]}' ({info_match[1]}) with AIOps keywords: {aiops_matches}",
                    metadata={"is_informational": True, "category": info_match[1], "matched_prefix": info_match[0], "domain": "aiops"},
                )
            # Default for webchat informational queries is customer concierge
            return RouteDecision(
                agent_name="customer",
                confidence=0.95,
                matched_intent="informational",
                routing_method="rule_informational",
                reasoning=f"Matched informational query prefix: '{info_match[0]}' (Category: {info_match[1]})",
                metadata={"is_informational": True, "category": info_match[1], "matched_prefix": info_match[0], "domain": "customer"},
            )

        # 3. Strong regex matches (e.g. direct parcel lookup or compartment code without informational phrasing)
        if self.CUSTOMER_REGEX.search(q):
            return RouteDecision(
                agent_name="customer",
                confidence=0.98,
                matched_intent="customer_locker_identifier",
                routing_method="rule_pattern",
                reasoning="Matched exact locker or package identifier regex",
            )

        # 4. Check security keywords (e.g. admin or staff testing in webchat)
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

        # 5. Check AIOps keywords (e.g. pod restarts, high CPU)
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

        # 6. Check Customer keywords
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

        # Check informational query prefix early
        info_match = self._match_informational(q)

        # 1. Security & Compliance
        sec_matches = self._match_keywords(q, self.SECURITY_KEYWORDS)
        if sec_matches or self.SECURITY_REGEX.search(q):
            confidence = 0.95 if (len(sec_matches) >= 2 or self.SECURITY_REGEX.search(q)) else 0.88
            intent = "informational" if info_match else "security_compliance"
            method = "rule_informational" if info_match else "rule_pattern"
            meta = {"is_informational": True, "category": info_match[1], "matched_prefix": info_match[0], "domain": "security"} if info_match else {}
            return RouteDecision(
                agent_name="security",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched security keywords: {sec_matches}",
                metadata=meta,
            )

        # 2. QA & Automated Testing
        qa_matches = self._match_keywords(q, self.QA_KEYWORDS)
        if qa_matches:
            confidence = 0.95 if len(qa_matches) >= 2 else 0.88
            intent = "informational" if info_match else "qa_testing"
            method = "rule_informational" if info_match else "rule_pattern"
            meta = {"is_informational": True, "category": info_match[1], "matched_prefix": info_match[0], "domain": "qa"} if info_match else {}
            return RouteDecision(
                agent_name="qa",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched QA keywords: {qa_matches}",
                metadata=meta,
            )

        # 3. Customer & Smart Locker
        cust_matches = self._match_keywords(q, self.CUSTOMER_KEYWORDS)
        if cust_matches or self.CUSTOMER_REGEX.search(q):
            confidence = 0.95 if (len(cust_matches) >= 2 or self.CUSTOMER_REGEX.search(q)) else 0.88
            intent = "informational" if info_match else "customer_locker"
            method = "rule_informational" if info_match else "rule_pattern"
            meta = {"is_informational": True, "category": info_match[1], "matched_prefix": info_match[0], "domain": "customer"} if info_match else {}
            return RouteDecision(
                agent_name="customer",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched customer keywords: {cust_matches}",
                metadata=meta,
            )

        # 4. SRE & AIOps
        aiops_matches = self._match_keywords(q, self.AIOPS_KEYWORDS)
        if aiops_matches or self.AIOPS_REGEX.search(q):
            confidence = 0.95 if (len(aiops_matches) >= 2 or self.AIOPS_REGEX.search(q)) else 0.88
            intent = "informational" if info_match else "aiops_sre"
            method = "rule_informational" if info_match else "rule_pattern"
            meta = {"is_informational": True, "category": info_match[1], "matched_prefix": info_match[0], "domain": "aiops"} if info_match else {}
            return RouteDecision(
                agent_name="aiops",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched AIOps keywords: {aiops_matches}",
                metadata=meta,
            )

        # 5. Developer & DevOps
        dev_matches = self._match_keywords(q, self.DEVELOPER_KEYWORDS)
        if dev_matches:
            confidence = 0.95 if len(dev_matches) >= 2 else 0.88
            intent = "informational" if info_match else "developer_devops"
            method = "rule_informational" if info_match else "rule_pattern"
            meta = {"is_informational": True, "category": info_match[1], "matched_prefix": info_match[0], "domain": "developer"} if info_match else {}
            return RouteDecision(
                agent_name="developer",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched developer keywords: {dev_matches}",
                metadata=meta,
            )

        # 6. Check General Informational query without domain keywords
        if info_match:
            return RouteDecision(
                agent_name="aiops",
                confidence=0.88,
                matched_intent="informational",
                routing_method="rule_informational",
                reasoning=f"Matched internal informational query prefix: '{info_match[0]}' (Category: {info_match[1]})",
                metadata={"is_informational": True, "category": info_match[1], "matched_prefix": info_match[0]},
            )

        # Default fallback for internal channels
        return RouteDecision(
            agent_name="aiops",
            confidence=0.40,
            matched_intent="general_fallback",
            routing_method="fallback",
            reasoning="No specific keyword matched; fallback to default AIOps agent",
        )
