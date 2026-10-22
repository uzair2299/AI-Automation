"""Unit tests for Intent Routing & Classification Layer."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from smiota.agents.base import AgentContext
from smiota.agents.routing import (
    CompositeIntentRouter,
    RouteDecision,
    RuleBasedRouter,
    SemanticRouter,
    get_intent_router,
)
from smiota.agents.orchestrator import AgentOrchestrator


@pytest.fixture
def base_context():
    return AgentContext(
        session_id="test-routing-session",
        user_id="user-123",
        tenant_id="tenant-abc",
        channel="webchat",
    )


@pytest.mark.asyncio
async def test_rule_router_exact_locker_identifiers(base_context):
    router = RuleBasedRouter()

    decision = await router.classify("My tracking code is pkg-998811", base_context)
    assert decision.agent_name == "customer"
    assert decision.confidence >= 0.95
    assert decision.routing_method == "rule_pattern"

    decision2 = await router.classify("Where is my sm-4421 locker compartment 12", base_context)
    assert decision2.agent_name == "customer"
    assert decision2.confidence >= 0.95


@pytest.mark.asyncio
async def test_rule_router_channel_routing(base_context):
    router = RuleBasedRouter()

    # Webchat channel recognizes informational query prefix or falls back to customer
    decision_web = await router.classify("What are the building hours?", base_context)
    assert decision_web.agent_name == "customer"
    assert decision_web.routing_method in {"channel_default", "rule_informational"}

    # General question without keyword or prefix triggers channel default
    decision_default = await router.classify("General unclassified query", base_context)
    assert decision_default.agent_name == "customer"
    assert decision_default.routing_method == "channel_default"

    # Internal channels
    internal_ctx = AgentContext(
        session_id="internal-session",
        user_id="eng-1",
        tenant_id="smiota",
        channel="slack",
    )

    decision_aiops = await router.classify("GKE pods are crash looping with OOMKilled", internal_ctx)
    assert decision_aiops.agent_name == "aiops"
    assert decision_aiops.confidence >= 0.90

    decision_sec = await router.classify("CVE vulnerability detected in Wazuh SIEM", internal_ctx)
    assert decision_sec.agent_name == "security"

    decision_qa = await router.classify("Playwright flaky test on checkout", internal_ctx)
    assert decision_qa.agent_name == "qa"

    decision_dev = await router.classify("Review the PR terraform plan diff", internal_ctx)
    assert decision_dev.agent_name == "developer"


@pytest.mark.asyncio
async def test_rule_router_conversation_continuity():
    router = RuleBasedRouter()
    context_with_history = AgentContext(
        session_id="chat-session",
        user_id="user-1",
        tenant_id="tenant-1",
        channel="webchat",
        conversation_history=[
            {"role": "user", "content": "Where is my locker?"},
            {"role": "assistant", "content": "Locker #4 is ready with PIN 1234."},
        ],
    )

    decision = await router.classify("open it again please", context_with_history)
    assert decision.agent_name == "customer"
    assert decision.routing_method == "context_continuity"
    assert decision.confidence >= 0.85


@pytest.mark.asyncio
async def test_composite_router_fast_path(base_context):
    mock_semantic = MagicMock(spec=SemanticRouter)
    mock_semantic.classify = AsyncMock()

    rule_router = RuleBasedRouter()
    composite = CompositeIntentRouter(
        rule_router=rule_router,
        semantic_router=mock_semantic,
        confidence_threshold=0.75,
    )

    # High-confidence query should NOT invoke semantic router
    decision = await composite.classify("I need to pick up my parcel from locker", base_context)
    assert decision.agent_name == "customer"
    assert decision.confidence >= 0.75
    mock_semantic.classify.assert_not_called()


@pytest.mark.asyncio
async def test_composite_router_semantic_fallback():
    mock_rule = MagicMock(spec=RuleBasedRouter)
    mock_rule.classify = AsyncMock(
        return_value=RouteDecision(
            agent_name="aiops",
            confidence=0.40,
            matched_intent="general_fallback",
            routing_method="fallback",
        )
    )

    mock_semantic = MagicMock(spec=SemanticRouter)
    mock_semantic.classify = AsyncMock(
        return_value=RouteDecision(
            agent_name="customer",
            confidence=0.92,
            matched_intent="locker_hardware_issue",
            routing_method="gemini_semantic",
            reasoning="User describes physical drawer jam",
        )
    )

    composite = CompositeIntentRouter(
        rule_router=mock_rule,
        semantic_router=mock_semantic,
        confidence_threshold=0.75,
    )

    ctx = AgentContext(
        session_id="test",
        user_id="u1",
        tenant_id="t1",
        channel="webchat",
    )

    decision = await composite.classify("The metallic compartment is stuck", ctx)
    assert decision.agent_name == "customer"
    assert decision.confidence == 0.92
    assert decision.routing_method == "gemini_semantic"
    mock_semantic.classify.assert_called_once()


@pytest.mark.asyncio
async def test_orchestrator_routing_metadata_attachment(base_context):
    orchestrator = AgentOrchestrator()
    result = await orchestrator.route_and_execute("Where is my package in locker 5B?", base_context)

    assert result.agent_name.lower() == "customer"
    assert "routing" in result.metadata
    routing_info = result.metadata["routing"]
    assert routing_info["confidence"] >= 0.80
    assert routing_info["routing_method"] in {"rule_pattern", "channel_default", "gemini_semantic"}


@pytest.mark.asyncio
async def test_rule_router_greetings_classification(base_context):
    from smiota.agents.routing.rules import GREETINGS

    router = RuleBasedRouter()

    # Test all greetings in webchat channel
    for greeting in GREETINGS:
        decision = await router.classify(greeting, base_context)
        assert decision.agent_name == "customer", f"Failed for greeting: {greeting}"
        assert decision.matched_intent == "greeting"
        assert decision.confidence >= 0.95
        assert decision.routing_method == "rule_greeting"

    # Test greetings with punctuation and common follow-ups
    for phrase in ["Hello!", "hey there", "good morning, ", "Greetings."]:
        decision = await router.classify(phrase, base_context)
        assert decision.agent_name == "customer"
        assert decision.matched_intent == "greeting"
        assert decision.confidence >= 0.95


@pytest.mark.asyncio
async def test_rule_router_greetings_internal_channel():
    from smiota.agents.routing.rules import GREETINGS

    router = RuleBasedRouter()
    internal_ctx = AgentContext(
        session_id="internal-session",
        user_id="eng-1",
        tenant_id="smiota",
        channel="slack",
    )

    for greeting in ["hi", "hello", "good morning"]:
        decision = await router.classify(greeting, internal_ctx)
        assert decision.agent_name == "aiops"
        assert decision.matched_intent == "greeting"
        assert decision.confidence >= 0.95


@pytest.mark.asyncio
async def test_composite_router_greetings_fast_path(base_context):
    mock_semantic = MagicMock(spec=SemanticRouter)
    mock_semantic.classify = AsyncMock()

    rule_router = RuleBasedRouter()
    composite = CompositeIntentRouter(
        rule_router=rule_router,
        semantic_router=mock_semantic,
        confidence_threshold=0.75,
    )

    decision = await composite.classify("hello", base_context)
    assert decision.agent_name == "customer"
    assert decision.matched_intent == "greeting"
    assert decision.confidence >= 0.95
    # Must NOT call semantic router (zero LLM cost, zero latency)
    mock_semantic.classify.assert_not_called()


@pytest.mark.asyncio
async def test_rule_router_informational_prefixes_webchat(base_context):
    from smiota.agents.routing.rules import INFORMATIONAL_CATEGORIES

    router = RuleBasedRouter()

    # Representative test queries across all 8 informational categories
    category_samples = {
        "how_to": "how to retrieve my delivery pickup code",
        "definitions": "what is a compartment PIN",
        "explanations": "why can't I access my locker",
        "instructions": "guide me through the pickup process",
        "general_knowledge": "can you explain how smart lockers work",
        "process_policy": "what is the policy for locker storage",
        "capabilities": "does smiota support refrigerated lockers",
        "troubleshooting": "why is my locker door not opening",
    }

    for expected_cat, sample_query in category_samples.items():
        decision = await router.classify(sample_query, base_context)
        assert decision.agent_name == "customer", f"Failed for query: {sample_query}"
        assert decision.matched_intent == "informational"
        assert decision.routing_method == "rule_informational"
        assert decision.confidence >= 0.90
        assert decision.metadata.get("is_informational") is True
        assert decision.metadata.get("category") == expected_cat


@pytest.mark.asyncio
async def test_rule_router_informational_internal_channel():
    router = RuleBasedRouter()
    internal_ctx = AgentContext(
        session_id="internal-session",
        user_id="eng-1",
        tenant_id="smiota",
        channel="slack",
    )

    decision = await router.classify("what is the process for incident escalation", internal_ctx)
    assert decision.agent_name == "aiops"
    assert decision.matched_intent == "informational"
    assert decision.routing_method == "rule_informational"
    assert decision.metadata.get("is_informational") is True


@pytest.mark.asyncio
async def test_composite_router_informational_fast_path(base_context):
    mock_semantic = MagicMock(spec=SemanticRouter)
    mock_semantic.classify = AsyncMock()

    rule_router = RuleBasedRouter()
    composite = CompositeIntentRouter(
        rule_router=rule_router,
        semantic_router=mock_semantic,
        confidence_threshold=0.75,
    )

    decision = await composite.classify("how can I pick up my parcel", base_context)
    assert decision.agent_name == "customer"
    assert decision.matched_intent == "informational"
    assert decision.confidence >= 0.75
    # Must NOT call semantic router (fast path < 1ms)
    mock_semantic.classify.assert_not_called()


@pytest.mark.asyncio
async def test_customer_agent_handles_informational_query(base_context):
    from unittest.mock import patch
    from smiota.agents.implementations.customer.agent import CustomerAgent

    agent = CustomerAgent()
    with patch("smiota.llm.provider.GeminiProvider.generate_completion", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "To pick up your package, scan the QR code at the locker kiosk."
        result = await agent.process("how do I pick up my package", base_context)
        assert result.metadata.get("is_informational") is True
        assert result.metadata.get("category") == "how_to"
        assert result.metadata.get("matched_prefix") == "how do i"
        assert "QR code" in result.content
        mock_llm.assert_called_once()
        prompt_arg = mock_llm.call_args[1]["prompt"]
        assert "[Informational Query - Category: how_to, Pattern: 'how do i']" in prompt_arg


