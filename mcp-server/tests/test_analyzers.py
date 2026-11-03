"""Unit tests for pure analyzers (exit codes, logs, events, scheduling, DNS)."""
from app.analyzers.dns_network import evaluate_dns_health, evaluate_network_policy
from app.analyzers.event_correlation import correlate_events
from app.analyzers.exit_codes import analyze_exit_code
from app.analyzers.log_patterns import analyze_log_content
from app.analyzers.scheduling import parse_scheduling_failure


def test_analyze_exit_codes():
    oom = analyze_exit_code(137, "OOMKilled")
    assert "OOMKilled" in oom["title"]

    sigterm = analyze_exit_code(143)
    assert "SIGTERM" in sigterm["title"]

    not_found = analyze_exit_code(127)
    assert "Command Not Found" in not_found["title"]


def test_analyze_log_content_patterns():
    lines = [
        "2026-11-03 10:00:00 INFO Server starting on port 8080",
        "2026-11-03 10:00:01 ERROR Connection refused to database:5432",
        "2026-11-03 10:00:02 FATAL panic: runtime error: invalid memory address",
        "2026-11-03 10:00:03 INFO Handled healthcheck request",
    ]
    res = analyze_log_content(lines)
    assert res["total_lines_analyzed"] == 4
    assert res["error_lines_detected"] == 2
    assert res["error_rate"] == 0.5
    top_pats = [p["pattern"] for p in res["top_patterns"]]
    assert "Panic / Fatal Crash" in top_pats
    assert "Database / Connection Timeout" in top_pats


def test_correlate_events():
    raw = [
        {"reason": "Scheduled", "type": "Normal", "message": "Successfully assigned default/pod to node-1", "count": 1},
        {"reason": "Pulling", "type": "Normal", "message": "Pulling image 'app:v1'", "count": 1},
        {"reason": "Pulled", "type": "Normal", "message": "Successfully pulled image", "count": 1},
        {"reason": "BackOff", "type": "Warning", "message": "Back-off restarting failed container", "count": 5},
    ]
    corr = correlate_events(raw)
    assert corr["causal_sequence"] == "Scheduled -> Pulling -> Pulled -> BackOff"
    assert corr["unique_event_types"] == 4


def test_parse_scheduling_failure():
    res = parse_scheduling_failure("0/5 nodes are available: 3 Insufficient memory, 2 node(s) had untolerated taint")
    assert "Insufficient memory" in res["probable_cause"] or len(res["reasons"]) >= 2
    assert len(res["suggested_steps"]) >= 1


def test_evaluate_dns_and_network_policy():
    dns_res = evaluate_dns_health(
        coredns_pods=[{"name": "coredns-1", "ready": True}],
        endpoints_ready=1,
        configmap_sanity=True,
        recent_errors=[],
    )
    assert dns_res["status"] == "healthy"

    pol_res = evaluate_network_policy(
        source_labels={"app": "frontend"},
        dest_labels={"app": "backend"},
        policies=[],
        port=80,
    )
    assert pol_res["allowed"] is True
