"""Automated incident postmortem & root cause analysis compiler."""
from datetime import datetime, timezone
from smiota.core.logging import logger
from smiota.llm.provider import GeminiProvider


async def generate_incident_postmortem(
    incident_id: str,
    service_name: str,
    timeline_events: list[dict],
) -> dict:
    """Compile an automated postmortem report following SRE incident resolution."""
    logger.info(f"Compiling incident postmortem for {incident_id} ({service_name})...")
    provider = GeminiProvider()

    prompt = (
        f"Generate a blameless postmortem for incident {incident_id} impacting {service_name}. "
        f"Timeline events: {timeline_events}"
    )

    summary = await provider.generate_completion(prompt)

    return {
        "incident_id": incident_id,
        "service_name": service_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "postmortem_content": summary,
        "action_items": [
            "Tune HPA memory thresholds to avoid OOMKilled evictions",
            "Update runbook documentation with new recovery commands",
        ],
    }
