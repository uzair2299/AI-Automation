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

    GREETINGS: ClassVar[set[str]] = GREETINGS
    INFORMATIONAL_PREFIXES: ClassVar[list[str]] = INFORMATIONAL_PREFIXES
    INFORMATIONAL_CATEGORIES: ClassVar[dict[str, list[str]]] = INFORMATIONAL_CATEGORIES

    GRATITUDE: ClassVar[set[str]] = {
        "thank you", "thanks", "thank u", "thx", "appreciate it", "many thanks",
        "thank you so much", "thanks a lot", "thank you very much",
    }
    FAREWELLS: ClassVar[set[str]] = {
        "bye", "byee", "goodbye", "cya", "see you", "take care", "have a good day",
        "have a nice day", "have a great day", "bye bye", "later", "see ya",
    }

    # High-certainty domain identifiers
    CUSTOMER_REGEX = re.compile(r"\b(sm|pkg)-[a-z0-9]+\b|\bpickup code\b|\bcompartment \d+\b", re.IGNORECASE)
    SECURITY_REGEX = re.compile(r"\bcve-\d{4}-\d+\b|\bbrute-force\b|\bwazuh\b|\bsiem\b", re.IGNORECASE)
    AIOPS_REGEX = re.compile(r"\boomkilled\b|\bgke pod\b|\breadiness probe\b|\bpromql\b", re.IGNORECASE)

    # Keyword dictionaries for domain classification
    SECURITY_KEYWORDS: ClassVar[list[str]] = [
        "security", "cve", "vulnerability", "iam", "wazuh", "threat", "siem",
        "service account", "revoke", "quarantine", "credential", "brute-force",
        "ssh login", "firewall", "audit", "exploit",
    ]

    QA_KEYWORDS: ClassVar[list[str]] = [
        "playwright", "selenium", "flaky", "regression", "test", "testrunner",
        "cypress", "end-to-end", "e2e", "assertion",
    ]

    CUSTOMER_KEYWORDS: ClassVar[list[str]] = [
        "locker", "customer", "ticket", "package", "door", "pickup", "dropoff",
        "parcel", "compartment", "track", "tracking", "sm-", "pkg-", "pin",
        "resident", "unlock", "delivery", "box", "deliveries", "collect", "collection", "mail",
        "uncollected", "unclaimed",
    ]

    AIOPS_KEYWORDS: ClassVar[list[str]] = [
        "cpu", "memory", "oom", "restart", "metric", "prometheus", "opensearch",
        "grafana", "gke", "pod", "incident", "rca", "crash", "probe", "readiness",
        "k8s", "kubernetes", "latency", "alert",
    ]

    DEVELOPER_KEYWORDS: ClassVar[list[str]] = [
        "pr", "pull request", "terraform", "code", "github", "promql", "ci/cd",
        "pipeline", "diff", "commit", "git", "merge", "repo", "repository",
    ]

    # Conversational continuity tokens
    CONTINUITY_WORDS: ClassVar[set[str]] = {
        "yes", "no", "open", "retry", "ok", "okay", "sure", "thanks", "thank you",
        "again", "code", "pin", "where", "how", "what", "please", "help",
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
        return bool(len(tokens) <= 3 and any(clean_query == greeting or clean_query.startswith(greeting + " ") for greeting in cls.GREETINGS))

    @classmethod
    def _is_gratitude(cls, query: str) -> bool:
        """Check if query expresses gratitude / appreciation."""
        clean_query = re.sub(r"[^\w\s]", "", query).strip().lower()
        if clean_query in cls.GRATITUDE:
            return True
        tokens = clean_query.split()
        return bool(len(tokens) <= 5 and any(clean_query == gratitude or clean_query.startswith(gratitude + " ") for gratitude in cls.GRATITUDE))

    @classmethod
    def _is_farewell(cls, query: str) -> bool:
        """Check if query is a closing / farewell."""
        clean_query = re.sub(r"[^\w\s]", "", query).strip().lower()
        if clean_query in cls.FAREWELLS:
            return True
        tokens = clean_query.split()
        return bool(len(tokens) <= 5 and any(clean_query == farewell or clean_query.startswith(farewell + " ") for farewell in cls.FAREWELLS))

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

            if query_normalized.startswith(prefix_normalized) or query_clean.startswith(prefix_normalized) or query_no_punct.startswith(prefix_no_punct):
                category = "general"
                for cat, prefixes in cls.INFORMATIONAL_CATEGORIES.items():
                    if prefix in prefixes:
                        category = cat
                        break
                return (prefix, category)

        return None

    async def classify(self, query: str, context: AgentContext) -> RouteDecision:
        """Classify user query based on channel, rules, and conversation continuity."""
        normalized_query = query.lower().strip()
        channel = (context.channel or "webchat").lower()

        # 1. Greetings classification check (Immediate high confidence < 1ms)
        if self._is_greeting(normalized_query):
            target_agent = "customer" if channel == "webchat" else "aiops"
            decision = RouteDecision(
                agent_name=target_agent,
                confidence=0.98,
                matched_intent="greeting",
                routing_method="rule_greeting",
                reasoning=f"Matched standard greeting intent in {channel} channel",
            )
            logger.debug(
                f"Rule greeting matched [{target_agent}] (channel={channel})",
                extra={
                    "event": "routing.rule.greeting",
                    "agent_name": target_agent,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                    "channel": channel,
                    "session_id": context.session_id,
                },
            )
            return decision

        # 1.1 Gratitude & Farewell checks (Immediate high confidence < 1ms)
        if self._is_gratitude(normalized_query):
            target_agent = "customer" if channel == "webchat" else "aiops"
            decision = RouteDecision(
                agent_name=target_agent,
                confidence=0.98,
                matched_intent="gratitude",
                routing_method="rule_conversational",
                reasoning=f"Matched gratitude intent in {channel} channel",
            )
            logger.debug(
                f"Rule conversational gratitude matched [{target_agent}] (channel={channel})",
                extra={
                    "event": "routing.rule.conversational",
                    "agent_name": target_agent,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                    "channel": channel,
                    "session_id": context.session_id,
                },
            )
            return decision

        if self._is_farewell(normalized_query):
            target_agent = "customer" if channel == "webchat" else "aiops"
            decision = RouteDecision(
                agent_name=target_agent,
                confidence=0.98,
                matched_intent="farewell",
                routing_method="rule_conversational",
                reasoning=f"Matched farewell intent in {channel} channel",
            )
            logger.debug(
                f"Rule conversational farewell matched [{target_agent}] (channel={channel})",
                extra={
                    "event": "routing.rule.conversational",
                    "agent_name": target_agent,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                    "channel": channel,
                    "session_id": context.session_id,
                },
            )
            return decision

        # 2. Multi-turn continuity check: Short queries in active conversations
        continuity_decision = self._check_continuity(normalized_query, context)
        if continuity_decision:
            logger.debug(
                f"Rule continuity matched [{continuity_decision.agent_name}] (session={context.session_id})",
                extra={
                    "event": "routing.rule.continuity",
                    "agent_name": continuity_decision.agent_name,
                    "confidence": continuity_decision.confidence,
                    "routing_method": continuity_decision.routing_method,
                    "matched_intent": continuity_decision.matched_intent,
                    "channel": channel,
                    "session_id": context.session_id,
                },
            )
            return continuity_decision

        # 3. Channel-specific routing logic
        if channel == "webchat":
            decision = self._classify_webchat(normalized_query)
        else:
            # 4. General internal routing (Slack, Teams, Eval, API)
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

    def _check_continuity(self, query: str, context: AgentContext) -> RouteDecision | None:
        """Detect follow-up messages (e.g. 'open it again', 'yes', 'retry') in active conversations."""
        tokens = set(re.findall(r"\b\w+\b", query))
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
                    reasoning="Short follow-up query continuing active conversation session",
                )
        return None

    @classmethod
    def _match_keywords(cls, query: str, keywords: list[str]) -> list[str]:
        """Match keywords with word boundaries to avoid false substring hits (e.g. 'pin' in 'looping')."""
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

    def _classify_webchat(self, query: str) -> RouteDecision:
        """Webchat channel classification (prioritizes customer locker support,
        with support for operational security & incident queries).
        """
        # 1. Check standard greeting intent
        if self._is_greeting(query):
            decision = RouteDecision(
                agent_name="customer",
                confidence=0.98,
                matched_intent="greeting",
                routing_method="rule_greeting",
                reasoning="Matched standard greeting in webchat channel",
            )
            logger.debug(
                "Webchat greeting rule matched",
                extra={
                    "event": "routing.rule.webchat.greeting",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # 1.1 Check gratitude and farewell in webchat
        if self._is_gratitude(query):
            decision = RouteDecision(
                agent_name="customer",
                confidence=0.98,
                matched_intent="gratitude",
                routing_method="rule_conversational",
                reasoning="Matched gratitude in webchat channel",
            )
            logger.debug(
                "Webchat gratitude rule matched",
                extra={
                    "event": "routing.rule.webchat.conversational",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        if self._is_farewell(query):
            decision = RouteDecision(
                agent_name="customer",
                confidence=0.98,
                matched_intent="farewell",
                routing_method="rule_conversational",
                reasoning="Matched farewell in webchat channel",
            )
            logger.debug(
                "Webchat farewell rule matched",
                extra={
                    "event": "routing.rule.webchat.conversational",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # 2. Check Informational questions in webchat (How-to, Definitions, Policies, Instructions, Capabilities, etc.)
        informational_match = self._match_informational(query)
        if informational_match:
            # Check if specifically asks about security
            security_matches = self._match_keywords(query, self.SECURITY_KEYWORDS)
            if security_matches or self.SECURITY_REGEX.search(query):
                decision = RouteDecision(
                    agent_name="security",
                    confidence=0.95,
                    matched_intent="informational",
                    routing_method="rule_informational",
                    reasoning=f"Matched informational prefix '{informational_match[0]}' ({informational_match[1]}) with security keywords: {security_matches}",
                    metadata={"is_informational": True, "category": informational_match[1], "matched_prefix": informational_match[0], "domain": "security"},
                )
                logger.debug(
                    f"Webchat informational security matched: category='{informational_match[1]}'",
                    extra={
                        "event": "routing.rule.webchat.informational",
                        "agent_name": decision.agent_name,
                        "confidence": decision.confidence,
                        "routing_method": decision.routing_method,
                        "matched_intent": decision.matched_intent,
                        "category": informational_match[1],
                    },
                )
                return decision
            # Check if specifically asks about AIOps
            aiops_matches = self._match_keywords(query, self.AIOPS_KEYWORDS)
            if aiops_matches or self.AIOPS_REGEX.search(query):
                decision = RouteDecision(
                    agent_name="aiops",
                    confidence=0.95,
                    matched_intent="informational",
                    routing_method="rule_informational",
                    reasoning=f"Matched informational prefix '{informational_match[0]}' ({informational_match[1]}) with AIOps keywords: {aiops_matches}",
                    metadata={"is_informational": True, "category": informational_match[1], "matched_prefix": informational_match[0], "domain": "aiops"},
                )
                logger.debug(
                    f"Webchat informational AIOps matched: category='{informational_match[1]}'",
                    extra={
                        "event": "routing.rule.webchat.informational",
                        "agent_name": decision.agent_name,
                        "confidence": decision.confidence,
                        "routing_method": decision.routing_method,
                        "matched_intent": decision.matched_intent,
                        "category": informational_match[1],
                    },
                )
                return decision
            # Default for webchat informational queries is customer concierge
            decision = RouteDecision(
                agent_name="customer",
                confidence=0.95,
                matched_intent="informational",
                routing_method="rule_informational",
                reasoning=f"Matched informational query prefix: '{informational_match[0]}' (Category: {informational_match[1]})",
                metadata={"is_informational": True, "category": informational_match[1], "matched_prefix": informational_match[0], "domain": "customer"},
            )
            logger.debug(
                f"Webchat informational customer matched: category='{informational_match[1]}'",
                extra={
                    "event": "routing.rule.webchat.informational",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                    "category": informational_match[1],
                },
            )
            return decision

        # 3. Strong regex matches (e.g. direct parcel lookup or compartment code without informational phrasing)
        if self.CUSTOMER_REGEX.search(query):
            decision = RouteDecision(
                agent_name="customer",
                confidence=0.98,
                matched_intent="customer_locker_identifier",
                routing_method="rule_pattern",
                reasoning="Matched exact locker or package identifier regex",
            )
            logger.debug(
                "Webchat customer locker identifier regex matched",
                extra={
                    "event": "routing.rule.webchat.regex",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # 4. Check security keywords (e.g. admin or staff testing in webchat)
        security_matches = self._match_keywords(query, self.SECURITY_KEYWORDS)
        if security_matches or self.SECURITY_REGEX.search(query):
            confidence = 0.95 if len(security_matches) >= 2 or self.SECURITY_REGEX.search(query) else 0.88
            decision = RouteDecision(
                agent_name="security",
                confidence=confidence,
                matched_intent="security_compliance",
                routing_method="rule_pattern",
                reasoning=f"Matched security keywords: {security_matches}",
            )
            logger.debug(
                "Webchat security keywords matched",
                extra={
                    "event": "routing.rule.webchat.keywords",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # 5. Check AIOps keywords (e.g. pod restarts, high CPU)
        aiops_matches = self._match_keywords(query, self.AIOPS_KEYWORDS)
        if aiops_matches or self.AIOPS_REGEX.search(query):
            confidence = 0.95 if len(aiops_matches) >= 2 or self.AIOPS_REGEX.search(query) else 0.88
            decision = RouteDecision(
                agent_name="aiops",
                confidence=confidence,
                matched_intent="aiops_sre",
                routing_method="rule_pattern",
                reasoning=f"Matched AIOps keywords: {aiops_matches}",
            )
            logger.debug(
                "Webchat AIOps keywords matched",
                extra={
                    "event": "routing.rule.webchat.keywords",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # 6. Check Customer keywords
        customer_matches = self._match_keywords(query, self.CUSTOMER_KEYWORDS)
        if customer_matches:
            confidence = 0.95 if len(customer_matches) >= 2 else 0.88
            decision = RouteDecision(
                agent_name="customer",
                confidence=confidence,
                matched_intent="customer_locker",
                routing_method="rule_pattern",
                reasoning=f"Matched customer keywords: {customer_matches}",
            )
            logger.debug(
                "Webchat customer keywords matched",
                extra={
                    "event": "routing.rule.webchat.keywords",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # Default webchat fallback is customer assistant
        decision = RouteDecision(
            agent_name="customer",
            confidence=0.65,
            matched_intent="customer_fallback",
            routing_method="channel_default",
            reasoning="Default concierge agent for webchat channel",
        )
        logger.debug(
            "Webchat channel fallback evaluated",
            extra={
                "event": "routing.rule.webchat.fallback",
                "agent_name": decision.agent_name,
                "confidence": decision.confidence,
                "routing_method": decision.routing_method,
                "matched_intent": decision.matched_intent,
            },
        )
        return decision

    def _classify_internal(self, query: str) -> RouteDecision:
        """Internal enterprise channels (Slack, Teams, Eval, API)."""
        # 0. Check standard greeting intent
        if self._is_greeting(query):
            decision = RouteDecision(
                agent_name="aiops",
                confidence=0.98,
                matched_intent="greeting",
                routing_method="rule_greeting",
                reasoning="Matched standard greeting in internal channel",
            )
            logger.debug(
                "Internal greeting rule matched",
                extra={
                    "event": "routing.rule.internal.greeting",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # Check informational query prefix early
        informational_match = self._match_informational(query)

        # 1. Security & Compliance
        security_matches = self._match_keywords(query, self.SECURITY_KEYWORDS)
        if security_matches or self.SECURITY_REGEX.search(query):
            confidence = 0.95 if (len(security_matches) >= 2 or self.SECURITY_REGEX.search(query)) else 0.88
            intent = "informational" if informational_match else "security_compliance"
            method = "rule_informational" if informational_match else "rule_pattern"
            meta = {"is_informational": True, "category": informational_match[1], "matched_prefix": informational_match[0], "domain": "security"} if informational_match else {}
            decision = RouteDecision(
                agent_name="security",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched security keywords: {security_matches}",
                metadata=meta,
            )
            logger.debug(
                "Internal security rule matched",
                extra={
                    "event": "routing.rule.internal.matched",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # 2. QA & Automated Testing
        qa_matches = self._match_keywords(query, self.QA_KEYWORDS)
        if qa_matches:
            confidence = 0.95 if len(qa_matches) >= 2 else 0.88
            intent = "informational" if informational_match else "qa_testing"
            method = "rule_informational" if informational_match else "rule_pattern"
            meta = {"is_informational": True, "category": informational_match[1], "matched_prefix": informational_match[0], "domain": "qa"} if informational_match else {}
            decision = RouteDecision(
                agent_name="qa",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched QA keywords: {qa_matches}",
                metadata=meta,
            )
            logger.debug(
                "Internal QA rule matched",
                extra={
                    "event": "routing.rule.internal.matched",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # 3. Customer & Smart Locker
        customer_matches = self._match_keywords(query, self.CUSTOMER_KEYWORDS)
        if customer_matches or self.CUSTOMER_REGEX.search(query):
            confidence = 0.95 if (len(customer_matches) >= 2 or self.CUSTOMER_REGEX.search(query)) else 0.88
            intent = "informational" if informational_match else "customer_locker"
            method = "rule_informational" if informational_match else "rule_pattern"
            meta = {"is_informational": True, "category": informational_match[1], "matched_prefix": informational_match[0], "domain": "customer"} if informational_match else {}
            decision = RouteDecision(
                agent_name="customer",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched customer keywords: {customer_matches}",
                metadata=meta,
            )
            logger.debug(
                "Internal customer rule matched",
                extra={
                    "event": "routing.rule.internal.matched",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # 4. SRE & AIOps
        aiops_matches = self._match_keywords(query, self.AIOPS_KEYWORDS)
        if aiops_matches or self.AIOPS_REGEX.search(query):
            confidence = 0.95 if (len(aiops_matches) >= 2 or self.AIOPS_REGEX.search(query)) else 0.88
            intent = "informational" if informational_match else "aiops_sre"
            method = "rule_informational" if informational_match else "rule_pattern"
            meta = {"is_informational": True, "category": informational_match[1], "matched_prefix": informational_match[0], "domain": "aiops"} if informational_match else {}
            decision = RouteDecision(
                agent_name="aiops",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched AIOps keywords: {aiops_matches}",
                metadata=meta,
            )
            logger.debug(
                "Internal AIOps rule matched",
                extra={
                    "event": "routing.rule.internal.matched",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # 5. Developer & DevOps
        developer_matches = self._match_keywords(query, self.DEVELOPER_KEYWORDS)
        if developer_matches:
            confidence = 0.95 if len(developer_matches) >= 2 else 0.88
            intent = "informational" if informational_match else "developer_devops"
            method = "rule_informational" if informational_match else "rule_pattern"
            meta = {"is_informational": True, "category": informational_match[1], "matched_prefix": informational_match[0], "domain": "developer"} if informational_match else {}
            decision = RouteDecision(
                agent_name="developer",
                confidence=confidence,
                matched_intent=intent,
                routing_method=method,
                reasoning=f"Matched developer keywords: {developer_matches}",
                metadata=meta,
            )
            logger.debug(
                "Internal developer rule matched",
                extra={
                    "event": "routing.rule.internal.matched",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                },
            )
            return decision

        # 6. Check General Informational query without domain keywords
        if informational_match:
            decision = RouteDecision(
                agent_name="aiops",
                confidence=0.88,
                matched_intent="informational",
                routing_method="rule_informational",
                reasoning=f"Matched internal informational query prefix: '{informational_match[0]}' (Category: {informational_match[1]})",
                metadata={"is_informational": True, "category": informational_match[1], "matched_prefix": informational_match[0]},
            )
            logger.debug(
                f"Internal informational rule matched: category='{informational_match[1]}'",
                extra={
                    "event": "routing.rule.internal.informational",
                    "agent_name": decision.agent_name,
                    "confidence": decision.confidence,
                    "routing_method": decision.routing_method,
                    "matched_intent": decision.matched_intent,
                    "category": informational_match[1],
                },
            )
            return decision

        # Default fallback for internal channels
        decision = RouteDecision(
            agent_name="aiops",
            confidence=0.40,
            matched_intent="general_fallback",
            routing_method="fallback",
            reasoning="No specific keyword matched; fallback to default AIOps agent",
        )
        logger.debug(
            "Internal channel fallback evaluated",
            extra={
                "event": "routing.rule.internal.fallback",
                "agent_name": decision.agent_name,
                "confidence": decision.confidence,
                "routing_method": decision.routing_method,
                "matched_intent": decision.matched_intent,
            },
        )
        return decision
