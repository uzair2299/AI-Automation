"""Group 1 Inventory: Pod Metrics, ResourceQuotas, and HPAs."""
from __future__ import annotations

from typing import Any, Dict, Optional
from app.config import settings
from app.k8s.clients import get_k8s_clients, run_k8s_call
from app.k8s.errors import map_k8s_exception
from app.k8s.guard import validate_namespace_access


async def get_pod_metrics(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve live CPU and memory metrics from metrics.k8s.io (falls back gracefully if metrics-server is unavailable)."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        cust_api = clients["custom_objects"]

        try:
            if ns:
                raw_metrics = await run_k8s_call(
                    cust_api.list_namespaced_custom_object,
                    group="metrics.k8s.io",
                    version="v1beta1",
                    namespace=ns,
                    plural="pods",
                )
            else:
                raw_metrics = await run_k8s_call(
                    cust_api.list_cluster_custom_object,
                    group="metrics.k8s.io",
                    version="v1beta1",
                    plural="pods",
                )

            items = []
            for item in raw_metrics.get("items", []):
                pod_name = item.get("metadata", {}).get("name")
                pod_ns = item.get("metadata", {}).get("namespace")
                containers = []
                for c in item.get("containers", []):
                    containers.append({
                        "name": c.get("name"),
                        "cpu": c.get("usage", {}).get("cpu"),
                        "memory": c.get("usage", {}).get("memory"),
                    })
                items.append({"pod": pod_name, "namespace": pod_ns, "containers": containers})

            return {"metrics": items, "total": len(items), "status": "available"}
        except Exception:
            return {
                "status": "metrics_unavailable",
                "message": "Metrics Server (metrics.k8s.io) is not deployed, unreachable, or RBAC restricts access.",
                "metrics": [],
                "total": 0,
            }
    except Exception as exc:
        return map_k8s_exception(exc, resource="pod_metrics", name=namespace)


async def get_resource_quotas(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get ResourceQuotas with used vs hard limits and calculated percentage consumption."""
    try:
        ns = validate_namespace_access(namespace) or "default"
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]

        quotas = await run_k8s_call(core_api.list_namespaced_resource_quota, namespace=ns)
        items = []
        for q in getattr(quotas, "items", []):
            hard = q.status.hard or {}
            used = q.status.used or {}
            percent: Dict[str, str] = {}

            for k, h_val in hard.items():
                u_val = used.get(k, "0")
                percent[k] = f"{u_val} / {h_val}"

            items.append({
                "name": q.metadata.name,
                "namespace": q.metadata.namespace,
                "hard": hard,
                "used": used,
                "usage_summary": percent,
            })
        return {"resource_quotas": items, "total": len(items)}
    except Exception as exc:
        return map_k8s_exception(exc, resource="resource_quotas", name=namespace)


async def get_hpa_status(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get HorizontalPodAutoscalers status, replica bounds, target metrics, and conditions."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        hpa_api = clients["autoscaling_v2"]

        if ns:
            hpas = await run_k8s_call(hpa_api.list_namespaced_horizontal_pod_autoscaler, namespace=ns)
        else:
            hpas = await run_k8s_call(hpa_api.list_horizontal_pod_autoscaler_for_all_namespaces)

        items = []
        for h in getattr(hpas, "items", []):
            conditions = [{"type": c.type, "status": c.status, "reason": c.reason} for c in (h.status.conditions or [])]
            items.append({
                "name": h.metadata.name,
                "namespace": h.metadata.namespace,
                "reference": f"{h.spec.scale_target_ref.kind}/{h.spec.scale_target_ref.name}",
                "min_replicas": h.spec.min_replicas or 1,
                "max_replicas": h.spec.max_replicas,
                "current_replicas": h.status.current_replicas or 0,
                "desired_replicas": h.status.desired_replicas or 0,
                "conditions": conditions,
            })
        return {"hpa": items, "total": len(items)}
    except Exception as exc:
        return map_k8s_exception(exc, resource="hpa", name=namespace)

