"""Pure analyzer: Container log pattern matching and anomaly detection."""
from __future__ import annotations

import re
from typing import Any, Dict, List
from app.k8s.redact import redact_text

_PATTERN_DEFINITIONS = [
    ("OOM / Memory Exhaustion", re.compile(r"(OutOfMemoryError|kill(?:ed)? process \d+ \(.*\) score \d+ or sacrifice child|invoked oom-killer)", re.I)),
    ("Panic / Fatal Crash", re.compile(r"(panic: |FATAL: |fatal error: |Assertion `.*` failed)", re.I)),
    ("Database / Connection Timeout", re.compile(r"(connection (?:timed out|refused)|read timeout|connect timeout|ETIMEDOUT|ECONNREFUSED)", re.I)),
    ("DNS Resolution Failure", re.compile(r"(nxdomain|name resolution error|cannot resolve host|dial tcp: lookup .* no such host)", re.I)),
    ("Authentication / Permission Failure", re.compile(r"(401 Unauthorized|403 Forbidden|AccessDenied|Permission denied|Invalid credentials)", re.I)),
    ("HTTP 5xx Server Error", re.compile(r"(500 Internal Server Error|502 Bad Gateway|503 Service Unavailable|504 Gateway Timeout)", re.I)),
    ("Stack Trace / Exception", re.compile(r"(Traceback \(most recent call last\)|Exception in thread|NullPointerException|TypeError:|ValueError:)", re.I)),
]


def analyze_log_content(lines: List[str]) -> Dict[str, Any]:
    """Pure analysis over log lines: counts pattern matches and extracts redacted samples."""
    pattern_matches: Dict[str, Dict[str, Any]] = {}
    total_lines = len(lines)
    error_line_count = 0

    for name, regex in _PATTERN_DEFINITIONS:
        pattern_matches[name] = {"count": 0, "samples": []}

    for line in lines:
        line_has_error = False
        for name, regex in _PATTERN_DEFINITIONS:
            if regex.search(line):
                line_has_error = True
                pattern_matches[name]["count"] += 1
                if len(pattern_matches[name]["samples"]) < 3:
                    pattern_matches[name]["samples"].append(redact_text(line.strip()))
        if line_has_error:
            error_line_count += 1

    top_patterns = [
        {"pattern": k, "count": v["count"], "sample_lines": v["samples"]}
        for k, v in pattern_matches.items()
        if v["count"] > 0
    ]
    top_patterns.sort(key=lambda x: x["count"], reverse=True)

    error_rate = (error_line_count / total_lines) if total_lines > 0 else 0.0

    return {
        "total_lines_analyzed": total_lines,
        "error_lines_detected": error_line_count,
        "error_rate": round(error_rate, 4),
        "top_patterns": top_patterns,
    }

