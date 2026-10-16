"""CLI tool to execute agent evaluations against the golden evaluation benchmark."""
import asyncio
import json
import os
import sys

from smiota.agents import register_default_agents
from smiota.agents.orchestrator import AgentOrchestrator
from smiota.agents.base import AgentContext


async def run_benchmark():
    register_default_agents()
    dataset_path = os.path.join(
        os.path.dirname(__file__), "..", "tests", "evals", "datasets", "golden_evals.json"
    )

    if not os.path.exists(dataset_path):
        print(f"Error: dataset not found at {dataset_path}")
        sys.exit(1)

    with open(dataset_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    orchestrator = AgentOrchestrator()
    context = AgentContext(
        session_id="benchmark-session",
        user_id="bench-user",
        tenant_id="benchmark",
        channel="cli",
    )

    print(f"\n=======================================================")
    print(f"  Smiota AI Agent Platform - Reasoning Evaluation")
    print(f"=======================================================\n")

    correct_domain = 0
    correct_safety = 0

    for idx, c in enumerate(cases, 1):
        res = await orchestrator.route_and_execute(c["query"], context)
        domain_ok = res.agent_name.lower() == c["expected_domain"]
        safety_ok = res.requires_approval == c["expected_approval"]

        if domain_ok:
            correct_domain += 1
        if safety_ok:
            correct_safety += 1

        status_flag = "PASS" if (domain_ok and safety_ok) else "FAIL"
        print(f"[{status_flag}] Case #{idx:02d}: {c['query'][:55]}...")
        print(f"       Domain: {res.agent_name.lower()} (Expected: {c['expected_domain']}) | Match: {domain_ok}")
        print(f"       Safety: RequiresApproval={res.requires_approval} (Expected: {c['expected_approval']}) | Match: {safety_ok}\n")

    total = len(cases)
    d_score = (correct_domain / total) * 100
    s_score = (correct_safety / total) * 100

    print("=======================================================")
    print(f"  FINAL SCORECARD:")
    print(f"  Intent Routing Accuracy: {d_score:.1f}% ({correct_domain}/{total})")
    print(f"  Safety Gate Accuracy:    {s_score:.1f}% ({correct_safety}/{total})")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
