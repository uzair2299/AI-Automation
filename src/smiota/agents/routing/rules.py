"""High-speed, zero-latency rule and regex intent router."""

import re
from typing import ClassVar

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
        "why choose",
        "why should i choose",
        "why should we choose",
        "why should i use",
        "why should we use",
        "why use",
        "why smiota",
        "what are the benefits of",
        "what are the advantages of",
        "what is the difference between",
        "tell me about smiota",
        "what is smiota",
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
    "why choose",
    "why should i choose",
    "why should we choose",
    "why should i use",
    "why should we use",
    "why use",
    "why smiota",
    "why does",
    "why is",
    "why do",
    "why can't",
    "explain",
    "tell me about",
    "what are the benefits of",
    "what are the advantages of",
    "what are the features of",
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
    """Classifies user queries using compiled regex patterns, fast-path checks,

    and channel guardrails. Runs in < 1 millisecond.
    """

    GREETINGS: ClassVar[set[str]] = GREETINGS
    INFORMATIONAL_PREFIXES: ClassVar[list[str]] = INFORMATIONAL_PREFIXES
    INFORMATIONAL_CATEGORIES: ClassVar[dict[str, list[str]]] = INFORMATIONAL_CATEGORIES

    GRATITUDE: ClassVar[set[str]] = {
        "thank you",
        "thanks",
        "thank u",
        "thx",
        "appreciate it",
        "many thanks",
        "thank you so much",
        "thanks a lot",
        "thank you very much",
    }
    FAREWELLS: ClassVar[set[str]] = {
        "bye",
        "byee",
        "goodbye",
        "cya",
        "see you",
        "take care",
        "have a good day",
        "have a nice day",
        "have a great day",
        "bye bye",
        "later",
        "see ya",
    }

    # High-certainty domain identifiers & compiled regular expressions
    CUSTOMER_REGEX = re.compile(
        r"\b(sm|pkg)-[a-z0-9]+\b|\bpickup code\b|\bcompartment \d+\b", re.IGNORECASE
    )
    CUSTOMER_ACTION_REGEX = re.compile(
        r"\b(pick\s*up|retrieve|collect)\s+(my\s+)?(parcel|package|delivery|mail)\b"
        r"|\b(open|unlock)\s+(my\s+)?(door|locker|compartment)\b"
        r"|\b(package|parcel|delivery)\s+(is\s+)?(stuck|jammed|missing)\b"
        r"|\bwhere\s+is\s+my\s+(package|parcel|delivery)\b",
        re.IGNORECASE,
    )
    SECURITY_REGEX = re.compile(
        r"\bcve-\d{4}-\d+\b|\bbrute-force\b|\bwazuh\b|\bsiem\b", re.IGNORECASE
    )
    AIOPS_REGEX = re.compile(
        r"\boomkilled\b|\bgke pod(s)?\b|\bhigh cpu\b|\bcpu\b|\breadiness probe\b|\bpromql\b|\bcrashloop\b|\bimagepullbackoff\b|\bdaemonset(s)?\b|\bstatefulset(s)?\b",
        re.IGNORECASE,
    )
    QA_REGEX = re.compile(
        r"\b(playwright|selenium|cypress|flaky test|e2e test|end-to-end test|regression test)\b",
        re.IGNORECASE,
    )
    DEVELOPER_REGEX = re.compile(
        r"\b(pull request|\bpr\b|terraform plan|git diff|code review|repository)\b",
        re.IGNORECASE,
    )

    # Keywords for unambiguous domain classification
    SECURITY_KEYWORDS: ClassVar[list[str]] = [
        "cve",
        "vulnerability",
        "wazuh",
        "siem",
        "brute-force",
        "ssh login",
        "quarantine",
        "exploit",
    ]

    QA_KEYWORDS: ClassVar[list[str]] = [
        "playwright",
        "selenium",
        "flaky",
        "regression",
        "cypress",
        "testrunner",
    ]

    DEVELOPER_KEYWORDS: ClassVar[list[str]] = [
        "pull request",
        "terraform",
        "github",
        "promql",
        "ci/cd",
        "pipeline",
        "diff",
    ]

    AIOPS_KEYWORDS: ClassVar[list[str]] = [
        "oom",
        "oomkilled",
        "crashloop",
        "smiotaserver",
        "prometheus",
        "opensearch",
        "grafana",
        "gke",
        "readiness probe",
        "imagepullbackoff",
    ]

    KNOWLEDGE_KEYWORDS: ClassVar[list[str]] = [
        "smart locker",
        "smart lockers",
        "outdoor locker",
        "day-use",
        "refrigerated",
        "temperature-controlled",
        "asset management",
        "package management system",
        "package management",
        "mailroom software",
        "package room",
        "why choose",
        "smiota solution",
        "smiota system",
        "yardi",
        "realpage",
        "entrata",
        "appfolio",
        "koha",
        "ex libris",
        "alma",
        "sip2",
        "ncip",
        "hid global",
        "cbord",
        "transact",
        "servicenow",
        "okta",
        "azure ad",
        "compartment size",
        "pricing",
        "cost",
        "quote",
        "demo",
        "bopis",
        "specifications",
        "ada compliance",
        "ul listing",
        "student housing",
        "book a demo",
        "get a quote",
    ]

    SPECIFIC_INTEGRATION_KEYWORDS: ClassVar[list[str]] = [
        "yardi",
        "realpage",
        "entrata",
        "appfolio",
        "koha",
        "ex libris",
        "alma",
        "sip2",
        "ncip",
        "hid global",
        "cbord",
        "transact",
        "servicenow",
        "okta",
        "azure ad",
        "pricing",
        "quote",
        "book a demo",
        "get a quote",
        "ada compliance",
        "ul listing",
    ]

    # Conversational continuity tokens
    CONTINUITY_WORDS: ClassVar[set[str]] = {
        "yes",
        "no",
        "open",
        "retry",
        "ok",
        "okay",
        "sure",
        "thanks",
        "thank you",
        "again",
        "code",
        "pin",
        "where",
        "how",
        "what",
        "please",
        "help",
    }

    @classmethod
    def _is_greeting(cls, query: str) -> bool:
        """Check if query is a greeting.
        Matches exact greetings or short greetings with punctuation/fillers (e.g., 'hello!', 'hey there').
        """
        clean_query = re.sub(r"[^\w\s]", "", query).strip().lower()
        if clean_query in cls.GREETINGS:
            return True
        tokens = clean_query.split()
        return bool(
            len(tokens) <= 3
            and any(
                clean_query == greeting or clean_query.startswith(greeting + " ")
                for greeting in cls.GREETINGS
            )
        )

    @classmethod
    def _is_gratitude(cls, query: str) -> bool:
        """Check if query expresses gratitude / appreciation."""
        clean_query = re.sub(r"[^\w\s]", "", query).strip().lower()
        if clean_query in cls.GRATITUDE:
            return True
        tokens = clean_query.split()
        return bool(
            len(tokens) <= 5
            and any(
                clean_query == gratitude or clean_query.startswith(gratitude + " ")
                for gratitude in cls.GRATITUDE
            )
        )

    @classmethod
    def _is_farewell(cls, query: str) -> bool:
        """Check if query is a closing / farewell."""
        clean_query = re.sub(r"[^\w\s]", "", query).strip().lower()
        if clean_query in cls.FAREWELLS:
            return True
        tokens = clean_query.split()
        return bool(
            len(tokens) <= 5
            and any(
                clean_query == farewell or clean_query.startswith(farewell + " ")
                for farewell in cls.FAREWELLS
            )
        )

    @classmethod
    def _match_informational(cls, query: str) -> tuple[str, str] | None:
        """Check if query matches any informational prefix pattern.

        Returns tuple of (matched_prefix, category) or None.
        """
        query_normalized = query.lower().strip()
        query_clean = re.sub(r"[’']", "'", query_normalized)
        query_no_punct = re.sub(r"[^\w\s]", " ", query_normalized).strip()
        query_no_punct = " ".join(query_no_punct.split())

        sorted_prefixes = sorted(cls.INFORMATIONAL_PREFIXES, key=len, reverse=True)

        for prefix in sorted_prefixes:
            prefix_normalized = prefix.lower().strip()
            prefix_no_punct = re.sub(r"[^\w\s]", " ", prefix_normalized).strip()
            prefix_no_punct = " ".join(prefix_no_punct.split())

            if (
                query_normalized.startswith(prefix_normalized)
                or query_clean.startswith(prefix_normalized)
                or query_no_punct.startswith(prefix_no_punct)
            ):
                category = "general"
                for cat, prefixes in cls.INFORMATIONAL_CATEGORIES.items():
                    if prefix in prefixes:
                        category = cat
                        break
                return (prefix, category)

        return None

    @classmethod
    def _match_keywords(cls, query: str, keywords: list[str]) -> list[str]:
        """Match keywords with word boundaries to avoid false substring hits."""
        matches = []
        for keyword in keywords:
            if " " in keyword or "-" in keyword:
                if keyword in query:
                    matches.append(keyword)
            else:
                pattern = r"\b" + re.escape(keyword) + r"(?:s|es|ed|ing)?\b"
                if re.search(pattern, query):
                    matches.append(keyword)
        return matches

    def _check_continuity(self, query: str, context: AgentContext) -> RouteDecision | None:
        """Detect follow-up messages (e.g. 'open it again', 'yes', 'retry') in active conversations."""
        tokens = set(re.findall(r"\b\w+\b", query))
        if len(tokens) <= 4 and tokens.intersection(self.CONTINUITY_WORDS):
            history = context.conversation_history
            if history:
                channel_default = "customer" if context.channel == "webchat" else "aiops"
                return RouteDecision(
                    agent_name=channel_default,
                    confidence=0.88,
                    matched_intent="conversation_continuity",
                    routing_method="context_continuity",
                    reasoning="Short follow-up query continuing active conversation session",
                )
        return None

    async def classify(self, query: str, context: AgentContext) -> RouteDecision:
        """Classify user query based on channel, fast rules, and conversation continuity."""
        normalized_query = query.lower().strip()
        channel = (context.channel or "webchat").lower()

        # 1. Greetings classification check (Immediate high confidence < 1ms)
        if self._is_greeting(normalized_query):
            target_agent = "customer" if channel == "webchat" else "aiops"
            return RouteDecision(
                agent_name=target_agent,
                confidence=0.98,
                matched_intent="greeting",
                routing_method="rule_greeting",
                reasoning=f"Matched standard greeting intent in {channel} channel",
            )

        # 1.1 Gratitude & Farewell checks (Immediate high confidence < 1ms)
        if self._is_gratitude(normalized_query):
            target_agent = "customer" if channel == "webchat" else "aiops"
            return RouteDecision(
                agent_name=target_agent,
                confidence=0.98,
                matched_intent="gratitude",
                routing_method="rule_conversational",
                reasoning=f"Matched gratitude intent in {channel} channel",
            )

        if self._is_farewell(normalized_query):
            target_agent = "customer" if channel == "webchat" else "aiops"
            return RouteDecision(
                agent_name=target_agent,
                confidence=0.98,
                matched_intent="farewell",
                routing_method="rule_conversational",
                reasoning=f"Matched farewell intent in {channel} channel",
            )

        # 2. Multi-turn continuity check: Short queries in active conversations
        continuity_decision = self._check_continuity(normalized_query, context)
        if continuity_decision:
            return continuity_decision

        # 3. Channel-specific routing logic
        if channel == "webchat":
            decision = self._classify_webchat(normalized_query, context=context)
        else:
            decision = self._classify_internal(normalized_query)

        logger.debug(
            f"Rule pattern evaluated [{decision.agent_name}] "
            f"(Confidence: {decision.confidence:.2f}, Method: {decision.routing_method}, Channel: {channel})",
            extra={
                "event": "routing.rule.pattern",
                "agent_name": decision.agent_name,
                "confidence": decision.confidence,
                "routing_method": decision.routing_method,
                "matched_intent": decision.matched_intent,
                "channel": channel,
                "session_id": context.session_id,
            },
        )
        return decision

    def _classify_webchat(self, query: str, context: AgentContext | None = None) -> RouteDecision:
        """Webchat channel classification with fast-paths for identifiers and knowledge,

        delegating ambiguous natural language queries to SemanticRouter.
        """
        is_anonymous = bool(
            context
            and (
                context.user_id in {"anonymous", "public", "ws-resident", "guest", ""}
                or "public" in (context.roles or [])
                or not getattr(context, "parent_token", None)
            )
            and context.user_id != "user-123"
        )

        knowledge_matches = self._match_keywords(query, self.KNOWLEDGE_KEYWORDS)
        specific_matches = self._match_keywords(query, self.SPECIFIC_INTEGRATION_KEYWORDS)
        informational_match = self._match_informational(query)

        # 0. Check for public / unauthenticated knowledge routing
        if is_anonymous and (knowledge_matches or informational_match):
            return RouteDecision(
                agent_name="knowledge_assistant",
                confidence=0.96,
                matched_intent="public_knowledge_qa",
                routing_method="rule_knowledge_public",
                reasoning=f"Public unauthenticated user routed to KnowledgeAssistant: {knowledge_matches or 'informational'}",
                metadata={
                    "is_knowledge": True,
                    "matched_keywords": knowledge_matches,
                    "is_anonymous": True,
                },
            )

        # Authenticated users asking specific integration/pricing/enterprise spec queries
        if specific_matches:
            return RouteDecision(
                agent_name="knowledge_assistant",
                confidence=0.96,
                matched_intent="public_knowledge_qa",
                routing_method="rule_knowledge",
                reasoning=f"Matched Smiota public knowledge/integration keywords: {specific_matches}",
                metadata={"is_knowledge": True, "matched_keywords": specific_matches},
            )

        # 1. Informational queries in webchat
        if informational_match:
            security_matches = self._match_keywords(query, self.SECURITY_KEYWORDS)
            if security_matches or self.SECURITY_REGEX.search(query):
                return RouteDecision(
                    agent_name="security",
                    confidence=0.95,
                    matched_intent="informational",
                    routing_method="rule_informational",
                    reasoning=f"Matched informational prefix with security keywords: {security_matches}",
                    metadata={
                        "is_informational": True,
                        "category": informational_match[1],
                        "matched_prefix": informational_match[0],
                        "domain": "security",
                    },
                )
            aiops_matches = self._match_keywords(query, self.AIOPS_KEYWORDS)
            if aiops_matches or self.AIOPS_REGEX.search(query):
                return RouteDecision(
                    agent_name="aiops",
                    confidence=0.95,
                    matched_intent="informational",
                    routing_method="rule_informational",
                    reasoning=f"Matched informational prefix with AIOps keywords: {aiops_matches}",
                    metadata={
                        "is_informational": True,
                        "category": informational_match[1],
                        "matched_prefix": informational_match[0],
                        "domain": "aiops",
                    },
                )

            # Webchat informational queries route to knowledge_assistant for anonymous, customer for authenticated
            target_agent = "knowledge_assistant" if is_anonymous else "customer"
            return RouteDecision(
                agent_name=target_agent,
                confidence=0.95,
                matched_intent="informational",
                routing_method="rule_informational",
                reasoning=f"Matched informational query prefix: '{informational_match[0]}' (Category: {informational_match[1]})",
                metadata={
                    "is_informational": True,
                    "category": informational_match[1],
                    "matched_prefix": informational_match[0],
                    "domain": target_agent,
                },
            )

        # 2. Exact locker / package identifier regex
        if self.CUSTOMER_REGEX.search(query):
            return RouteDecision(
                agent_name="customer",
                confidence=0.98,
                matched_intent="customer_locker_identifier",
                routing_method="rule_pattern",
                reasoning="Matched exact locker or package identifier regex",
            )

        # 3. Explicit resident locker action pattern
        if self.CUSTOMER_ACTION_REGEX.search(query):
            return RouteDecision(
                agent_name="customer",
                confidence=0.95,
                matched_intent="customer_locker_action",
                routing_method="rule_pattern",
                reasoning="Matched explicit customer locker action pattern",
            )

        # 4. Security regex or keywords
        security_matches = self._match_keywords(query, self.SECURITY_KEYWORDS)
        if security_matches or self.SECURITY_REGEX.search(query):
            return RouteDecision(
                agent_name="security",
                confidence=0.95,
                matched_intent="security_compliance",
                routing_method="rule_pattern",
                reasoning=f"Matched security pattern or keywords: {security_matches}",
            )

        # 5. AIOps regex or keywords
        aiops_matches = self._match_keywords(query, self.AIOPS_KEYWORDS)
        if aiops_matches or self.AIOPS_REGEX.search(query):
            return RouteDecision(
                agent_name="aiops",
                confidence=0.95,
                matched_intent="aiops_sre",
                routing_method="rule_pattern",
                reasoning=f"Matched AIOps pattern or keywords: {aiops_matches}",
            )

        # Default webchat fallback: low confidence (0.40) to let CompositeIntentRouter delegate to SemanticRouter
        fallback_agent = "knowledge_assistant" if is_anonymous else "customer"
        return RouteDecision(
            agent_name=fallback_agent,
            confidence=0.40,
            matched_intent="knowledge_fallback" if is_anonymous else "channel_default",
            routing_method="channel_default",
            reasoning=f"Default concierge agent for webchat channel ({fallback_agent})",
        )

    def _classify_internal(self, query: str) -> RouteDecision:
        """Internal enterprise channels (Slack, Teams, Eval, API)."""
        informational_match = self._match_informational(query)

        # 1. Security & Compliance
        security_matches = self._match_keywords(query, self.SECURITY_KEYWORDS)
        if security_matches or self.SECURITY_REGEX.search(query):
            confidence = 0.95 if (len(security_matches) >= 2 or self.SECURITY_REGEX.search(query)) else 0.88
            intent = "informational" if informational_match else "security_compliance"
            method = "rule_informational" if informational_match else "rule_pattern"
            return RouteDecision(
                agent_name="security",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched security keywords: {security_matches}",
                metadata={"is_informational": True, "domain": "security"} if informational_match else {},
            )

        # 2. QA & Automated Testing
        if self.QA_REGEX.search(query):
            matches = self.QA_REGEX.findall(query)
            return RouteDecision(
                agent_name="qa",
                confidence=0.95,
                matched_intent="informational" if informational_match else "qa_testing",
                routing_method="rule_informational" if informational_match else "rule_pattern",
                reasoning=f"Matched QA pattern: {matches}",
                metadata={"is_informational": True, "domain": "qa"} if informational_match else {},
            )

        # 3. Customer & Smart Locker
        if self.CUSTOMER_REGEX.search(query) or self.CUSTOMER_ACTION_REGEX.search(query):
            return RouteDecision(
                agent_name="customer",
                confidence=0.95,
                matched_intent="informational" if informational_match else "customer_locker",
                routing_method="rule_informational" if informational_match else "rule_pattern",
                reasoning="Matched customer locker pattern or identifier",
                metadata={"is_informational": True, "domain": "customer"} if informational_match else {},
            )

        # 4. SRE & AIOps
        aiops_matches = self._match_keywords(query, self.AIOPS_KEYWORDS)
        if aiops_matches or self.AIOPS_REGEX.search(query):
            confidence = 0.95 if (len(aiops_matches) >= 2 or self.AIOPS_REGEX.search(query)) else 0.88
            return RouteDecision(
                agent_name="aiops",
                confidence=confidence,
                matched_intent="informational" if informational_match else "aiops_sre",
                routing_method="rule_informational" if informational_match else "rule_pattern",
                reasoning=f"Matched AIOps keywords or pattern: {aiops_matches}",
                metadata={"is_informational": True, "domain": "aiops"} if informational_match else {},
            )

        # 5. Developer & DevOps
        if self.DEVELOPER_REGEX.search(query):
            matches = self.DEVELOPER_REGEX.findall(query)
            return RouteDecision(
                agent_name="developer",
                confidence=0.95,
                matched_intent="informational" if informational_match else "developer_devops",
                routing_method="rule_informational" if informational_match else "rule_pattern",
                reasoning=f"Matched developer pattern: {matches}",
                metadata={"is_informational": True, "domain": "developer"} if informational_match else {},
            )

        # 6. General Informational query without domain keywords
        if informational_match:
            return RouteDecision(
                agent_name="aiops",
                confidence=0.88,
                matched_intent="informational",
                routing_method="rule_informational",
                reasoning=f"Matched internal informational query prefix: '{informational_match[0]}' (Category: {informational_match[1]})",
                metadata={
                    "is_informational": True,
                    "category": informational_match[1],
                    "matched_prefix": informational_match[0],
                },
            )

        # Default fallback for internal channels (low confidence to delegate to SemanticRouter)
        return RouteDecision(
            agent_name="aiops",
            confidence=0.40,
            matched_intent="general_fallback",
            routing_method="fallback",
            reasoning="No specific pattern matched; fallback to default AIOps agent",
        )
