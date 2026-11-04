"""Pure analyzer: Linux and Kubernetes container exit codes."""
from __future__ import annotations

from typing import Dict, Tuple

_EXIT_CODE_MAP: Dict[int, Tuple[str, str]] = {
    137: ("OOMKilled / SIGKILL", "Container was killed by kernel OOM killer (Out of Memory) or received SIGKILL (128 + 9)."),
    143: ("SIGTERM", "Container gracefully received termination request (128 + 15) during pod shutdown or eviction."),
    1: ("Application Error", "Application exited with generic non-zero status. Check previous logs for runtime exceptions."),
    126: ("Command Invocation Error", "Command found but cannot be invoked (permissions or architecture mismatch)."),
    127: ("Command Not Found", "Specified entrypoint binary or command was not found in container filesystem PATH."),
    130: ("Script Interrupted", "Process terminated by Ctrl+C or SIGINT (128 + 2)."),
    139: ("Segmentation Fault", "Process crashed with SIGSEGV (128 + 11). Check native memory corruption."),
}


def analyze_exit_code(exit_code: int | None, reason: str | None = None) -> Dict[str, str]:
    """Pure analysis of container exit code and termination reason."""
    if exit_code is None:
        return {
            "title": reason or "Unknown Termination",
            "description": "Container terminated without reporting an exit code.",
            "probable_cause": "Node failure or kubelet abrupt restart.",
        }

    if exit_code in _EXIT_CODE_MAP:
        title, desc = _EXIT_CODE_MAP[exit_code]
    elif exit_code > 128:
        sig = exit_code - 128
        title = f"Fatal Signal {sig}"
        desc = f"Container terminated due to uncaught OS signal {sig}."
    else:
        title = f"Exit Code {exit_code}"
        desc = f"Container application exited with non-zero code {exit_code}."

    if reason and "OOM" in reason.upper():
        title = "OOMKilled"
        desc = "Memory limit was exceeded; Linux kernel killed the main container process."

    return {
        "title": title,
        "description": desc,
        "probable_cause": "Process crashed or resource constraints breached." if exit_code != 0 else "Normal termination.",
    }

