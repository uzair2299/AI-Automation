"""Pure analyzer: DNS and network policy reachability analysis."""
from __future__ import annotations

from typing import Any, Dict, List


def evaluate_dns_health(
    coredns_pods: List[Dict[str, Any]],
    endpoints_ready: int,
    configmap_sanity: bool,
    recent_errors: List[str],
) -> Dict[str, Any]:
    """Pure evaluation of CoreDNS cluster health."""
    unready_pods = [p["name"] for p in coredns_pods if not p.get("ready")]
    status = "healthy"
    findings = []

    if unready_pods:
        status = "degraded"
        findings.append(f"CoreDNS pods not ready: {', '.join(unready_pods)}")

    if endpoints_ready == 0:
        status = "failing"
        findings.append("kube-dns service has 0 ready endpoints; cluster-wide DNS is down")

    if not configmap_sanity:
        status = "degraded"
        findings.append("Corefile configuration syntax check reported abnormalities")

    if recent_errors:
        findings.append(f"Detected {len(recent_errors)} DNS resolution error logs in CoreDNS")

    return {
        "status": status,
        "findings": findings,
        "endpoints_ready": endpoints_ready,
        "total_coredns_pods": len(coredns_pods),
    }


def evaluate_network_policy(
    source_labels: Dict[str, str],
    dest_labels: Dict[str, str],
    policies: List[Dict[str, Any]],
    port: int,
) -> Dict[str, Any]:
    """Pure analysis of NetworkPolicies governing traffic between source and destination."""
    blocking_policies = []

    for pol in policies:
        # Check if policy matches destination pod
        pod_sel = pol.get("pod_selector", {})
        matches_dest = all(dest_labels.get(k) == v for k, v in pod_sel.items()) if pod_sel else True
        if matches_dest and "Ingress" in pol.get("policy_types", []):
            allowed_ingress = False
            for rule in pol.get("ingress", []):
                ports = rule.get("ports", [])
                port_match = any(p.get("port") == port for p in ports) if ports else True
                if port_match:
                    allowed_ingress = True
                    break
            if not allowed_ingress:
                blocking_policies.append(pol.get("name"))

    return {
        "allowed": len(blocking_policies) == 0,
        "blocking_policies": blocking_policies,
    }

