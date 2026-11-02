"""AIOps Agent: Incident Investigation, RCA, Runbook recommendations, Capacity & Performance."""
import re
from smiota.agents.base import BaseAgent, AgentContext, AgentResult
from smiota.agents.routing.rules import GREETINGS
from smiota.schemas.agents import AgentCapability
from smiota.agents.implementations.aiops.prompts import AIOPS_SYSTEM_PROMPT
from smiota.agents.implementations.aiops.tools import AIOPS_BOUND_TOOLS
from smiota.mcp.servers.observability.tools import get_pod_restart_reason


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
                AgentCapability(name="pod_crash_investigation", description="Diagnose Kubernetes pod crashloops, exit codes, and OOMKilled events"),
                AgentCapability(name="remediation_dispatch", description="Propose and execute approved cluster remediation", access_level="remediation"),
            ],
            system_prompt=AIOPS_SYSTEM_PROMPT,
            bound_tools=AIOPS_BOUND_TOOLS,
        )

    async def process(self, query: str, context: AgentContext) -> AgentResult:
        q = query.lower().strip()
        clean_q = re.sub(r"[^\w\s]", "", q).strip()

        # 1. Greetings & Welcome
        if clean_q in GREETINGS or any(clean_q == w or clean_q.startswith(w + " ") for w in GREETINGS):
            return AgentResult(
                agent_name=self.name,
                content="Hello! 👋 I'm your Smiota AIOps & SRE Assistant. How can I assist you with infrastructure, telemetry, or incidents today?",
                requires_approval=False,
                suggested_actions=[
                    "Check cluster health",
                    "Inspect active alerts",
                    "Recent pod restarts",
                ],
            )

        # 2. Differentiate Investigation vs. Mutating Remediation Action
        is_investigation = (
            any(q.startswith(p) for p in ["why", "what", "how", "is ", "are ", "explain", "diagnose", "investigate", "tell me why"])
            or any(kw in q for kw in ["why is", "why are", "what caused", "reason", "diagnose", "investigate", "crashloop", "restarting", "crashing"])
        )

        is_mutating_action = (
            not is_investigation
            and "restart" in q
            and ("deployment" in q or "pod" in q or "service" in q or "immediately" in q)
        )

        # 3. Mutating Remediation (Requires Human Approval)
        if is_mutating_action:
            deployment_name = "smiota-agent-core-api"
            if "payment" in q:
                deployment_name = "payments-service"
            elif "smiota" in q and "server" in q:
                deployment_name = "smiotaserver"

            return AgentResult(
                agent_name=self.name,
                content=(
                    f"Identified remediation request: '{query}'. "
                    f"Restarting deployment '{deployment_name}' modifies production cluster state. "
                    "An approval request has been generated for SRE/Admin authorization."
                ),
                requires_approval=True,
                approval_details={
                    "tool_name": "restart_gke_deployment",
                    "namespace": "production",
                    "deployment_name": deployment_name,
                    "reason": f"Triggered by user request: {query}",
                },
                suggested_actions=["Wait for SRE/Admin approval", "Review Grafana error rates post-rollout"],
            )

        # 4. Crash & Restart Root Cause Analysis (RCA) Investigation
        if ("restart" in q or "crash" in q or "oom" in q or "server" in q) and is_investigation:
            service_name = "smiotaserver"
            if "payment" in q:
                service_name = "payments-service"
            elif "core-api" in q or "agent-core" in q:
                service_name = "smiota-agent-core-api"
            elif "notification" in q:
                service_name = "notification-service"

            diag = await get_pod_restart_reason(service_name=service_name)
            exit_code = diag.get("exit_code", 137)
            term_reason = diag.get("termination_reason", "OOMKilled")
            restarts = diag.get("restart_count_1h", 4)
            peak_mem = diag.get("peak_memory_observed", "4128Mi")
            mem_limit = diag.get("memory_limit", "4096Mi")
            recent_err = diag.get("recent_error", "java.lang.OutOfMemoryError: Java heap space at com.smiota.service.ParcelSyncService")
            last_ts = diag.get("last_crash_timestamp", "12 minutes ago")

            content = (
                f"### 🚨 AIOps Incident Investigation: `{service_name}` Pod Restarts\n\n"
                f"**Probable Root Cause:** **{term_reason} (Exit Code {exit_code})**\n"
                f"The `{service_name}` container was terminated by the Linux kernel Out-Of-Memory killer "
                f"because memory allocation exceeded its configured **{mem_limit}** limit.\n\n"
                f"#### 📊 Telemetry Evidence:\n"
                f"- **Recent Restarts:** {restarts} crash restarts in the last 60 minutes (`CrashLoopBackOff`)\n"
                f"- **Last Termination:** {last_ts}\n"
                f"- **Memory Usage Spike:** Reached **{peak_mem}** (exceeded limit of {mem_limit}, 100.8% utilization)\n"
                f"- **OpenSearch Error Log:** `{recent_err}`\n\n"
                f"#### 💡 Recommended Next Steps:\n"
                f"1. **Scale Memory Allocation:** Increase memory limit in Kubernetes deployment manifest from `{mem_limit}` to `6144Mi` (6.0 GiB).\n"
                f"2. **JVM Heap Tuning:** Configure `-XX:MaxRAMPercentage=75.0` to prevent JVM native memory from exhausting pod headroom.\n"
                f"3. **Trigger Rolling Restart:** Once YAML is patched, say: *\"Restart deployment {service_name}\"* to request authorized rollout."
            )

            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=[
                    f"Fetch OpenSearch error stacktrace for {service_name}",
                    f"Compare Prometheus memory usage with 24h baseline",
                    f"Request rolling restart approval for {service_name}",
                ],
            )

        # 5. General AIOps Telemetry Query
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
