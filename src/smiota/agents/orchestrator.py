"""Agent Orchestration & Reasoning Layer: Task planning, intent classification, and multi-agent coordination."""
from typing import Optional
from smiota.agents.base import AgentContext, AgentResult
from smiota.agents.memory import ConversationMemory
from smiota.agents.registry import AgentRegistry
from smiota.core.logging import logger
from smiota.repositories.chat_repository import get_chat_repository
from smiota.schemas.chat_session import MessageType


class AgentOrchestrator:
    """Orchestrates incoming requests across specialized agents using intent classification."""

    def __init__(self):
        pass

    async def route_and_execute(
        self,
        query: str,
        context: AgentContext,
        preferred_agent: Optional[str] = None,
    ) -> AgentResult:
        """Determines the most appropriate agent or executes the requested agent directly."""
        selected_agent_name = preferred_agent or self._classify_intent(query, context.channel)
        logger.info(f"Routing query to agent: [{selected_agent_name}] (Session: {context.session_id})")

        # 1. Ensure session is tracked in the repository
        repo = get_chat_repository()
        await repo.get_or_create_session(
            session_id=context.session_id,
            user_id=context.user_id,
            tenant_id=context.tenant_id,
            channel=context.channel,
            metadata=context.metadata,
        )

        # 2. Record incoming user turn in chat repository
        user_display_name = (
            context.metadata.get("user_name")
            or context.metadata.get("recipient_name")
            or None
        )
        await repo.append_message(
            session_id=context.session_id,
            role="user",
            content=query,
            sender_name=user_display_name,
            message_type="text",
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
        await repo.append_message(
            session_id=context.session_id,
            role="assistant",
            content=result.content,
            agent_name=result.agent_name,
            sender_name=f"{result.agent_name} Assistant",
            message_type=msg_type,
            card_payload=card_data,
            suggested_actions=result.suggested_actions,
            metadata=result.metadata,
        )

        # Record assistant response in legacy conversation memory
        try:
            await memory.add_message(role="assistant", content=result.content)
        except Exception:
            pass

        return result

    def _classify_intent(self, query: str, channel: Optional[str] = None) -> str:
        """Classifies intent using keywords or Gemini function calling router.

        In production, this queries Gemini / Vertex AI with tool/agent definitions.
        """
        q = query.lower()
        # For customer webchat channel, prioritize Customer & Smart Locker intents
        if channel == "webchat":
            if any(w in q for w in ["security", "cve", "vulnerability", "iam"]):
                return "security"
            if any(w in q for w in ["cpu", "memory", "oom", "restart", "metric", "prometheus", "opensearch", "grafana", "gke", "pod", "incident", "rca", "crash"]):
                return "aiops"
            return "customer"

        # 1. Security & Compliance
        if any(w in q for w in ["security", "cve", "vulnerability", "iam", "wazuh", "threat", "siem", "service account", "revoke", "quarantine", "credential"]):
            return "security"
        # 2. QA & Automated Testing
        if any(w in q for w in ["playwright", "selenium", "flaky", "regression", "test"]):
            return "qa"
        # 3. Customer & Smart Locker
        if any(w in q for w in ["locker", "customer", "ticket", "package", "door", "pickup", "dropoff", "parcel", "compartment", "track", "tracking", "sm-", "pkg-"]):
            return "customer"
        # 4. SRE & AIOps (Incident, restart, metrics, OOM, logs)
        if any(w in q for w in ["cpu", "memory", "oom", "restart", "metric", "prometheus", "opensearch", "grafana", "gke", "pod", "incident", "rca", "crash"]):
            return "aiops"
        # 5. Developer & DevOps (PRs, code, terraform, pipelines)
        if any(w in q for w in ["pr", "pull request", "terraform", "code", "github", "promql", "ci/cd", "pipeline", "diff"]):
            return "developer"
        return "aiops"

