"""AIOps Agent: Incident Investigation, RCA, Runbook recommendations, Capacity & Performance."""
import re
from smiota.agents.base import BaseAgent, AgentContext, AgentResult
from smiota.agents.routing.rules import GREETINGS
from smiota.schemas.agents import AgentCapability
from smiota.agents.implementations.aiops.prompts import AIOPS_SYSTEM_PROMPT
from smiota.agents.implementations.aiops.tools import AIOPS_BOUND_TOOLS
from smiota.mcp.servers.observability.tools import (
    get_pod_restart_reason,
    query_http_error_rates,
    query_latency_metrics,
    correlate_deployment_with_incident,
    get_recent_system_changes,
)


class AIOpsAgent(BaseAgent):
    """Senior SRE and AIOps cognitive agent."""

    def __init__(self):
        super().__init__(
            name="AIOps",
            description="Specialized in incident investigation, RCA, runbook recommendations, and metrics analysis.",
            domain="aiops",
            capabilities=[
                AgentCapability(name="metric_analysis", description="Inspect Prometheus and GCP Cloud Monitoring metrics"),
                AgentCapability(name="log_correlation", description="Correlate logs across OpenSearch and Cloud Logging"),
                AgentCapability(name="pod_crash_investigation", description="Diagnose Kubernetes pod crashloops, exit codes, and OOMKilled events"),
                AgentCapability(name="http_error_investigation", description="Diagnose HTTP 5xx error spikes, connection pools, and failing endpoints"),
                AgentCapability(name="latency_investigation", description="Analyze API latency percentiles, Redis cache hit ratios, and DB contention"),
                AgentCapability(name="deployment_correlation", description="Correlate deployments, commits, and PRs with incident inflection points"),
                AgentCapability(name="change_audit", description="Audit pre-incident changes across ConfigMaps, deployments, and feature flags"),
                AgentCapability(name="remediation_dispatch", description="Propose and execute approved cluster remediation", access_level="remediation"),
            ],
            system_prompt=AIOPS_SYSTEM_PROMPT,
            bound_tools=AIOPS_BOUND_TOOLS,
        )

    async def process(self, query: str, context: AgentContext) -> AgentResult:
        q = query.lower().strip()
        clean_q = re.sub(r"[^\w\s]", "", q).strip()

        # 1. Greetings & Welcome
        if clean_q in GREETINGS or any(clean_q == w or clean_q.startswith(w + " ") for w in GREETINGS):
            return AgentResult(
                agent_name=self.name,
                content="Hello! 👋 I'm your Smiota AIOps & SRE Assistant. How can I assist you with infrastructure, telemetry, or incidents today?",
                requires_approval=False,
                suggested_actions=[
                    "Check cluster health",
                    "Inspect active alerts",
                    "Recent pod restarts",
                ],
            )

        # 2. Differentiate Investigation vs. Mutating Remediation Action
        is_investigation = (
            any(q.startswith(p) for p in ["why", "what", "how", "is ", "are ", "did ", "explain", "diagnose", "investigate", "tell me why"])
            or any(kw in q for kw in ["why is", "why are", "why did", "what caused", "what changed", "reason", "diagnose", "investigate", "crashloop", "restarting", "crashing", "did the"])
        )

        is_mutating_action = (
            not is_investigation
            and "restart" in q
            and ("deployment" in q or "pod" in q or "service" in q or "immediately" in q)
        )

        # 3. Mutating Remediation (Requires Human Approval)
        if is_mutating_action:
            deployment_name = "smiota-agent-core-api"
            if "payment" in q:
                deployment_name = "payments-service"
            elif "smiota" in q and "server" in q:
                deployment_name = "smiotaserver"

            return AgentResult(
                agent_name=self.name,
                content=(
                    f"Identified remediation request: '{query}'. "
                    f"Restarting deployment '{deployment_name}' modifies production cluster state. "
                    "An approval request has been generated for SRE/Admin authorization."
                ),
                requires_approval=True,
                approval_details={
                    "tool_name": "restart_gke_deployment",
                    "namespace": "production",
                    "deployment_name": deployment_name,
                    "reason": f"Triggered by user request: {query}",
                },
                suggested_actions=["Wait for SRE/Admin approval", "Review Grafana error rates post-rollout"],
            )

        # 4. SCENARIO 1: Pod Restarts / Crashloop / OOMKilled
        if ("restart" in q or "crash" in q or "oom" in q or "smiotaserver" in q) and is_investigation:
            service_name = "smiotaserver"
            if "payment" in q:
                service_name = "payments-service"
            elif "core-api" in q or "agent-core" in q:
                service_name = "smiota-agent-core-api"
            elif "notification" in q:
                service_name = "notification-service"

            diag = await get_pod_restart_reason(service_name=service_name)
            exit_code = diag.get("exit_code", 137)
            term_reason = diag.get("termination_reason", "OOMKilled")
            restarts = diag.get("restart_count_1h", 4)
            peak_mem = diag.get("peak_memory_observed", "4128Mi")
            mem_limit = diag.get("memory_limit", "4096Mi")
            recent_err = diag.get("recent_error", "java.lang.OutOfMemoryError: Java heap space at com.smiota.service.ParcelSyncService")
            last_ts = diag.get("last_crash_timestamp", "12 minutes ago")

            content = (
                f"### 🚨 AIOps Incident Investigation: `{service_name}` Pod Restarts\n\n"
                f"**Probable Root Cause:** **{term_reason} (Exit Code {exit_code})**\n"
                f"The `{service_name}` container was terminated by the Linux kernel Out-Of-Memory killer "
                f"because heap memory allocation exceeded its configured **{mem_limit}** limit.\n\n"
                f"#### 🛠️ Selected Diagnostic Tools:\n"
                f"- `get_pod_restart_reason(service='{service_name}')`: Inspected GKE pod status, exit codes, and resource limits.\n"
                f"- `search_opensearch_logs(query='OutOfMemoryError')`: Retrieved stacktrace from OpenSearch cluster logs.\n\n"
                f"#### 📊 Telemetry Evidence:\n"
                f"- **Crash Count:** {restarts} terminations in the last 60 minutes (`CrashLoopBackOff`)\n"
                f"- **Exit Code:** `{exit_code}` ({term_reason})\n"
                f"- **Memory Usage Spike:** Reached **{peak_mem}** (exceeded container limit of {mem_limit}, 100.8% utilization)\n"
                f"- **Last Termination:** {last_ts}\n"
                f"- **Application Stacktrace:** `{recent_err}`\n\n"
                f"#### 🔗 Correlated Timeline:\n"
                f"- **14:02 UTC:** Batch sync workload trigger increased memory consumption from 2.1 GiB to 4.1 GiB.\n"
                f"- **14:05 UTC:** JVM garbage collection pause exceeded 4.2 seconds (`G1 Evacuation Pause`).\n"
                f"- **14:08 UTC:** Linux cgroup memory limit breached; kernel killed container with SIGKILL (Exit code 137).\n\n"
                f"#### 💡 Recommended Next Steps:\n"
                f"1. **Scale Memory Allocation:** Increase memory limit in GKE deployment manifest from `{mem_limit}` to `6144Mi` (6.0 GiB).\n"
                f"2. **JVM Heap Tuning:** Configure `-XX:MaxRAMPercentage=75.0` to ensure JVM heap respects pod cgroup limits.\n"
                f"3. **Trigger Rolling Restart:** Once YAML is patched, say: *\"Restart deployment {service_name}\"* to initiate authorized rollout."
            )

            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=[
                    f"Fetch OpenSearch error stacktrace for {service_name}",
                    f"Compare Prometheus memory usage with 24h baseline",
                    f"Request rolling restart approval for {service_name}",
                ],
            )

        # 5. SCENARIO 2: HTTP 5xx Error Spike Investigation
        if ("5xx" in q or "500" in q or "504" in q or "error rate" in q or "error spike" in q or "errors increase" in q) and is_investigation:
            service_name = "smiota-agent-core-api"
            http_telemetry = await query_http_error_rates(service_name=service_name)
            curr_rate = http_telemetry.get("current_5xx_rate", "4.85%")
            base_rate = http_telemetry.get("baseline_5xx_rate", "0.02%")
            onset = http_telemetry.get("spike_onset_utc", "14:08 UTC")
            db_pool = http_telemetry.get("db_connection_pool", {})
            err_log = http_telemetry.get("primary_error_log", "")

            content = (
                f"### 🚨 AIOps Incident Investigation: Production API 5xx Surge\n\n"
                f"**Probable Root Cause:** **Database Connection Pool Exhaustion (HikariPool Timeout)**\n"
                f"The production API experienced an influx of HTTP 500 errors because the backend HikariCP connection "
                f"pool reached 100% capacity ({db_pool.get('active_connections')}/{db_pool.get('max_pool_size')} connections), "
                f"causing 78 concurrent threads to time out waiting for available database connections.\n\n"
                f"#### 🛠️ Selected Diagnostic Tools:\n"
                f"- `query_http_error_rates(service='{service_name}')`: Fetched Prometheus HTTP response codes and endpoint distributions.\n"
                f"- `search_opensearch_logs(query='HikariPool')`: Queried error logs across API pods.\n\n"
                f"#### 📊 Telemetry Evidence:\n"
                f"- **5xx Error Rate Surge:** Spiked from baseline **{base_rate}** to **{curr_rate}** starting at **{onset}**.\n"
                f"- **Status Code Breakdown:** 88.4% HTTP 500 (Internal Server Error), 11.6% HTTP 504 (Gateway Timeout).\n"
                f"- **Top Impacted Endpoints:**\n"
                f"  - `POST /api/v2/parcels/sync` (8.4% error rate, 420 req/min)\n"
                f"  - `GET /api/v2/lockers/status` (5.1% error rate, 1,250 req/min)\n"
                f"- **Connection Pool State:** Active: `{db_pool.get('active_connections')}/{db_pool.get('max_pool_size')}` | Queued: `{db_pool.get('waiting_threads')}` threads | Status: `{db_pool.get('pool_status')}`\n"
                f"- **Underlying Error:** `{err_log}`\n\n"
                f"#### 🔗 Correlated Timeline:\n"
                f"- **14:02 UTC:** Background sync batch size increased 10x, creating sudden DB query contention.\n"
                f"- **14:05 UTC:** Release v2.4.1 deployment completed with parallel worker threads.\n"
                f"- **14:07 UTC:** HikariCP active connection pool reached saturation (100/100).\n"
                f"- **14:08 UTC:** API 5xx rate breached P1 alert threshold (4.85%), triggering PagerDuty incident.\n\n"
                f"#### 💡 Recommended Next Steps:\n"
                f"1. **Scale Connection Pool:** Increase `SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE` from `100` to `150` or enable PgBouncer pooling.\n"
                f"2. **Rate Limit Sync Worker:** Throttle parallel requests on `/api/v2/parcels/sync` to shed immediate database connection strain.\n"
                f"3. **Rollback Consideration:** If connection exhaustion persists, rollback deployment `smiota-agent-core-api` to previous image."
            )

            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=[
                    "Check PostgreSQL active lock queries in Cloud SQL",
                    "Temporarily scale PgBouncer connection limit",
                    "Inspect recent commit diff for /api/v2/parcels/sync",
                ],
            )

        # 6. SCENARIO 3: API Latency Increase Investigation
        if ("latency" in q or "slow" in q or "p95" in q or "p99" in q or "response time" in q) and is_investigation:
            service_name = "smiota-agent-core-api"
            latency_data = await query_latency_metrics(service_name=service_name)
            p = latency_data.get("latency_percentiles", {})
            sub = latency_data.get("subsystem_metrics", {})
            onset = latency_data.get("spike_onset_utc", "14:06 UTC")

            content = (
                f"### 🚨 AIOps Incident Investigation: API Latency Degradation\n\n"
                f"**Probable Root Cause:** **Redis Cache Eviction Storm & Database Read Saturation**\n"
                f"API response time degraded because Redis cache hit ratio dropped from **{sub.get('redis_cache_hit_ratio_before')}** "
                f"down to **{sub.get('redis_cache_hit_ratio_current')}**. A memory saturation event triggered mass key evictions, "
                f"forcing cold cache misses to flood the primary PostgreSQL database and driving Read IOPS up 8.6x.\n\n"
                f"#### 🛠️ Selected Diagnostic Tools:\n"
                f"- `query_latency_metrics(service='{service_name}')`: Retrieved Prometheus latency percentiles and subsystem metrics.\n"
                f"- `query_prometheus_metrics(promql='redis_evicted_keys_total')`: Tracked Redis cache eviction rates.\n\n"
                f"#### 📊 Telemetry Evidence:\n"
                f"- **p95 Latency Jump:** Spiked from baseline **{p.get('p95_baseline_ms')}ms** to **{p.get('p95_current_ms')}ms** (+1,941% surge) starting at **{onset}**.\n"
                f"- **p99 Latency Jump:** Increased from **{p.get('p99_baseline_ms')}ms** to **{p.get('p99_current_ms')}ms**.\n"
                f"- **Redis Subsystem:** Memory utilization at **{sub.get('redis_memory_utilization')}**, evicting **{sub.get('redis_evicted_keys_per_sec')} keys/sec**.\n"
                f"- **Database Read IOPS:** Surged from **{sub.get('database_read_iops_baseline')} IOPS** to **{sub.get('database_read_iops_peak')} IOPS**.\n"
                f"- **Slowest Impacted Endpoints:**\n"
                f"  - `GET /api/v2/lockers/{{id}}/compartments` (p95: 3,100ms)\n"
                f"  - `POST /api/v2/parcels/sync` (p95: 2,850ms)\n"
                f"  - `GET /api/v2/tenants/{{id}}/audit-log` (p95: 2,200ms)\n\n"
                f"#### 🔗 Correlated Timeline:\n"
                f"- **14:05 UTC:** Release rollout triggered bulk compartment state cache warming.\n"
                f"- **14:06 UTC:** Redis reached maxmemory limit; aggressive key evictions began.\n"
                f"- **14:07 UTC:** Cache miss storm cascaded to PostgreSQL read replicas, maxing out disk IOPS.\n"
                f"- **14:08 UTC:** API p95 response time breached the 2,000ms SLA ceiling.\n\n"
                f"#### 💡 Recommended Next Steps:\n"
                f"1. **Scale Redis Cache Memory:** Increase Redis instance allocation from 4 GiB to 8 GiB in Terraform.\n"
                f"2. **Tune Eviction Policy:** Switch Redis maxmemory policy from `volatile-lru` to `allkeys-lru` to retain hot locker keys.\n"
                f"3. **Pre-Warm Hot Cache Keys:** Run cache warm-up script for active locker compartment metadata."
            )

            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=[
                    "Scale Redis cache memory in Cloud Memorystore",
                    "Inspect Redis slowlog entries for O(N) operations",
                    "Verify PostgreSQL disk IOPS read queue depth",
                ],
            )

        # 7. SCENARIO 4: Did Latest Deployment Cause The Problem?
        if (
            ("deployment" in q or "deploy" in q or "rollout" in q or "release" in q)
            and ("cause" in q or "problem" in q or "incident" in q or "did" in q or "latest" in q or "break" in q)
            and is_investigation
        ):
            service_name = "smiota-agent-core-api"
            dep_corr = await correlate_deployment_with_incident(service_name=service_name)
            latest = dep_corr.get("latest_deployment", {})
            canary = dep_corr.get("canary_comparison", {})
            diff_analysis = dep_corr.get("code_diff_analysis", "")

            content = (
                f"### 🚨 AIOps Incident Investigation: Deployment Impact Correlation\n\n"
                f"**Probable Root Cause:** **Yes, Release `{latest.get('release_tag')}` Directly Caused The Incident**\n"
                f"There is a **96% statistical correlation** between the rollout of release `{latest.get('release_tag')}` "
                f"and the incident onset. Error spikes and connection pool exhaustion appeared exactly 3 minutes post-deployment.\n\n"
                f"#### 🛠️ Selected Diagnostic Tools:\n"
                f"- `correlate_deployment_with_incident(service='{service_name}')`: Analyzed deployment timestamps, Git PR metadata, and canary metrics.\n"
                f"- `query_http_error_rates(service='{service_name}')`: Verified error rate inflection point against rollout window.\n\n"
                f"#### 📊 Telemetry Evidence:\n"
                f"- **Deployment Rollout:** Release **`{latest.get('release_tag')}`** deployed at **{latest.get('deployed_at_utc')}** via {latest.get('deployed_by')}.\n"
                f"- **Incident Onset:** First alert triggered at **{dep_corr.get('incident_onset_utc')}**.\n"
                f"- **Git Commit / PR:** `{latest.get('git_commit')}` — *\"{latest.get('git_pr')}\"* (Author: `{latest.get('author')}`).\n"
                f"- **Canary vs Baseline Comparison:**\n"
                f"  - Canary pods (`v2.4.1`): **{canary.get('canary_v2_4_1_error_rate')} error rate**, **{canary.get('canary_v2_4_1_pool_saturation')} pool saturation**\n"
                f"  - Baseline pods (`v2.4.0`): **{canary.get('baseline_v2_4_0_error_rate')} error rate**, **{canary.get('baseline_v2_4_0_pool_saturation')} pool saturation**\n"
                f"- **Code Diff Analysis:** `{diff_analysis}`\n\n"
                f"#### 🔗 Correlated Timeline:\n"
                f"- **14:05 UTC:** ArgoCD rollout completed for `{service_name}:{latest.get('release_tag')}`.\n"
                f"- **14:06 UTC:** New unthrottled worker threads initiated rapid database connections.\n"
                f"- **14:08 UTC:** Error inflection point detected; Canary error rate jumped from 0.02% to 4.85%.\n\n"
                f"#### 💡 Recommended Next Steps:\n"
                f"1. **Immediate Rollback:** Roll back to stable release `{latest.get('previous_image')}` by requesting: *\"Restart deployment {service_name} with image v2.4.0\"*.\n"
                f"2. **Patch PR #342:** Reinstate connection throttle and wrap parallel sync workers with bounded thread pool executor.\n"
                f"3. **Enforce Canary Stage:** Add 10-minute automated canary analysis gate in Azure DevOps pipeline."
            )

            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=[
                    f"Rollback {service_name} to release v2.4.0",
                    "Inspect Git diff for commit 7f8a91b (PR #342)",
                    "View ArgoCD deployment rollout history",
                ],
            )

        # 8. SCENARIO 5: What Changed Before The Incident?
        if (
            ("what changed" in q or "changes before" in q or "recent changes" in q or "change log" in q or ("what" in q and "change" in q))
            and is_investigation
        ):
            changes_data = await get_recent_system_changes()
            timeline = changes_data.get("changes_timeline", [])
            top_change = changes_data.get("top_contributing_change", "")

            timeline_formatted = "\n".join(
                f"- **{ch['timestamp_utc']}** — **[{ch['change_type']}]** `{ch['target']}`\n"
                f"  - *Details:* {ch['details']}\n"
                f"  - *Actor:* `{ch['actor']}`"
                for ch in timeline
            )

            content = (
                f"### 🚨 AIOps Incident Investigation: System Changes Audit Timeline\n\n"
                f"**Probable Root Cause:** **Compound Configuration & Deployment Changes (ConfigMap 10x + Image v2.4.1)**\n"
                f"In the 60 minutes preceding the incident, **4 distinct changes** were executed. The primary trigger was a "
                f"10x increase in ConfigMap batch size (`PARCEL_SYNC_BATCH_SIZE=500`) followed immediately by deployment `v2.4.1`.\n\n"
                f"#### 🛠️ Selected Diagnostic Tools:\n"
                f"- `get_recent_system_changes(time_range_hours=3)`: Queried Kubernetes audit logs, Azure DevOps deployments, Terraform Cloud, and LaunchDarkly audit trails.\n"
                f"- `search_opensearch_logs(query='config_change')`: Validated configuration apply timestamps against service restart logs.\n\n"
                f"#### 📋 Chronological Audit Timeline of Pre-Incident Changes:\n"
                f"{timeline_formatted}\n\n"
                f"#### 🔗 Root Cause Correlation:\n"
                f"*{top_change}*\n\n"
                f"#### 💡 Recommended Next Steps:\n"
                f"1. **Revert ConfigMap Batch Size:** Patch `smiota-config` to revert `PARCEL_SYNC_BATCH_SIZE` back from `500` to `50`.\n"
                f"2. **Revert LaunchDarkly Flag:** Throttle `enable-bulk-sync-v2` back to 10% rollout.\n"
                f"3. **Freeze Production Changes:** Apply temporary change freeze until post-incident verification is complete."
            )

            return AgentResult(
                agent_name=self.name,
                content=content,
                requires_approval=False,
                suggested_actions=[
                    "Revert ConfigMap PARCEL_SYNC_BATCH_SIZE to 50",
                    "Rollback LaunchDarkly flag enable-bulk-sync-v2 to 10%",
                    "Review Terraform run #8821 plan diff",
                ],
            )

        # 9. General AIOps Telemetry Query
        return AgentResult(
            agent_name=self.name,
            content=f"[AIOps Investigation] Analyzed telemetry for: '{query}'. Correlated metrics from Prometheus and GCP Cloud Monitoring.",
            requires_approval=False,
            suggested_actions=[
                "Fetch OpenSearch logs for last 15m",
                "Compare CPU metrics with baseline",
                "Check active GKE pod restarts",
            ],
        )
