"""QA Agent: Test Case Generation, Test Failure Analysis, Regression Analysis, Automated Tests."""
from smiota.agents.base import BaseAgent, AgentContext, AgentResult
from smiota.schemas.agents import AgentCapability
from smiota.agents.implementations.qa.prompts import QA_SYSTEM_PROMPT
from smiota.agents.implementations.qa.tools import QA_BOUND_TOOLS


class QAAgent(BaseAgent):
    """Staff QA & Test Automation agent."""

    def __init__(self):
        super().__init__(
            name="QA",
            description="Specialized in automated test case generation, test failure analysis, and Playwright/Selenium runs.",
            domain="qa",
            capabilities=[
                AgentCapability(name="test_generation", description="Generate Playwright and Selenium test scripts"),
                AgentCapability(name="failure_analysis", description="Analyze stack traces, flaky tests, and regression logs"),
                AgentCapability(name="synthetic_data", description="Generate realistic test mock payloads and edge cases"),
                AgentCapability(name="run_load_test", description="Execute high-scale synthetic load tests", access_level="remediation"),
            ],
            system_prompt=QA_SYSTEM_PROMPT,
            bound_tools=QA_BOUND_TOOLS,
        )

    async def process(self, query: str, context: AgentContext) -> AgentResult:
        q = query.lower()
        if "load test" in q or "stress test" in q:
            return AgentResult(
                agent_name=self.name,
                content=(
                    f"Identified load/stress test execution: '{query}'. "
                    "Stress tests generate artificial traffic spikes on target environments. "
                    "An approval request has been queued for QA Lead authorization."
                ),
                requires_approval=True,
                approval_details={
                    "tool_name": "run_load_test",
                    "reason": f"Load test triggered by: {query}",
                },
                suggested_actions=["Wait for QA Lead approval", "Notify SRE on-call before triggering load"],
            )

        return AgentResult(
            agent_name=self.name,
            content=f"[QA Automation] Analyzed test failure stack traces and generated regression scenarios for: '{query}'.",
            requires_approval=False,
            suggested_actions=[
                "Generate Playwright E2E test",
                "Analyze Selenium flakiness report",
                "Trigger regression suite",
            ],
        )
