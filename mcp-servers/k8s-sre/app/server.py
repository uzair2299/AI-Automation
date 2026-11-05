"""Official SRE Kubernetes Model Context Protocol (MCP) Server.

Exposes:
- 22 Group 1 Kubernetes Inventory Tools (Strictly Read-Only)
- 15 Group 2 Kubernetes Troubleshooting & RCA Tools (Structured DiagnosisReport)
- Fast-Scanning Format Validation & Retry Tools (Preserved)
- Resources: format://rules (Preserved)
- Prompts: formatting_system_prompt (Preserved) & k8s_sre_playbook
"""
from __future__ import annotations

import logging
import sys
from typing import Any, Dict, List, Optional

try:
    from mcp.server.mcpserver import MCPServer as FastMCP
except (ImportError, ModuleNotFoundError):
    from mcp.server.fastmcp import FastMCP

try:
    from .config import settings
except ImportError:
    from app.config import settings
from app.tools.format_validator import build_retry_instruction, validate_format

# Group 1 Inventory Tools
from app.tools.inventory_clusters import (
    get_cluster_info,
    get_namespace,
    get_node_details,
    list_clusters,
    list_namespaces,
    list_nodes,
)
from app.tools.inventory_config import (
    list_configmaps,
    list_events,
    list_secrets_metadata,
)
from app.tools.inventory_metrics import (
    get_hpa_status,
    get_pod_metrics,
    get_resource_quotas,
)
from app.tools.inventory_network import (
    list_ingresses,
    list_services,
)
from app.tools.inventory_workloads import (
    get_deployment_details,
    get_pod_details,
    get_pod_logs,
    get_pod_previous_logs,
    list_daemonsets,
    list_deployments,
    list_pods,
    list_statefulsets,
)

# Group 2 Troubleshooting & RCA Tools
from app.tools.diagnose_infrastructure import (
    check_pvc_status,
    check_resource_pressure,
    diagnose_node,
)
from app.tools.diagnose_network import (
    check_dns_resolution,
    check_network_connectivity,
    diagnose_ingress,
    diagnose_service,
)
from app.tools.diagnose_workloads import (
    analyze_container_logs,
    analyze_pod_events,
    check_pod_restarts,
    diagnose_crashloop,
    diagnose_deployment,
    diagnose_image_pull,
    diagnose_pending_pod,
    diagnose_pod,
)

from app.tools.devops import (
    fetch_github_pr_diff as fetch_github_pr_diff_impl,
    generate_promql_query as generate_promql_query_impl,
    trigger_cicd_pipeline as trigger_cicd_pipeline_impl,
    validate_terraform_plan as validate_terraform_plan_impl,
)
from app.tools.qa import (
    generate_synthetic_test_data as generate_synthetic_test_data_impl,
    parse_test_failure_logs as parse_test_failure_logs_impl,
    run_load_test as run_load_test_impl,
    run_playwright_e2e_test as run_playwright_e2e_test_impl,
)
from app.tools.security import (
    audit_gcp_iam_bindings as audit_gcp_iam_bindings_impl,
    query_wazuh_alerts as query_wazuh_alerts_impl,
    revoke_compromised_credentials as revoke_compromised_credentials_impl,
    scan_container_vulnerabilities as scan_container_vulnerabilities_impl,
)

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='{"time":"%(asctime)s","level":"%(levelname)s","server":"k8s-sre-mcp","message":"%(message)s"}',
)
logger = logging.getLogger("k8s-sre-mcp")

mcp = FastMCP("KubernetesSREServer", host=settings.MCP_HOST, port=settings.MCP_PORT)

# Tool safety annotations applied to all tools
_TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
}


# ==============================================================================
# 0. Preserved Formatting Tools & Prompts (DO NOT BREAK)
# ==============================================================================

@mcp.tool(**_TOOL_ANNOTATIONS)
def tool_validate_format(text: str) -> Dict[str, Any]:
    """Validate text against 600-char paragraph limits, code-fence stripping, and table constraints."""
    return validate_format(text)


@mcp.tool(**_TOOL_ANNOTATIONS)
def tool_build_retry_instruction(issues: List[str]) -> str:
    """Build corrective system instruction suffix when format violations occur."""
    return build_retry_instruction(issues)


@mcp.prompt("formatting_system_prompt")
def formatting_system_prompt() -> str:
    """Verbatim formatting guidelines, rules, and few-shot examples."""
    return (
        "You are an AI assistant. Follow strict response formatting rules:\n"
        "1. Never wrap responses in triple backtick code blocks.\n"
        "2. Keep every paragraph strictly under 600 characters.\n"
        "3. Provide direct, grounded technical answers."
    )


@mcp.prompt("k8s_sre_playbook")
def k8s_sre_playbook() -> str:
    """Master SRE troubleshooting playbook for Kubernetes incidents."""
    return (
        "You are a Senior Kubernetes SRE. When investigating incidents, follow this exact procedure:\n"
        "1. Start with high-level inventory: list_pods or get_pod_details to inspect phase and container statuses.\n"
        "2. If CrashLoopBackOff: call diagnose_crashloop, inspect exit codes (e.g. 137 OOMKilled), and review previous logs.\n"
        "3. If ImagePullBackOff: call diagnose_image_pull, check imagePullSecrets, registry, and tags.\n"
        "4. If Pending: call diagnose_pending_pod to check scheduler events, taints, quotas, or volume binding.\n"
        "5. If Service unreachable: call diagnose_service to verify pod selector and endpoint readiness.\n"
        "6. Always return root cause, evidence, and clear suggested next steps."
    )


@mcp.resource("format://rules")
def formatting_rules_resource() -> str:
    """Fast-scanning formatting rules and validation thresholds."""
    return (
        "Paragraph limit: 600 characters\n"
        "Prohibited: Unescaped triple-backtick markdown blocks\n"
        "Read-Only: Kubernetes SRE inspection operations only\n"
    )


# ==============================================================================
# 1. Group 1: Inventory Tools (22 tools, Strictly Read-Only)
# ==============================================================================

@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_clusters() -> Dict[str, Any]:
    """List available Kubernetes cluster contexts."""
    return await list_clusters()


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_get_cluster_info(cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get Kubernetes API version, host endpoint, and node count (no credentials)."""
    return await get_cluster_info(cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_namespaces(cluster: Optional[str] = None) -> Dict[str, Any]:
    """List namespaces in cluster."""
    return await list_namespaces(cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_get_namespace(name: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get details, status, and labels for a single namespace."""
    return await get_namespace(name, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_nodes(cluster: Optional[str] = None) -> Dict[str, Any]:
    """List worker nodes with readiness and kubelet versions."""
    return await list_nodes(cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_get_node_details(name: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get node conditions, capacity, allocatable resources, and taints."""
    return await get_node_details(name, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_pods(
    namespace: Optional[str] = None,
    label_selector: Optional[str] = None,
    field_selector: Optional[str] = None,
    status_filter: Optional[str] = None,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """List pods with label and status filters."""
    return await list_pods(namespace, label_selector, field_selector, status_filter, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_get_pod_details(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get pod status, container details, conditions, restart counts, and recent events."""
    return await get_pod_details(name, namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_get_pod_logs(
    name: str,
    namespace: str,
    container: Optional[str] = None,
    tail_lines: Optional[int] = None,
    since_seconds: Optional[int] = None,
    timestamps: bool = True,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve logs for a running container with redaction and bounded lines."""
    return await get_pod_logs(name, namespace, container, tail_lines, since_seconds, timestamps, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_get_pod_previous_logs(
    name: str,
    namespace: str,
    container: Optional[str] = None,
    tail_lines: Optional[int] = None,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve logs from previous crashed instance of a container (previous=True)."""
    return await get_pod_previous_logs(name, namespace, container, tail_lines, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_deployments(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List deployments across namespace or cluster."""
    return await list_deployments(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_get_deployment_details(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get deployment spec, status conditions, selector, and replica counts."""
    return await get_deployment_details(name, namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_statefulsets(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List StatefulSets in namespace or cluster."""
    return await list_statefulsets(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_daemonsets(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List DaemonSets in namespace or cluster."""
    return await list_daemonsets(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_services(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List Services and their ports/types."""
    return await list_services(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_ingresses(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List Ingress rules and TLS host configurations."""
    return await list_ingresses(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_configmaps(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List ConfigMaps. Returns key names and sizes only (no values unless K8S_ALLOW_CONFIGMAP_VALUES=true)."""
    return await list_configmaps(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_secrets_metadata(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """CRITICAL SAFETY: Returns secret METADATA and KEY NAMES only. NEVER returns secret values."""
    return await list_secrets_metadata(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_list_events(
    namespace: Optional[str] = None,
    involved_object: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: Optional[int] = 100,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """List cluster events sorted newest first with redaction and object filtering."""
    return await list_events(namespace, involved_object, event_type, limit, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_get_pod_metrics(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve live CPU and memory metrics from metrics.k8s.io (graceful fallback if unavailable)."""
    return await get_pod_metrics(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_get_resource_quotas(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get ResourceQuotas with used vs hard limits and calculated consumption."""
    return await get_resource_quotas(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_get_hpa_status(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get HorizontalPodAutoscalers status, replica bounds, and conditions."""
    return await get_hpa_status(namespace, cluster)


# ==============================================================================
# 2. Group 2: Troubleshooting / RCA Tools (15 tools, returning DiagnosisReport)
# ==============================================================================

@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_diagnose_pod(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Overall pod health entrypoint. Inspects phase, container states, conditions, events, and restarts."""
    return await diagnose_pod(name, namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_diagnose_crashloop(name: str, namespace: str, container: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose CrashLoopBackOff: exit code, OOMKilled, restart timing, previous logs tail, memory limits."""
    return await diagnose_crashloop(name, namespace, container, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_diagnose_image_pull(name: str, namespace: str, container: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose ImagePullBackOff / ErrImagePull: registry errors, auth failures, imagePullSecrets, tags."""
    return await diagnose_image_pull(name, namespace, container, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_diagnose_pending_pod(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose scheduler bottlenecks: FailedScheduling, insufficient cpu/memory, taints vs tolerations, PVCs."""
    return await diagnose_pending_pod(name, namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_diagnose_node(name: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose node conditions (Ready, MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable), taints, and pods."""
    return await diagnose_node(name, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_diagnose_deployment(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose rollout status, unavailable replicas, ReplicaSet history, progressDeadlineExceeded."""
    return await diagnose_deployment(name, namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_diagnose_service(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose Service: pod selector matches, endpoints ready count, port/targetPort mismatch, pod readiness."""
    return await diagnose_service(name, namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_diagnose_ingress(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose Ingress: ingress class, backend service existence, endpoints ready, TLS secret presence."""
    return await diagnose_ingress(name, namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_analyze_pod_events(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Correlate and group pod events by reason and time, reconstruct causal chain, and dedupe repeats."""
    return await analyze_pod_events(name, namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_analyze_container_logs(
    name: str,
    namespace: str,
    container: Optional[str] = None,
    previous: bool = False,
    tail_lines: int = 500,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch log tail, detect exceptions, error rate, repeated messages, OOM, timeouts, DNS failures, panic/fatal."""
    return await analyze_container_logs(name, namespace, container, previous, tail_lines, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_check_pod_restarts(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Rank pods across namespace by restart count and recent restart rate, including last termination reason."""
    return await check_pod_restarts(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_check_resource_pressure(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Compare requests/limits across namespace and flag pods near memory limits and nodes >85% allocatable."""
    return await check_resource_pressure(namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_check_pvc_status(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose PVC phase, storage class binding, and mount events (ProvisioningFailed, FailedMount)."""
    return await check_pvc_status(name, namespace, cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_check_dns_resolution(cluster: Optional[str] = None) -> Dict[str, Any]:
    """READ-ONLY analysis of cluster DNS: CoreDNS pods, kube-dns endpoints, Corefile sanity, recent logs."""
    return await check_dns_resolution(cluster)


@mcp.tool(**_TOOL_ANNOTATIONS)
async def k8s_check_network_connectivity(
    source_service: str,
    target_service: str,
    namespace: str,
    port: int = 80,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """READ-ONLY passive analysis of network connectivity between services (active exec probes out of scope)."""
    return await check_network_connectivity(source_service, target_service, namespace, port, cluster)




# ==============================================================================
# 3. DevOps, CI/CD, and IaC Tools
# ==============================================================================

@mcp.tool(**_TOOL_ANNOTATIONS)
async def tool_fetch_github_pr_diff(repo: str, pr_number: int) -> Dict[str, Any]:
    """Fetch pull request code diff and changed files from GitHub / GitLab."""
    return await fetch_github_pr_diff_impl(repo, pr_number)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def fetch_github_pr_diff(repo: str, pr_number: int) -> Dict[str, Any]:
    """Alias: Fetch pull request code diff and changed files."""
    return await fetch_github_pr_diff_impl(repo, pr_number)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def tool_validate_terraform_plan(directory_path: str = ".") -> Dict[str, Any]:
    """Validate Terraform / OpenTofu syntax and simulate dry-run plan."""
    return await validate_terraform_plan_impl(directory_path)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def validate_terraform_plan(directory_path: str = ".") -> Dict[str, Any]:
    """Alias: Validate Terraform / OpenTofu syntax."""
    return await validate_terraform_plan_impl(directory_path)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def tool_generate_promql_query(metric_intent: str) -> Dict[str, Any]:
    """Synthesize an optimized PromQL query from natural language requirements."""
    return await generate_promql_query_impl(metric_intent)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def generate_promql_query(metric_intent: str) -> Dict[str, Any]:
    """Alias: Synthesize an optimized PromQL query."""
    return await generate_promql_query_impl(metric_intent)

@mcp.tool(readOnlyHint=False, destructiveHint=False, idempotentHint=False)
async def tool_trigger_cicd_pipeline(
    pipeline_name: str, target_branch: str = "main", approval_token: Optional[str] = None
) -> Dict[str, Any]:
    """Trigger deployment or rerun CI/CD pipeline in GitHub Actions / Cloud Build."""
    return await trigger_cicd_pipeline_impl(pipeline_name, target_branch, approval_token)

@mcp.tool(readOnlyHint=False, destructiveHint=False, idempotentHint=False)
async def trigger_cicd_pipeline(
    pipeline_name: str, target_branch: str = "main", approval_token: Optional[str] = None
) -> Dict[str, Any]:
    """Alias: Trigger deployment or rerun CI/CD pipeline."""
    return await trigger_cicd_pipeline_impl(pipeline_name, target_branch, approval_token)


# ==============================================================================
# 4. QA & Automated Testing Tools
# ==============================================================================

@mcp.tool(**_TOOL_ANNOTATIONS)
async def tool_run_playwright_e2e_test(test_spec: str, environment: str = "staging") -> Dict[str, Any]:
    """Run a headless Playwright test suite against staging web endpoints."""
    return await run_playwright_e2e_test_impl(test_spec, environment)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def run_playwright_e2e_test(test_spec: str, environment: str = "staging") -> Dict[str, Any]:
    """Alias: Run a headless Playwright test suite."""
    return await run_playwright_e2e_test_impl(test_spec, environment)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def tool_parse_test_failure_logs(build_id: str) -> Dict[str, Any]:
    """Parse test runner failure logs, stack traces, and screenshots to identify flakiness."""
    return await parse_test_failure_logs_impl(build_id)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def parse_test_failure_logs(build_id: str) -> Dict[str, Any]:
    """Alias: Parse test runner failure logs."""
    return await parse_test_failure_logs_impl(build_id)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def tool_generate_synthetic_test_data(schema_type: str, count: int = 5) -> List[Dict[str, Any]]:
    """Generate realistic mock fixtures, user personas, and IoT payload schemas."""
    return await generate_synthetic_test_data_impl(schema_type, count)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def generate_synthetic_test_data(schema_type: str, count: int = 5) -> List[Dict[str, Any]]:
    """Alias: Generate realistic mock fixtures."""
    return await generate_synthetic_test_data_impl(schema_type, count)

@mcp.tool(readOnlyHint=False, destructiveHint=False, idempotentHint=False)
async def tool_run_load_test(
    target_url: str, virtual_users: int = 50, approval_token: Optional[str] = None
) -> Dict[str, Any]:
    """Execute synthetic load/stress test generating high-concurrency traffic."""
    return await run_load_test_impl(target_url, virtual_users, approval_token)

@mcp.tool(readOnlyHint=False, destructiveHint=False, idempotentHint=False)
async def run_load_test(
    target_url: str, virtual_users: int = 50, approval_token: Optional[str] = None
) -> Dict[str, Any]:
    """Alias: Execute synthetic load/stress test."""
    return await run_load_test_impl(target_url, virtual_users, approval_token)


# ==============================================================================
# 5. Security & SIEM Tools
# ==============================================================================

@mcp.tool(**_TOOL_ANNOTATIONS)
async def tool_query_wazuh_alerts(severity_threshold: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
    """Query Wazuh SIEM security events, intrusion alerts, and CIS benchmark findings."""
    return await query_wazuh_alerts_impl(severity_threshold, limit)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def query_wazuh_alerts(severity_threshold: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
    """Alias: Query Wazuh SIEM security events."""
    return await query_wazuh_alerts_impl(severity_threshold, limit)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def tool_scan_container_vulnerabilities(image_tag: str) -> Dict[str, Any]:
    """Scan container image or repository dependencies with Trivy / Snyk for CVEs."""
    return await scan_container_vulnerabilities_impl(image_tag)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def scan_container_vulnerabilities(image_tag: str) -> Dict[str, Any]:
    """Alias: Scan container image with Trivy scanner."""
    return await scan_container_vulnerabilities_impl(image_tag)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def tool_audit_gcp_iam_bindings(project_id: str = "smiota-prod") -> List[Dict[str, Any]]:
    """Inspect GCP IAM service account permissions and detect over-privileged roles."""
    return await audit_gcp_iam_bindings_impl(project_id)

@mcp.tool(**_TOOL_ANNOTATIONS)
async def audit_gcp_iam_bindings(project_id: str = "smiota-prod") -> List[Dict[str, Any]]:
    """Alias: Inspect GCP IAM service account permissions."""
    return await audit_gcp_iam_bindings_impl(project_id)

@mcp.tool(readOnlyHint=False, destructiveHint=True, idempotentHint=False)
async def tool_revoke_compromised_credentials(
    credential_id: str, reason: str, approval_token: Optional[str] = None
) -> Dict[str, Any]:
    """Revoke compromised API key or service account key (Requires Approval)."""
    return await revoke_compromised_credentials_impl(credential_id, reason, approval_token)

@mcp.tool(readOnlyHint=False, destructiveHint=True, idempotentHint=False)
async def revoke_compromised_credentials(
    credential_id: str, reason: str, approval_token: Optional[str] = None
) -> Dict[str, Any]:
    """Alias: Revoke compromised API key or service account key."""
    return await revoke_compromised_credentials_impl(credential_id, reason, approval_token)


def main() -> None:
    """Run FastMCP Kubernetes SRE Server on selected transport."""
    transport = settings.MCP_TRANSPORT.lower().strip()
    logger.info(f"Starting Kubernetes SRE MCP Server on transport '{transport}'")

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport in ("streamable-http", "sse", "http"):
        run_transport = "streamable-http" if transport in ("streamable-http", "http") else "sse"
        try:
            mcp.run(transport=run_transport, host=settings.MCP_HOST, port=settings.MCP_PORT)
        except Exception:
            mcp.run(transport="sse", host=settings.MCP_HOST, port=settings.MCP_PORT)
    else:
        logger.error(f"Unsupported transport '{transport}'. Use 'stdio' or 'streamable-http'.")
        sys.exit(1)


if __name__ == "__main__":
    main()

