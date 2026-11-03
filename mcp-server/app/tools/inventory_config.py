"""Group 1 Inventory: ConfigMaps, Secrets Metadata (Redacted), and Events."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.config import settings
from app.k8s.clients import get_k8s_clients, run_k8s_call
from app.k8s.errors import map_k8s_exception
from app.k8s.guard import validate_namespace_access
from app.k8s.redact import redact_data, redact_text
from app.models.inventory import SecretMetadata


async def list_configmaps(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """List ConfigMaps. Returns key names and sizes only (no values) unless K8S_ALLOW_CONFIGMAP_VALUES=true."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]

        if ns:
            cms = await run_k8s_call(core_api.list_namespaced_config_map, namespace=ns, limit=settings.K8S_MAX_LIST_ITEMS)
        else:
            cms = await run_k8s_call(core_api.list_config_map_for_all_namespaces, limit=settings.K8S_MAX_LIST_ITEMS)

        items = []
        for cm in getattr(cms, "items", []):
            raw_data = cm.data or {}
            key_summary: Dict[str, Any] = {}
            for k, v in raw_data.items():
                if settings.K8S_ALLOW_CONFIGMAP_VALUES:
                    key_summary[k] = redact_text(v)
                else:
                    key_summary[k] = f"{len(str(v))} bytes"

            items.append({
                "name": cm.metadata.name,
                "namespace": cm.metadata.namespace,
                "keys": key_summary,
                "created_at": str(cm.metadata.creation_timestamp),
            })
        return {
            "configmaps": items,
            "total": len(items),
            "values_included": settings.K8S_ALLOW_CONFIGMAP_VALUES,
        }
    except Exception as exc:
        return map_k8s_exception(exc, resource="configmaps", name=namespace)


async def list_secrets_metadata(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """CRITICAL SAFETY: Returns secret METADATA and KEY NAMES only. NEVER returns secret values, data, or stringData."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]

        if ns:
            secrets = await run_k8s_call(core_api.list_namespaced_secret, namespace=ns, limit=settings.K8S_MAX_LIST_ITEMS)
        else:
            secrets = await run_k8s_call(core_api.list_secret_for_all_namespaces, limit=settings.K8S_MAX_LIST_ITEMS)

        items: List[Dict[str, Any]] = []
        for s in getattr(secrets, "items", []):
            # Extract key names only
            key_names = list((s.data or {}).keys()) if s.data else []

            # Scrub last-applied-configuration from annotations
            safe_labels = redact_data(s.metadata.labels or {})

            meta = SecretMetadata(
                name=s.metadata.name,
                namespace=s.metadata.namespace,
                type=s.type or "Opaque",
                keys=key_names,
                created_at=str(s.metadata.creation_timestamp),
                labels=safe_labels,
            )
            items.append(meta.model_dump())

        return {
            "secrets": items,
            "total": len(items),
            "security_notice": "Secret data and values are strictly withheld and redacted by non-negotiable safety policy.",
        }
    except Exception as exc:
        return map_k8s_exception(exc, resource="secrets_metadata", name=namespace)


async def list_events(
    namespace: Optional[str] = None,
    involved_object: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: Optional[int] = 100,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """List cluster events sorted newest first with redaction and object filtering."""
    try:
        ns = validate_namespace_access(namespace)
        clients = get_k8s_clients(cluster)
        core_api = clients["core_v1"]

        kwargs: Dict[str, Any] = {"limit": limit or 100}
        field_selectors = []
        if involved_object:
            field_selectors.append(f"involvedObject.name={involved_object}")
        if event_type:
            field_selectors.append(f"type={event_type}")

        if field_selectors:
            kwargs["field_selector"] = ",".join(field_selectors)

        if ns:
            events = await run_k8s_call(core_api.list_namespaced_event, namespace=ns, **kwargs)
        else:
            events = await run_k8s_call(core_api.list_event_for_all_namespaces, **kwargs)

        items = []
        for ev in getattr(events, "items", []):
            items.append({
                "type": ev.type,
                "reason": ev.reason,
                "message": redact_text(ev.message or ""),
                "object": f"{ev.involved_object.kind}/{ev.involved_object.name}" if ev.involved_object else "Unknown",
                "count": ev.count or 1,
                "first_time": str(ev.first_timestamp or ev.event_time or ""),
                "last_time": str(ev.last_timestamp or ev.event_time or ""),
            })

        # Sort newest first
        items.sort(key=lambda x: x["last_time"], reverse=True)

        return {"events": items, "total": len(items)}
    except Exception as exc:
        return map_k8s_exception(exc, resource="events", name=namespace)
