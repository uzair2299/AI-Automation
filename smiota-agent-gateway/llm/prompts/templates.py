"""Prompt templates for intent classification, agent handoff, and HITL explanations."""

INTENT_ROUTING_PROMPT = """Classify the following query into exactly one of the five domain agents:
- aiops: Infrastructure metrics, incident investigation, RCA, logs, Kubernetes, crashes.
- security: Vulnerabilities, CVEs, IAM policies, Wazuh SIEM, threat containment.
- developer: Code review, PR diffs, Terraform IaC, PromQL syntax, CI/CD builds.
- qa: Test failure logs, Playwright/Selenium scripts, test flakiness, regression suites.
- customer: Smart locker status, package delivery, pickup, door sensors, support tickets.

Query: {query}

Return only the domain name.
"""

HITL_EXPLANATION_TEMPLATE = """# Action Requires Human Authorization
**Tool Requested**: `{tool_name}`
**Risk Level**: High / Infrastructure Mutation
**Target Resource**: `{resource_id}`
**Operational Reason**: {reason}

To authorize execution, click Approve or supply your signed authorization token.
"""
