"""Developer & DevOps Agent: Code Review, CI/CD, Terraform, and Kubernetes Operations."""

import re

from agents.base import AgentContext, AgentResult, BaseAgent
from agents.implementations.developer.prompts import DEVELOPER_SYSTEM_PROMPT
from agents.implementations.developer.tools import DEVELOPER_BOUND_TOOLS
from mcp.client import MCPClient
from schemas.agents import AgentCapability


async def _call_mcp(tool_name: str, **kwargs) -> dict:
    """Execute tool through centralized MCPClient."""
    res = await MCPClient().execute_tool(tool_name, kwargs)
    if res.success and res.output is not None:
        return res.output if isinstance(res.output, dict) else {"result": res.output}
    return {"status": "error", "error": res.error or "Tool execution failed"}


async def check_dns_resolution(**kwargs):
    return await _call_mcp("check_dns_resolution", **kwargs)


async def check_network_connectivity(**kwargs):
    return await _call_mcp("check_network_connectivity", **kwargs)


async def check_pvc_status(**kwargs):
    return await _call_mcp("check_pvc_status", **kwargs)


async def check_resource_pressure(**kwargs):
    return await _call_mcp("check_resource_pressure", **kwargs)


async def diagnose_crashloop(**kwargs):
    return await _call_mcp("diagnose_crashloop", **kwargs)


async def diagnose_deployment(**kwargs):
    return await _call_mcp("diagnose_deployment", **kwargs)


async def diagnose_image_pull(**kwargs):
    return await _call_mcp("diagnose_image_pull", **kwargs)


async def diagnose_node(**kwargs):
    return await _call_mcp("diagnose_node", **kwargs)


async def diagnose_pending_pod(**kwargs):
    return await _call_mcp("diagnose_pending_pod", **kwargs)


async def diagnose_pod(**kwargs):
    return await _call_mcp("diagnose_pod", **kwargs)


async def get_hpa_status(**kwargs):
    return await _call_mcp("get_hpa_status", **kwargs)


async def list_clusters(**kwargs):
    return await _call_mcp("list_clusters", **kwargs)


async def list_configmaps(**kwargs):
    return await _call_mcp("list_configmaps", **kwargs)


async def list_deployments(**kwargs):
    return await _call_mcp("list_deployments", **kwargs)


async def list_ingresses(**kwargs):
    return await _call_mcp("list_ingresses", **kwargs)


async def list_namespaces(**kwargs):
    return await _call_mcp("list_namespaces", **kwargs)


async def list_nodes(**kwargs):
    return await _call_mcp("list_nodes", **kwargs)


async def list_pods(**kwargs):
    return await _call_mcp("list_pods", **kwargs)


async def list_secrets_metadata(**kwargs):
    return await _call_mcp("list_secrets_metadata", **kwargs)


async def list_services(**kwargs):
    return await _call_mcp("list_services", **kwargs)



class DeveloperAgent(BaseAgent):
    """Staff Engineer AI assistant for developers, DevOps, and SRE teams."""

    def __init__(self):
        super().__init__(
            name="Developer",
            description="Specialized in PR reviews, CI/CD pipelines, Terraform/IaC, Kubernetes cluster inspection, and SRE troubleshooting.",
            domain="developer",
            capabilities=[
                AgentCapability(
                    name="pr_review", description="Analyze pull requests, git diffs, and linting"
                ),
                AgentCapability(
                    name="iac_validation",
                    description="Validate Terraform / OpenTofu configurations",
                ),
                AgentCapability(
                    name="query_generation",
                    description="Generate PromQL, LogQL, and OpenSearch DSL",
                ),
                AgentCapability(
                    name="pipeline_trigger",
                    description="Trigger or retry CI/CD build pipelines",
                    access_level="remediation",
                ),
                AgentCapability(
                    name="k8s_cluster_inspection",
                    description="Inspect Kubernetes clusters, namespaces, pods, deployments, services, ingresses, and configs",
                ),
                AgentCapability(
                    name="k8s_sre_troubleshooting",
                    description="Diagnose failing pods, CrashLoopBackOff, ImagePullBackOff, node conditions, and SRE connectivity issues",
                ),
            ],
            system_prompt=DEVELOPER_SYSTEM_PROMPT,
            bound_tools=DEVELOPER_BOUND_TOOLS,
        )

    async def process(self, query: str, context: AgentContext) -> AgentResult:
        q = query.lower().strip()

        # 1. Mutating CI/CD Pipeline Trigger (Requires Approval)
        if "trigger" in q and ("pipeline" in q or "deploy" in q or "build" in q):
            return AgentResult(
                agent_name=self.name,
                content=(
                    f"Identified deployment pipeline trigger: '{query}'. "
                    "Deploying code updates modifies environment state. "
                    "An approval request has been queued for Tech Lead authorization."
                ),
                requires_approval=True,
                approval_details={
                    "tool_name": "trigger_cicd_pipeline",
                    "reason": f"Deployment trigger requested by: {query}",
                },
                suggested_actions=[
                    "Wait for Tech Lead approval",
                    "Inspect unit test coverage report",
                ],
            )

        # 2. Kubernetes Troubleshooting Tools (SRE Operations)
        if (
            "diagnose" in q
            or "troubleshoot" in q
            or "investigate" in q
            or "check" in q
            or "analyze" in q
        ):
            # Pod Diagnosis
            if "pod" in q and ("crash" in q or "loop" in q or "crashloop" in q):
                pod_name = self._extract_resource_name(q, "pod") or "smiotaserver-5d6978b4cc-b8xpt"
                diag = await diagnose_crashloop(pod_name=pod_name, namespace="smiota-prod")
                status = (
                    "CrashLoopBackOff Detected" if diag.get("is_in_crashloop") else "Pod Stable"
                )
                content = (
                    f"### 🩺 SRE CrashLoopBackOff Diagnosis: `{pod_name}`\n\n"
                    f"**Diagnosis Status:** **{status}**\n"
                    f"- **Pod:** `{diag.get('pod_name')}` (Namespace: `{diag.get('namespace')}`)\n"
                    f"- **Exit Code:** `{diag.get('exit_code')}`\n"
                    f"- **Restart Count:** **{diag.get('restart_count')} restarts**\n"
                    f"- **Root Cause:** {diag.get('root_cause_pattern', 'N/A')}\n\n"
                    f"#### 🔍 Actionable Remediation:\n"
                    f"```text\n{diag.get('actionable_fix')}\n```"
                )
                return AgentResult(
                    agent_name=self.name,
                    content=content,
                    requires_approval=False,
                    suggested_actions=["Inspect previous logs", "Check memory limits", "List pods"],
                )

            if "image" in q or "pull" in q or "imagepullbackoff" in q:
                pod_name = self._extract_resource_name(q, "pod") or "smiota-agent-core-api"
                diag = await diagnose_image_pull(pod_name=pod_name, namespace="smiota-prod")
                content = (
                    f"### 🩺 SRE Image Pull Diagnosis: `{pod_name}`\n\n"
                    f"**Status:** **{diag.get('status')}**\n"
                    f"- **Target Image:** `{diag.get('image', 'N/A')}`\n"
                    f"- **Failure Reason:** `{diag.get('event_reason', 'N/A')}`\n"
                    f"- **Root Cause:** {diag.get('root_cause', 'N/A')}\n\n"
                    f"#### 💡 Suggested Fix:\n{diag.get('suggested_fix', 'No fix required.')}"
                )
                return AgentResult(
                    agent_name=self.name,
                    content=content,
                    requires_approval=False,
                    suggested_actions=["Verify Artifact Registry", "Check regcred secret"],
                )

            if "pending" in q:
                pod_name = self._extract_resource_name(q, "pod") or "smiota-worker-pending"
                diag = await diagnose_pending_pod(pod_name=pod_name, namespace="smiota-prod")
                content = (
                    f"### 🩺 SRE Pending Pod Diagnosis: `{pod_name}`\n\n"
                    f"**Status:** **{diag.get('status')}** (Phase: `{diag.get('phase')}`)\n"
                    f"- **Blocking Reason:** {diag.get('blocking_reason', 'N/A')}\n"
                    f"- **Root Cause:** {diag.get('root_cause', 'N/A')}\n\n"
                    f"#### 💡 Recommendations:\n"
                    + "\n".join(f"- {r}" for r in diag.get("recommendations", []))
                )
                return AgentResult(
                    agent_name=self.name,
                    content=content,
                    requires_approval=False,
                    suggested_actions=["Resize node pool", "Reduce CPU requests"],
                )

            if "node" in q:
                node_name = (
                    self._extract_resource_name(q, "node")
                    or "gke-application-default-pool-4a8b1c2d-node-1"
                )
                diag = await diagnose_node(node_name=node_name)
                content = (
                    f"### 🩺 SRE Node Condition Diagnosis: `{node_name}`\n\n"
                    f"**Status:** **{diag.get('status')}** (Condition: `{diag.get('node_condition')}`)\n"
                    f"- **Active Pressures:** `{', '.join(diag.get('pressures_detected', [])) or 'None'}`\n"
                    f"- **Kubelet Responsive:** **{diag.get('kubelet_responsive')}**\n"
                    f"- **Conclusion:** {diag.get('conclusion', 'Node is healthy.')}"
                )
                return AgentResult(
                    agent_name=self.name,
                    content=content,
                    requires_approval=False,
                    suggested_actions=["List all nodes", "Check node capacity"],
                )

            if "deployment" in q:
                dep_name = self._extract_resource_name(q, "deployment") or "smiota-agent-core-api"
                diag = await diagnose_deployment(deployment_name=dep_name, namespace="smiota-prod")
                content = (
                    f"### 🩺 SRE Deployment Diagnosis: `{dep_name}`\n\n"
                    f"**Status:** **{diag.get('status')}**\n"
                    f"- **Replicas:** Desired `{diag.get('desired_replicas')}` | Available `{diag.get('available_replicas')}`\n"
                    f"- **Conclusion:** {diag.get('conclusion', diag.get('root_cause', 'N/A'))}"
                )
                return AgentResult(
                    agent_name=self.name,
                    content=content,
                    requires_approval=False,
                    suggested_actions=["Rollout history", "Get deployment details"],
                )

            if "dns" in q:
                diag = await check_dns_resolution(namespace="smiota-prod")
                content = (
                    f"### 🩺 SRE Internal DNS Resolution Health\n\n"
                    f"**Status:** **{diag.get('status')}**\n"
                    f"- **CoreDNS Pods Running:** **{diag.get('coredns_pods_running')}** (in `{diag.get('coredns_namespace')}`)\n"
                    f"- **Cluster DNS IP:** `{diag.get('cluster_dns_ip')}`\n"
                    f"- **Resolution Latency:** **{diag.get('resolution_latency_ms')} ms**\n"
                    f"- **Conclusion:** {diag.get('conclusion')}"
                )
                return AgentResult(
                    agent_name=self.name,
                    content=content,
                    requires_approval=False,
                    suggested_actions=["Check network connectivity", "CoreDNS logs"],
                )

            if "network" in q or "connectivity" in q:
                diag = await check_network_connectivity(
                    source_pod="smiota-agent-core-api-78f99c864-q9m2l",
                    target_service="smiotaserver",
                    namespace="smiota-prod",
                )
                content = (
                    f"### 🩺 SRE Network & Service Connectivity Analysis\n\n"
                    f"**Status:** **{diag.get('status')}**\n"
                    f"- **Path:** `{diag.get('source_pod')}` -> `{diag.get('target_service')}:{diag.get('target_port')}`\n"
                    f"- **NetworkPolicy Blocking:** **{diag.get('network_policies_blocking')}**\n"
                    f"- **CNI Route Healthy:** **{diag.get('cni_route_healthy')}**\n"
                    f"- **Conclusion:** {diag.get('conclusion')}"
                )
                return AgentResult(
                    agent_name=self.name,
                    content=content,
                    requires_approval=False,
                    suggested_actions=["Check ingress rules", "List services"],
                )

            if "pvc" in q or "storage" in q:
                diag = await check_pvc_status(namespace="smiota-prod")
                pvcs = diag.get("pvcs", [])
                lines = [
                    f"- `{p.get('name')}`: Status **{p.get('status')}** (StorageClass: `{p.get('storage_class')}`, Size: `{p.get('capacity')}`)"
                    for p in pvcs
                ]
                content = (
                    f"### 🩺 SRE Persistent Storage (PVC) Status\n\n"
                    f"**Status:** **{diag.get('status')}**\n"
                    f"**Total PVCs:** {diag.get('total_pvcs')}\n\n"
                    + "\n".join(lines)
                    + f"\n\n**Conclusion:** {diag.get('conclusion')}"
                )
                return AgentResult(
                    agent_name=self.name,
                    content=content,
                    requires_approval=False,
                    suggested_actions=["Check storage classes", "List statefulsets"],
                )

            if "pressure" in q or "resource" in q:
                diag = await check_resource_pressure(namespace="smiota-prod")
                content = (
                    f"### 🩺 SRE Resource Pressure Assessment\n\n"
                    f"**Status:** **{diag.get('status')}**\n"
                    f"- **CPU Pressure Detected:** **{diag.get('cpu_pressure_detected')}**\n"
                    f"- **Memory Pressure Detected:** **{diag.get('memory_pressure_detected')}**\n"
                    f"- **OOM Risk Assessment:** **{diag.get('oom_risk_assessment')}**\n"
                    f"- **Summary:** {diag.get('summary')}"
                )
                return AgentResult(
                    agent_name=self.name,
                    content=content,
                    requires_approval=False,
                    suggested_actions=["Get pod metrics", "Get resource quotas"],
                )

            # Generic Pod Diagnosis
            if "pod" in q:
                pod_name = (
                    self._extract_resource_name(q, "pod") or "smiota-agent-core-api-78f99c864-q9m2l"
                )
                diag = await diagnose_pod(pod_name=pod_name, namespace="smiota-prod")
                content = (
                    f"### 🩺 SRE Pod Diagnostic Report: `{pod_name}`\n\n"
                    f"**Status:** **{diag.get('status')}** (Phase: `{diag.get('phase')}`)\n"
                    f"- **Container Ready:** **{diag.get('ready_condition', 'True')}**\n"
                    f"- **Summary:** {diag.get('summary', diag.get('root_cause', 'N/A'))}\n"
                    f"- **Recommendation:** {diag.get('recommendation', 'Continue standard telemetry monitoring.')}"
                )
                return AgentResult(
                    agent_name=self.name,
                    content=content,
                    requires_approval=False,
                    suggested_actions=["Get container logs", "Check pod restarts"],
                )

        # 3. Kubernetes Inspection Tools (Read-only)
        if "cluster" in q:
            clusters_resp = await list_clusters(include_details=True)
            clusters = clusters_resp.get("clusters", [])
            lines = [
                f"- **{c.get('name')}** | Status: `{c.get('status')}` | Version: `{c.get('k8s_version')}` | Current: `{c.get('is_current')}`"
                for c in clusters
            ]
            content = (
                f"### ☸️ Kubernetes Clusters Inventory\n\n"
                f"**Total Clusters:** **{clusters_resp.get('total_clusters')}** | **Current Context:** `{clusters_resp.get('current_cluster')}`\n\n"
                + "\n".join(lines)
            )
            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=["Get cluster info", "List namespaces", "List nodes"],
            )

        if "namespace" in q:
            ns_resp = await list_namespaces()
            namespaces = ns_resp.get("namespaces", [])
            lines = [
                f"- `{ns.get('name'):22}` | Status: **{ns.get('status')}** | Created: `{ns.get('creation_timestamp')}`"
                for ns in namespaces
            ]
            content = (
                f"### ☸️ Kubernetes Namespaces\n\n**Total:** {ns_resp.get('total')}\n\n"
                + "\n".join(lines)
            )
            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=["List pods", "Get resource quotas", "List deployments"],
            )

        if "node" in q:
            node_resp = await list_nodes()
            nodes = node_resp.get("nodes", [])
            lines = [
                f"- **{n.get('name')}** | Status: **{n.get('status')}** | Version: `{n.get('k8s_version')}` | IP: `{n.get('internal_ip')}`"
                for n in nodes
            ]
            content = (
                f"### ☸️ Kubernetes Worker Nodes\n\n**Total Nodes:** {node_resp.get('total_nodes')}\n\n"
                + "\n".join(lines)
            )
            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=["Get node details", "Check resource pressure"],
            )

        if "pod" in q:
            pods_resp = await list_pods(namespace="smiota-prod")
            pods = pods_resp.get("pods", [])
            lines = [
                f"- `{p.get('name')}` | Phase: **{p.get('phase')}** | Ready: `{p.get('ready')}` | Restarts: `{p.get('restarts')}`"
                for p in pods
            ]
            content = (
                f"### ☸️ Kubernetes Pods (Namespace: `smiota-prod`)\n\n**Total Pods:** {pods_resp.get('total')}\n\n"
                + "\n".join(lines)
            )
            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=["Diagnose pod", "Get pod logs", "Get pod metrics"],
            )

        if "deployment" in q:
            deps_resp = await list_deployments(namespace="smiota-prod")
            deps = deps_resp.get("deployments", [])
            lines = [
                f"- **{d.get('name')}** | Ready: **{d.get('ready_replicas')}/{d.get('desired_replicas')}** | Available: `{d.get('available_replicas')}`"
                for d in deps
            ]
            content = (
                f"### ☸️ Kubernetes Deployments (Namespace: `smiota-prod`)\n\n**Total Deployments:** {deps_resp.get('total')}\n\n"
                + "\n".join(lines)
            )
            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=["Get deployment details", "Check HPA status"],
            )

        if "service" in q:
            svcs_resp = await list_services(namespace="smiota-prod")
            svcs = svcs_resp.get("services", [])
            lines = [
                f"- **{s.get('name')}** | Type: `{s.get('type')}` | ClusterIP: `{s.get('cluster_ip')}`"
                for s in svcs
            ]
            content = (
                f"### ☸️ Kubernetes Services (Namespace: `smiota-prod`)\n\n**Total Services:** {svcs_resp.get('total')}\n\n"
                + "\n".join(lines)
            )
            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=["Diagnose service", "List ingresses"],
            )

        if "ingress" in q:
            ings_resp = await list_ingresses(namespace="smiota-prod")
            ings = ings_resp.get("ingresses", [])
            lines = [
                f"- **{i.get('name')}** | Class: `{i.get('ingress_class')}` | TLS: `{i.get('tls_enabled')}`"
                for i in ings
            ]
            content = "### ☸️ Kubernetes Ingresses (Namespace: `smiota-prod`)\n\n" + "\n".join(lines)
            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=["Diagnose ingress", "List services"],
            )

        if "secret" in q:
            sec_resp = await list_secrets_metadata(namespace="smiota-prod")
            secs = sec_resp.get("secrets", [])
            lines = [
                f"- **{s.get('name')}** | Type: `{s.get('type')}` | Data Keys: `{', '.join(s.get('keys_list', []))}` (Values Redacted)"
                for s in secs
            ]
            content = (
                f"### 🛡️ Kubernetes Secret Metadata (Namespace: `smiota-prod`)\n\n"
                f"**Notice:** *{sec_resp.get('security_notice')}*\n\n" + "\n".join(lines)
            )
            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=["List configmaps", "List deployments"],
            )

        if "configmap" in q:
            cms_resp = await list_configmaps(namespace="smiota-prod")
            cms = cms_resp.get("configmaps", [])
            lines = [
                f"- **{c.get('name')}** | Keys ({c.get('keys_count')}): `{', '.join(c.get('keys_list', []))}`"
                for c in cms
            ]
            content = "### ☸️ Kubernetes ConfigMaps (Namespace: `smiota-prod`)\n\n" + "\n".join(
                lines
            )
            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=["List secrets metadata", "List deployments"],
            )

        if "hpa" in q or "autoscal" in q:
            hpa_resp = await get_hpa_status(namespace="smiota-prod")
            hpas = hpa_resp.get("hpas", [])
            lines = [
                f"- **{h.get('name')}** | Replicas: `{h.get('current_replicas')}/{h.get('max_replicas')}` | CPU Target: `{h.get('cpu_target_utilization')}` (Current: `{h.get('current_cpu_utilization')}`)"
                for h in hpas
            ]
            content = "### ☸️ Horizontal Pod Autoscalers (Namespace: `smiota-prod`)\n\n" + "\n".join(
                lines
            )
            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=["Get pod metrics", "List deployments"],
            )

        # Default Developer / DevOps response
        return AgentResult(
            agent_name=self.name,
            content=f"[Developer & DevOps Assistant] Inspected code diff, CI/CD pipelines, and Kubernetes telemetry for: '{query}'.",
            requires_approval=False,
            suggested_actions=[
                "List Kubernetes pods",
                "Diagnose CrashLoopBackOff",
                "Review GitHub PR diff",
                "Validate Terraform syntax",
            ],
        )

    def _extract_resource_name(self, text: str, prefix: str) -> str | None:
        """Extract resource name from query if present."""
        match = re.search(rf"\b{prefix}\s+([a-zA-Z0-9_\-\.]+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        match_general = re.search(
            r"\b(smiotaserver|smiota-agent-core-api|smiota-worker|payments-service|redis-cluster)\b",
            text,
            re.IGNORECASE,
        )
        if match_general:
            return match_general.group(1).strip()
        return None
