# AutoAudit — AKS Scaling Baseline

> **Status:** Captured 2026-05-10 from the `feature/proof-of-concept-deployment-26t1-imp-dha-003` branch, against the live POC chart at `helm/autoaudit/`.
>
> This document is the **panel "before" snapshot**. Its companion is [scaling-after.md](./scaling-after.md) (filled in at the end of the implementation sprint). Together they show what changed and by how much.

## Why this document exists

The proof-of-concept demonstrated AutoAudit running end-to-end on AKS. The panel needs to see the *next-stage* engineering: how we take that POC and prepare it to scale as a multi-tenant SaaS. This baseline captures the chart and application as they exist today — every replicaCount, every probe, every queue, every gap — so the changes that follow can be measured against a recorded starting point, not against memory.

Scope is deliberate. This document covers only the five long-running workloads that need to scale: **`backend-api`, `worker`, `powershell-service`, `opa`, `frontend`**. Other AKS concerns (cluster topology, Postgres PaaS, ingress, identity, image supply chain) are addressed elsewhere ([saas-scaling-aks-platform.md](./saas-scaling-aks-platform.md)) and are not part of this sprint.

## How to read this document

Each workload section lists:

- **Replicas** — what's set today and where.
- **Probes** — liveness / readiness / startup state.
- **Resources** — requests and limits.
- **Lifecycle** — graceful-shutdown plumbing.
- **Topology** — anti-affinity / spread.
- **Autoscaling** — what's in place. (Spoiler: nothing.)
- **Disruption budget** — what's in place. (Spoiler: nothing.)
- **Observability hooks** — what Prometheus / metrics exposure exists.

A "Gaps" subsection at the end of each workload calls out the deltas the implementation sprint will close.

File paths and line numbers are quoted throughout. Where a capability is absent, the entry says `none` so it's unambiguous.

---

## Chart-wide baseline summary

Every workload in the chart is **`replicaCount: 1`, hardcoded**, with **no HorizontalPodAutoscaler**, **no PodDisruptionBudget**, **no KEDA `ScaledObject`**, and **no `PodMonitor` / `ServiceMonitor` / `PrometheusRule`** templates. None of the five Deployments have `topologySpreadConstraints`, `podAntiAffinity`, `startupProbe`, `terminationGracePeriodSeconds`, or `lifecycle.preStop` configured.

| Workload | Replicas | Liveness | Readiness | Startup | preStop | TGPS | Anti-affinity | HPA | PDB | KEDA | PodMonitor |
|---|---|---|---|---|---|---|---|---|---|---|---|
| backend-api | 1 | `GET /` | `GET /` | none | none | none | none | none | none | none | none |
| worker | 1 | `celery inspect ping` | **none** | none | none | none | none | none | none | none | none |
| powershell-service | 1 | `GET /health` | `GET /health` | none | none | none | none | none | none | none | none |
| opa | 1 | `GET /health` | `GET /health` | none | none | none | none | none | none | none | none |
| frontend | 1 | `GET /` | `GET /` | none | none | none | none | none | none | none | none |

Static replicas are bound directly to `.Values.{component}.replicaCount` in every deployment template, so no runtime mechanism today can grow or shrink the workload count.

---

## 1. backend-api

**Deployment template:** `helm/autoaudit/templates/backend-api/deployment.yaml`

### Current state

| Property | Value | Source |
|---|---|---|
| Replicas | 1 | `templates/backend-api/deployment.yaml:8`, `values.yaml:63` |
| Strategy | default RollingUpdate (25%/25%) | not declared in template |
| Liveness probe | `GET /` every 10s, initial delay 15s | `deployment.yaml:34-41` |
| Readiness probe | `GET /` every 5s, initial delay 10s | `deployment.yaml:42-49` |
| Startup probe | none | — |
| `terminationGracePeriodSeconds` | none (Kubernetes default 30s) | — |
| `lifecycle.preStop` | none | — |
| `topologySpreadConstraints` | none | — |
| `affinity` / `podAntiAffinity` | none | — |
| Resources requests | CPU 250m, memory 512Mi | `values.yaml:80-83` |
| Resources limits | CPU 1, memory 1Gi | `values.yaml:84-86` |

### Application-layer state

- **No `/health` or `/healthz` endpoint.** Probes hit `/`, which `backend-api/app/main.py:34` returns with `{"status": "ok"}`. The probe doesn't verify DB/Redis/OPA connectivity, so a pod with broken downstream connectivity passes readiness.
- **No Prometheus instrumentation.** `prometheus_client` and `prometheus-fastapi-instrumentator` are absent from `backend-api/pyproject.toml` and the codebase. No `/metrics` endpoint.
- **Endpoints under `app/api/v1/`:** `auth`, `test`, `platforms`, `m365_connections`, `scans`, `benchmarks`, `evidence`, `contact`, `settings`. The `test` router (`app/api/v1/test.py`) already provides `/test/public`, `/test/protected`, `/test/protected-admin`, `/test/protected-auditor` — useful baseline endpoints for auth/RBAC load.
- **Scan trigger:** `POST /v1/scans` enqueues `worker.tasks.run_scan` to the Celery queue `autoaudit` (`app/api/v1/scans.py:114-115`, `app/services/celery_client.py:25`).
- **Middleware** (`backend-api/app/main.py`): request-logging only; no rate limiting; no per-request `request_id` propagation.

### Gaps the sprint will close

1. No autoscaling primitive of any kind (HPA missing).
2. No PodDisruptionBudget — pod can be evicted at any time during a node drain.
3. Probe targets `/`, not a real health check.
4. No Prometheus instrumentation, so RPS-based or latency-based scaling has no signal source.
5. No graceful-shutdown plumbing — in-flight requests can be killed mid-response.
6. No anti-affinity or zone-spread, so two pods can land on the same node and a single node loss doubles as a service outage.

---

## 2. worker — the headline gap

**Deployment template:** `helm/autoaudit/templates/worker/deployment.yaml`

### Current state — Helm

| Property | Value | Source |
|---|---|---|
| Replicas | 1 | `templates/worker/deployment.yaml:8`, `values.yaml:90` |
| Command | `celery -A worker.celery_app worker --pool=prefork --concurrency=4 --loglevel=info` | `deployment.yaml:23-30`, `values.yaml:95-98` |
| Liveness probe | `celery inspect ping` (exec, 30s period, 30s initial delay) | `deployment.yaml:33-46` |
| Readiness probe | **none** | — |
| Startup probe | none | — |
| `terminationGracePeriodSeconds` | none (Kubernetes default 30s — too short for in-flight tasks) | — |
| `lifecycle.preStop` | none | — |
| `topologySpreadConstraints` | none | — |
| `affinity` / `podAntiAffinity` | none | — |
| Resources requests | CPU 500m, memory 512Mi | `values.yaml:100-102` |
| Resources limits | CPU 2, memory 2Gi | `values.yaml:103-105` |

### Current state — application

- **Single queue, single worker pool.** `engine/worker/celery_app.py:8-12` constructs the Celery app with broker = Redis, **no result backend**. `celery_app.py:26` sets `task_default_queue="autoaudit"` — the only queue used today.
- **No `task_routes` configured.** All tasks land on the default queue.
- **No Beat / Redbeat scheduler.** No `app/scheduled/`, no periodic-task definitions, no Beat container.
- **Pool mismatch:** `celery_app.py:31` has `worker_concurrency=10` (gevent-style), but the deployment command passes `--pool=prefork --concurrency=4` which overrides at CLI level. So today's effective config is `prefork × 4` per pod.
- **Fan-out model:** `engine/worker/tasks.py:51` defines `run_scan(scan_id)` which iterates pending controls and uses plain `evaluate_control.delay()` (`tasks.py:164`) — no `chord`, no `group`. The "last task to complete" calls `finalize_scan_if_complete()` (documented race in [saas-scaling-architecture.md §3]).
- **Tasks defined:** `run_scan` (orchestrator), `evaluate_control` (per-control evaluator). `evaluate_control._evaluate_control_async()` (`tasks.py:324`) routes to `PowerShellClient` or `GraphClient` based on `collector_id` prefix at `tasks.py:360-375`. This is the natural seam for queue routing — the routing is already happening, it just isn't a Celery routing decision yet.

### Why this workload is the headline

The application's scan pipeline already routes work to two very different downstream collectors — Microsoft Graph (HTTP/IO-bound, fast, parallelisable to dozens of concurrent calls per pod) and Exchange Online via the powershell-service (CPU/process-bound, slow, bounded by service capacity). Today they share a single queue with `prefork × 4`. A slow Exchange cmdlet behind a fast Graph call is the exact failure mode the sprint will fix.

### Gaps the sprint will close

1. Single-queue topology — workloads with incompatible concurrency profiles compete on the same pool.
2. No HPA, no KEDA — worker count cannot grow with backlog.
3. No PDB — voluntary disruption can wipe out the worker pool.
4. No readiness probe — rolling updates can briefly serve traffic to a worker that hasn't connected to Redis.
5. No graceful shutdown — TGPS=30s default cuts off Celery tasks that take longer than that.
6. No metrics exposure for queue depth or task throughput.

---

## 3. powershell-service

**Deployment template:** `helm/autoaudit/templates/powershell-service/deployment.yaml`

### Current state — Helm

| Property | Value | Source |
|---|---|---|
| Replicas | 1 | `templates/powershell-service/deployment.yaml:8`, `values.yaml:146` |
| Liveness probe | `GET /health` every 10s, initial delay 30s | `deployment.yaml:30-37` |
| Readiness probe | `GET /health` every 10s, initial delay 10s | `deployment.yaml:38-45` |
| Startup probe | none | — |
| `terminationGracePeriodSeconds` | none — pwsh subprocess timeout is 120s (`executor.py:185`); default TGPS truncates in-flight executions | — |
| `lifecycle.preStop` | none | — |
| `topologySpreadConstraints` | none | — |
| `affinity` / `podAntiAffinity` | none | — |
| `nodeSelector` | `kubernetes.io/arch: amd64` | `values.yaml:154-155`, `deployment.yaml:18-20` |
| Resources requests | CPU 250m, memory 512Mi | `values.yaml:157-159` |
| Resources limits | CPU 1, memory 1Gi | `values.yaml:160-162` |

### Current state — application

- **FastAPI** at `engine/powershell/service/main.py`. Routes: `GET /health` (returns `{"status": "ok"}`, `main.py:15`) and `POST /execute` (`main.py:21`).
- **Execution model: subprocess-per-request.** `engine/powershell/service/executor.py:181` is `subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-Command", script], ..., timeout=120)`. Each request spawns a fresh `pwsh` process — full module-import cost (5–15s for ExchangeOnlineManagement) on every call.
- **No concurrency limit** inside the service. With FastAPI's default uvicorn settings, requests can pile up unbounded against a single pod.
- **No `/metrics` endpoint, no `prometheus_client` dependency.** No way to count active subprocesses, request rate, or pool utilisation today.
- **`/health` is unconditional** — does not validate `pwsh` is on PATH, does not validate Exchange Online module is loadable.

### Why this workload needs a separate scaling story

The subprocess-per-request model means each in-flight cmdlet pegs ~1 core for ~5–15s of module import + actual work. CPU correlates well with active execution (unlike backend-api, where CPU under-reports IO-wait load). The right architectural answer is a runspace pool — but that's multi-day work and not needed to *demonstrate* scaling. CPU-based HPA is the right fit for now; the sprint adds a `pwsh_active_subprocesses` gauge so the metric is in place when the pool work happens later.

### Gaps the sprint will close

1. No HPA — pod count cannot grow with concurrent cmdlet load.
2. No PDB.
3. No `/metrics` and no active-subprocess gauge.
4. `/health` doesn't reflect actual readiness.
5. TGPS missing — in-flight pwsh runs can be SIGKILLed before their 120s timeout.
6. Single replica means a single node restart blackouts all M365 PowerShell scanning.

---

## 4. opa

**Deployment template:** `helm/autoaudit/templates/opa/deployment.yaml`

### Current state

| Property | Value | Source |
|---|---|---|
| Replicas | 1 | `templates/opa/deployment.yaml:8`, `values.yaml:127` |
| Args | `run --server --addr=0.0.0.0:8181 --log-level=info /policies` | `deployment.yaml:22-27` |
| Liveness probe | `GET /health` every 10s, initial delay 10s | `deployment.yaml:32-39` |
| Readiness probe | `GET /health` every 10s, initial delay 5s | `deployment.yaml:40-47` |
| Startup probe | none | — |
| `terminationGracePeriodSeconds` | none | — |
| `lifecycle.preStop` | none | — |
| `topologySpreadConstraints` | none | — |
| `affinity` / `podAntiAffinity` | none | — |
| Resources requests | CPU 100m, memory 128Mi | `values.yaml:136-138` |
| Resources limits | CPU 500m, memory 256Mi | `values.yaml:139-142` |

### Application-layer state

- **OPA exposes `/metrics` natively** (Prometheus format) — zero application-side instrumentation work needed; only a `PodMonitor` to scrape it.
- **Policy bundle baked into image** (`autoaudit/opa` repository, `args` mount `/policies`). No bundle service, no signed bundles, no hot-reload at this stage.
- **Worker access pattern** (`engine/opa_client.py:42-46`): `httpx.AsyncClient.post(f"{base_url}/v1/data/{url_path}/result", ...)` per `evaluate_control` task. No client-side cache; every control evaluation hits OPA fresh.

### Why a single OPA replica is a real risk

Every scan finding goes through OPA. With the worker scaling to N pods running concurrent `evaluate_control` tasks, OPA becomes a synchronous fan-in. One replica is a blast-radius problem (any node restart = scanning halts) before it is a capacity problem.

### Gaps the sprint will close

1. Single replica — node-loss kills all policy evaluation.
2. No HPA — even when scans pile up, OPA stays at 1.
3. No PDB.
4. Native `/metrics` is unscrape-able without a `PodMonitor`.
5. No anti-affinity — the single replica that exists has no zone-spread story.

---

## 5. frontend

**Deployment template:** `helm/autoaudit/templates/frontend/deployment.yaml`

### Current state

| Property | Value | Source |
|---|---|---|
| Replicas | 1 | `templates/frontend/deployment.yaml:8`, `values.yaml:109` |
| Image | `autoaudit/frontend` (nginx serving `/dist/`) | `values.yaml:110-113`, `frontend/Dockerfile.prod` |
| Liveness probe | `GET /` every 10s, initial delay 5s | `deployment.yaml:26-33` |
| Readiness probe | `GET /` every 5s, initial delay 5s | `deployment.yaml:34-41` |
| Startup probe | none | — |
| `terminationGracePeriodSeconds` | none | — |
| `lifecycle.preStop` | none | — |
| `topologySpreadConstraints` | none | — |
| `affinity` / `podAntiAffinity` | none | — |
| Resources requests | CPU 50m, memory 64Mi | `values.yaml:118-120` |
| Resources limits | CPU 200m, memory 128Mi | `values.yaml:121-123` |

### Why frontend is the small section

The frontend is already doing the right things at the container layer: `frontend/Dockerfile.prod` is a multi-stage build that ends in nginx-alpine serving static assets. CPU rarely climbs because the work is just file serving and TLS termination upstream. The point of including it in this baseline is **completeness for the panel** — every workload is accounted for, even when the answer is "scaled but doesn't need to."

### Gaps the sprint will close

1. Single replica — same node-loss blast-radius story as the others.
2. No HPA — even at min/max 2/4, two replicas is the cheap-insurance baseline for HA.
3. No PDB.

---

## App-layer cross-cutting baseline

These are the application-side characteristics that affect *whether scaling can happen at all*:

| Capability | State today | Implication for scaling |
|---|---|---|
| `/healthz` with downstream checks | Absent | Probes can't reflect dependency health; HPA scale-down may target healthy-looking pods that have lost Redis connectivity |
| Prometheus metrics on backend-api | Absent | No RPS or latency signal for HPA's custom-metrics path |
| Prometheus metrics on powershell-service | Absent | No `pwsh_active_subprocesses` for HPA's custom-metrics path |
| Multi-queue Celery routing | Absent | All scan work serialises through one pool; can't scale Graph independently of PowerShell |
| Celery result backend | Disabled (`celery_app.py:8-12`) | No `chord`-based finaliser available; the existing finaliser race ([ARCH §3]) remains |
| Synthetic load endpoints | Absent | No way to demonstrate scaling under load without real M365 tenant credentials |
| k6 / Locust / load tooling | Absent | No `tests/load/`, no scripts in repo |
| Existing test endpoints | Present (`app/api/v1/test.py`) | `/test/public` and `/test/protected` are usable as-is for HTTP-layer load |

---

## Runtime evidence (filled in during the sprint)

This section is the panel-facing numerical "before" — it is captured by running the unmodified chart on the AKS dev cluster and recording observed behaviour.

### A. Static manifest output

```text
# Run before any chart changes:
$ kubectl get deploy,hpa,pdb,scaledobject,podmonitor -n autoaudit
```

Expected output (paste here when captured):

```text
TODO: paste output. Expected to show 5 Deployments, all replicas=1, and zero HPA/PDB/ScaledObject/PodMonitor resources.
```

### B. Behaviour under load — `tests/load/api-baseline.js` against unmodified chart

```text
# Run after kube-prometheus-stack is installed but before chart changes:
$ k6 run tests/load/api-baseline.js
```

Capture and paste:

- k6 summary table (RPS achieved, p95/p99 latency, error rate).
- Screenshot of `kubectl get pods -n autoaudit -w` showing pod count flat at `1/1` for backend-api throughout the run.
- Screenshot of Grafana panel showing CPU climbing on the single backend-api pod with no scale event.

### C. Behaviour under load — `tests/load/scan-fanout.js` against unmodified chart

Capture and paste:

- k6 summary table.
- Screenshot of `kubectl get pods -n autoaudit -w` showing worker pod count flat at `1/1` while Redis queue depth grows.
- Screenshot of Grafana panel showing `controls.graph` and `controls.powershell` queue depths (both populated even though only one queue exists today — the script uses the routing arg that maps to the existing single queue) climbing without scale-out.
- Time-to-finish for a fixed N-control scan, used as the headline number for the "after" comparison.

### D. Resilience evidence — single-pod blast radius

Capture and paste:

- `kubectl delete pod <backend-api-pod>` mid-load — record duration of 5xx errors.
- `kubectl drain <node>` of any node hosting AutoAudit pods — record what fails.

---

## What this baseline does *not* address

Out of scope for this sprint, recorded so the panel sees the conscious deferral:

- **Cluster topology / node pools / NAP** — covered in [saas-scaling-aks-platform.md §1](./saas-scaling-aks-platform.md#1-aks-cluster-topology), unchanged here.
- **PostgreSQL Flex Server migration** — covered in [§2a](./saas-scaling-aks-platform.md#2a-postgresql--azure-database-for-postgresql-flexible-server), unchanged here.
- **Ingress / Gateway / Front Door** — covered in [§3](./saas-scaling-aks-platform.md#3-networking--ingress).
- **Identity, Workload Identity, ESO** — covered in [§4](./saas-scaling-aks-platform.md#4-identity--secrets).
- **ACR / image signing / multi-arch** — covered in [§5](./saas-scaling-aks-platform.md#5-image--build-supply-chain).
- **Per-workspace tenancy / token-bucket fairness** — application-layer concern in [saas-scaling-architecture.md §1](./saas-scaling-architecture.md), not addressed by this scaling sprint.
- **PowerShell runspace pool** — the architecturally-correct speedup for `powershell-service`. Acknowledged but deferred; the sprint adds the metric scaffolding so it can be flipped to drive scaling later.
- **Celery `chord`-based finaliser, drift queue, Beat/Redbeat** — additional queues are values-driven so adding them later is a values change, not a chart change.
- **Network policies** — absent today, called out for awareness, not closed by this sprint.

---

## Where this leads

The implementation plan at `~/.claude/plans/no-need-for-the-distributed-swan.md` (or its content as merged into this repo) lays out the day-by-day work that closes the gaps in this baseline. After implementation, [scaling-after.md](./scaling-after.md) records the same workload table with the new state and a deltas comparison, so the panel sees both the starting point (this document) and the destination (that document) in matching shape.
