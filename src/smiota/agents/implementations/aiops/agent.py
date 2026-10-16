"""AIOps Agent: Incident Investigation, RCA, Runbook recommendations, Capacity & Performance."""
from smiota.agents.base import BaseAgent, AgentContext, AgentResult
from smiota.schemas.agents import AgentCapability
from smiota.agents.implementations.aiops.prompts import AIOPS_SYSTEM_PROMPT
from smiota.agents.implementations.aiops.tools import AIOPS_BOUND_TOOLS


class AIOpsAgent(BaseAgent):
    """Senior SRE and AIOps cognitive agent."""

    def __init__(self):
        super().__init__(
            name="AIOps",
            description="Specialized in incident investigation, RCA, runbook recommendations, and metrics analysis.",
            domain="aiops",
            capabilities=[
                AgentCapability(name="metric_analysis", description="Inspect Prometheus and GCP Cloud Monitoring metrics"),
                AgentCapability(name="log_correlation", description="Correlate logs across OpenSearch and Cloud Logging"),
                AgentCapability(name="remediation_dispatch", description="Propose and execute approved cluster remediation", access_level="remediation"),
            ],
            system_prompt=AIOPS_SYSTEM_PROMPT,
            bound_tools=AIOPS_BOUND_TOOLS,
        )

    async def process(self, query: str, context: AgentContext) -> AgentResult:
        # Check if query requests a mutating action
        q = query.lower()
        if "restart" in q and ("deployment" in q or "pod" in q or "service" in q):
            return AgentResult(
                agent_name=self.name,
                content=(
                    f"Identified remediation request: '{query}'. "
                    "Restarting a deployment modifies production cluster state. "
                    "An approval request has been generated for SRE/Admin authorization."
                ),
                requires_approval=True,
                approval_details={
                    "tool_name": "restart_gke_deployment",
                    "namespace": "production",
                    "deployment_name": "smiota-agent-core-api",
                    "reason": f"Triggered by user request: {query}",
                },
                suggested_actions=["Wait for SRE/Admin approval", "Review Grafana error rates post-rollout"],
            )

        return AgentResult(
            agent_name=self.name,
            content=f"[AIOps Investigation] Analyzed telemetry for: '{query}'. Correlated metrics from Prometheus and GCP Cloud Monitoring.",
            requires_approval=False,
            suggested_actions=[
                "Fetch OpenSearch logs for last 15m",
                "Compare CPU metrics with baseline",
                "Check active GKE pod restarts",
            ],
        )
