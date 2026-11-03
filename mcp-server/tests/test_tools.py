"""Unit tests for FastMCP registered tools and diagnosis schemas."""
from unittest.mock import MagicMock, patch
from app.tools.format_validator import build_retry_instruction, validate_format
from app.tools.inventory_clusters import list_clusters
from app.tools.inventory_config import list_secrets_metadata
from app.tools.diagnose_workloads import diagnose_pod


def run_sync(coro):
    """Synchronous runner for async coroutine test execution."""
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value
    raise RuntimeError("Coroutine did not resolve synchronously")


def test_format_validator():
    res = validate_format("Short valid paragraph.")
    assert res["is_valid"] is True

    res_long = validate_format("A" * 700)
    assert res_long["is_valid"] is False
    assert len(res_long["issues"]) == 1

    retry_inst = build_retry_instruction(res_long["issues"])
    assert "CRITICAL FORMATTING CORRECTION" in retry_inst


def test_list_clusters():
    res = run_sync(list_clusters())
    assert "clusters" in res
    assert res["total"] >= 1


def test_secrets_metadata_never_exposes_secret_values():
    mock_secret = MagicMock()
    mock_secret.metadata.name = "database-credentials"
    mock_secret.metadata.namespace = "smiota-prod"
    mock_secret.metadata.creation_timestamp = "2026-10-01T00:00:00Z"
    mock_secret.metadata.labels = {"app": "smiota"}
    mock_secret.type = "Opaque"
    mock_secret.data = {"username": "YWRtaW4=", "password": "c2VjcmV0cGFzc3dvcmQ="}

    mock_client = MagicMock()
    mock_client.list_namespaced_secret.return_value = MagicMock(items=[mock_secret])

    with patch("app.tools.inventory_config.get_k8s_clients", return_value={"core_v1": mock_client}):
        with patch("app.tools.inventory_config.run_k8s_call", side_effect=lambda f, *args, **kwargs: f(*args, **kwargs)):
            res = run_sync(list_secrets_metadata(namespace="smiota-prod"))
            assert res["total"] == 1
            sec = res["secrets"][0]
            assert sec["name"] == "database-credentials"
            # Key names are included
            assert sec["keys"] == ["username", "password"]
            # Raw data and encoded secrets are NEVER present
            assert "data" not in sec
            assert "stringData" not in sec
            assert "c2VjcmV0cGFzc3dvcmQ=" not in str(sec)
            assert "YWRtaW4=" not in str(sec)


def test_diagnose_pod_report_contract():
    mock_pod = MagicMock()
    mock_pod.metadata.name = "failing-pod-123"
    mock_pod.metadata.namespace = "default"
    mock_pod.status.phase = "Running"
    
    mock_cs = MagicMock()
    mock_cs.name = "api"
    mock_cs.ready = False
    mock_cs.restart_count = 15
    mock_cs.state.waiting.reason = "CrashLoopBackOff"
    mock_pod.status.container_statuses = [mock_cs]

    mock_client = MagicMock()
    mock_client.read_namespaced_pod.return_value = mock_pod

    with patch("app.tools.diagnose_workloads.get_k8s_clients", return_value={"core_v1": mock_client}):
        with patch("app.tools.diagnose_workloads.run_k8s_call", side_effect=lambda f, *args, **kwargs: f(*args, **kwargs)):
            res = run_sync(diagnose_pod("failing-pod-123", "default"))
            assert res["target"]["name"] == "failing-pod-123"
            assert res["status"] == "failing"
            assert len(res["findings"]) >= 1
            f = res["findings"][0]
            assert f["severity"] == "critical"
            assert "CrashLoopBackOff" in f["title"]
            assert len(f["suggested_next_steps"]) >= 1
            assert "checked" in res
