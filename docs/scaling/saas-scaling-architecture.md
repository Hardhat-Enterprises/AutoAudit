# AutoAudit — SaaS Scaling: Logical Architecture Deep-Dive

> **Status:** Planning. Companion to [saas-scaling-aks-platform.md](./saas-scaling-aks-platform.md). All decisions here are **revisitable** — the doc states defaults so we can move forward, not because they are final.

## Why this document exists

The proof-of-concept on `feature/proof-of-concept-deployment-26t1-imp-dha-003` was published live and worked. The next step is to take AutoAudit from a per-user prototype to a multi-tenant SaaS that can host hundreds of M365 customer organisations on AKS. This document covers the *logical* changes — schema, API shape, scan pipeline, OPA, secrets, observability. **Platform engineering on AKS** (cluster topology, autoscalers, ingress, GitOps) is a separate document because the two concerns can be reasoned about independently and changed independently.

## Decisions that frame this document

| Decision | Value |
|---|---|
| Scale target | Mid-market, 100s of M365 tenant organisations |
| Customer model | Workspaces with multiple users; per-membership roles (owner / admin / auditor / viewer) |
| Audit targets | M365 / Azure now; extensibility for further frameworks |
| Scan cadence | On-demand + per-tenant scheduled + continuous drift; no event-driven webhooks at MVP |
| Tenant compute isolation | Pooled, with hooks designed in for per-tier or per-tenant separation later |
| Compliance scope (IRAP / ISO 27001 / SOC 2) | Out of scope for MVP, documented as upgrade path in the AKS doc |

## Component-maturity bar

Every recommendation here points at a mature, off-the-shelf component (CNCF graduated/incubating, vendor-supported, or in broad production use). When two mature options exist the rejection reasoning is recorded so the design history is preserved. We are explicitly **avoiding developer-driven assemblies** of small libraries when a well-known component already does the job.

## How to read this document

Each section follows the same shape:

1. **Recommendation** — the position and the off-the-shelf component it leans on
2. **Alternatives considered** — what we rejected and why
3. **Files affected** — concrete code paths that change
4. **Open questions** — unresolved decisions, each with a default

Cross-references to the AKS document are marked with `[AKS §N]`.

---

## 1. Tenancy & identity model

### Recommendation

Introduce a first-class **`workspace`** as the unit of tenancy and a **`workspace_membership`** join holding a per-user role within each workspace. Every tenant-scoped resource (M365/Azure/AWS/GCP connections, scans, scan_results, evidence_validations, schedules, drift baselines) gets a NOT NULL `workspace_id` FK. The existing `User.role` enum is retained for **system-level** roles only (`platform_admin`, `support`); product-level RBAC moves to the membership row.

Schema shape:

- `workspace(id uuid pk, slug text unique, name text, plan text, created_at, deleted_at, settings jsonb, encrypted_dek bytea, kek_version int)`
- `workspace_membership(workspace_id fk, user_id fk, role text check in ('owner','admin','auditor','viewer'), invited_by, accepted_at, primary key(workspace_id,user_id))`
- `workspace_invitation(id, workspace_id, email, role, token_hash, expires_at, accepted_user_id)` — populated now even though SSO/email-send is deferred, so the API surface is stable.

UUIDs (not bigserial) for `workspace.id` so external references in URLs, logs, and webhooks do not leak ordinal counts. Existing tables keep integer PKs internally; only the workspace identifier needs to be opaque externally.

**Workspace context propagation**: workspace ID lives in the URL path (`/v1/workspaces/{workspace_id}/...`). It is **not** baked into the JWT — a user can belong to many workspaces, the JWT stays a clean identity token, and switching workspace does not require token re-issue. A FastAPI dependency `get_current_workspace_member(workspace_id, user) -> WorkspaceMembership` resolves and authorises in one shot, raising **404** (not 403) on non-membership to avoid existence leaks.

**RLS posture**: enable Postgres Row-Level Security as **defence in depth**, not as the primary enforcement. Every connection (API or worker) executes `SET LOCAL app.workspace_id = '<uuid>'` at the start of the request/task; RLS policies enforce `workspace_id = current_setting('app.workspace_id')::uuid`. Application-layer filters remain primary because they are explicit, debuggable, and testable. RLS catches misplaced queries that forget the predicate. The pattern is well-trodden (Supabase, GitLab Geo, Crunchy Bridge tenant guides) so the maturity bar is met.

**Roles** within a workspace:

- `owner` — billing, deletion, member management
- `admin` — connections, schedules, members (no billing/delete)
- `auditor` — create/run scans, edit comments
- `viewer` — read-only

`backend-api/app/core/permissions.py` `RoleChecker` keeps its shape but acts on `WorkspaceMembership.role` not `User.role`.

**SSO / invitations**: design hooks now, defer implementation. The invitation table exists; FastAPI-Users OAuth association mapping is already present (`oauth_account` table). SAML/OIDC-per-workspace is a future feature where IdP config will live on `workspace.settings`.

### Alternatives considered

- **Schema-per-tenant** — rejected. Hundreds of schemas blow up Alembic migration time, complicate connection pooling, and Postgres catalog bloat is real at that count. Pooled with RLS is the documented mid-market sweet spot.
- **Database-per-tenant** — rejected for the same reasons amplified — operational toil, no economies in shared queries, hostile to mid-market unit economics.
- **Workspace ID in JWT claim** — rejected. Multi-workspace users force token re-mint on every switch, and any token leak escalates to a specific workspace rather than just identity.
- **Reuse `User.role` for workspace roles** — rejected. The same human is `auditor` in workspace A and `owner` in workspace B; one global role can't express that.

### Files affected

- `backend-api/app/models/user.py` — keep, but stop using `role` for product authorisation
- `backend-api/app/models/compliance.py` — add `workspace_id` to `Scan`
- `backend-api/app/models/scan_result.py` — add `workspace_id` (denormalised for RLS efficiency and partitioning)
- `backend-api/app/models/m365_connection.py` — add `workspace_id`, drop `user_id` semantic dependence
- `backend-api/app/models/evidence_validation.py` — add `workspace_id`
- New: `backend-api/app/models/workspace.py`, `workspace_membership.py`, `workspace_invitation.py`
- New: `backend-api/app/core/workspace_context.py` — dependency that loads membership + sets the `app.workspace_id` GUC on the session
- New Alembic migration: `backend-api/alembic/versions/<rev>_introduce_workspaces.py` — create tables, backfill (one workspace per existing user, single owner), add NOT NULL `workspace_id`, enable RLS, install policies. Multi-step (expand → backfill → contract), see §6.

### Open questions

- **Free-tier / personal workspaces?** *Default: yes — allow one personal workspace per user, capped to the free plan.* Affects defaults for `plan` and member-count limits.
- **Cross-workspace artefacts?** *Default: no — everything strictly partitioned. Benchmark library is platform-level (shared by all).*
- **Soft- vs hard-delete?** *Default: soft-delete via `deleted_at` with 30-day retention before hard-delete cascade (housekeeping task).*

---

## 2. API & control plane

### Recommendation

Reshape the `/v1` API under workspace scoping:

- `/v1/workspaces` — list/create workspaces the user belongs to
- `/v1/workspaces/{id}/members` — invite, remove, role-change
- `/v1/workspaces/{id}/connections/m365` — replaces `/v1/m365-connections`
- `/v1/workspaces/{id}/scans` — replaces `/v1/scans`
- `/v1/workspaces/{id}/schedules` — new
- `/v1/workspaces/{id}/baselines` — new (drift)
- `/v1/workspaces/{id}/exports` — new (data export)
- `/v1/workspaces/{id}/audit` — new (audit log read)
- `/v1/me` — identity-only, outside workspace scope
- `/v1/admin/...` — platform-admin only, gated by `is_superuser`

**Authorisation layer**: a single dependency `WorkspaceMember(role_min=...)` resolves the workspace, verifies membership, sets the Postgres GUC for RLS, and attaches the membership row to `request.state`. Every route under `/v1/workspaces/{id}/*` declares it. Drift between routes is prevented by:

1. A pytest collection asserting that every workspace-prefixed route declares the dependency (introspect FastAPI's routes table).
2. A parametrised `assert_workspace_isolation(other_workspace)` suite that fuzzes a token from workspace A against IDs in workspace B and asserts 404.

CI fails if a new endpoint isn't covered.

**Rate limiting / quotas**: introduce **`slowapi`** (Starlette-native, mature) backed by Redis for per-IP login throttling and per-user request rate. For *quota* (scans/day, controls/month, concurrent scans per workspace), enforce inside the scan-create handler against a `workspace_quota` row and on the worker via a Redis token bucket keyed by `workspace_id`. The bucket exists day one as identity even if its capacity is set effectively unlimited — the goal is *hooks now, enforcement later*.

**Token model**:

- Keep stateless JWTs (FastAPI-Users JWTStrategy, already wired). Lifetime 30 min.
- **Add refresh tokens** stored server-side as opaque hashed strings in a `refresh_token` table with rotation-on-use and family-revoke on reuse. Pure-stateless JWTs become operationally painful (can't revoke) once you have paying tenants.
- **Service-to-service** auth: API → worker is via Celery (broker auth, no HTTP). Worker → PowerShell service and Worker → OPA need explicit mutual auth — see §4 and [AKS §3].

**Background-work API contract**:

- `POST /v1/workspaces/{id}/scans` returns 202 with the scan id and a `status_url`.
- `GET` on the scan returns live progress (totals + per-status counters already exist on `Scan`).
- Real-time updates over **Server-Sent Events** (`/v1/workspaces/{id}/scans/{scan_id}/events`) using **`sse-starlette`** fed by Redis pub/sub. SSE is mature, traverses corporate proxies as plain HTTP, and doesn't need sticky sessions when Redis fans out. The client library is trivial.
- Long-poll fallback by simply hitting GET — no design needed.

### Alternatives considered

- **WebSockets for progress** — rejected as primary. Bidirectional channel is overkill for read-only progress; SSE is simpler, plays nicely with HTTP/2, and load balancers handle it.
- **GraphQL** — rejected. The current REST surface is small and a GraphQL schema is a larger contract to maintain than the use case demands.
- **Stateful sessions instead of JWT** — rejected. FastAPI-Users JWT is already wired; refresh tokens close the revocation gap without a wholesale rewrite.
- **Token bucket on API only (skip worker)** — rejected. A single tenant can fan out 1000 control evaluations from one POST, so the worker needs the gate.

### Files affected

- `backend-api/app/api/v1/router.py` — restructure under workspace prefix
- `backend-api/app/api/v1/scans.py`, `m365_connections.py`, `evidence.py`, `settings.py` — re-scope all routes
- New: `backend-api/app/api/v1/workspaces.py`, `members.py`, `schedules.py`, `baselines.py`, `exports.py`, `audit.py`
- New: `backend-api/app/core/workspace_context.py`
- New: `backend-api/app/core/rate_limit.py` (slowapi setup, Redis backend)
- New: `backend-api/app/api/v1/sse.py` — scan event stream
- `backend-api/app/main.py` — wire slowapi middleware, SSE router

### Open questions

- **`X-Workspace-Id` header shortcut?** *Default: no — strict path-only. The path is auditable in access logs without parsing headers.*
- **Quota numbers** — *Default: deferred to product/finance.* Scaffold the table now.
- **Refresh-token rotation policy** — *Default: 30-day absolute, 7-day idle, family-revoke on reuse.*

---

## 3. Scan execution pipeline

### Recommendation

**Queue topology** — split the single `autoaudit` queue into:

- `scans.orchestrate` — light, one task per scan, dispatches the children (replaces today's `run_scan`)
- `controls.graph` — Microsoft Graph evaluations (IO-bound, fast, high-fanout)
- `controls.powershell` — Exchange / Compliance / Teams collectors (calls PowerShell service; bound by service capacity)
- `scheduled` — Beat-triggered nightly/weekly scans
- `drift` — continuous detection comparisons
- `housekeeping` — reaper, finaliser-poller, retention, soft-delete cascade

Workloads have different latency profiles and different downstream constraints: Graph tasks are fast IO with no external concurrency cap; PowerShell tasks queue against a finite pool of pwsh sessions and need backpressure separately. Mixing them in one queue creates head-of-line blocking the moment a tenant runs an Exchange-heavy scan.

**Worker pools** — separate Celery worker Deployments per queue:

- Graph workers — **gevent** pool, concurrency 50–100 (async-IO bound).
- PowerShell workers — **prefork** pool, concurrency 4–8 (synchronous HTTP wait, downstream is the binding limit).
- Orchestrator / scheduled / drift / housekeeping — prefork, concurrency 2–4.

The current code calls `asyncio.run()` inside a Celery task (`engine/worker/tasks.py:254`). With gevent that is fine; with prefork it works but spins up a fresh event loop per task. Acceptable; revisit only if profiling shows it.

**Result backend**: today there is no Celery result backend (intentionally — results go to Postgres). Keep that for control evaluation results. **Add Redis as the result backend for orchestration tasks** (`scans.orchestrate`, finaliser, schedule firings) so chord callbacks and `app.AsyncResult.get()` work for those control-plane operations. This is the standard Celery + Redis pattern.

**Retry & DLQ**:

- `autoretry_for` with exponential backoff and jitter (Celery built-in). Cap attempts at 3 for transient errors (Graph 429, network flap).
- Distinguish *transient* (retry) from *permanent* (skip, mark error) at the collector level.
- **Dead letter**: route Nth failure to a `controls.failed` queue; persist to Postgres `failed_task` table with full context for human review. Use `Task.on_failure`. Housekeeping reaps stale `pending` `scan_result` rows past SLA.
- **Idempotency**: every `evaluate_control` task is keyed by `(scan_id, control_id)` and the row carries a unique constraint already (`uq_scan_result_scan_control`). Add a guard at the top of `evaluate_control` that exits early if `scan_result.status != 'pending'` to absorb at-least-once re-delivery.

**Finalisation race fix** — replace "last task wins" (`engine/worker/db.py:291` `finalize_scan_if_complete`) with a **Celery chord**. The orchestrator builds `group(evaluate_control.s(...) for ...)` and chords it to a `finalize_scan` callback. Chord callbacks fire once when the group completes — deterministic, no `SELECT FOR UPDATE` race window. Belt-and-braces: a **scheduled poll** in the housekeeping queue finds scans `running` past N minutes with all results non-pending and finalises them — covers the case where a worker died mid-flight and the chord coordinator lost track. The `SELECT FOR UPDATE` finaliser stays as the third line of defence inside the callback.

**Scheduling for nightly/weekly** — **Celery Beat with `redbeat` (Redis-backed scheduler)**. Schedules live in Postgres (`workspace_schedule(workspace_id, framework, benchmark, version, cron_expr, enabled, last_run_at)`); redbeat coordinates Beat across replicas. Mature and ships in many Celery deployments. Beat publishes to the `scheduled` queue.

**Drift detection** — `drift_baseline(workspace_id, scope, key, hash, snapshot jsonb, taken_at)` per "interesting object" (CA policy, role assignment, transport rule, etc.). A periodic `drift.scan` task per workspace fetches current state via the same collectors, hashes per object, and only emits `drift_event` rows for deltas. This is *delta scanning*, not fan-out re-scanning of all controls. Cadence per workspace lives on `workspace.settings.drift_interval_minutes`.

**Per-tenant fairness hooks** — design now, enforce later:

- Every dispatched control task carries `workspace_id` in headers.
- A `before_task_publish` Celery signal consults a Redis token bucket `bucket:{workspace_id}:controls` and either dispatches or stashes to a `parking` ZSET keyed by workspace with a release scheduler.
- Day one the bucket is sized so it never trips; the wiring is the deliverable.
- A future move to **priority queues** (Celery supports `x-priority` on RabbitMQ; on Redis broker, use distinct queues per priority level).

### Alternatives considered

- **Switch broker to RabbitMQ** — rejected for now. Redis is already in the stack; adding another stateful service for slightly better priority/DLX is cost the team doesn't need. Revisit if peak fan-out exceeds Redis ergonomics.
- **Workflow engine (Temporal, Prefect, Dagster) instead of Celery** — rejected. Celery is wired, the team is small, and Celery + chord covers the orchestration shape. **Documented as future option** at higher scale or if step-level versioned workflows become important — Temporal in particular is mature for that.
- **Kubernetes CronJob for scheduled scans** — rejected as primary. Per-workspace schedules with different cadences would mean N CronJobs to manage. A DB-backed scheduler with one Beat process is cleaner.
- **Keep "last task wins" finaliser** — rejected. A worker SIGKILL between `update_scan_result` and the count increment leaves the scan stuck at "running" forever. Chord + housekeeping reaper closes the window.

### Files affected

- `engine/worker/celery_app.py` — define multiple queues, task routing map, results backend for orchestrator
- `engine/worker/tasks.py` — split into `tasks_orchestration.py`, `tasks_controls.py`, `tasks_drift.py`, `tasks_housekeeping.py`; replace fan-out + `finalize_scan_if_complete` with `chord(...)(finalize_scan.s(scan_id))`
- `engine/worker/db.py` — workspace-aware queries; remove decrypt-in-process (see §7)
- New: `engine/worker/fairness.py` — token bucket helpers
- New: `engine/worker/beat_schedule.py` and `redbeat` config
- `backend-api/app/services/celery_client.py` — route to `scans.orchestrate`
- New tables: `workspace_schedule`, `drift_baseline`, `drift_event`, `failed_task`

### Open questions

- **Drift detection scope per platform** — *Default: CA policies, role assignments, transport rules, sharing settings as v1 set; expand by benchmark.* Needs product input.
- **Continuous drift cadence** — *Default: 4h; per-workspace override.*
- **Maximum concurrent scans per workspace** — *Default: 2 free / 5 paid / 10 enterprise (placeholder).*

---

## 4. PowerShell service

### Recommendation

**Mandate the HTTP service path; remove the docker-subprocess fallback from production code.** `engine/collectors/powershell_client.py` today supports both `POWERSHELL_SERVICE_URL` (HTTP) and a `docker run` subprocess path. The HTTP service (`engine/powershell/service/main.py`) is the production execution model; the subprocess path is a developer-machine fallback that cannot work on AKS (Docker-in-Docker is an anti-pattern). Remove the fallback in production code paths and make `POWERSHELL_SERVICE_URL` required.

**Sizing model**: stateless service, horizontally scaled, **but with a per-pod warm pwsh runspace pool**. The current `executor.py` spawns `pwsh` per request. Startup cost for fresh pwsh + module imports is **5–15 seconds** — unacceptable per-control. Approach:

- Pre-warm a pool of long-lived pwsh runspaces inside each pod, with `ExchangeOnlineManagement`, `MicrosoftTeams`, `Microsoft.Graph` modules pre-imported once on pod start.
- Each `/execute` request acquires a runspace, calls `Connect-ExchangeOnline -AccessToken ...`, runs the cmdlet, calls `Disconnect-`, returns the runspace.
- **Implementation choice**:
  - **Option A (recommended): pwsh daemon process per pod** with a JSON-line protocol over stdin/stdout. Simpler, no .NET interop, the team is already comfortable with subprocess management.
  - **Option B: pythonnet hosting `System.Management.Automation`** inside the FastAPI process. More idiomatic, finer control of runspaces, but adds .NET interop complexity.
  - Decide via a quick spike measuring p50/p95 latency and pod RSS for a representative cmdlet under each model.

**Per-tenant warm sessions** are explicitly *not* in scope. Token TTL (~1h), runspace state pollution, and cardinality (hundreds of tenants) make this a poor trade. Invest instead in module-import warmth (one-off pod startup cost) and accept per-request `Connect-`/`Disconnect-`.

**Auth between worker and service**: an HMAC header (`Authorization: HMAC <key-id>:<sig>`) over the request body + timestamp at the application layer (defence in depth) **plus** mTLS at the platform layer ([AKS §3] via Cilium / WireGuard at node level). Application HMAC is cheap to keep even when mTLS arrives — it gives a per-request authn signal independent of the network identity.

**Concurrency / backpressure**: the service exposes pool utilisation at `/health` and returns **HTTP 429 with `Retry-After`** when saturated. The worker's `PowerShellClient` honours `Retry-After` and Celery retries the task with backoff. This naturally bounds parallelism without the worker needing to know the service's pool size.

### Alternatives considered

- **Keep DinD fallback for production** — hard reject. Docker-in-Docker on AKS is operationally hostile and a security/blast-radius risk.
- **Per-tenant warm sessions** — rejected. Token TTL, runspace state, cardinality.
- **One-pwsh-per-request with no pool** — rejected. Module-import cost dominates scan time; scans become unusably slow.

### Files affected

- `engine/worker/config.py` — make `POWERSHELL_SERVICE_URL` required
- `engine/collectors/powershell_client.py` — drop subprocess code path; HTTP-only
- `engine/powershell/service/main.py` — add `/health` with utilisation, HMAC auth dependency, 429 with `Retry-After`
- `engine/powershell/service/executor.py` — replace per-request `subprocess.run` with a runspace pool (daemon process or PSHost)
- New: `engine/powershell/service/runspace_pool.py`

### Open questions

- **pwsh daemon vs pythonnet** — *Default: daemon (lower interop risk).* Decide post-spike.
- **Pool size per pod** — *Default: empirical; 4–8 a starting guess.* Measure, don't design.
- **Exchange managed-identity auth** as alternative to client secret — *Default: not at MVP; client secret continues, managed identity is a customer-friendly upgrade later.*

---

## 5. OPA / policy distribution

### Recommendation

Replace the bake-into-image pattern (`engine/opa/Dockerfile` copies `engine/policies` at build time) with **OPA's bundle service protocol**. Policies are packaged into a `.tar.gz` bundle and published to **Azure Blob Storage** [AKS §2c]. OPA pods are configured with a `services` + `bundles` config block to pull on a 60s interval with ETag-based no-op when unchanged. OPA's bundle support is core, mature, and the canonical answer.

Bundle build flow (logical, not platform):

1. CI step on merge to main: `opa build -b engine/policies -o autoaudit-policies-<git-sha>.tar.gz` and upload to versioned Blob path `policies/<channel>/<git-sha>.tar.gz`. Channels: `stable`, `canary`.
2. OPA config points at `https://<account>.blob.core.windows.net/policies/<channel>/latest` via a tiny indirection blob containing the current SHA.
3. **Versioning**: bundle SHA is the version. Maintain `policy_release(channel, sha, created_at, notes)` table for audit visibility from the app side.
4. **Rollback**: write to the indirection blob to point `latest` at a previous SHA. OPA picks it up within 60s. No image rebuild, no rollout.

**Replicas + caching**: 2+ OPA replicas per env behind a service. OPA itself is stateless beyond the loaded bundle; horizontal scale is trivial. An optional in-process LRU on the worker `opa_client.evaluate_policy` keyed by `(package_path, hash(input))` is a skippable optimisation — most evaluations differ per tenant, so cache hit rate is low.

**Signed bundles**: enable OPA's bundle signing (HS256 or RS256). The signing key lives in Key Vault (referenced by [AKS §4]). A compromised blob upload cannot push a malicious policy without also stealing the signing key.

**Per-workspace policy overrides** are explicitly *out of scope* until a customer needs custom policies. OPA's bundle discovery feature is the natural extension point at that future inflection.

### Alternatives considered

- **Keep image-baked policies** — rejected. Every policy edit requires a full image rebuild + rollout, slowing the iteration cadence for compliance content.
- **Embed OPA as a library in the worker (Wasm or sidecar)** — rejected. Sidecar adds complexity per worker pod; Wasm-compiled OPA is mature but limits the policy language features available. The HTTP service is fine for the scale targeted.
- **Discovery + multiple bundles per workspace** — out of scope (above).

### Files affected

- `engine/opa/Dockerfile` — strip the COPY, replace with base OPA image plus a config file (or push config via env in [AKS §2c])
- New: `engine/opa/config.yaml` — bundle service config template (account/container/path env-substituted)
- New: `scripts/build_policy_bundle.sh` — CI helper
- `engine/opa_client.py` — no app changes needed; URL stays `/v1/data/...`

### Open questions

- **Signing key rotation cadence** — *Default: 90 days.*
- **Canary channel rollout strategy** — *Default: canary points at HEAD on merge to main; stable cuts on a manual promote step. Specific staging-fleet workspaces not yet defined.*

---

## 6. Data layer

### Recommendation

**Connection pooling** — deploy **PgBouncer in transaction-pooling mode** in front of Postgres. With many API replicas + Celery workers + Beat + housekeeping, raw connection count to Postgres explodes. PgBouncer is mature, ubiquitous, and drops max DB connections to the dozens while application code sees thousands of logical connections. Caveats:

- Transaction pooling forbids session-scoped state. Our use of `SET LOCAL app.workspace_id` is per-transaction, so it works correctly with transaction pooling.
- asyncpg + PgBouncer requires `statement_cache_size=0` on the engine. Wire that in `app/db/base.py`.
- Worker uses sync SQLAlchemy (`engine/worker/db.py`); same PgBouncer fronts both.
- Specific deployment shape (Flex Server's built-in PgBouncer vs in-cluster Pod) lives in [AKS §2a].

**Pool sizing principles** (numbers tuned in [AKS §2a]):

- API: small per-replica pool (5–10), short-lived checkouts.
- Worker (per process for prefork; per pool for gevent): 5–15.
- Beat: 2.
- Total max under PgBouncer × pool ≤ Postgres `max_connections` × 0.7.

**Read replicas**: not now. Workload is write-heavy on `scan_result` and reads are mostly recent-scope (one workspace's recent scans). Add a read-replica routing layer when a measurable bottleneck shows up. Document the seam: SQLAlchemy supports binds with a custom routing session.

**Indexing / partitioning**:

- Composite indexes: `(workspace_id, started_at desc)` on `scan`; `(workspace_id, control_id)` on `scan_result`; `(workspace_id, is_active)` on connections.
- **Partition `scan_result` by `RANGE(created_at)` monthly** when volume warrants. Native Postgres declarative partitioning is mature in 14+. Alembic 1.13+ handles partition DDL via raw `op.execute`. Do **not** partition by `workspace_id` — too many partitions, hostile to platform-level queries.
- `evidence_validation` is small; no partitioning needed.

**Migrations / zero-downtime**:

- Adopt **expand → migrate data → contract**. Add nullable columns + indexes (concurrently, where Alembic supports it) in one release; deploy code that writes both old and new shape; backfill in a job; cut readers over; drop old columns in a later release.
- The `introduce_workspaces` migration must follow this pattern because every existing FK changes shape.
- **Run migrations as a pre-deploy job**, not on application start. The application checks `alembic current == head` at boot and refuses to start otherwise. The Job pattern lives in [AKS §6].
- Long-running data backfills go to a Celery task in the `housekeeping` queue, not into the migration step.

**Backup / PITR**: principles only — managed Postgres with automated backups, PITR retention ≥ 14 days, monthly restore drill into a non-prod env. Specific service from [AKS §2a].

**Redis role split**:

- Broker: dedicated Redis instance / DB with persistence enabled (AOF). Celery task loss is unacceptable.
- Result backend (orchestrator results only): same instance as broker, separate DB index.
- Cache (rate-limit, MSAL token cache, OPA result cache): separate Redis instance, ephemeral, no persistence — losing it just causes cold starts.
- A memory-pressure event in cache (cache fill) must not evict broker entries; persistence settings differ; ops can scale them independently.

### Alternatives considered

- **Direct connections (no PgBouncer)** — rejected at this scale. Postgres connection ceiling becomes the bottleneck.
- **Supavisor / pgcat** — both mature alternatives. PgBouncer chosen because it's the most production-tested in the Postgres community and has the broadest operational documentation. **pgcat noted as future option** for sharding-aware routing.
- **Partition `scan_result` by `workspace_id`** — rejected. Partition cardinality (1 per tenant) is wrong for Postgres and hurts cross-tenant platform queries.
- **Single Redis for everything** — rejected for the persistence/eviction conflict above.

### Files affected

- `backend-api/app/db/base.py` — engine kwargs for asyncpg+PgBouncer compatibility (`statement_cache_size=0`), pool tuning
- `engine/worker/db.py` — same on the sync engine
- `backend-api/app/core/workspace_context.py` — `SET LOCAL app.workspace_id` GUC at session start
- New Alembic migrations split into expand/contract pairs
- `backend-api/alembic/env.py` — leave alone; jobification happens in [AKS §6]

### Open questions

- **Retention horizon for `scan_result`** — *Default: 24 months hot, archive to Blob.* Drives partition strategy and storage cost.
- **PITR window length** — *Default: 14 days.* Cost-vs-RPO trade-off.

---

## 7. Credentials & secrets

### Recommendation

Move from a single global `ENCRYPTION_KEY` (Fernet) to **envelope encryption with Azure Key Vault as the KMS**:

- **Per-workspace Data Encryption Key (DEK)** generated at workspace creation, stored *encrypted* on the workspace row (`workspace.encrypted_dek` + `kek_version`). The wrapping Key Encryption Key (KEK) lives in Key Vault and is non-exportable.
- **Encrypting**: API fetches workspace → asks Key Vault to **unwrap** the DEK (single Key Vault call, cached briefly in process) → encrypts the secret with the DEK using AES-GCM → persists `encrypted_client_secret` + a wrapped-DEK reference.
- **Decrypting**: same flow in reverse.
- Per-workspace DEK means a leak of one workspace's DEK only exposes that workspace; KEK rotation is one Key Vault operation; per-DEK rotation re-encrypts a workspace's small set of secrets.

**Credential access from the worker**: worker calls Key Vault directly via Workload Identity ([AKS §4]) to unwrap the DEK, then decrypts in-process. This keeps the data path simple and preserves blast radius (one workspace's DEK at a time, in memory only for the duration of the task). It avoids creating a new HTTP coupling between worker and API, so the API isn't a single point of failure for scans.

We considered "API mints a one-time credential token" — it adds a synchronous API call to the hot path of every scan, the API would need to be sized for it, and the token is just a different shape of the same secret.

**MSAL token caching**: cache Graph/Exchange/Teams access tokens **per `(workspace_id, tenant_id, scope)`** in Redis with `TTL = expires_in - 300s`. MSAL's `SerializableTokenCache` plus a Redis-backed serialiser is the canonical pattern. The current code mints a fresh token per cmdlet (slow, throttled by Entra). Purely additive change, large per-scan win.

### Alternatives considered

- **Keep single Fernet key, just rotate** — rejected. Blast radius for compromise is the entire fleet.
- **Per-tenant separate KEK in Key Vault (skip the DEK layer)** — rejected. Key Vault has key-count limits and per-key cost; a KEK per workspace at hundreds of workspaces is operationally awkward. Envelope encryption is the standard answer.
- **HashiCorp Vault instead of Azure Key Vault** — rejected for AKS target. Key Vault integrates natively with AKS Workload Identity. **Documented as future option** if multi-cloud becomes a requirement.

### Files affected

- `backend-api/app/services/encryption.py` — replace with envelope encryption module
- New: `backend-api/app/services/keyvault.py` — Key Vault client (KEK unwrap)
- New: `backend-api/app/services/credentials.py` — high-level encrypt/decrypt API
- `backend-api/app/api/v1/m365_connections.py` — use new credentials service
- `engine/worker/db.py` — replace `decrypt(...)` with workspace-aware unwrap
- New: `backend-api/app/services/msal_cache.py` and matching usage in `engine/collectors/graph_client.py`, `powershell_client.py`
- New migration: add `workspace.encrypted_dek` and `workspace.kek_version`

### Open questions

- **KEK rotation cadence** — *Default: 90 days.*
- **Worker pod identity Key Vault permission scope** — *Default: per-Deployment ServiceAccount with workspace-scoped unwrap permission via Azure RBAC.* Detail in [AKS §4].

---

## 8. Frontend

### Recommendation

The frontend is **already on Vite 7 + React 19** with `Dockerfile.prod` (multi-stage → nginx) and `nginx.conf`. No CRA migration is needed. Real gaps:

- **Make `Dockerfile.prod` the production target** for non-dev environments. The dev `Dockerfile` (`vite` dev server) stays dev-only.
- **Workspace context**: extend `frontend/src/api/client.ts` so every method takes a `workspaceId`. Add `WorkspaceContext` provider holding the active workspace and a switcher. URL is the source of truth (path `/w/:workspaceSlug/...`); the context subscribes to the route.
- **Token refresh**: the AuthContext stores the token in memory + localStorage. With refresh tokens (§2), add an interceptor in `client.ts` that on 401 attempts a refresh once and retries.
- **Selective TanStack Query adoption**: hand-rolled fetch is tolerable now but the moment per-workspace cache invalidation and live scan progress arrive, TanStack Query saves a lot of bespoke code. Recommend introducing it incrementally — start with the scan-list view and grow.
- **Multi-workspace session**: a single token works across all workspaces the user has membership in; the active workspace is purely a UI/URL concern. No re-auth on switch.

### Alternatives considered

- **CRA → Vite migration** — not applicable; already done. (The earlier exploration framing was stale; verified against `frontend/package.json`.)
- **Adopt Next.js** — rejected. SSR / edge isn't a stated need; SPA + nginx static-host is operationally simpler.
- **Stay with hand-rolled fetch wrapper indefinitely** — tolerable, but the case for TanStack Query grows; introducing it incrementally is cheap.

### Files affected

- `frontend/Dockerfile.prod` — confirm production target in CI/CD
- `frontend/src/api/client.ts` — accept workspace scoping in every method; refresh-token interceptor
- New: `frontend/src/context/WorkspaceContext.tsx`
- New: `frontend/src/components/WorkspaceSwitcher.tsx`
- `frontend/src/App.tsx` — route under `/w/:workspaceSlug/*`
- `frontend/src/context/AuthContext.tsx` — silent-refresh path
- (Optional) introduce TanStack Query

### Open questions

- **Switcher UX** — *Default: dropdown in the top bar.* Product call.
- **Viewers see other workspaces?** — *Default: yes — show all memberships in the switcher; route guard handles the per-route role check.*

---

## 9. Observability (app instrumentation)

### Recommendation

**Logging** — structured JSON via **`structlog`** (mature, async-friendly, FastAPI-friendly). Replace dict-into-stdlib-logger patterns in `app/core/middleware.py` and stray `print()` calls. Bind `request_id`, `user_id`, `workspace_id`, `scan_id`, `control_id` as contextvars at request entry / task entry. Celery has a `before_task_publish` + `task_prerun` signal pair to propagate context across the queue: publish `workspace_id` in task headers, read on `prerun`, bind to logger context.

**Metrics** — Prometheus exposition is the obvious choice (broad ecosystem, vendor-agnostic):

- API: **`prometheus-fastapi-instrumentator`** for RED (rate, errors, duration) per route.
- Workers: **`celery-prometheus-exporter`** plus custom counters/histograms — `scan_duration_seconds`, `control_evaluation_seconds{collector,result}`. `queue_depth{queue}` is usually scraped from Redis directly via **`redis_exporter`**.
- PowerShell service: `prometheus-fastapi-instrumentator` plus a pool-utilisation gauge.
- OPA: emits Prometheus metrics natively at `/metrics`.

**Cardinality discipline**: `workspace_id` as a label is dangerous at hundreds of workspaces. Recommend dimensioning by `plan` (free/starter/pro/enterprise) and tracking the unique-workspace count as a separate gauge. Per-workspace dashboards come from logs + traces, not metrics labels.

**Tracing** — **OpenTelemetry**, end-to-end. Native instrumentation exists for FastAPI, requests/httpx, SQLAlchemy, Celery (`opentelemetry-instrumentation-celery`), and OPA emits OTel spans on demand. Trace context propagates:

- HTTP API → API spans
- API → Celery: trace context in task headers (the OTel Celery instrumentation does this)
- Celery → PowerShell service / OPA: outbound httpx instrumentation injects W3C `traceparent`

One trace per scan from POST to finalize. `scan_id` and `workspace_id` as span attributes. Backend selection (App Insights, etc.) lives in [AKS §8].

**Audit log** — separate from app logs. New table `audit_event(id, workspace_id, actor_user_id, action, target_type, target_id, payload jsonb, ip, user_agent, occurred_at)`. Written for: workspace member changes, connection create/update/delete, scan start, schedule changes, credential rotations, exports, deletes. Read-only via `/v1/workspaces/{id}/audit` for owners/admins. Retention policy on the table (e.g. 365 days hot, archived to Blob).

### Alternatives considered

- **OpenSearch / ELK only, no metrics** — rejected. Log-derived metrics are slow and expensive at scale; Prometheus is the standard.
- **Single vendor (Datadog / New Relic) at the SDK layer** — rejected. Vendor lock-in. Keep app code on OTel + Prometheus standards so backends are swappable.
- **Reuse request log middleware as audit log** — rejected. Different retention, access control, and format. They are different concerns.

### Files affected

- `backend-api/app/core/logging.py` — switch to `structlog`
- `backend-api/app/core/middleware.py` — bind context vars
- New: `backend-api/app/core/telemetry.py` — OTel setup
- `engine/worker/celery_app.py` — OTel Celery instrumentation
- `engine/powershell/service/main.py` — OTel + Prometheus instrumentation
- New table + service: `backend-api/app/models/audit_event.py`, `app/services/audit.py`
- Wire audit calls in every mutating route

### Open questions

- **Cardinality budget** — *Default: max 50 distinct labels per metric series; CI sanity-check.*
- **Audit log retention** — *Default: 365 days hot, archive to Blob, 7-year archive default.* Driven by future customer compliance commitments.

---

## 10. Multi-tenancy security

### Recommendation

Defence in depth, three independent layers:

1. **Application** — `WorkspaceMember` dependency on every workspace-scoped route; ORM filters always include `workspace_id`. Primary enforcement.
2. **Database** — Postgres RLS on every tenant table, gated by `app.workspace_id` GUC. A query without the GUC set returns zero rows. Catches application-layer bugs.
3. **Test** — a parametrised pytest suite that, for every endpoint, mints a token in workspace A, hits the endpoint with an ID belonging to workspace B, and asserts **404** (not 403, to avoid existence leak). Plus a property-test fuzzer that generates random workspace IDs for cross-tenant probes. CI fails if a new endpoint isn't covered (achieved via a registry: every workspace-scoped route registers itself, the test introspects the registry).

**Credential blast radius** — addressed by the per-workspace DEK (§7). One workspace's compromised DEK exposes only that workspace's credentials. The MSAL token cache is keyed by `(workspace_id, tenant_id, scope)` — never share tokens across workspaces even if they happen to point at the same M365 tenant ID.

**Tenant data export / deletion (GDPR-style)**:

- **Export**: an async job produces a per-workspace `.zip` with scans, results, audit events, evidence artefacts (JSON for structured data, raw files where applicable). Triggered via owner-only API; result delivered as a signed Blob URL. Use a Celery task in `housekeeping`. Implementation incremental; the API surface (`POST /v1/workspaces/{id}/exports`) and table (`workspace_export(id, status, requested_by, signed_url, expires_at)`) exist day one.
- **Deletion**: soft-delete on `workspace.deleted_at`; hard-delete after a retention window (default 30 days) via a housekeeping task that cascades workspace_id-scoped rows. RLS continues to apply to the deletion path. Use Postgres `ON DELETE CASCADE` only for tightly bound child rows; otherwise prefer task-driven deletion so we can audit each step.
- **Right to be forgotten** for individual users: tombstone identity fields (email, name), remove `workspace_membership` rows, but keep `audit_event.actor_user_id` referencing a tombstone row — preserving forensic value while satisfying erasure.

### Alternatives considered

- **RLS as primary enforcement, skip app-level filters** — rejected. RLS errors are opaque ("no rows" is hard to debug); explicit app-layer filters are easier to reason about, with RLS as the safety net.
- **App-only with no DB safety net** — rejected. Want the safety net.
- **Hard-delete immediately** — rejected. Accidental deletion is unrecoverable; soft-delete + window is the industry norm.

### Files affected

- New: `backend-api/tests/security/test_workspace_isolation.py`
- New: `backend-api/app/api/v1/exports.py`
- New: `engine/worker/tasks_housekeeping.py` (deletion + export)
- Alembic: RLS policy migrations, `workspace_export` table

### Open questions

- **Export format** — *Default: JSON for structured data + raw files where applicable, packed as zip.*
- **Deletion retention window** — *Default: 30 days.*
- **Customer-managed keys (BYOK)?** — *Default: not at MVP; documented as upgrade path for enterprise tier.*

---

## 11. Open questions / decisions to surface

These are the explicit revisitable defaults:

| Question | Default |
|---|---|
| Pricing/plan tiers | Free / Starter / Pro / Enterprise placeholders; quota dimensions defined; values placeholder |
| Drift detection scope per platform | CA policies, role assignments, transport rules, sharing settings as v1 set; expand by benchmark |
| Continuous drift cadence | 4h with per-workspace override |
| Refresh token rotation | 30-day absolute, 7-day idle, family-revoke on reuse |
| SSO timeline | Schema hooks now; SAML/OIDC implementation deferred (Q+1) |
| Audit log retention | 365 days hot, archive to Blob, 7-year archive default |
| Deletion retention window | 30 days soft-delete before hard-delete |
| Backup PITR window | 14 days |
| PowerShell pool runtime: pwsh daemon vs pythonnet | pwsh daemon (lower interop risk); revisit on benchmark |
| Per-workspace policy overrides | Not in scope; reserve OPA package naming dimension |
| Read-replica timing | Design seam now, deploy on load-test signal |
| Workspace public ID format | UUID for API, slug for URLs, both stored |
| Cross-workspace platform-admin "impersonate" | Yes, gated by `is_superuser`, audit-logged; design hook now, build later |
| Customer-managed keys (BYOK) | Not at MVP; upgrade path for enterprise tier |

All of the above are explicitly **revisitable**. A change to any one of them should not invalidate the rest of this document; that's the point of giving each its own section above.

---

## Cross-reference index to AKS document

| App-layer concern (this doc) | AKS implementation ([saas-scaling-aks-platform.md](./saas-scaling-aks-platform.md)) |
|---|---|
| Workspace KEK in Key Vault (§7) | Workload Identity binding + ESO/CSI choice (AKS §4) |
| OPA bundles in Blob (§5) | Bundle-source URL, signing key in Key Vault (AKS §2c) |
| PgBouncer (§6) | Flex Server's built-in PgBouncer (AKS §2a) |
| mTLS worker ↔ PowerShell (§4) | Cilium / service mesh choice (AKS §3) |
| Migrations as pre-deploy Job (§6) | Helm hook implementation (AKS §6) |
| Per-queue worker Deployments (§3) | KEDA ScaledObject per queue (AKS §7) |
| Structured JSON logging (§9) | Log Analytics ingestion (AKS §8) |
| OTel traces (§9) | App Insights backend (AKS §8) |
| Prometheus metrics (§9) | Managed Prometheus + Managed Grafana (AKS §8) |
| Per-workspace cost attribution (§9 audit + §10 export) | OpenCost on AKS (AKS §10) |
