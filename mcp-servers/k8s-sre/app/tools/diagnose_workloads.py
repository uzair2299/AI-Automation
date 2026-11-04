"""Group 2 Diagnosis: Pod, CrashLoopBackOff, ImagePull, Pending, Deployments, Logs, and Events."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.analyzers.event_correlation import correlate_events
from app.analyzers.exit_codes import analyze_exit_code
from app.analyzers.log_patterns import analyze_log_content
from app.analyzers.scheduling import parse_scheduling_failure
from app.k8s.clients import get_k8s_clients, run_k8s_call
from app.k8s.guard import validate_bounded_int, validate_dns_subdomain, validate_namespace_access
from app.k8s.redact import redact_text
from app.models.diagnosis import DiagnosisReport, Finding, TargetResource


async def diagnose_pod(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Overall pod health entrypoint. Evaluates phase, container states, conditions, events, and restart counts."""
    validate_dns_subdomain(name, "pod")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="Pod", name=name, namespace=ns, cluster=cluster or "default")
    checked = ["phase", "container_statuses", "conditions", "events", "restart_count"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        pod = await run_k8s_call(core_api.read_namespaced_pod, name=name, namespace=ns)
        phase = pod.status.phase or "Unknown"

        if phase == "Pending":
            status = "degraded"
            findings.append(Finding(
                severity="warning",
                title="Pod in Pending Phase",
                evidence=[f"Pod status is {phase}"],
                probable_cause="Scheduler has not assigned pod to a node or required volumes/images are pending.",
                suggested_next_steps=["Run diagnose_pending_pod for detailed scheduler evaluation."],
            ))
        elif phase == "Failed":
            status = "failing"
            findings.append(Finding(
                severity="critical",
                title="Pod in Failed Phase",
                evidence=[f"Pod terminated with phase {phase}"],
                probable_cause="All containers in the pod have terminated, and at least one container has terminated in failure.",
                suggested_next_steps=["Inspect previous logs using get_pod_previous_logs."],
            ))

        # Check containers
        for cs in (pod.status.container_statuses or []):
            if cs.state and cs.state.waiting:
                reason = cs.state.waiting.reason or "Waiting"
                if reason in ("CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull"):
                    status = "failing"
                    findings.append(Finding(
                        severity="critical",
                        title=f"Container '{cs.name}' in {reason}",
                        evidence=[f"Waiting reason: {reason}", f"Restart count: {cs.restart_count}"],
                        probable_cause="Container repeatedly crashing or image failed to pull.",
                        suggested_next_steps=[
                            f"Run diagnose_{'crashloop' if 'Crash' in reason else 'image_pull'} on container '{cs.name}'."
                        ],
                    ))

        return DiagnosisReport(
            target=target,
            status=status,
            findings=findings,
            checked=checked,
            truncated=False,
        ).model_dump()
    except Exception as exc:
        return DiagnosisReport(
            target=target,
            status="unknown",
            findings=[Finding(
                severity="warning",
                title="Failed to inspect pod",
                evidence=[str(exc)],
                probable_cause="Pod not found or API communication error.",
                suggested_next_steps=["Verify pod name and namespace spelling."],
            )],
            checked=checked,
        ).model_dump()


async def diagnose_crashloop(name: str, namespace: str, container: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose CrashLoopBackOff: exit code, OOMKilled, restart timing, previous logs tail, memory limits."""
    validate_dns_subdomain(name, "pod")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="Pod", name=name, namespace=ns, cluster=cluster or "default")
    checked = ["container_lastState", "exit_code", "restart_count", "previous_logs", "memory_limits"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        pod = await run_k8s_call(core_api.read_namespaced_pod, name=name, namespace=ns)
        statuses = pod.status.container_statuses or []
        target_cs = next((c for c in statuses if c.name == container), statuses[0] if statuses else None)

        if not target_cs:
            return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()

        last_state = target_cs.last_state.terminated if (target_cs.last_state and target_cs.last_state.terminated) else None

        if target_cs.restart_count > 0:
            status = "failing"
            exit_code = last_state.exit_code if last_state else None
            term_reason = last_state.reason if last_state else "CrashLoopBackOff"
            analysis = analyze_exit_code(exit_code, term_reason)

            findings.append(Finding(
                severity="critical",
                title=f"Container '{target_cs.name}' Crashing ({analysis['title']})",
                evidence=[
                    f"Restart count: {target_cs.restart_count}",
                    f"Last termination reason: {term_reason}",
                    f"Last exit code: {exit_code}",
                    analysis["description"],
                ],
                probable_cause=analysis["probable_cause"],
                suggested_next_steps=[
                    "Increase container memory limit if exit code 137 (OOMKilled)",
                    "Check previous container logs with analyze_container_logs",
                    "Verify application startup dependencies and database connections",
                ],
            ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(
            target=target,
            status="unknown",
            findings=[Finding(severity="warning", title="Inspection Error", evidence=[str(exc)], probable_cause="Kubernetes API error", suggested_next_steps=[])],
            checked=checked,
        ).model_dump()


async def diagnose_image_pull(name: str, namespace: str, container: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose ImagePullBackOff / ErrImagePull: registry errors, auth failures, imagePullSecrets, tags."""
    validate_dns_subdomain(name, "pod")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="Pod", name=name, namespace=ns, cluster=cluster or "default")
    checked = ["events", "image_tag", "image_pull_secrets", "container_spec"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        events = await run_k8s_call(core_api.list_namespaced_event, namespace=ns, field_selector=f"involvedObject.name={name}", limit=25)
        pod = await run_k8s_call(core_api.read_namespaced_pod, name=name, namespace=ns)

        # Names of imagePullSecrets only (never contents)
        secrets = [s.name for s in (pod.spec.image_pull_secrets or [])]

        pull_errors = [
            ev.message for ev in getattr(events, "items", [])
            if "Failed" in ev.reason or "BackOff" in ev.reason or "InspectFailed" in ev.reason
        ]

        if pull_errors:
            status = "failing"
            first_err = pull_errors[0]
            probable_cause = "Invalid image tag, repository not found, or authentication failed."
            if "unauthorized" in first_err.lower() or "denied" in first_err.lower():
                probable_cause = "Container registry authentication failed (imagePullSecrets missing or invalid)."

            findings.append(Finding(
                severity="critical",
                title="Container Image Pull Failure",
                evidence=[redact_text(first_err), f"imagePullSecrets configured: {secrets or 'None'}"],
                probable_cause=probable_cause,
                suggested_next_steps=[
                    "Verify image tag exists in container registry",
                    "Verify imagePullSecrets exists in target namespace and has registry access",
                ],
            ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()


async def diagnose_pending_pod(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose scheduler bottlenecks: FailedScheduling, insufficient cpu/memory, taints vs tolerations, PVCs."""
    validate_dns_subdomain(name, "pod")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="Pod", name=name, namespace=ns, cluster=cluster or "default")
    checked = ["scheduler_events", "node_selector", "tolerations", "pvc_bindings"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        events = await run_k8s_call(core_api.list_namespaced_event, namespace=ns, field_selector=f"involvedObject.name={name}", limit=25)
        sched_events = [ev for ev in getattr(events, "items", []) if ev.reason == "FailedScheduling"]

        if sched_events:
            status = "failing"
            msg = sched_events[0].message or ""
            parsed = parse_scheduling_failure(msg)

            findings.append(Finding(
                severity="critical",
                title="Scheduler Failed to Place Pod",
                evidence=[redact_text(msg)],
                probable_cause=parsed["probable_cause"],
                suggested_next_steps=parsed["suggested_steps"],
            ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()


async def diagnose_deployment(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose rollout status, unavailable replicas, ReplicaSet history, progressDeadlineExceeded."""
    validate_dns_subdomain(name, "deployment")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    apps_api = clients["apps_v1"]

    target = TargetResource(kind="Deployment", name=name, namespace=ns, cluster=cluster or "default")
    checked = ["rollout_status", "replica_counts", "conditions", "replicasets"]
    findings: List[Finding] = []
    status = "healthy"

    try:
        d = await run_k8s_call(apps_api.read_namespaced_deployment, name=name, namespace=ns)
        desired = d.spec.replicas or 0
        ready = d.status.ready_replicas or 0
        unavailable = d.status.unavailable_replicas or 0

        if unavailable > 0 or ready < desired:
            status = "degraded" if ready > 0 else "failing"
            findings.append(Finding(
                severity="critical" if ready == 0 else "warning",
                title=f"Deployment Replicas Degraded ({ready}/{desired} ready)",
                evidence=[f"Desired: {desired}", f"Ready: {ready}", f"Unavailable: {unavailable}"],
                probable_cause="Underlying pods are failing health probes, crashing, or unable to be scheduled.",
                suggested_next_steps=[
                    f"List pods with label selector to identify failing replicas: list_pods(namespace='{ns}')",
                    "Check rollout conditions for ProgressDeadlineExceeded",
                ],
            ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()


async def analyze_pod_events(name: str, namespace: str, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Correlate and group pod events by reason and time, reconstruct causal chain, and dedupe repeats."""
    validate_dns_subdomain(name, "pod")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="Pod", name=name, namespace=ns, cluster=cluster or "default")
    checked = ["event_history", "causal_transitions", "warnings"]

    try:
        events = await run_k8s_call(core_api.list_namespaced_event, namespace=ns, field_selector=f"involvedObject.name={name}", limit=100)
        raw = [
            {
                "reason": ev.reason,
                "type": ev.type,
                "message": ev.message,
                "count": ev.count,
                "first_timestamp": str(ev.first_timestamp),
                "last_timestamp": str(ev.last_timestamp),
            }
            for ev in getattr(events, "items", [])
        ]
        correlated = correlate_events(raw)

        has_warning = any(ev.get("type") == "Warning" for ev in raw)
        status = "degraded" if has_warning else "healthy"

        findings = []
        if correlated.get("causal_sequence"):
            findings.append(Finding(
                severity="warning" if has_warning else "info",
                title=f"Causal Event Sequence: {correlated['causal_sequence']}",
                evidence=[f"Total unique events: {correlated['unique_event_types']}"],
                probable_cause="State transitions recorded by kubelet and kube-scheduler.",
                suggested_next_steps=["Correlate timestamps with deployment rollouts or infrastructure maintenance."],
            ))

        return DiagnosisReport(
            target=target,
            status=status,
            findings=findings,
            checked=checked,
            truncated=False,
        ).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()


async def analyze_container_logs(
    name: str,
    namespace: str,
    container: Optional[str] = None,
    previous: bool = False,
    tail_lines: int = 500,
    cluster: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch log tail, detect exceptions, error rate, repeated messages, OOM, timeouts, DNS failures, panic/fatal."""
    validate_dns_subdomain(name, "pod")
    ns = validate_namespace_access(namespace) or "default"
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="Pod", name=name, namespace=ns, cluster=cluster or "default")
    checked = ["exceptions", "error_rate", "network_timeouts", "auth_failures", "panics"]

    try:
        kwargs: Dict[str, Any] = {"tail_lines": min(tail_lines, 5000), "timestamps": False}
        if container:
            kwargs["container"] = container
        if previous:
            kwargs["previous"] = True

        log_raw = await run_k8s_call(core_api.read_namespaced_pod_log, name=name, namespace=ns, **kwargs)
        lines = (log_raw or "").splitlines()
        analysis = analyze_log_content(lines)

        findings: List[Finding] = []
        status = "healthy"
        if analysis["error_lines_detected"] > 0:
            status = "degraded" if analysis["error_rate"] < 0.20 else "failing"
            for pat in analysis["top_patterns"]:
                findings.append(Finding(
                    severity="critical" if "Panic" in pat["pattern"] or "OOM" in pat["pattern"] else "warning",
                    title=f"Pattern: {pat['pattern']} ({pat['count']} occurrences)",
                    evidence=pat["sample_lines"],
                    probable_cause="Repeated runtime exceptions or external dependency failures logged by container process.",
                    suggested_next_steps=["Investigate downstream services or inspect stack trace evidence."],
                ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()


async def check_pod_restarts(namespace: Optional[str] = None, cluster: Optional[str] = None) -> Dict[str, Any]:
    """Rank pods across namespace by restart count and recent restart rate, including last termination reason."""
    ns = validate_namespace_access(namespace)
    clients = get_k8s_clients(cluster)
    core_api = clients["core_v1"]

    target = TargetResource(kind="Namespace", name=ns or "cluster-wide", namespace=ns, cluster=cluster or "default")
    checked = ["restart_counts", "last_termination_reasons"]

    try:
        if ns:
            pods = await run_k8s_call(core_api.list_namespaced_pod, namespace=ns)
        else:
            pods = await run_k8s_call(core_api.list_pod_for_all_namespaces)

        ranked = []
        for p in getattr(pods, "items", []):
            statuses = p.status.container_statuses or []
            total_restarts = sum(cs.restart_count for cs in statuses)
            if total_restarts > 0:
                last_reasons = [
                    f"{cs.name}: {cs.last_state.terminated.reason} (code {cs.last_state.terminated.exit_code})"
                    for cs in statuses
                    if cs.last_state and cs.last_state.terminated
                ]
                ranked.append({
                    "pod": p.metadata.name,
                    "namespace": p.metadata.namespace,
                    "restarts": total_restarts,
                    "reasons": last_reasons,
                })

        ranked.sort(key=lambda x: x["restarts"], reverse=True)
        status = "degraded" if ranked else "healthy"

        findings = []
        if ranked:
            top_offender = ranked[0]
            findings.append(Finding(
                severity="warning",
                title=f"Top Restarting Pod: {top_offender['pod']} ({top_offender['restarts']} restarts)",
                evidence=top_offender["reasons"],
                probable_cause="Recurring crashes or health probe failures.",
                suggested_next_steps=[f"Run diagnose_crashloop on pod '{top_offender['pod']}'"],
            ))

        return DiagnosisReport(target=target, status=status, findings=findings, checked=checked).model_dump()
    except Exception as exc:
        return DiagnosisReport(target=target, status="unknown", checked=checked).model_dump()

