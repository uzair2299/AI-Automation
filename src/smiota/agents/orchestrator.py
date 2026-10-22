"""Agent Orchestration & Reasoning Layer: Task planning, intent classification, and multi-agent coordination."""
from typing import Optional
from smiota.agents.base import AgentContext, AgentResult
from smiota.agents.memory import ConversationMemory
from smiota.agents.registry import AgentRegistry
from smiota.agents.routing import BaseIntentRouter, get_intent_router
from smiota.core.logging import logger
from smiota.repositories.chat_repository import get_chat_repository
from smiota.schemas.chat_session import MessageType


class AgentOrchestrator:
    """Orchestrates incoming requests across specialized agents using intent classification."""

    def __init__(self, router: Optional[BaseIntentRouter] = None):
        self.router = router or get_intent_router()

    async def route_and_execute(
        self,
        query: str,
        context: AgentContext,
        preferred_agent: Optional[str] = None,
    ) -> AgentResult:
        """Determines the most appropriate agent or executes the requested agent directly."""
        if preferred_agent:
            selected_agent_name = preferred_agent
            routing_metadata = {
                "routing_method": "preferred_override",
                "confidence": 1.0,
                "matched_intent": "manual_override",
            }
        else:
            decision = await self.router.classify(query, context)
            selected_agent_name = decision.agent_name
            routing_metadata = {
                "routing_method": decision.routing_method,
                "confidence": decision.confidence,
                "matched_intent": decision.matched_intent,
                "reasoning": decision.reasoning,
            }

        logger.info(
            f"Routing query to agent: [{selected_agent_name}] "
            f"(Confidence: {routing_metadata.get('confidence', 1.0):.2f}, "
            f"Method: {routing_metadata.get('routing_method')}, Session: {context.session_id})"
        )

        # 1. Ensure session is tracked in the repository
        user_info = context.user or (context.metadata.get("user") if isinstance(context.metadata, dict) else None) or {}
        parent_token = getattr(context, "parent_token", None) or user_info.get("parent_token") or context.metadata.get("parent_token")
        session_metadata = dict(context.metadata)
        if user_info:
            session_metadata.setdefault("user", user_info)
        if parent_token:
            session_metadata.setdefault("parent_token", parent_token)

        repo = get_chat_repository()
        await repo.get_or_create_session(
            session_id=context.session_id,
            user_id=context.user_id,
            tenant_id=context.tenant_id,
            channel=context.channel,
            metadata=session_metadata,
        )

        # 2. Record incoming user turn in chat repository
        user_display_name = (
            context.metadata.get("user_name")
            or context.metadata.get("recipient_name")
            or (user_info.get("name") if isinstance(user_info, dict) else None)
            or None
        )
        user_turn_metadata = dict(context.metadata)
        if user_info:
            user_turn_metadata.setdefault("user", user_info)
        if parent_token:
            user_turn_metadata.setdefault("parent_token", parent_token)

        await repo.append_message(
            session_id=context.session_id,
            role="user",
            content=query,
            sender_name=user_display_name,
            message_type="text",
            metadata=user_turn_metadata,
        )

        # 3. Populate context.conversation_history with recent turns
        recent_turns = await repo.get_messages(context.session_id, limit=10)
        context.conversation_history = [
            {
                "role": m.role or (m.sender.role if hasattr(m, "sender") else "user"),
                "content": m.text if hasattr(m, "text") else (m.content.get("text", "") if isinstance(m.content, dict) else str(m.content)),
            }
            for m in recent_turns
        ]

        # Maintain legacy ConversationMemory for backward compatibility
        try:
            memory = ConversationMemory(session_id=context.session_id)
            await memory.add_message(role="user", content=query)
        except Exception:
            pass

        # 4. Route to specialized agent
        default_fallback = "customer" if context.channel == "webchat" else "aiops"
        try:
            agent = AgentRegistry.get(selected_agent_name)
        except KeyError:
            logger.warning(f"Requested agent '{selected_agent_name}' not found. Falling back to '{default_fallback}'.")
            agent = AgentRegistry.get(default_fallback)

        result = await agent.process(query, context)

        # 5. Classify message type (text vs. card vs. approval gate)
        msg_type: MessageType = "text"
        card_data: Optional[dict] = None

        if result.requires_approval:
            msg_type = "approval_gate"
            card_data = {
                "action": "security_approval_required",
                "approval_details": result.approval_details,
                "approval_id": result.approval_id,
            }
        elif result.metadata.get("card_payload"):
            msg_type = "card"
            card_data = result.metadata["card_payload"]

        # 6. Record assistant response in chat repository
        assistant_metadata = dict(result.metadata)
        if user_info:
            assistant_metadata.setdefault("user", user_info)
            result.metadata.setdefault("user", user_info)

        await repo.append_message(
            session_id=context.session_id,
            role="assistant",
            content=result.content,
            agent_name=result.agent_name,
            sender_name=f"{result.agent_name} Assistant",
            message_type=msg_type,
            card_payload=card_data,
            suggested_actions=result.suggested_actions,
            metadata=assistant_metadata,
        )

        # Record assistant response in legacy conversation memory
        try:
            await memory.add_message(role="assistant", content=result.content)
        except Exception:
            pass

        # Attach routing metadata to result
        result.metadata.setdefault("routing", routing_metadata)

        return result

    def _classify_intent(self, query: str, channel: Optional[str] = None) -> str:
        """Synchronous intent classification helper preserving backward compatibility."""
        from smiota.agents.routing.rules import RuleBasedRouter

        rule_router = RuleBasedRouter()
        ch = (channel or "webchat").lower()
        if ch == "webchat":
            return rule_router._classify_webchat(query.lower()).agent_name
        return rule_router._classify_internal(query.lower()).agent_name


