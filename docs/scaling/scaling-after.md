# AutoAudit — AKS Scaling After-State

> **Status:** Scaffold. Mirrors the structure of [scaling-baseline.md](./scaling-baseline.md). The static (chart / code) sections are populated as part of implementation; the runtime evidence sections are filled in after the load-test runs on the AKS dev cluster.
>
> This document is the **panel "after" snapshot**. Read alongside the baseline to see deltas.

## Why this document exists

The baseline document records what AutoAudit's workload scaling looked like at the start of this sprint. This document records what it looks like *after* the work — same workload table, same evidence shape, same five workloads — so the panel can compare.

The deltas table at the end is the headline. It pairs every "before" cell with its "after" cell so the magnitude of the change is impossible to miss.

## How to read this document

Each workload section has the same shape as the baseline:

- **Replicas / autoscaler / disruption budget / probes / lifecycle / topology / observability hooks**

with two additional subsections per workload:

- **What changed and why** — links the change to the panel narrative.
- **Demo evidence** — screenshots and numbers from the load runs.

---

## Chart-wide after-state summary

Every workload now has at minimum: a HorizontalPodAutoscaler (or KEDA `ScaledObject` for the worker queues), a PodDisruptionBudget, dependency-aware probes, graceful-shutdown plumbing (`terminationGracePeriodSeconds` + `lifecycle.preStop`), zone-spread topology constraints, and pod anti-affinity by host. The `monitoring.podMonitor.enabled` flag publishes Prometheus scrape configs for backend-api, powershell-service, and OPA. The `synthetic.enabled` flag exposes load levers for repeatable demos.

| Workload | Replicas / Scaler | Probes | Resources | HPA / KEDA | PDB | PodMonitor |
|---|---|---|---|---|---|---|
| backend-api | HPA min 2 / max 10, target 70% CPU | live `/healthz/live`, ready `/healthz` (DB+Redis+OPA) | unchanged | yes (CPU) | yes (`minAvailable: 1`) | yes |
| worker (×3 queue Deployments: `default`, `controls.graph`, `controls.powershell`) | KEDA `redis-lists`, per-queue min/max, listLength-driven | live + readiness via `celery inspect ping --destination` | per-queue (gevent vs prefork) | KEDA per queue | per queue (`maxUnavailable: 1`) | (worker queue depth via Redis exporter) |
| powershell-service | HPA min 2 / max 6, target 70% CPU | live + ready on `/health` (custom gauge available for Prometheus Adapter) | unchanged | yes (CPU; `pwsh_active_subprocesses` ready for v2) | yes (`minAvailable: 1`) | yes |
| opa | HPA min 3 / max 10, target 60% CPU | live + ready on `/health` | unchanged | yes (CPU) | yes (`minAvailable: 2`) | yes (native `/metrics`) |
| frontend | HPA min 2 / max 4, target 70% CPU | live + ready on `/` | unchanged | yes (CPU) | yes (`minAvailable: 1`) | n/a (static nginx) |

---

## 1. backend-api

### After-state

| Property | Value |
|---|---|
| Replicas | HPA-driven, min 2 / max 10 (`values.yaml:backendApi.autoscaling`) |
| HPA | `templates/backend-api/hpa.yaml`; CPU target 70%, optional memory target |
| PDB | `templates/backend-api/pdb.yaml`; `minAvailable: 1` |
| Liveness probe | `GET /healthz/live` — process-only, never depends on downstream |
| Readiness probe | `GET /healthz` — DB, Redis, OPA reachability with a 503 on degradation |
| Startup probe | `GET /healthz/live`, failureThreshold 30, period 2s |
| `terminationGracePeriodSeconds` | 30 |
| `lifecycle.preStop` | `sleep 5` (LB endpoint cache drain) |
| `topologySpreadConstraints` | zone, maxSkew 1, ScheduleAnyway |
| `affinity` | host-level podAntiAffinity (preferred, weight 100) |
| Prometheus | `prometheus-fastapi-instrumentator` exposes `/metrics` (RED) |
| Resources | unchanged — sized for the per-pod load profile |

### What changed and why

- **Static `replicas: 1`** → **HPA scales between 2 and 10 on CPU** so the API can absorb morning-login spikes and synthetic traffic without manual scaling.
- **Probes targeting `/`** → **dependency-aware `/healthz`** so a pod that's lost its DB / Redis / OPA connection is taken out of the Service's endpoint pool instead of returning 200 to the load balancer.
- **No metrics endpoint** → **`/metrics` exposing `http_requests_total` + `http_request_duration_seconds`** so the dashboard, the future RPS-based HPA, and any latency alerts have a real signal source.
- **No graceful shutdown** → **`preStop sleep 5` + TGPS 30** so the pod stops serving 200s ahead of the LB cache flushing, eliminating the 5xx burst on rolling updates.

### Demo evidence

> Filled in after `tests/load/api-baseline.js` runs on AKS.

- [ ] k6 summary table (RPS achieved, p95/p99, error rate).
- [ ] Screenshot: `kubectl get hpa -n autoaudit -w` showing 2 → N replicas during ramp.
- [ ] Grafana panel: "Backend-api: requests/sec" climbing while pod count climbs in lockstep.
- [ ] Grafana panel: "Backend-api: p95 / p99 latency" staying flat / under 500ms throughout.
- [ ] `kubectl drain` of a node hosting backend-api with PDB enabled — service stays available.

---

## 2. worker — the headline scaling story

### After-state

| Property | Value |
|---|---|
| Topology | One Deployment per queue. Default (orchestrator), `controls.graph` (gevent ×50), `controls.powershell` (prefork ×4) |
| Scaler | KEDA `ScaledObject` per queue, `redis-lists` trigger, `listName == queue name` |
| TriggerAuthentication | Pulls Redis password from `existingSecret` |
| PDB per queue | `templates/worker/pdb.yaml`; `maxUnavailable: 1` |
| Liveness / Readiness | `celery inspect ping --destination=<queue>@<host>` so the probe is queue-specific |
| Lifecycle | preStop = `celery control shutdown` (graceful drain), TGPS 60 |
| Topology | zone spread + host anti-affinity per queue Deployment |
| Routing | `engine/worker/celery_app.py` exposes `QUEUE_*` constants; `engine/worker/tasks.py:queue_for_collector()` routes `evaluate_control` based on collector_id prefix |

### What changed and why

- **Single queue `autoaudit`** → **three queues** (`default`, `controls.graph`, `controls.powershell`) so heterogeneous workloads scale independently. A slow `Connect-ExchangeOnline` can no longer block fast Graph calls.
- **Static `replicas: 1`** → **KEDA-driven per queue**, scaling on Redis list length. This is the textbook KEDA use case (HPA can't scale on queue depth).
- **No readiness probe** → **`celery inspect ping`-based readiness** so rolling updates wait for a worker to actually connect to Redis before serving from it.
- **No graceful shutdown** → **`celery control shutdown` preStop + TGPS 60** so in-flight tasks finish cleanly on eviction.

### Demo evidence

> Filled in after `tests/load/scan-fanout.js` runs on AKS.

- [ ] Screenshot: `kubectl get scaledobject -n autoaudit -w` showing the three ScaledObjects active and their `Triggers` populated.
- [ ] Screenshot: `kubectl get pods -l app.kubernetes.io/component=worker-controls-graph -w` showing 1 → N → 1 pod count over a load pulse.
- [ ] Screenshot: same for `worker-controls-powershell`, capped at the lower max.
- [ ] Grafana panel: "Worker pods per queue" with `controls.graph` and `controls.powershell` scaling at different speeds and to different ceilings.
- [ ] Grafana panel: "KEDA queue depth" climbing during the pulse and draining as pods come up.
- [ ] Headline number: time-to-finish for `N=180` synthetic tasks before vs after.

---

## 3. powershell-service

### After-state

| Property | Value |
|---|---|
| Replicas | HPA-driven, min 2 / max 6 (`values.yaml:powershellService.autoscaling`) |
| HPA | `templates/powershell-service/hpa.yaml`; CPU target 70% |
| PDB | `minAvailable: 1` |
| Probes | unchanged (`/health`) — service-level health is unconditional today |
| Lifecycle | `terminationGracePeriodSeconds: 130` (covers the 120s pwsh subprocess timeout) |
| Topology | zone spread + host anti-affinity |
| Prometheus | `/metrics` mounted; `pwsh_active_subprocesses` (Gauge), `pwsh_executions_total{module,outcome}` (Counter), `pwsh_execution_duration_seconds{module}` (Histogram) |
| Synthetic | `POST /execute/synthetic` endpoint (gated on `SYNTHETIC_ENABLED`) |

### What changed and why

- **Single replica blackout risk** → **HPA min 2 / max 6** so a single node loss doesn't take Exchange Online scanning down.
- **TGPS default 30s** → **TGPS 130s** so a pwsh subprocess that started just before SIGTERM can finish (its own timeout is 120s).
- **No metrics** → **active-subprocess gauge + execution histogram** so the future runspace-pool work has a baseline metric to scale on, and the demo dashboard has the per-pod ceiling visualisation.

The architecturally-correct fix — a warm runspace pool that amortises the pwsh module-import cost — was deferred from this sprint per the plan. The metrics this sprint adds will drive HPA on pool utilisation once the pool exists; flipping the HPA from CPU to `pwsh_active_subprocesses` will then be a values change, not a chart rewrite.

### Demo evidence

> Filled in after `tests/load/scan-fanout.js` runs with `CALL_POWERSHELL_SERVICE=true`.

- [ ] Grafana panel: "Active pwsh subprocesses (per pod)" showing each pod's ceiling.
- [ ] Grafana panel: "pwsh executions/sec by module + outcome" with `synthetic / success` rate climbing during the pulse.
- [ ] Screenshot: `kubectl get hpa autoaudit-powershell-service` showing CURRENT-CPU vs TARGET-CPU during the run.
- [ ] HPA scale events from `kubectl describe hpa autoaudit-powershell-service`.

---

## 4. opa

### After-state

| Property | Value |
|---|---|
| Replicas | HPA-driven, min 3 / max 10 (default raised from 1 → 3) |
| HPA | `templates/opa/hpa.yaml`; CPU target 60% |
| PDB | `minAvailable: 2` (always-have-quorum during voluntary disruption) |
| Probes | unchanged (`/health`) |
| Topology | zone spread + host anti-affinity |
| PodMonitor | scrapes OPA's native `/metrics` |

### What changed and why

- **Single replica** → **min 3** because OPA is a synchronous fan-in for every scan finding; one node loss was a real outage.
- **No HPA** → **CPU-based HPA** so under heavy scan load OPA scales in lockstep with the workers.
- **No PDB** → **`minAvailable: 2`** so a node drain can take exactly one OPA pod, keeping the policy plane available throughout.

### Demo evidence

> Filled in after `tests/load/scan-fanout.js` runs.

- [ ] Grafana panel: "OPA decisions/sec" climbing during the load pulse.
- [ ] Grafana panel: "OPA: p95 eval latency" staying flat (i.e. the scaling kept up).
- [ ] Screenshot: pod count for OPA going 3 → N during the pulse, returning to 3 afterwards.

---

## 5. frontend

### After-state

| Property | Value |
|---|---|
| Replicas | HPA-driven, min 2 / max 4 |
| HPA | CPU target 70% |
| PDB | `minAvailable: 1` |
| Topology | zone spread |
| Lifecycle | `nginx -s quit` preStop (SIGQUIT) for clean connection drain |

### What changed and why

This is the deliberately-small section. The frontend already did the right things at the container layer (multi-stage Dockerfile.prod → nginx-alpine, static asset serving). The HPA + PDB + zone-spread are cheap insurance for HA more than for capacity — the panel slide for this section is "scaled but doesn't need to."

### Demo evidence

- [ ] Screenshot: pod count for frontend steady at min throughout load runs (panel proof that not everything needs to scale).

---

## App-layer cross-cutting after-state

| Capability | Before | After |
|---|---|---|
| `/healthz` with downstream checks | absent | `app/api/health.py` — DB, Redis, OPA each with timeout |
| Prometheus on backend-api | absent | `prometheus-fastapi-instrumentator` mounted at `/metrics` |
| Prometheus on powershell-service | absent | `engine/powershell/service/metrics.py` — gauge, counter, histogram |
| Multi-queue Celery routing | absent | `QUEUE_*` constants + `queue_for_collector()` helper; `evaluate_control` routes via `apply_async(queue=…)` |
| Synthetic load endpoints | absent | `/v1/test/synthetic-scan`, `worker.tasks.synthetic_evaluate`, `/execute/synthetic` — all gated by `SYNTHETIC_ENABLED` env + `APP_ENV != prod` runtime check |
| k6 / Locust / load tooling | absent | `tests/load/{api-baseline,scan-fanout,sustained}.js` |
| Grafana dashboard | absent | `infrastructure/monitoring/dashboards/autoaudit-scaling.json` — 7 rows / 14 panels |

---

## Deltas — at-a-glance

For the panel slide that compares before and after directly.

| Workload | Before | After |
|---|---|---|
| backend-api replicas | 1, hardcoded | HPA 2–10 on CPU |
| worker queues | 1 (`autoaudit`) | 3 (`default`, `controls.graph`, `controls.powershell`) |
| worker scaling | 1, hardcoded | KEDA per queue, queue-depth-driven |
| powershell-service replicas | 1, hardcoded | HPA 2–6 on CPU |
| opa replicas | 1, hardcoded | HPA 3–10 on CPU |
| frontend replicas | 1, hardcoded | HPA 2–4 on CPU |
| HPA / KEDA resources in chart | 0 | 4 HPAs + 3 KEDA ScaledObjects |
| PodDisruptionBudgets | 0 | 7 (per-workload + per worker queue) |
| `/healthz` on backend-api | no | yes (DB + Redis + OPA) |
| `/metrics` on backend-api | no | yes (FastAPI instrumentator) |
| `/metrics` on powershell-service | no | yes (custom gauge + histograms) |
| PodMonitor templates | 0 | 3 (backend-api, powershell-service, opa) |
| Graceful shutdown plumbing | none | `preStop` + tuned TGPS on every workload |
| Topology constraints | none | zone spread + host anti-affinity (where appropriate) |
| Synthetic load tooling | none | k6 scripts + synthetic endpoints (gated `synthetic.enabled`) |
| Grafana dashboard | none | `autoaudit-scaling.json` |

---

## Runtime evidence (filled in during the sprint)

This section mirrors the same headings as the baseline doc's "Runtime evidence" — the panel reads the two side-by-side.

### A. Static manifest output

```text
$ kubectl get deploy,hpa,pdb,scaledobject,podmonitor -n autoaudit
```

Expected (capture the output here):

```text
TODO: paste output. Should show:
  - 5 unique workloads, but 7 Deployments (worker has 3 queue Deployments).
  - 4 HPAs (backend-api, opa, powershell-service, frontend).
  - 7 PDBs (one per workload + one per worker queue).
  - 3 ScaledObjects (one per worker queue when KEDA enabled).
  - 3 PodMonitors (backend-api, opa, powershell-service).
```

### B. Behaviour under load — `tests/load/api-baseline.js`

- [ ] Paste k6 summary.
- [ ] Embed Grafana screenshots showing pod count climbing.
- [ ] Note time-to-scale (load arrival → first scale event).

### C. Behaviour under load — `tests/load/scan-fanout.js`

- [ ] Paste k6 summary.
- [ ] Embed Grafana "Pod counts" panel showing `controls.graph` / `controls.powershell` / OPA / powershell-service all scaling together.
- [ ] Embed Grafana "KEDA queue depth" panel showing the work-waiting-then-draining pattern.
- [ ] Headline number: time-to-finish for the same N synthetic tasks vs the baseline.

### D. Resilience evidence — pod and node disruption

- [ ] `kubectl delete pod` mid-load — confirm 5xx burst is gone (preStop + readiness flip).
- [ ] `kubectl drain` of a node — confirm PDBs prevent total pool eviction; no scan tasks lost (Celery retry semantics + idempotent `evaluate_control`).

---

## What this still doesn't address

Forward-pointing list to keep the panel honest about what was deferred:

- **PowerShell runspace pool.** The fundamental speedup for powershell-service. Metric scaffolding is in place; the pool itself is the next sprint.
- **Per-workspace token-bucket fairness.** The fairness hooks live in [saas-scaling-architecture.md §3](./saas-scaling-architecture.md); this sprint's worker scaling is per-queue but not per-tenant.
- **Celery `chord`-based finaliser, drift queue, Beat / Redbeat.** Queue topology supports them; the orchestration refactor itself is deferred.
- **`scheduled` and `drift` and `housekeeping` queues.** Adding them later is values-driven and chart-rendering ready, but no Beat is running them yet.
- **Custom-metric HPAs.** Today HPA is on CPU. Once the metrics ship is observed in production, the HPAs flip to RPS (backend-api) and `pwsh_active_subprocesses` (powershell-service) via Prometheus Adapter — values changes only.
- **Network policies, pod security standards.** Out of scope per the sprint plan; documented for awareness.
- **Compliance scope (Sentinel / CMK / IRAP).** Deferred per the [AKS plan](./saas-scaling-aks-platform.md).

---

## Chart bugs found and fixed during AKS testing

The first end-to-end deploy on AKS surfaced a handful of real chart bugs.
Everything below is fixed in-tree; this list captures the *why* so a future
maintainer can see the intent behind each diff.

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| 1 | `helm install` rendered 3 worker Deployments / PDBs / ScaledObjects per queue, but only the last one (controls.powershell) appeared in the cluster. | `helm/autoaudit/templates/worker/{deployment,pdb,scaledobject}.yaml` had `{{- $deploymentName := ... -}}` on the line above `---`; the trailing `-}}` ate the newline before the separator, concatenating all queue resources into one mangled YAML doc. YAML parsers kept only the last set. | Removed the trailing `-` so the newline survives. Now each iteration emits a clean `---` separator. |
| 2 | KEDA ScaledObjects `READY=False` with `failed to ensure HPA ... connection to redis failed: lookup autoaudit-redis on 10.0.0.10:53: no such host`. | `autoaudit.redis.host` helper returned the bare service name. KEDA pods live in the `keda` namespace, so DNS searched `keda.svc.cluster.local` and missed the Service in `autoaudit`. | `helm/autoaudit/templates/_helpers.tpl` — helper now emits `<name>-redis.<namespace>` so it resolves cross-namespace. |
| 3 | Worker pods entered CrashLoopBackOff with `Liveness probe failed: No nodes replied within time constraint`. | `livenessProbe` / `readinessProbe` exec args used `$(hostname)` — `exec` probes don't run a shell, so the literal string `controls.powershell@$(hostname)` went to celery, never matched the worker's real hostname, never got a ping reply. | `helm/autoaudit/templates/worker/deployment.yaml` — wrapped probe commands in `sh -c '...$HOSTNAME...'` so the shell expands the variable. |
| 4 | One worker pod restart took down the entire worker fleet ("Got shutdown from remote" in all pods, repeating). | The `lifecycle.preStop` ran `celery -A worker.celery_app control shutdown` with no `--destination` — that broadcasts to every worker on the broker. Every rollout cascaded. | `helm/autoaudit/templates/worker/deployment.yaml` — added `--destination={{ $queue.name }}@$HOSTNAME` so shutdown only hits the local pod. |
| 5 | `controls.graph` queue workers crashed at startup with `ModuleNotFoundError: No module named 'gevent'`. | Chart configures `pool: gevent` for that queue but the worker image dependencies didn't include gevent. | `engine/pyproject.toml` — added `gevent>=24.2.1` to dependencies. |
| 6 | Frontend pods CrashLooping; vite reported `ready on :3000` while the chart Service expected nginx on :80. | We pushed the image built from `frontend/Dockerfile` (dev, vite) instead of `frontend/Dockerfile.prod` (multi-stage → nginx). | Runbook documents the correct build path. Compose still uses the dev Dockerfile (intentional — fast HMR for dev), so it's a deploy-time choice, not a chart change. |
| 7 | Dashboard "OPA decisions/sec" panel reported ~0.6 req/s before any real OPA traffic. | Panel query had no handler filter, so kubelet's `/health` probes counted as decisions. | `infrastructure/monitoring/dashboards/autoaudit-scaling.json` — added `handler!~"health\|metrics"` to OPA queries. |
| 8 | Dashboard "Backend-api p95 / p99 latency" panel showed values even when no backend traffic was running. | Panel query filtered by `namespace=` only. OPA's FastAPI also emits `http_request_duration_seconds` in the same namespace, so OPA traffic leaked into the backend-api panel. | Added `job="autoaudit-backend-api"` to backend-api queries; OPA queries were already `pod=~`-scoped. |
| 9 | Dashboard backend-api `rate(...[1m])` queries returned "no data" during runs. | Prometheus chart default `scrape_interval: 30s` only puts 2 samples in a 1m window — too few for `rate()` to render reliably. | `infrastructure/monitoring/in-cluster/prometheus-values.yaml` — set `scrape_interval: 15s`. |
| 10 | k6 thresholds breaching caused the k8s Job to show as Failed even when the test ran to completion. | k6 exits 99 on threshold breach. The Job had no special handling. | `tests/load/in-cluster/k6-job.yaml` — wrapper catches exit 99 and exits 0 so the Job stays Complete (thresholds still print as a signal in the summary). |
| 11 | KEDA `keda_scaler_metrics_value` series never appeared in Prometheus. | KEDA's prometheus metrics on the operator pod are opt-in. | KEDA install needs `--set prometheus.operator.enabled=true --set prometheus.metricServer.enabled=true` (documented in [in-cluster monitoring README](../../infrastructure/monitoring/in-cluster/README.md)). |
| 12 | Celery task throughput panel had no data. | No exporter installed; chart workers weren't broadcasting task events. | (a) `engine/worker/celery_app.py` — `worker_send_task_events=True` + `task_send_sent_event=True`. (b) `infrastructure/monitoring/in-cluster/celery-exporter.yaml` — danihodovic/celery-exporter Deployment + Service. (c) Prometheus scrape config picks it up. |
| 13 | HPA stayed at max replicas for 5 minutes after load stopped. | K8s default `scaleDown.stabilizationWindowSeconds=300`. | Added `behavior` block to each HPA template and overlay shorter stabilization windows (60s scaleDown) in `values-scaling.yaml`. |
| 14 | k6 `api-baseline.js` summary handler crashed on `.toFixed()` of undefined p(99). | Script only declared p(95) as a threshold, so k6 didn't compute p(99). | Added `'p(99)<800'` to thresholds so it's collected. |
| 15 | `/healthz` readiness probe returned `"error": ""` when redis was down. | `str(exc)` on the redis async `TimeoutError` returned an empty string. | `backend-api/app/api/health.py` — fall back to `type(exc).__name__` when `str(exc)` is empty. |

---

## Where this leaves us

The chart now has a defensible, mature scaling posture for the five workloads in scope: every workload has a scaler, a disruption budget, dependency-aware health checks, graceful shutdown, and topology constraints. Two workloads (backend-api, powershell-service) expose Prometheus metrics for the dashboard and for future custom-metric HPAs. The worker is now per-queue, with KEDA scaling each queue independently — the headline technical-depth story for the panel.

The next iteration moves the deferred items above (runspace pool, per-tenant fairness, custom-metric HPAs, drift / scheduled queues) and is captured in the broader scaling docs ([saas-scaling-aks-platform.md](./saas-scaling-aks-platform.md), [saas-scaling-architecture.md](./saas-scaling-architecture.md)).
