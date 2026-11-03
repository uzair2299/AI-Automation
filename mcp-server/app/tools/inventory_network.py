"""Group 1 Inventory: Services and Ingresses."""
from __future__ import annotations

from typing import Any, Dict, Optional
from app.config import settings
from app.k8s.clients import get_k8s_clients, run_k8s_call
from app.k8s.errors import map_k8s_exception
from app.k8s.guard import validate_namespace_access


async def list_services(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List Services and their ports/types."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]

        if ns:
            svc_list = await run_k8s_call(core_api.list_namespaced_service, namespace=ns, limit=settings.K8S_MAX_LIST_ITEMS)
        else:
            svc_list = await run_k8s_call(core_api.list_service_for_all_namespaces, limit=settings.K8S_MAX_LIST_ITEMS)

        items = []
        for s in getattr(svc_list, "items", []):
            ports = [f"{p.port}:{p.target_port}/{p.protocol}" for p in (s.spec.ports or [])]
            items.append({
                "name": s.metadata.name,
                "namespace": s.metadata.namespace,
                "type": s.spec.type,
                "cluster_ip": s.spec.cluster_ip,
                "ports": ports,
                "selector": s.spec.selector or {},
            })
        return {"services": items, "total": len(items)}
    except Exception as exc:
        return map_k8s_exception(exc, resource="services", name=namespace)


async def list_ingresses(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List Ingress rules and TLS host configurations."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        net_api = clients["networking_v1"]

        if ns:
            ing_list = await run_k8s_call(net_api.list_namespaced_ingress, namespace=ns, limit=settings.K8S_MAX_LIST_ITEMS)
        else:
            ing_list = await run_k8s_call(net_api.list_ingress_for_all_namespaces, limit=settings.K8S_MAX_LIST_ITEMS)

        items = []
        for ing in getattr(ing_list, "items", []):
            hosts = [rule.host for rule in (ing.spec.rules or []) if rule.host]
            tls_hosts = []
            for t in (ing.spec.tls or []):
                tls_hosts.extend(t.hosts or [])

            items.append({
                "name": ing.metadata.name,
                "namespace": ing.metadata.namespace,
                "ingress_class": ing.spec.ingress_class_name or ing.metadata.annotations.get("kubernetes.io/ingress.class") if ing.metadata.annotations else None,
                "hosts": hosts,
                "tls_hosts": tls_hosts,
            })
        return {"ingresses": items, "total": len(items)}
    except Exception as exc:
        return map_k8s_exception(exc, resource="ingresses", name=namespace)

