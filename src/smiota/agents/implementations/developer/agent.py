"""Developer Agent: Code Review, PR Analysis, CI/CD Analysis, IaC / Terraform, Query Generation."""
from smiota.agents.base import BaseAgent, AgentContext, AgentResult
from smiota.schemas.agents import AgentCapability
from smiota.agents.implementations.developer.prompts import DEVELOPER_SYSTEM_PROMPT
from smiota.agents.implementations.developer.tools import DEVELOPER_BOUND_TOOLS


class DeveloperAgent(BaseAgent):
    """Staff Engineer AI assistant for developers and DevOps engineers."""

    def __init__(self):
        super().__init__(
            name="Developer",
            description="Specialized in PR reviews, CI/CD pipeline analysis, Terraform/IaC validation, and query generation.",
            domain="developer",
            capabilities=[
                AgentCapability(name="pr_review", description="Analyze pull requests, git diffs, and linting"),
                AgentCapability(name="iac_validation", description="Validate Terraform / OpenTofu configurations"),
                AgentCapability(name="query_generation", description="Generate PromQL, LogQL, and OpenSearch DSL"),
                AgentCapability(name="pipeline_trigger", description="Trigger or retry CI/CD build pipelines", access_level="remediation"),
            ],
            system_prompt=DEVELOPER_SYSTEM_PROMPT,
            bound_tools=DEVELOPER_BOUND_TOOLS,
        )

    async def process(self, query: str, context: AgentContext) -> AgentResult:
        q = query.lower()
        if "trigger" in q and ("pipeline" in q or "deploy" in q or "build" in q):
            return AgentResult(
                agent_name=self.name,
                content=(
                    f"Identified deployment pipeline trigger: '{query}'. "
                    "Deploying code updates modifies environment state. "
                    "An approval request has been queued for Tech Lead authorization."
                ),
                requires_approval=True,
                approval_details={
                    "tool_name": "trigger_cicd_pipeline",
                    "reason": f"Deployment trigger requested by: {query}",
                },
                suggested_actions=["Wait for Tech Lead approval", "Inspect unit test coverage report"],
            )

        return AgentResult(
            agent_name=self.name,
            content=f"[Developer Assistant] Inspected code diff and CI/CD pipelines for: '{query}'.",
            requires_approval=False,
            suggested_actions=[
                "Review GitHub PR diff",
                "Validate Terraform syntax",
                "Generate PromQL alert rule",
            ],
        )
