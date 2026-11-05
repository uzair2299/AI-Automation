"""Security & SIEM MCP Tools (Wazuh, Trivy, GCP IAM, HashiCorp Vault)."""
from typing import Optional
from smiota.mcp.security import mcp_tool
from smiota.schemas.mcp import ToolAccessLevel


@mcp_tool(
    name="query_wazuh_alerts",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Query Wazuh SIEM security events, intrusion alerts, and CIS benchmark findings.",
)
async def query_wazuh_alerts(severity_threshold: int = 7, limit: int = 10) -> list[dict]:
    """Query Wazuh SIEM for active security alerts."""
    return [
        {
            "id": "alert-8821",
            "timestamp": "2026-10-15T11:45:00Z",
            "rule_id": "5710",
            "level": 8,
            "description": "sshd: Multiple failed login attempts from anomalous subnet",
            "agent_name": "gke-node-pool-01",
        }
    ]


@mcp_tool(
    name="scan_container_vulnerabilities",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Scan container image or repository dependencies with Trivy / Snyk for CVEs.",
)
async def scan_container_vulnerabilities(image_tag: str) -> dict:
    """Scan container image with Trivy scanner."""
    return {
        "image": image_tag,
        "vulnerabilities": {
            "CRITICAL": 0,
            "HIGH": 1,
            "MEDIUM": 4,
            "LOW": 12,
        },
        "top_cve": "CVE-2026-3112 (OpenSSL buffer edge condition, patch available in 3.1.2)",
    }


@mcp_tool(
    name="audit_gcp_iam_bindings",
    access_level=ToolAccessLevel.READ_ONLY,
    description="Inspect GCP IAM service account permissions and detect over-privileged roles.",
)
async def audit_gcp_iam_bindings(project_id: str) -> list[dict]:
    """Audit GCP IAM bindings for least privilege compliance."""
    return [
        {
            "member": "serviceAccount:deploy-runner@smiota-cloud-prod.iam.gserviceaccount.com",
            "role": "roles/owner",
            "status": "VIOLATION",
            "recommendation": "Demote to roles/container.developer and roles/clouddeploy.operator",
        }
    ]


@mcp_tool(
    name="revoke_compromised_credentials",
    access_level=ToolAccessLevel.REMEDIATION,
    description="Revoke compromised API key or service account key (Requires Human-in-the-Loop approval).",
)
async def revoke_compromised_credentials(
    credential_id: str,
    reason: str,
    approval_token: Optional[str] = None,
) -> dict:
    """Revoke compromised credentials across GCP Secret Manager and Vault."""
    return {
        "status": "revoked",
        "credential_id": credential_id,
        "reason": reason,
        "approved_by_token": approval_token,
    }
