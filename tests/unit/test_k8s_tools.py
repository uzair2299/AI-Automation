"""Unit tests for Kubernetes Inspection and SRE Troubleshooting MCP Tools."""

# Ensure DevOps and Kubernetes MCP tools are loaded
import smiota.mcp.servers.devops.tools  # noqa: F401
from smiota.agents import register_default_agents
from smiota.agents.base import AgentContext
from smiota.agents.registry import AgentRegistry
from smiota.agents.routing.rules import RuleBasedRouter
from smiota.mcp.registry import MCPToolRegistry
from smiota.mcp.servers.devops.k8s_tools import (
    analyze_container_logs,
    analyze_pod_events,
    check_dns_resolution,
    check_network_connectivity,
    check_pod_restarts,
    check_pvc_status,
    check_resource_pressure,
    diagnose_crashloop,
    diagnose_deployment,
    diagnose_image_pull,
    diagnose_ingress,
    diagnose_node,
    diagnose_pending_pod,
    diagnose_pod,
    diagnose_service,
    get_cluster_info,
    get_deployment_details,
    get_hpa_status,
    get_namespace,
    get_node_details,
    get_pod_details,
    get_pod_logs,
    get_pod_metrics,
    get_pod_previous_logs,
    get_resource_quotas,
    list_clusters,
    list_configmaps,
    list_daemonsets,
    list_deployments,
    list_events,
    list_ingresses,
    list_namespaces,
    list_nodes,
    list_pods,
    list_secrets_metadata,
    list_services,
    list_statefulsets,
)
from smiota.schemas.mcp import ToolAccessLevel


def run_coro(coro):
    """Run an async coroutine synchronously to ensure fast execution."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value
    raise RuntimeError("Coroutine did not complete synchronously")


K8S_INSPECTION_TOOLS = [
    "list_clusters",
    "get_cluster_info",
    "list_namespaces",
    "get_namespace",
    "list_nodes",
    "get_node_details",
    "list_pods",
    "get_pod_details",
    "get_pod_logs",
    "get_pod_previous_logs",
    "list_deployments",
    "get_deployment_details",
    "list_statefulsets",
    "list_daemonsets",
    "list_services",
    "list_ingresses",
    "list_configmaps",
    "list_secrets_metadata",
    "list_events",
    "get_pod_metrics",
    "get_resource_quotas",
    "get_hpa_status",
]

K8S_TROUBLESHOOTING_TOOLS = [
    "diagnose_pod",
    "diagnose_crashloop",
    "diagnose_image_pull",
    "diagnose_pending_pod",
    "diagnose_node",
    "diagnose_deployment",
    "diagnose_service",
    "diagnose_ingress",
    "analyze_pod_events",
    "analyze_container_logs",
    "check_pod_restarts",
    "check_resource_pressure",
    "check_pvc_status",
    "check_dns_resolution",
    "check_network_connectivity",
]

ALL_K8S_TOOLS = K8S_INSPECTION_TOOLS + K8S_TROUBLESHOOTING_TOOLS


def test_all_37_k8s_tools_registered_in_mcp_registry():
    """Verify all 37 Kubernetes and SRE tools are registered in central registry with READ_ONLY access."""
    registered = {t.name: t for t in MCPToolRegistry.list_tools()}
    for tool_name in ALL_K8S_TOOLS:
        assert tool_name in registered, f"Tool '{tool_name}' missing from MCPToolRegistry"
        definition = registered[tool_name]
        assert definition.access_level == ToolAccessLevel.READ_ONLY, (
            f"Tool '{tool_name}' access level must be READ_ONLY, got {definition.access_level}"
        )


def test_k8s_inspection_tools_execution():
    """Verify all 22 Kubernetes inspection tools execute cleanly and return valid structure."""
    # 1. list_clusters
    res = run_coro(list_clusters())
    assert res["status"] == "success"
    assert res["total_clusters"] >= 1

    # 2. get_cluster_info
    res = run_coro(get_cluster_info())
    assert res["status"] == "success"
    assert "git_version" in res

    # 3. list_namespaces
    res = run_coro(list_namespaces())
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 4. get_namespace
    res = run_coro(get_namespace(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["name"] == "smiota-prod"

    # 5. list_nodes
    res = run_coro(list_nodes())
    assert res["status"] == "success"
    assert res["total_nodes"] >= 1

    # 6. get_node_details
    res = run_coro(get_node_details(node_name="gke-application-default-pool-4a8b1c2d-node-1"))
    assert res["status"] == "success"
    assert "conditions" in res
    assert res["conditions"]["Ready"] == "True"

    # 7. list_pods
    res = run_coro(list_pods(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 8. get_pod_details
    res = run_coro(
        get_pod_details(pod_name="smiota-agent-core-api-78f99c864-q9m2l", namespace="smiota-prod")
    )
    assert res["status"] == "success"
    assert res["name"] == "smiota-agent-core-api-78f99c864-q9m2l"

    # 9. get_pod_logs
    res = run_coro(
        get_pod_logs(pod_name="smiota-agent-core-api-78f99c864-q9m2l", namespace="smiota-prod")
    )
    assert res["status"] == "success"
    assert "logs" in res

    # 10. get_pod_previous_logs
    res = run_coro(
        get_pod_previous_logs(pod_name="smiotaserver-5d6978b4cc-b8xpt", namespace="smiota-prod")
    )
    assert res["status"] == "success"
    assert "previous_logs" in res

    # 11. list_deployments
    res = run_coro(list_deployments(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 12. get_deployment_details
    res = run_coro(
        get_deployment_details(deployment_name="smiota-agent-core-api", namespace="smiota-prod")
    )
    assert res["status"] == "success"
    assert res["name"] == "smiota-agent-core-api"

    # 13. list_statefulsets
    res = run_coro(list_statefulsets(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 14. list_daemonsets
    res = run_coro(list_daemonsets(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 15. list_services
    res = run_coro(list_services(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 16. list_ingresses
    res = run_coro(list_ingresses(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 17. list_configmaps
    res = run_coro(list_configmaps(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 18. list_secrets_metadata
    res = run_coro(list_secrets_metadata(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 19. list_events
    res = run_coro(list_events(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 20. get_pod_metrics
    res = run_coro(get_pod_metrics(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 21. get_resource_quotas
    res = run_coro(get_resource_quotas(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1

    # 22. get_hpa_status
    res = run_coro(get_hpa_status(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["total"] >= 1


def test_secrets_metadata_security_never_exposes_values():
    """CRITICAL SECURITY TEST: Ensure list_secrets_metadata NEVER exposes secret values."""
    res = run_coro(list_secrets_metadata(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert "security_notice" in res
    assert "redacted" in res["security_notice"].lower()

    for secret in res["secrets"]:
        # 1. No secret content dictionaries
        assert "data" not in secret, (
            f"Secret '{secret.get('name')}' improperly exposes 'data' dict!"
        )
        assert "stringData" not in secret, (
            f"Secret '{secret.get('name')}' improperly exposes 'stringData' dict!"
        )

        # 2. Only keys list allowed
        assert "keys_list" in secret
        assert isinstance(secret["keys_list"], list)

        # 3. Verify no secret values are embedded in key names
        for key in secret["keys_list"]:
            assert isinstance(key, str)
            # Ensure key is a standard environment variable name, not a base64 string or secret value
            assert len(key) < 64


def test_k8s_troubleshooting_tools_execution():
    """Verify all 15 SRE troubleshooting tools execute cleanly and return actionable diagnostics."""
    # 23. diagnose_pod
    res = run_coro(
        diagnose_pod(pod_name="smiota-agent-core-api-78f99c864-q9m2l", namespace="smiota-prod")
    )
    assert res["status"] == "healthy"
    assert not res["is_failing"]

    # 24. diagnose_crashloop
    res = run_coro(diagnose_crashloop(pod_name="smiota-agent-core-api", namespace="smiota-prod"))
    assert not res["is_in_crashloop"]

    # 25. diagnose_image_pull
    res = run_coro(diagnose_image_pull(pod_name="smiota-agent-core-api", namespace="smiota-prod"))
    assert not res["has_image_pull_issue"]

    # 26. diagnose_pending_pod
    res = run_coro(diagnose_pending_pod(pod_name="smiota-agent-core-api", namespace="smiota-prod"))
    assert not res["is_stuck_pending"]

    # 27. diagnose_node
    res = run_coro(diagnose_node(node_name="gke-application-default-pool-4a8b1c2d-node-1"))
    assert res["status"] == "healthy"

    # 28. diagnose_deployment
    res = run_coro(
        diagnose_deployment(deployment_name="smiota-agent-core-api", namespace="smiota-prod")
    )
    assert res["status"] == "healthy"

    # 29. diagnose_service
    res = run_coro(diagnose_service(service_name="smiota-agent-core-api", namespace="smiota-prod"))
    assert res["has_endpoints"]

    # 30. diagnose_ingress
    res = run_coro(diagnose_ingress(ingress_name="smiota-ingress", namespace="smiota-prod"))
    assert res["status"] == "healthy"

    # 31. analyze_pod_events
    res = run_coro(analyze_pod_events(pod_name="smiota-agent-core-api", namespace="smiota-prod"))
    assert res["status"] == "success"
    assert "timeline" in res

    # 32. analyze_container_logs
    res = run_coro(
        analyze_container_logs(pod_name="smiota-agent-core-api", namespace="smiota-prod")
    )
    assert res["status"] == "nominal"

    # 33. check_pod_restarts
    res = run_coro(check_pod_restarts(namespace="smiota-prod", restart_threshold=3))
    assert res["status"] == "success"
    assert "high_restart_pods" in res

    # 34. check_resource_pressure
    res = run_coro(check_resource_pressure(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert not res["cpu_pressure_detected"]

    # 35. check_pvc_status
    res = run_coro(check_pvc_status(namespace="smiota-prod"))
    assert res["status"] == "success"
    assert res["unbound_pvcs_count"] == 0

    # 36. check_dns_resolution
    res = run_coro(check_dns_resolution(namespace="smiota-prod"))
    assert res["status"] == "healthy"
    assert res["coredns_pods_running"] >= 1

    # 37. check_network_connectivity
    res = run_coro(
        check_network_connectivity(
            source_pod="smiota-agent-core-api",
            target_service="smiotaserver",
            namespace="smiota-prod",
        )
    )
    assert res["status"] == "connected"
    assert not res["network_policies_blocking"]


def test_troubleshooting_diagnoses_crashloop_and_imagepull():
    """Verify troubleshooting tools accurately detect CrashLoopBackOff and ImagePullBackOff."""
    # CrashLoopBackOff diagnosis
    crash_res = run_coro(
        diagnose_crashloop(pod_name="smiotaserver-crashloop", namespace="smiota-prod")
    )
    assert crash_res["is_in_crashloop"] is True
    assert crash_res["exit_code"] == 137
    assert "OOMKilled" in crash_res["root_cause_pattern"]
    assert "actionable_fix" in crash_res

    # ImagePullBackOff diagnosis
    image_res = run_coro(
        diagnose_image_pull(pod_name="image-pull-err-pod", namespace="smiota-prod")
    )
    assert image_res["status"] == "image_pull_error_detected"
    assert "ErrImagePull" in image_res["event_reason"]
    assert "suggested_fix" in image_res


def test_developer_and_aiops_agent_tool_bindings():
    """Verify Developer and AIOps agents have all 37 tools bound."""
    register_default_agents()
    dev_agent = AgentRegistry.get("developer")
    aiops_agent = AgentRegistry.get("aiops")

    for tool in ALL_K8S_TOOLS:
        assert tool in dev_agent.bound_tools, f"Tool '{tool}' not bound to DeveloperAgent!"
        assert tool in aiops_agent.bound_tools, f"Tool '{tool}' not bound to AIOpsAgent!"


def test_teams_channel_routing_for_k8s_queries():
    """Verify Kubernetes and SRE queries in Microsoft Teams channel route with high confidence."""
    router = RuleBasedRouter()
    context = AgentContext(
        session_id="teams-sre-session",
        user_id="sre-devops-lead",
        tenant_id="default",
        channel="teams",
    )

    test_queries = [
        "List Kubernetes clusters",
        "Diagnose CrashLoopBackOff for pod",
        "Check internal DNS resolution",
        "Check PVC status and storage mounting",
        "List namespaces in cluster",
        "Diagnose ImagePullBackOff error",
        "Check node condition NotReady",
    ]

    for query in test_queries:
        decision = run_coro(router.classify(query, context))
        assert decision.agent_name in ("aiops", "developer"), (
            f"Query '{query}' routed to unexpected agent '{decision.agent_name}'"
        )
        assert decision.confidence >= 0.88, (
            f"Query '{query}' confidence {decision.confidence} fell below 0.88"
        )
