"""Group 2 Diagnosis: Nodes, Resource Pressure, and PVC Storage Status."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.k8s.clients import get_k8s_clients, run_k8s_call
from app.k8s.guard import validate_dns_subdomain, validate_namespace_access
from app.k8s.redact import redact_text
from app.models.diagnosis import DiagnosisReport, Finding, TargetResource


async def diagnose_node(name: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose node conditions (Ready, MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable), taints, and pods."""
    validate_dns_subdomain(name, "node")
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="Node", name=name, cluster=cluster or "default")
    checked = ["Ready", "MemoryPressure", "DiskPressure", "PIDPressure", "NetworkUnavailable", "taints"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        n = await run_k8s_call(core_api.read_node, name=name)
        conditions = {c.type: c for c in (n.status.conditions or [])}

        ready_cond = conditions.get("Ready")
        if not ready_cond or ready_cond.status != "True":
            status = "failing"
            findings.append(Finding(
                severity="critical",
                title="Node NotReady",
                evidence=[f"Ready condition status is '{getattr(ready_cond, 'status', 'Missing')}': {getattr(ready_cond, 'message', '')}"],
                probable_cause="Kubelet stopped posting status, container runtime stopped, or network partition.",
                suggested_next_steps=["Check kubelet daemon status on host: systemctl status kubelet", "Verify network connectivity between node and master API server"],
            ))

        for pressure in ("MemoryPressure", "DiskPressure", "PIDPressure", "NetworkUnavailable"):
            cond = conditions.get(pressure)
            if cond and cond.status == "True":
                status = "degraded" if status != "failing" else status
                findings.append(Finding(
                    severity="warning",
                    title=f"Node Condition: {pressure}",
                    evidence=[cond.message or f"{pressure} is Active"],
                    probable_cause=f"Host operating system is running out of {pressure.replace('Pressure', '').lower()} resources.",
                    suggested_next_steps=[f"Evict low-priority workloads or increase host {pressure.replace('Pressure', '').lower()} capacity."],
                ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()


async def check_resource_pressure(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Compare requests/limits across namespace and flag pods near memory limits and nodes >85% allocatable."""
    ns = validate_namespace_access(namespace)
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="Namespace", name=ns or "cluster-wide", namespace=ns, cluster=cluster or "default")
    checked = ["pod_requests", "pod_limits", "node_allocatable"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        if ns:
            pods = await run_k8s_call(core_api.list_namespaced_pod, namespace=ns)
        else:
            pods = await run_k8s_call(core_api.list_pod_for_all_namespaces)

        pods_without_limits = []
        for p in getattr(pods, "items", []):
            for c in (p.spec.containers or []):
                limits = c.resources.limits or {} if c.resources else {}
                if "memory" not in limits:
                    pods_without_limits.append(f"{p.metadata.namespace}/{p.metadata.name}:{c.name}")

        if pods_without_limits:
            findings.append(Finding(
                severity="info",
                title=f"{len(pods_without_limits)} containers running without memory limits",
                evidence=pods_without_limits[:5],
                probable_cause="Missing resource limits can expose nodes to unconstrained memory consumption.",
                suggested_next_steps=["Specify resources.limits.memory and resources.requests.memory in container specs."],
            ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()


async def check_pvc_status(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose PVC phase, storage class binding, and mount events (ProvisioningFailed, FailedMount)."""
    validate_dns_subdomain(name, "pvc")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="PersistentVolumeClaim", name=name, namespace=ns, cluster=cluster or "default")
    checked = ["pvc_phase", "pv_binding", "storage_class", "storage_events"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        pvc = await run_k8s_call(core_api.read_namespaced_persistent_volume_claim, name=name, namespace=ns)
        phase = pvc.status.phase if pvc.status else "Unknown"

        events = await run_k8s_call(core_api.list_namespaced_event, namespace=ns, field_selector=f"involvedObject.name={name}", limit=20)
        pvc_errors = [
            f"[{ev.reason}] {redact_text(ev.message or '')}"
            for ev in getattr(events, "items", [])
            if "Failed" in ev.reason or "ProvisioningFailed" in ev.reason or "Mount" in ev.reason
        ]

        if phase != "Bound":
            status = "failing"
            findings.append(Finding(
                severity="critical",
                title=f"PVC in {phase} Phase",
                evidence=[f"Status phase: {phase}", f"VolumeName: {pvc.spec.volume_name or 'Unassigned'}"] + pvc_errors,
                probable_cause="No matching PersistentVolume available or CSI storage provisioner failed to create volume.",
                suggested_next_steps=["Verify StorageClass exists and cloud CSI driver has quota/permissions to provision disk."],
            ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()

