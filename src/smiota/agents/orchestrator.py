"""Agent Orchestration & Reasoning Layer: Task planning, intent classification, and multi-agent coordination."""
from typing import Optional
from smiota.agents.base import AgentContext, AgentResult
from smiota.agents.registry import AgentRegistry
from smiota.agents.memory import ConversationMemory
from smiota.core.logging import logger


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
        selected_agent_name = preferred_agent or self._classify_intent(query)
        logger.info(f"Routing query to agent: [{selected_agent_name}] (Session: {context.session_id})")

        # Record incoming user turn in conversation memory
        memory = ConversationMemory(session_id=context.session_id)
        await memory.add_message(role="user", content=query)

        try:
            agent = AgentRegistry.get(selected_agent_name)
        except KeyError:
            logger.warning(f"Requested agent '{selected_agent_name}' not found. Falling back to 'AIOps'.")
            agent = AgentRegistry.get("aiops")

        result = await agent.process(query, context)

        # Record assistant response in conversation memory
        await memory.add_message(role="assistant", content=result.content)

        return result

    def _classify_intent(self, query: str) -> str:
        """Classifies intent using keywords or Gemini function calling router.

        In production, this queries Gemini / Vertex AI with tool/agent definitions.
        """
        q = query.lower()
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
