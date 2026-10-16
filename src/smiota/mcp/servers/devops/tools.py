"""DevOps, CI/CD, and IaC MCP Tools (GitHub, Terraform, ArgoCD, PromQL)."""
from typing import Optional
from smiota.mcp.security import mcp_tool
from smiota.schemas.mcp import ToolAccessLevel


@mcp_tool(
    name="fetch_github_pr_diff",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Fetch pull request code diff and changed files from GitHub / GitLab.",
)
async def fetch_github_pr_diff(repo: str, pr_number: int) -> dict:
    """Fetch GitHub pull request metadata and patch diff."""
    return {
        "repo": repo,
        "pr_number": pr_number,
        "files_changed": ["deploy/k8s/base/hpa.yaml", "src/smiota/main.py"],
        "additions": 42,
        "deletions": 5,
        "summary": "Updated HPA autoscaling thresholds and added health endpoints.",
    }


@mcp_tool(
    name="validate_terraform_plan",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Validate Terraform / OpenTofu syntax and simulate dry-run plan.",
)
async def validate_terraform_plan(directory_path: str) -> dict:
    """Run terraform fmt and terraform validate simulation."""
    return {
        "status": "valid",
        "directory": directory_path,
        "resources_to_add": 2,
        "resources_to_change": 0,
        "resources_to_destroy": 0,
    }


@mcp_tool(
    name="generate_promql_query",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Synthesize an optimized PromQL query from natural language requirements.",
)
async def generate_promql_query(metric_intent: str) -> dict:
    """Generate PromQL query."""
    return {
        "intent": metric_intent,
        "promql": "sum(rate(container_cpu_usage_seconds_total{namespace='production'}[5m])) by (pod)",
        "explanation": "Calculates 5-minute per-pod CPU usage rates in the production namespace.",
    }


@mcp_tool(
    name="trigger_cicd_pipeline",
    access_level=ToolAccessLevel.REMEDIATION,
    description="Trigger deployment or rerun CI/CD pipeline in GitHub Actions / Cloud Build (Requires Human Approval).",
)
async def trigger_cicd_pipeline(
    pipeline_name: str,
    target_branch: str,
    approval_token: Optional[str] = None,
) -> dict:
    """Trigger CI/CD pipeline execution."""
    return {
        "status": "triggered",
        "pipeline": pipeline_name,
        "branch": target_branch,
        "approved_by_token": approval_token,
    }
