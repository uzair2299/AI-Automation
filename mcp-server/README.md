# Kubernetes SRE Troubleshooting MCP Server

A production-grade, strictly read-only Model Context Protocol (MCP) server providing 37 specialized Kubernetes inspection and troubleshooting tools for Site Reliability Engineering (SRE) and incident root-cause analysis (RCA).

## Features

- **Strictly Read-Only Guarantee**: Zero mutation verbs (`create`, `patch`, `delete`, `scale`, `exec`, `port-forward`). Verified by automated Abstract Syntax Tree (AST) unit test scanners.
- **Zero Secrets Exposure**: `list_secrets_metadata` returns only key names, namespaces, and timestamps. Values (`data`, `stringData`, `last-applied-configuration`) are permanently scrubbed.
- **Comprehensive PII & Sensitive Redaction**: Redacts tokens, passwords, PEM blocks, and basic-auth URLs across all logs, events, and specs.
- **Multi-Cluster Support**: Reads multiple kubeconfig contexts or `clusters.yaml` aliases with thread-safe client pooling.
- **Unified Diagnosis Report Model**: All 15 troubleshooting tools emit the standardized `DiagnosisReport` schema (`target`, `status`, `findings`, `checked`, `truncated`).
- **Safety Annotations**: Every tool carries `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`.

## Tool Summary

### Group 1: Inventory Tools (22 tools)
- `k8s_list_clusters`, `k8s_get_cluster_info`
- `k8s_list_namespaces`, `k8s_get_namespace`
- `k8s_list_nodes`, `k8s_get_node_details`
- `k8s_list_pods`, `k8s_get_pod_details`, `k8s_get_pod_logs`, `k8s_get_pod_previous_logs`
- `k8s_list_deployments`, `k8s_get_deployment_details`
- `k8s_list_statefulsets`, `k8s_list_daemonsets`
- `k8s_list_services`, `k8s_list_ingresses`
- `k8s_list_configmaps`, `k8s_list_secrets_metadata`, `k8s_list_events`
- `k8s_get_pod_metrics`, `k8s_get_resource_quotas`, `k8s_get_hpa_status`

### Group 2: Troubleshooting Tools (15 tools)
- `k8s_diagnose_pod`, `k8s_diagnose_crashloop`, `k8s_diagnose_image_pull`
- `k8s_diagnose_pending_pod`, `k8s_diagnose_node`, `k8s_diagnose_deployment`
- `k8s_diagnose_service`, `k8s_diagnose_ingress`
- `k8s_analyze_pod_events`, `k8s_analyze_container_logs`
- `k8s_check_pod_restarts`, `k8s_check_resource_pressure`, `k8s_check_pvc_status`
- `k8s_check_dns_resolution`, `k8s_check_network_connectivity`

*Note: `k8s_check_network_connectivity` is purely passive/read-only (active exec probe pods are intentionally out of scope).*

## Installation & Running

### Stdio Transport
```bash
export MCP_TRANSPORT=stdio
python -m app.server
```

### Streamable HTTP Transport
```bash
export MCP_TRANSPORT=streamable-http
export MCP_PORT=8080
python -m app.server
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```
