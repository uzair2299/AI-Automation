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


def main() -> None:
    """Run FastMCP Kubernetes SRE Server on selected transport."""
    transport = settings.MCP_TRANSPORT.lower().strip()
    logger.info(f"Starting Kubernetes SRE MCP Server on transport '{transport}'")

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport in ("streamable-http", "sse", "http"):
        mcp.settings.host = settings.MCP_HOST
        mcp.settings.port = settings.MCP_PORT
        try:
            mcp.run(transport="streamable-http")
        except Exception:
            mcp.run(transport="sse")
    else:
        logger.error(f"Unsupported transport '{transport}'. Use 'stdio' or 'streamable-http'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
