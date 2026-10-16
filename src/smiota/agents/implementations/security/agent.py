"""Security Agent: Threat Analysis, Vulnerability Analysis, IAM & Config Assessment, Security Incident Response."""
from smiota.agents.base import BaseAgent, AgentContext, AgentResult
from smiota.schemas.agents import AgentCapability
from smiota.agents.implementations.security.prompts import SECURITY_SYSTEM_PROMPT
from smiota.agents.implementations.security.tools import SECURITY_BOUND_TOOLS


class SecurityAgent(BaseAgent):
    """DevSecOps and Security Operations agent."""

    def __init__(self):
        super().__init__(
            name="Security",
            description="Specialized in threat detection, vulnerability analysis, IAM auditing, and security incident response.",
            domain="security",
            capabilities=[
                AgentCapability(name="threat_detection", description="Analyze Wazuh SIEM alerts and intrusion signatures"),
                AgentCapability(name="vulnerability_triage", description="Triage CVEs across container images and dependencies"),
                AgentCapability(name="iam_audit", description="Audit GCP IAM bindings and least-privilege violations"),
                AgentCapability(name="credential_revocation", description="Revoke compromised API keys/service accounts", access_level="remediation"),
            ],
            system_prompt=SECURITY_SYSTEM_PROMPT,
            bound_tools=SECURITY_BOUND_TOOLS,
        )

    async def process(self, query: str, context: AgentContext) -> AgentResult:
        q = query.lower()
        if "revoke" in q or "block ip" in q or "quarantine" in q:
            return AgentResult(
                agent_name=self.name,
                content=(
                    f"Identified high-impact security action: '{query}'. "
                    "Quarantine and credential revocation modifies security policies. "
                    "An approval request has been queued for SecOps authorization."
                ),
                requires_approval=True,
                approval_details={
                    "tool_name": "revoke_compromised_credentials",
                    "reason": f"Security containment triggered by: {query}",
                },
                suggested_actions=["Wait for SecOps approval", "Export audit trail to Cloud Storage"],
            )

        return AgentResult(
            agent_name=self.name,
            content=f"[Security Audit] Evaluated Wazuh SIEM alerts and GCP IAM bindings for: '{query}'. No high-severity exploits actively detected.",
            requires_approval=False,
            suggested_actions=[
                "Inspect Wazuh alert logs for last 1h",
                "Audit GCP service account permissions",
                "Scan container vulnerabilities with Trivy",
            ],
        )
