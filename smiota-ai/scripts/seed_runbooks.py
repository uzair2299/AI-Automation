"""Utility script to seed vector database with baseline engineering runbooks."""
import asyncio
from core.logging import logger
from rag_client.client import RAGServiceClient

SAMPLE_RUNBOOKS = [
    {
        "title": "GKE Pod OOMKilled & High Memory Incident Response",
        "category": "runbook",
        "content": """# GKE High Memory Investigation Runbook
## Symptoms:
- Pods transitioning to CrashLoopBackOff or status terminated with reason OOMKilled.
- High memory utilization alerts (>90%) triggered on container pods.

## Investigation Steps:
1. Identify failing pods using `kubectl get pods -n <namespace> -o wide`.
2. Check memory limits in pod spec versus current consumption using Prometheus.
3. Review container logs before exit via OpenSearch.
4. Verify if JVM heap or memory leak occurred.

## Safe Remediation:
- Scale up pod memory request/limit in deployment spec.
- If node is under memory pressure, cordoning and draining node requires SRE approval.
""",
        "tags": ["gke", "kubernetes", "memory", "oom", "aiops"],
    },
    {
        "title": "Wazuh SIEM Intrusion & Brute Force Containment Runbook",
        "category": "runbook",
        "content": """# Wazuh SIEM Security Containment Runbook
## Symptoms:
- Repeated SSH authentication failures alert triggered.
- Multiple 401/403 brute force spikes detected by Cloud Armor.

## Safe Remediation:
- Temporarily block offending source IP at Cloud Armor security policy level.
- Rotate service account keys if compromised.
""",
        "tags": ["security", "siem", "wazuh", "brute-force", "soc"],
    },
    {
        "title": "Smart Locker Solenoid Bus Communication Timeout Runbook",
        "category": "hardware",
        "content": """# Smart Locker Hardware & Solenoid Diagnostics
## Symptoms:
- Touchscreen reports 'Door actuation timed out'.
- Solenoid controller fails to respond over internal RS-485 bus.

## Investigation Steps:
1. Query door status via IoT sensor telemetry API.
2. Check 12V DC power rail output from 1500VA UPS battery.
3. Verify RS-485 bus termination resistor and wiring continuity.

## Safe Remediation:
- Issue remote controller reset command.
- If hardware solenoid is stuck, dispatch local field technician with master override key.
""",
        "tags": ["iot", "smart-locker", "hardware", "customer"],
    },
]

async def seed():
    logger.info("Seeding knowledge base via RAG service client...")
    client = RAGServiceClient()
    for rb in SAMPLE_RUNBOOKS:
        res = await client.ingest(
            title=rb["title"],
            content=rb["content"],
            category=rb["category"],
            tags=rb["tags"],
        )
        logger.info(f"Seeded: '{rb['title']}' -> {res.get('data', {}).get('document_id', 'indexed')}")

    logger.info("Knowledge base seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed())
