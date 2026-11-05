"""Kubernetes and SRE Troubleshooting MCP Tools.

Read-only cluster inspection, configuration verification, and incident
diagnostics for DevOps and SRE teams.

Enforces:
- Strict read-only cluster inspection.
- Zero secret exposure: Secret values are never exposed.
- Structured SRE telemetry and diagnostics.
"""

from typing import Any

from clients.k8s_client import get_k8s_client
from mcp.security import mcp_tool
from schemas.mcp import ToolAccessLevel

# =============================================================================
# 1. Kubernetes Tools (Read-only first)
# =============================================================================


@mcp_tool(
    name="list_clusters",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List available Kubernetes clusters and active context.",
)
async def list_clusters(include_details: bool = False) -> dict[str, Any]:
    """List available Kubernetes clusters."""
    client = get_k8s_client()
    return await client.list_clusters(include_details=include_details)


@mcp_tool(
    name="get_cluster_info",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Cluster version, endpoint and configuration details.",
)
async def get_cluster_info(cluster_name: str | None = None) -> dict[str, Any]:
    """Cluster version, endpoint and configuration."""
    client = get_k8s_client()
    return await client.get_cluster_info(cluster_name=cluster_name)


@mcp_tool(
    name="list_namespaces",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List Kubernetes namespaces in the cluster.",
)
async def list_namespaces(label_selector: str | None = None) -> dict[str, Any]:
    """List namespaces."""
    client = get_k8s_client()
    return await client.list_namespaces(label_selector=label_selector)


@mcp_tool(
    name="get_namespace",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Namespace details, status, and annotations.",
)
async def get_namespace(namespace: str) -> dict[str, Any]:
    """Namespace details and status."""
    client = get_k8s_client()
    return await client.get_namespace(namespace=namespace)


@mcp_tool(
    name="list_nodes",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List all worker and control-plane nodes.",
)
async def list_nodes(label_selector: str | None = None) -> dict[str, Any]:
    """List all worker/control-plane nodes."""
    client = get_k8s_client()
    return await client.list_nodes(label_selector=label_selector)


@mcp_tool(
    name="get_node_details",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Node conditions, capacity and allocatable resources.",
)
async def get_node_details(node_name: str) -> dict[str, Any]:
    """Node conditions, capacity and allocatable resources."""
    client = get_k8s_client()
    return await client.get_node_details(node_name=node_name)


@mcp_tool(
    name="list_pods",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List pods by namespace with status, restarts, and nodes.",
)
async def list_pods(
    namespace: str = "default",
    label_selector: str | None = None,
    field_selector: str | None = None,
) -> dict[str, Any]:
    """List pods by namespace."""
    client = get_k8s_client()
    return await client.list_pods(
        namespace=namespace,
        label_selector=label_selector,
        field_selector=field_selector,
    )


@mcp_tool(
    name="get_pod_details",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Pod status, labels, events and container conditions.",
)
async def get_pod_details(pod_name: str, namespace: str = "default") -> dict[str, Any]:
    """Pod status, labels, events and conditions."""
    client = get_k8s_client()
    return await client.get_pod_details(pod_name=pod_name, namespace=namespace)


@mcp_tool(
    name="get_pod_logs",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Retrieve container logs from a specific pod.",
)
async def get_pod_logs(
    pod_name: str,
    namespace: str = "default",
    container: str | None = None,
    tail_lines: int = 100,
    timestamps: bool = True,
) -> dict[str, Any]:
    """Retrieve container logs."""
    client = get_k8s_client()
    return await client.get_pod_logs(
        pod_name=pod_name,
        namespace=namespace,
        container=container,
        tail_lines=tail_lines,
        timestamps=timestamps,
    )


@mcp_tool(
    name="get_pod_previous_logs",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Retrieve logs from previous crashed containers for crash analysis.",
)
async def get_pod_previous_logs(
    pod_name: str,
    namespace: str = "default",
    container: str | None = None,
    tail_lines: int = 100,
) -> dict[str, Any]:
    """Retrieve logs from previous crashed containers."""
    client = get_k8s_client()
    return await client.get_pod_previous_logs(
        pod_name=pod_name,
        namespace=namespace,
        container=container,
        tail_lines=tail_lines,
    )


@mcp_tool(
    name="list_deployments",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List deployments and replica availability in a namespace.",
)
async def list_deployments(
    namespace: str = "default", label_selector: str | None = None
) -> dict[str, Any]:
    """List deployments."""
    client = get_k8s_client()
    return await client.list_deployments(namespace=namespace, label_selector=label_selector)


@mcp_tool(
    name="get_deployment_details",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Deployment configuration, replica status, and pod templates.",
)
async def get_deployment_details(
    deployment_name: str, namespace: str = "default"
) -> dict[str, Any]:
    """Deployment configuration and status."""
    client = get_k8s_client()
    return await client.get_deployment_details(deployment_name=deployment_name, namespace=namespace)


@mcp_tool(
    name="list_statefulsets",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List StatefulSets in a namespace.",
)
async def list_statefulsets(namespace: str = "default") -> dict[str, Any]:
    """List StatefulSets."""
    client = get_k8s_client()
    return await client.list_statefulsets(namespace=namespace)


@mcp_tool(
    name="list_daemonsets",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List DaemonSets and scheduled node counts.",
)
async def list_daemonsets(namespace: str = "default") -> dict[str, Any]:
    """List DaemonSets."""
    client = get_k8s_client()
    return await client.list_daemonsets(namespace=namespace)


@mcp_tool(
    name="list_services",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List Kubernetes services, ClusterIPs, and exposed ports.",
)
async def list_services(
    namespace: str = "default", label_selector: str | None = None
) -> dict[str, Any]:
    """List Kubernetes services."""
    client = get_k8s_client()
    return await client.list_services(namespace=namespace, label_selector=label_selector)


@mcp_tool(
    name="list_ingresses",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List ingress resources, host rules, and TLS configurations.",
)
async def list_ingresses(namespace: str = "default") -> dict[str, Any]:
    """List ingress resources."""
    client = get_k8s_client()
    return await client.list_ingresses(namespace=namespace)


@mcp_tool(
    name="list_configmaps",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List ConfigMaps and key names in a namespace.",
)
async def list_configmaps(namespace: str = "default") -> dict[str, Any]:
    """List ConfigMaps."""
    client = get_k8s_client()
    return await client.list_configmaps(namespace=namespace)


@mcp_tool(
    name="list_secrets_metadata",
    access_level=ToolAccessLevel.READ_ONLY,
    description="List secret names and metadata (never expose values).",
)
async def list_secrets_metadata(namespace: str = "default") -> dict[str, Any]:
    """List secret names and metadata (never expose values)."""
    client = get_k8s_client()
    return await client.list_secrets_metadata(namespace=namespace)


@mcp_tool(
    name="list_events",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Retrieve Kubernetes events for a namespace or specific resource.",
)
async def list_events(
    namespace: str = "default",
    involved_object_name: str | None = None,
    involved_object_kind: str | None = None,
    event_type: str | None = None,
) -> dict[str, Any]:
    """Retrieve Kubernetes events."""
    client = get_k8s_client()
    return await client.list_events(
        namespace=namespace,
        involved_object_name=involved_object_name,
        involved_object_kind=involved_object_kind,
        event_type=event_type,
    )


@mcp_tool(
    name="get_pod_metrics",
    access_level=ToolAccessLevel.READ_ONLY,
    description="CPU and memory usage across containers in a pod.",
)
async def get_pod_metrics(
    namespace: str = "default", pod_name: str | None = None
) -> dict[str, Any]:
    """CPU and memory usage."""
    client = get_k8s_client()
    return await client.get_pod_metrics(namespace=namespace, pod_name=pod_name)


@mcp_tool(
    name="get_resource_quotas",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Namespace resource quotas and current utilization percentages.",
)
async def get_resource_quotas(namespace: str = "default") -> dict[str, Any]:
    """Namespace resource quotas."""
    client = get_k8s_client()
    return await client.get_resource_quotas(namespace=namespace)


@mcp_tool(
    name="get_hpa_status",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Horizontal Pod Autoscaler status, current replicas, and targets.",
)
async def get_hpa_status(namespace: str = "default", hpa_name: str | None = None) -> dict[str, Any]:
    """Horizontal Pod Autoscaler status."""
    client = get_k8s_client()
    return await client.get_hpa_status(namespace=namespace, hpa_name=hpa_name)


# =============================================================================
# 2. Kubernetes Troubleshooting Tools (SRE Operations)
# =============================================================================


@mcp_tool(
    name="diagnose_pod",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Identify why a pod is failing with root cause and remediation recommendations.",
)
async def diagnose_pod(pod_name: str, namespace: str = "default") -> dict[str, Any]:
    """Identify why a pod is failing."""
    client = get_k8s_client()
    return await client.diagnose_pod(pod_name=pod_name, namespace=namespace)


@mcp_tool(
    name="diagnose_crashloop",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Investigate CrashLoopBackOff: exit codes, restart frequency, and previous logs.",
)
async def diagnose_crashloop(
    pod_name: str,
    namespace: str = "default",
    container: str | None = None,
) -> dict[str, Any]:
    """Investigate CrashLoopBackOff."""
    client = get_k8s_client()
    return await client.diagnose_crashloop(
        pod_name=pod_name, namespace=namespace, container=container
    )


@mcp_tool(
    name="diagnose_image_pull",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Investigate ImagePullBackOff, ErrImagePull, registry auth, and missing tags.",
)
async def diagnose_image_pull(
    pod_name: str,
    namespace: str = "default",
    container: str | None = None,
) -> dict[str, Any]:
    """Investigate ImagePullBackOff."""
    client = get_k8s_client()
    return await client.diagnose_image_pull(
        pod_name=pod_name, namespace=namespace, container=container
    )


@mcp_tool(
    name="diagnose_pending_pod",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Investigate pods stuck in Pending (scheduling constraints, resources, taints, PVCs).",
)
async def diagnose_pending_pod(pod_name: str, namespace: str = "default") -> dict[str, Any]:
    """Investigate pods stuck in Pending."""
    client = get_k8s_client()
    return await client.diagnose_pending_pod(pod_name=pod_name, namespace=namespace)


@mcp_tool(
    name="diagnose_node",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Investigate node NotReady conditions, disk/memory pressure, and affected pods.",
)
async def diagnose_node(node_name: str) -> dict[str, Any]:
    """Investigate node NotReady conditions."""
    client = get_k8s_client()
    return await client.diagnose_node(node_name=node_name)


@mcp_tool(
    name="diagnose_deployment",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Identify deployment failures, rollout timeouts, and ReplicaSet errors.",
)
async def diagnose_deployment(deployment_name: str, namespace: str = "default") -> dict[str, Any]:
    """Identify deployment failures."""
    client = get_k8s_client()
    return await client.diagnose_deployment(deployment_name=deployment_name, namespace=namespace)


@mcp_tool(
    name="diagnose_service",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Diagnose service connectivity, missing endpoints, and port mismatches.",
)
async def diagnose_service(service_name: str, namespace: str = "default") -> dict[str, Any]:
    """Diagnose service connectivity."""
    client = get_k8s_client()
    return await client.diagnose_service(service_name=service_name, namespace=namespace)


@mcp_tool(
    name="diagnose_ingress",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Diagnose ingress/routing issues, 502/503 errors, and TLS certificate problems.",
)
async def diagnose_ingress(ingress_name: str, namespace: str = "default") -> dict[str, Any]:
    """Diagnose ingress/routing issues."""
    client = get_k8s_client()
    return await client.diagnose_ingress(ingress_name=ingress_name, namespace=namespace)


@mcp_tool(
    name="analyze_pod_events",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Correlate chronological pod events to identify failure cascade patterns.",
)
async def analyze_pod_events(
    pod_name: str,
    namespace: str = "default",
    time_window_minutes: int = 60,
) -> dict[str, Any]:
    """Correlate pod events."""
    client = get_k8s_client()
    return await client.analyze_pod_events(
        pod_name=pod_name,
        namespace=namespace,
        time_window_minutes=time_window_minutes,
    )


@mcp_tool(
    name="analyze_container_logs",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Identify exceptions, stack traces, and recurring error patterns in container logs.",
)
async def analyze_container_logs(
    pod_name: str,
    namespace: str = "default",
    container: str | None = None,
    tail_lines: int = 200,
) -> dict[str, Any]:
    """Identify exceptions and error patterns."""
    client = get_k8s_client()
    return await client.analyze_container_logs(
        pod_name=pod_name,
        namespace=namespace,
        container=container,
        tail_lines=tail_lines,
    )


@mcp_tool(
    name="check_pod_restarts",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Identify frequently restarting pods exceeding a given threshold.",
)
async def check_pod_restarts(
    namespace: str = "default", restart_threshold: int = 3
) -> dict[str, Any]:
    """Identify frequently restarting pods."""
    client = get_k8s_client()
    return await client.check_pod_restarts(namespace=namespace, restart_threshold=restart_threshold)


@mcp_tool(
    name="check_resource_pressure",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Identify CPU/memory pressure on nodes and pods approaching limits.",
)
async def check_resource_pressure(
    namespace: str = "default", node_name: str | None = None
) -> dict[str, Any]:
    """Identify CPU/memory pressure."""
    client = get_k8s_client()
    return await client.check_resource_pressure(namespace=namespace, node_name=node_name)


@mcp_tool(
    name="check_pvc_status",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Investigate storage mounting issues, unbound PVCs, and volume attachment errors.",
)
async def check_pvc_status(
    namespace: str = "default", pvc_name: str | None = None
) -> dict[str, Any]:
    """Investigate storage mounting issues."""
    client = get_k8s_client()
    return await client.check_pvc_status(namespace=namespace, pvc_name=pvc_name)


@mcp_tool(
    name="check_dns_resolution",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Diagnose internal CoreDNS issues, resolution latency, and ndots configuration.",
)
async def check_dns_resolution(
    namespace: str = "default",
    target_host: str | None = "kubernetes.default.svc.cluster.local",
) -> dict[str, Any]:
    """Diagnose internal DNS issues."""
    client = get_k8s_client()
    return await client.check_dns_resolution(namespace=namespace, target_host=target_host)


@mcp_tool(
    name="check_network_connectivity",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Investigate service connectivity, CNI routing, and NetworkPolicy blocks.",
)
async def check_network_connectivity(
    source_pod: str,
    target_service: str,
    namespace: str = "default",
    target_port: int | None = None,
) -> dict[str, Any]:
    """Investigate service connectivity."""
    client = get_k8s_client()
    return await client.check_network_connectivity(
        source_pod=source_pod,
        target_service=target_service,
        namespace=namespace,
        target_port=target_port,
    )
