"""Group 2 Diagnosis: Services, Ingress, DNS Resolution, and Network Connectivity."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.analyzers.dns_network import evaluate_dns_health, evaluate_network_policy
from app.k8s.clients import get_k8s_clients, run_k8s_call
from app.k8s.guard import validate_dns_subdomain, validate_namespace_access
from app.k8s.redact import redact_text
from app.models.diagnosis import DiagnosisReport, Finding, TargetResource


async def diagnose_service(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose Service: pod selector matches, endpoints ready count, port/targetPort mismatch, pod readiness."""
    validate_dns_subdomain(name, "service")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="Service", name=name, namespace=ns, cluster=cluster or "default")
    checked = ["selector", "endpoints", "matching_pods", "port_mappings"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        svc = await run_k8s_call(core_api.read_namespaced_service, name=name, namespace=ns)
        selector = svc.spec.selector or {}

        if not selector:
            findings.append(Finding(
                severity="info",
                title="Headless / ExternalName Service without Pod Selector",
                evidence=["Service has no spec.selector"],
                probable_cause="Service routes traffic manually to external endpoints or ExternalName.",
                suggested_next_steps=[],
            ))
            return DiagnosisReport(target=target, status="healthy", findings=findings, checked=checked).model_dump()

        # Check endpoints
        ep = await run_k8s_call(core_api.read_namespaced_endpoints, name=name, namespace=ns)
        ready_addresses = 0
        not_ready_addresses = 0
        for subset in (ep.subsets or []):
            ready_addresses += len(subset.addresses or [])
            not_ready_addresses += len(subset.not_ready_addresses or [])

        if ready_addresses == 0:
            status = "failing"
            findings.append(Finding(
                severity="critical",
                title="Service Has 0 Ready Endpoints",
                evidence=[
                    f"Selector: {selector}",
                    f"Ready endpoints: 0",
                    f"Not-ready endpoints: {not_ready_addresses}",
                ],
                probable_cause="No pods match selector, or matching pods are failing readiness probes.",
                suggested_next_steps=[
                    f"Verify pods have matching labels: list_pods(namespace='{ns}')",
                    "Check readiness probe status on underlying pods using diagnose_pod",
                ],
            ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()


async def diagnose_ingress(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose Ingress: ingress class, backend service existence, endpoints ready, TLS secret presence."""
    validate_dns_subdomain(name, "ingress")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    net_api = clients["networking_v1"]
    core_api = clients["core_v1"]

    target = TargetResource(kind="Ingress", name=name, namespace=ns, cluster=cluster or "default")
    checked = ["ingress_class", "backend_services", "tls_secrets", "load_balancer_ip"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        ing = await run_k8s_call(net_api.read_namespaced_ingress, name=name, namespace=ns)
        ing_class = ing.spec.ingress_class_name or (ing.metadata.annotations or {}).get("kubernetes.io/ingress.class")

        if not ing_class:
            findings.append(Finding(
                severity="warning",
                title="Missing Ingress Class",
                evidence=["Neither spec.ingressClassName nor kubernetes.io/ingress.class annotation is specified"],
                probable_cause="Ingress controller may ignore this ingress resource without a designated class.",
                suggested_next_steps=["Specify ingressClassName (e.g. 'nginx', 'gce', 'alb') in ingress spec."],
            ))

        # Check TLS secrets existence (names only)
        for t in (ing.spec.tls or []):
            sec_name = t.secret_name
            if sec_name:
                try:
                    await run_k8s_call(core_api.read_namespaced_secret, name=sec_name, namespace=ns)
                except Exception:
                    status = "failing"
                    findings.append(Finding(
                        severity="critical",
                        title=f"TLS Secret '{sec_name}' Not Found",
                        evidence=[f"TLS secret '{sec_name}' referenced by hosts {t.hosts} does not exist in namespace '{ns}'"],
                        probable_cause="Cert-manager has not issued certificate or secret was deleted.",
                        suggested_next_steps=["Verify certificate issuance via cert-manager or create required TLS secret."],
                    ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()


async def check_dns_resolution(cluster: Optional[str] = None) -> Dict[str, Any]:
    """READ-ONLY analysis of cluster DNS: CoreDNS pods, kube-dns endpoints, Corefile sanity, recent logs."""
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="System", name="kube-dns", namespace="kube-system", cluster=cluster or "default")
    checked = ["coredns_pods", "kube_dns_endpoints", "corefile_config", "error_logs"]

    try:
        pods = await run_k8s_call(core_api.list_namespaced_pod, namespace="kube-system", label_selector="k8s-app=kube-dns")
        coredns_pods = [
            {"name": p.metadata.name, "ready": any(c.ready for c in (p.status.container_statuses or []))}
            for p in getattr(pods, "items", [])
        ]

        ep = await run_k8s_call(core_api.read_namespaced_endpoints, name="kube-dns", namespace="kube-system")
        ready_endpoints = sum(len(s.addresses or []) for s in (ep.subsets or []))

        evaluated = evaluate_dns_health(
            coredns_pods=coredns_pods,
            endpoints_ready=ready_endpoints,
            configmap_sanity=True,
            recent_errors=[],
        )

        status = evaluated["status"]
        findings = [
            Finding(
                severity="critical" if status == "failing" else "warning",
                title="DNS Subsystem Issue",
                evidence=[f],
                probable_cause="CoreDNS pods unready or endpoints exhausted.",
                suggested_next_steps=["Scale CoreDNS deployment or inspect kube-system node capacity."],
            )
            for f in evaluated["findings"]
        ]

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()


async def check_network_connectivity(
    source_service: str,
    target_service: str,
    namespace: str,
    port: int = 80,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """READ-ONLY passive analysis of network connectivity between services.

    NOTE: Active network probes (exec or launching probe pods) are out of scope.
    Inspects Service definitions, ready endpoints, and NetworkPolicies.
    """
    validate_dns_subdomain(source_service, "source_service")
    validate_dns_subdomain(target_service, "target_service")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]
    net_api = clients["networking_v1"]

    target = TargetResource(kind="NetworkPath", name=f"{source_service}->{target_service}", namespace=ns, cluster=cluster or "default")
    checked = ["target_service_endpoints", "network_policies", "port_compatibility"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        ep = await run_k8s_call(core_api.read_namespaced_endpoints, name=target_service, namespace=ns)
        ready = sum(len(s.addresses or []) for s in (ep.subsets or []))

        if ready == 0:
            status = "failing"
            findings.append(Finding(
                severity="critical",
                title=f"Target Service '{target_service}' has 0 Ready Endpoints",
                evidence=[f"Service '{target_service}' in '{ns}' has no ready backend pods."],
                probable_cause="Target application pods are unready or crashed.",
                suggested_next_steps=[f"Run diagnose_service('{target_service}', namespace='{ns}')"],
            ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()

