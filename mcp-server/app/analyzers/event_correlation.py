"""Pure analyzer: Kubernetes event correlation and causal chain reconstruction."""
from __future__ import annotations

from typing import Any, Dict, List


def correlate_events(raw_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pure function: groups, dedupes, and extracts causal transition chains from k8s events."""
    if not raw_events:
        return {"causal_chain": [], "grouped_events": {}, "summary": "No events found."}

    # Dedupe events by (reason, message, type)
    deduped: Dict[str, Dict[str, Any]] = {}
    chronological = []

    for ev in raw_events:
        reason = ev.get("reason", "Unknown")
        ev_type = ev.get("type", "Normal")
        message = ev.get("message", "")
        count = ev.get("count", 1) or 1
        key = f"{reason}:{message}"

        if key in deduped:
            deduped[key]["count"] += count
        else:
            item = {
                "reason": reason,
                "type": ev_type,
                "message": message,
                "count": count,
                "first_time": ev.get("first_timestamp"),
                "last_time": ev.get("last_timestamp"),
            }
            deduped[key] = item
            chronological.append(reason)

    # Build simple causal sequence
    causal_chain: List[str] = []
    for r in chronological:
        if not causal_chain or causal_chain[-1] != r:
            causal_chain.append(r)

    grouped_by_reason: Dict[str, List[Dict[str, Any]]] = {}
    for item in deduped.values():
        r = item["reason"]
        grouped_by_reason.setdefault(r, []).append(item)

    chain_str = " -> ".join(causal_chain)

    return {
        "causal_chain": causal_chain,
        "causal_sequence": chain_str,
        "grouped_by_reason": grouped_by_reason,
        "unique_event_types": len(deduped),
    }
