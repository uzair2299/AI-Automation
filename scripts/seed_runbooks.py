"""Utility script to seed vector database with baseline engineering runbooks."""
import asyncio
from smiota.rag.vector_store import VectorStoreClient
from smiota.rag.embeddings import EmbeddingService
from smiota.rag.chunking import DocumentChunker
from smiota.core.logging import logger

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
        "content": """# Wazuh SIEM Intrusion Containment Runbook
## Symptoms:
- Repeated Rule 5710 alerts (sshd failed login attempts).
- Unusual outbound network egress to unclassified external IP.

## Investigation Steps:
1. Query Wazuh SIEM for source IP addresses and targeted usernames.
2. Cross-reference source IP against threat intelligence feeds.
3. Check GCP Cloud Armor security policy logs.

## Containment:
- Revoke compromised service account keys immediately.
- Block offender CIDR at Cloud Armor perimeter (Requires SecOps Approval).
""",
        "tags": ["security", "siem", "wazuh", "iam"],
    },
    {
        "title": "Smart Locker Solenoid Hardware Diagnostic Runbook",
        "category": "runbook",
        "content": """# Smart Locker Solenoid Hardware Runbook
## Symptoms:
- Resident reports locker compartment door fails to click open upon barcode scan.
- IoT telemetry reports door state 'closed' despite unlock trigger.

## Diagnostic Steps:
1. Check battery percentage (>15% required for solenoid pulse).
2. Inspect hardware controller ping and MQTT connection status.
3. Verify if package pickup code was already redeemed.

## Remediation:
- Dispatch remote electronic pulse test.
- If mechanical lock is physically jammed, dispatch on-site technician.
""",
        "tags": ["iot", "smart-locker", "hardware", "customer"],
    },
]


async def seed():
    logger.info("Seeding knowledge base with engineering runbooks...")
    store = VectorStoreClient()
    embedder = EmbeddingService()
    chunker = DocumentChunker()

    for rb in SAMPLE_RUNBOOKS:
        chunks = chunker.split_text(rb["content"])
        for idx, chunk in enumerate(chunks):
            emb = await embedder.get_embedding(chunk)
            doc_id = await store.insert_document(
                title=f"{rb['title']} (Part {idx+1})" if len(chunks) > 1 else rb["title"],
                content=chunk,
                embedding=emb,
                category=rb["category"],
                metadata={"tags": rb["tags"]},
            )
            logger.info(f"Seeded: '{rb['title']}' chunk {idx+1} -> {doc_id}")

    logger.info("Knowledge base seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
