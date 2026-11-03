"""Pure analyzer: Kubernetes scheduler failure parsing."""
from __future__ import annotations

import re
from typing import Any, Dict, List


def parse_scheduling_failure(message: str) -> Dict[str, Any]:
    """Parse scheduler failure message to pinpoint root bottleneck."""
    reasons: List[str] = []
    probable_cause = "Pod unschedulable."
    suggested_steps: List[str] = []

    msg = message.lower()

    if "insufficient cpu" in msg:
        reasons.append("Insufficient CPU capacity across available nodes")
        suggested_steps.append("Reduce container cpu requests or scale up node pool")
        probable_cause = "Cluster CPU exhaustion."

    if "insufficient memory" in msg:
        reasons.append("Insufficient memory capacity across available nodes")
        suggested_steps.append("Reduce container memory requests or add nodes with larger RAM")
        probable_cause = "Cluster Memory exhaustion."

    if "taint" in msg:
        reasons.append("Node taint was not tolerated by pod tolerations")
        suggested_steps.append("Add matching tolerations to pod spec or remove untolerated node taint")
        probable_cause = "Taint/Toleration mismatch."

    if "nodeselector" in msg or "node affinity" in msg:
        reasons.append("Pod nodeSelector or nodeAffinity matched 0 nodes")
        suggested_steps.append("Verify node labels match pod nodeSelector requirements")
        probable_cause = "Node selector mismatch."

    if "unbound" in msg or "pvc" in msg or "persistentvolumeclaim" in msg:
        reasons.append("Required PersistentVolumeClaim is not bound")
        suggested_steps.append("Inspect PVC status and check storage class provisioning")
        probable_cause = "Storage volume provisioning failure."

    if "quota" in msg:
        reasons.append("ResourceQuota exceeded in target namespace")
        suggested_steps.append("Increase namespace ResourceQuota or clean up unused workloads")
        probable_cause = "Namespace ResourceQuota limit reached."

    if not reasons:
        reasons.append(message)
        suggested_steps.append("Inspect cluster nodes and events for detailed scheduling constraints")

    return {
        "reasons": reasons,
        "probable_cause": probable_cause,
        "suggested_steps": suggested_steps,
    }
