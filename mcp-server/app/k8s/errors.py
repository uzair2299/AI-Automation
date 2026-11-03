"""ApiException mapper and timeout error formatting."""
from __future__ import annotations

import asyncio
from typing import Any, Dict
from kubernetes.client.exceptions import ApiException


def map_k8s_exception(exc: Exception, resource: str, name: str | None = None) -> Dict[str, Any]:
    """Map Kubernetes exceptions or timeouts into clean, non-leaky error responses without stack traces."""
    res_id = f"'{name}'" if name else "resources"

    if isinstance(exc, asyncio.TimeoutError):
        return {
            "error": "timeout",
            "message": f"Kubernetes API timed out while querying {resource} {res_id}.",
            "status_code": 504,
        }

    if isinstance(exc, ApiException):
        status = exc.status or 500
        if status == 401:
            msg = "Kubernetes API authentication failed. Verify kubeconfig credentials or service account tokens."
        elif status == 403:
            msg = f"Forbidden: Insufficient RBAC permissions to read {resource} {res_id}."
        elif status == 404:
            msg = f"NotFound: {resource} {res_id} does not exist in cluster/namespace."
        elif status == 429:
            msg = "Kubernetes API rate limit reached (HTTP 429). Please back off and retry."
        elif status >= 500:
            msg = f"Kubernetes API server returned internal server error ({status})."
        else:
            msg = f"Kubernetes API request failed ({status})."

        return {
            "error": "k8s_api_error",
            "message": msg,
            "status_code": status,
        }

    return {
        "error": "unexpected_error",
        "message": f"An error occurred while inspecting {resource} {res_id}.",
        "status_code": 500,
    }
