"""Group 1 Inventory: Clusters, Namespaces, and Nodes."""
from __future__ import annotations

from typing import Any, Dict, Optional
from app.k8s.clients import get_cluster_list, get_k8s_clients, run_k8s_call
from app.k8s.errors import map_k8s_exception
from app.k8s.guard import validate_dns_label, validate_dns_subdomain, validate_namespace_access
from app.k8s.redact import redact_data
from app.models.inventory import ClusterInfo, NodeDetails


async def list_clusters() -> Dict[str, Any]:
    """List available Kubernetes cluster contexts."""
    clusters = get_cluster_list()
    return {"clusters": clusters, "total": len(clusters)}


async def get_cluster_info(cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get Kubernetes API version, host, and node count for a cluster."""
    try:
        clients = get_k8s_clients(cluster)
        v_api = clients["version"]
        core_api = clients["core_v1"]

        version_info = await run_k8s_call(v_api.get_code)
        nodes = await run_k8s_call(core_api.list_node, limit=200)

        # Host endpoint only, no credentials or tokens
        host = clients["api_client"].configuration.host if clients["api_client"] else "in-cluster"
        host_sanitized = host.split("://")[-1].split(":")[0] if "://" in host else host

        info = ClusterInfo(
            name=cluster or "default",
            kubernetes_version=version_info.git_version if hasattr(version_info, "git_version") else "unknown",
            api_endpoint_host=host_sanitized,
            node_count=len(nodes.items) if hasattr(nodes, "items") else 0,
        )
        return info.model_dump()
    except Exception as exc:
        return map_k8s_exception(exc, resource="cluster_info", name=cluster)


async def list_namespaces(cluster: Optional[str] = None) -> Dict[str, Any]:
    """List namespaces in cluster."""
    try:
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]
        ns_list = await run_k8s_call(core_api.list_namespace)
        items = [ns.metadata.name for ns in ns_list.items] if hasattr(ns_list, "items") else []
        return {"namespaces": items, "total": len(items)}
    except Exception as exc:
        return map_k8s_exception(exc, resource="namespaces")


async def get_namespace(name: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get details and status for a single namespace."""
    try:
        validate_dns_label(name, "namespace")
        validate_namespace_access(name)
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]
        ns = await run_k8s_call(core_api.read_namespace, name=name)
        return {
            "name": ns.metadata.name,
            "status": ns.status.phase if hasattr(ns, "status") and ns.status else "Active",
            "labels": redact_data(ns.metadata.labels or {}),
            "created_at": str(ns.metadata.creation_timestamp),
        }
    except Exception as exc:
        return map_k8s_exception(exc, resource="namespace", name=name)


async def list_nodes(cluster: Optional[str] = None) -> Dict[str, Any]:
    """List all worker nodes in the cluster with status."""
    try:
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]
        nodes = await run_k8s_call(core_api.list_node)
        items = []
        for n in getattr(nodes, "items", []):
            conditions = {c.type: c.status for c in (n.status.conditions or [])}
            items.append({
                "name": n.metadata.name,
                "ready": conditions.get("Ready") == "True",
                "roles": [k.split("/")[-1] for k in (n.metadata.labels or {}) if "node-role" in k],
                "kubelet_version": n.status.node_info.kubelet_version if n.status and n.status.node_info else "unknown",
            })
        return {"nodes": items, "total": len(items)}
    except Exception as exc:
        return map_k8s_exception(exc, resource="nodes")


async def get_node_details(name: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get conditions, allocatable resources, capacity, and taints for a node."""
    try:
        validate_dns_subdomain(name, "node")
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]
        n = await run_k8s_call(core_api.read_node, name=name)

        conditions = {c.type: c.status for c in (n.status.conditions or [])}
        capacity = n.status.capacity or {}
        allocatable = n.status.allocatable or {}
        taints = [{"key": t.key, "value": t.value, "effect": t.effect} for t in (n.spec.taints or [])]

        details = NodeDetails(
            name=n.metadata.name,
            kubelet_version=n.status.node_info.kubelet_version if n.status and n.status.node_info else "unknown",
            conditions=conditions,
            capacity=capacity,
            allocatable=allocatable,
            taints=taints,
        )
        return details.model_dump()
    except Exception as exc:
        return map_k8s_exception(exc, resource="node", name=name)

