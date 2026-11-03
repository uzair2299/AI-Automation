"""Group 1 Inventory: Pods, Logs, Deployments, StatefulSets, DaemonSets."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.config import settings
from app.k8s.clients import get_k8s_clients, run_k8s_call
from app.k8s.errors import map_k8s_exception
from app.k8s.guard import validate_bounded_int, validate_dns_subdomain, validate_namespace_access
from app.k8s.redact import redact_data, redact_text
from app.models.inventory import ContainerStatus, PodDetails


async def list_pods(
    namespace: Optional[str] = None,
    label_selector: Optional[str] = None,
    field_selector: Optional[str] = None,
    status_filter: Optional[str] = None,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """List pods with label and status filters."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]

        kwargs: Dict[str, Any] = {"limit": settings.K8S_MAX_LIST_ITEMS}
        if label_selector:
            kwargs["label_selector"] = label_selector
        if field_selector:
            kwargs["field_selector"] = field_selector

        if ns:
            pods = await run_k8s_call(core_api.list_namespaced_pod, namespace=ns, **kwargs)
        else:
            pods = await run_k8s_call(core_api.list_pod_for_all_namespaces, **kwargs)

        items = []
        for p in getattr(pods, "items", []):
            phase = p.status.phase if p.status else "Unknown"
            if status_filter and phase.lower() != status_filter.lower():
                continue
            restarts = sum(cs.restart_count for cs in (p.status.container_statuses or [])) if p.status else 0
            items.append({
                "name": p.metadata.name,
                "namespace": p.metadata.namespace,
                "phase": phase,
                "node": p.spec.node_name if p.spec else None,
                "restart_count": restarts,
                "created_at": str(p.metadata.creation_timestamp),
            })
        return {
            "pods": items,
            "total": len(items),
            "truncated": len(items) >= settings.K8S_MAX_LIST_ITEMS,
        }
    except Exception as exc:
        return map_k8s_exception(exc, resource="pods", name=namespace)


async def get_pod_details(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get pod status, container details, conditions, restart counts, and recent events."""
    try:
        validate_dns_subdomain(name, "pod")
        ns = validate_namespace_access(namespace) or "default"
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]

        pod = await run_k8s_call(core_api.read_namespaced_pod, name=name, namespace=ns)
        events = await run_k8s_call(
            core_api.list_namespaced_event,
            namespace=ns,
            field_selector=f"involvedObject.name={name}",
            limit=20,
        )

        containers = []
        for cs in (pod.status.container_statuses or []):
            state = "unknown"
            reason = None
            exit_code = None
            if cs.state:
                if cs.state.running:
                    state = "running"
                elif cs.state.waiting:
                    state = "waiting"
                    reason = cs.state.waiting.reason
                elif cs.state.terminated:
                    state = "terminated"
                    reason = cs.state.terminated.reason
                    exit_code = cs.state.terminated.exit_code

            containers.append(ContainerStatus(
                name=cs.name,
                ready=cs.ready,
                restart_count=cs.restart_count,
                state=state,
                reason=reason,
                exit_code=exit_code,
            ))

        conditions = {c.type: c.status for c in (pod.status.conditions or [])}
        recent_events = [
            f"[{ev.type}] {ev.reason}: {redact_text(ev.message or '')}"
            for ev in getattr(events, "items", [])
        ]

        details = PodDetails(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            phase=pod.status.phase or "Unknown",
            node_name=pod.spec.node_name,
            labels=redact_data(pod.metadata.labels or {}),
            containers=containers,
            conditions=conditions,
            recent_events=recent_events,
        )
        return details.model_dump()
    except Exception as exc:
        return map_k8s_exception(exc, resource="pod", name=f"{namespace}/{name}")


async def get_pod_logs(
    name: str,
    namespace: str,
    container: Optional[str] = None,
    tail_lines: Optional[int] = None,
    since_seconds: Optional[int] = None,
    timestamps: bool = True,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve logs for a running container with redaction and bounded lines."""
    try:
        validate_dns_subdomain(name, "pod")
        ns = validate_namespace_access(namespace) or "default"
        lines = validate_bounded_int(
            tail_lines,
            default=settings.K8S_DEFAULT_LOG_LINES,
            min_val=1,
            max_val=settings.K8S_HARD_CAP_LOG_LINES,
            field_name="tail_lines",
        )
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]

        kwargs: Dict[str, Any] = {
            "tail_lines": lines,
            "timestamps": timestamps,
        }
        if container:
            kwargs["container"] = container
        if since_seconds:
            kwargs["since_seconds"] = validate_bounded_int(
                since_seconds, default=3600, min_val=1, max_val=86400, field_name="since_seconds"
            )

        log_raw = await run_k8s_call(
            core_api.read_namespaced_pod_log,
            name=name,
            namespace=ns,
            **kwargs,
        )

        redacted = redact_text(log_raw or "")
        return {
            "pod": name,
            "namespace": ns,
            "container": container,
            "tail_lines": lines,
            "logs": redacted,
            "truncated": len(redacted.encode("utf-8")) >= settings.K8S_MAX_LOG_BYTES,
        }
    except Exception as exc:
        return map_k8s_exception(exc, resource="pod_logs", name=f"{namespace}/{name}")


async def get_pod_previous_logs(
    name: str,
    namespace: str,
    container: Optional[str] = None,
    tail_lines: Optional[int] = None,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve logs from previous crashed instance of a container (previous=True)."""
    try:
        validate_dns_subdomain(name, "pod")
        ns = validate_namespace_access(namespace) or "default"
        lines = validate_bounded_int(
            tail_lines,
            default=settings.K8S_DEFAULT_LOG_LINES,
            min_val=1,
            max_val=settings.K8S_HARD_CAP_LOG_LINES,
            field_name="tail_lines",
        )
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]

        kwargs: Dict[str, Any] = {
            "previous": True,
            "tail_lines": lines,
            "timestamps": True,
        }
        if container:
            kwargs["container"] = container

        log_raw = await run_k8s_call(
            core_api.read_namespaced_pod_log,
            name=name,
            namespace=ns,
            **kwargs,
        )

        redacted = redact_text(log_raw or "")
        return {
            "pod": name,
            "namespace": ns,
            "container": container,
            "previous": True,
            "tail_lines": lines,
            "logs": redacted,
            "truncated": False,
        }
    except Exception as exc:
        return map_k8s_exception(exc, resource="pod_previous_logs", name=f"{namespace}/{name}")


async def list_deployments(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List deployments across namespace or cluster."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        apps_api = clients["apps_v1"]

        if ns:
            deps = await run_k8s_call(apps_api.list_namespaced_deployment, namespace=ns, limit=settings.K8S_MAX_LIST_ITEMS)
        else:
            deps = await run_k8s_call(apps_api.list_deployment_for_all_namespaces, limit=settings.K8S_MAX_LIST_ITEMS)

        items = []
        for d in getattr(deps, "items", []):
            items.append({
                "name": d.metadata.name,
                "namespace": d.metadata.namespace,
                "replicas": d.spec.replicas or 0,
                "ready_replicas": d.status.ready_replicas or 0,
                "updated_replicas": d.status.updated_replicas or 0,
                "available_replicas": d.status.available_replicas or 0,
            })
        return {"deployments": items, "total": len(items)}
    except Exception as exc:
        return map_k8s_exception(exc, resource="deployments", name=namespace)


async def get_deployment_details(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Get deployment spec, status conditions, selector, and replica counts."""
    try:
        validate_dns_subdomain(name, "deployment")
        ns = validate_namespace_access(namespace) or "default"
        clients = get_k8s_clients(cluster)
        apps_api = clients["apps_v1"]

        d = await run_k8s_call(apps_api.read_namespaced_deployment, name=name, namespace=ns)
        conditions = {c.type: {"status": c.status, "reason": c.reason, "message": c.message} for c in (d.status.conditions or [])}

        return {
            "name": d.metadata.name,
            "namespace": d.metadata.namespace,
            "replicas": d.spec.replicas or 0,
            "ready_replicas": d.status.ready_replicas or 0,
            "selector": d.spec.selector.match_labels or {},
            "strategy": d.spec.strategy.type if d.spec.strategy else "RollingUpdate",
            "conditions": conditions,
            "containers": [c.name for c in (d.spec.template.spec.containers or [])],
        }
    except Exception as exc:
        return map_k8s_exception(exc, resource="deployment", name=f"{namespace}/{name}")


async def list_statefulsets(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List StatefulSets in namespace or cluster."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        apps_api = clients["apps_v1"]

        if ns:
            res = await run_k8s_call(apps_api.list_namespaced_stateful_set, namespace=ns, limit=settings.K8S_MAX_LIST_ITEMS)
        else:
            res = await run_k8s_call(apps_api.list_stateful_set_for_all_namespaces, limit=settings.K8S_MAX_LIST_ITEMS)

        items = [
            {"name": s.metadata.name, "namespace": s.metadata.namespace, "replicas": s.spec.replicas or 0, "ready_replicas": s.status.ready_replicas or 0}
            for s in getattr(res, "items", [])
        ]
        return {"statefulsets": items, "total": len(items)}
    except Exception as exc:
        return map_k8s_exception(exc, resource="statefulsets", name=namespace)


async def list_daemonsets(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List DaemonSets in namespace or cluster."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        apps_api = clients["apps_v1"]

        if ns:
            res = await run_k8s_call(apps_api.list_namespaced_daemon_set, namespace=ns, limit=settings.K8S_MAX_LIST_ITEMS)
        else:
            res = await run_k8s_call(apps_api.list_daemon_set_for_all_namespaces, limit=settings.K8S_MAX_LIST_ITEMS)

        items = [
            {"name": d.metadata.name, "namespace": d.metadata.namespace, "desired": d.status.desired_number_scheduled or 0, "current": d.status.current_number_scheduled or 0}
            for d in getattr(res, "items", [])
        ]
        return {"daemonsets": items, "total": len(items)}
    except Exception as exc:
        return map_k8s_exception(exc, resource="daemonsets", name=namespace)
