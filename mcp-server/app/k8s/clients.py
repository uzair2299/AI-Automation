"""Multi-cluster Kubernetes client factory and thread-safe cache."""
from __future__ import annotations

import asyncio
import os
import threading
from typing import Any, Callable, Dict, Optional
import yaml

from kubernetes import client, config
from app.config import settings

_CLIENTS_LOCK = threading.Lock()
_CLUSTER_CLIENTS: Dict[str, Dict[str, Any]] = {}
_CLUSTER_METADATA: Dict[str, Dict[str, Any]] = {}


def _load_clusters_config() -> None:
    """Load optional clusters.yaml file if present."""
    if os.path.exists(settings.K8S_CLUSTERS_CONFIG):
        try:
            with open(settings.K8S_CLUSTERS_CONFIG, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                for cluster in data.get("clusters", []):
                    name = cluster.get("name")
                    if name:
                        _CLUSTER_METADATA[name] = cluster
        except Exception:
            pass


def get_cluster_list() -> list[str]:
    """Retrieve list of recognized cluster names or contexts."""
    _load_clusters_config()
    if _CLUSTER_METADATA:
        return list(_CLUSTER_METADATA.keys())

    # Try listing kubeconfig contexts
    try:
        contexts, active_context = config.list_kube_config_contexts(config_file=settings.KUBECONFIG)
        if contexts:
            return [c["name"] for c in contexts]
    except Exception:
        pass

    return [settings.K8S_DEFAULT_CLUSTER]


def get_k8s_clients(cluster: Optional[str] = None) -> Dict[str, Any]:
    """Obtain or initialize thread-safe Kubernetes API clients for target cluster."""
    target = cluster or settings.K8S_DEFAULT_CLUSTER
    _load_clusters_config()

    with _CLIENTS_LOCK:
        if target in _CLUSTER_CLIENTS:
            return _CLUSTER_CLIENTS[target]

        api_client = None
        context_name = None

        if target in _CLUSTER_METADATA:
            context_name = _CLUSTER_METADATA[target].get("context")

        # Try loading configuration
        try:
            # 1. Kubeconfig context
            config.load_kube_config(config_file=settings.KUBECONFIG, context=context_name or target)
            api_client = client.ApiClient()
        except Exception:
            # 2. In-cluster fallback
            try:
                config.load_incluster_config()
                api_client = client.ApiClient()
            except Exception:
                # 3. Default empty client for unit test mocks
                api_client = client.ApiClient()

        clients = {
            "core_v1": client.CoreV1Api(api_client),
            "apps_v1": client.AppsV1Api(api_client),
            "networking_v1": client.NetworkingV1Api(api_client),
            "autoscaling_v2": client.AutoscalingV2Api(api_client),
            "custom_objects": client.CustomObjectsApi(api_client),
            "version": client.VersionApi(api_client),
            "api_client": api_client,
        }
        _CLUSTER_CLIENTS[target] = clients
        return clients


async def run_k8s_call(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute blocking Kubernetes API call off the main asyncio event loop with timeout."""
    timeout = settings.K8S_DEFAULT_TIMEOUT_SECONDS
    return await asyncio.wait_for(
        asyncio.to_thread(func, *args, **kwargs),
        timeout=timeout,
    )
