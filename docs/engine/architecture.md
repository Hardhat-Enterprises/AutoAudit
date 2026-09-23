# Engine architecture

This page describes how the Compliance Engine runs a scan. Procedures for writing collectors, SharePoint setup, and PR checks live in the documents linked below.

New contributors should start at the [Engine onboarding hub](README.md).

## Purpose and boundaries

The Engine turns cloud configuration into compliance outcomes. It:

- receives background scan tasks
- loads control metadata for a framework, benchmark, and version
- skips controls that are not `ready`
- collects evidence through Microsoft Graph or PowerShell
- evaluates Rego policies in OPA
- writes control results and scan progress to PostgreSQL

The Engine is **not** the React UI, **not** the main REST API, and **not** the database. Those services create scans, store connections, and display results. The Engine is the execution layer.

Collectors report facts. Rego policies interpret those facts. The worker coordinates the path between them.

## Services

AutoAudit runs as a Compose stack. Roles that matter for Engine work:

| Component | Role |
| --- | --- |
| Frontend | Connections, scans, and results in the browser |
| Backend API | Creates scans, stores encrypted connections, exposes REST, enqueues Celery tasks |
| Redis | Celery broker between backend and worker |
| Celery worker | Orchestrates `run_scan` and `evaluate_control` in [`engine/worker/`](../../engine/worker/tasks.py) |
| Collectors | Python classes that return a normalized evidence dict |
| PowerShell service | HTTP service that runs Exchange, SharePoint PnP, and Compliance cmdlets |
| OPA | Executes Rego against the evidence dict |
| PostgreSQL | Durable scans, `ScanResult` rows, evidence, and counters |

Typical local path:

```text
Frontend → Backend API → Redis → Worker
                              ├── Microsoft Graph
                              ├── PowerShell service
                              ├── OPA
                              └── PostgreSQL
```

Stack bring-up: [Getting Started](../GETTING_STARTED.md). Compose file: [`docker-compose.yml`](../../docker-compose.yml).

[`potential-folder-structure.md`](potential-folder-structure.md) is a **historical proposal** for a future `engine/` layout. It is not the current tree.

## Scan lifecycle

After a user starts a scan:

1. **Scan creation** — The backend inserts a scan row and one pending result per selected control.
2. **Task dispatch** — The backend enqueues `worker.tasks.run_scan` with the scan ID. Redis holds the message.
3. **Orchestration** — `run_scan` loads the scan, marks it running, and reads pending results plus the matching `metadata.json`.
4. **Filtering** — Controls whose `automation_status` is not `ready` are stored as skipped. Ready controls without a `data_collector_id` are stored as error.
5. **Parallel evaluation** — Each remaining control is dispatched as `evaluate_control`.
6. **Collector lookup** — [`registry.py`](../../engine/collectors/registry.py) maps `data_collector_id` to a collector class.
7. **Evidence collection** — The collector uses Graph or the PowerShell service and returns a dict.
8. **Policy evaluation** — [`opa_client.py`](../../engine/opa_client.py) posts that dict as OPA `input` and reads the `result` rule.
9. **Persistence** — The worker writes passed, failed, skipped, or error, plus message and evidence.
10. **Finalization** — When the last control finishes, the scan is completed and aggregate counts are stored.

`run_scan` returns after dispatch. It does not wait for every control. Each `evaluate_control` task writes PostgreSQL directly and may retry transient failures.

Implementation: [`engine/worker/tasks.py`](../../engine/worker/tasks.py), [`engine/worker/celery_app.py`](../../engine/worker/celery_app.py).

## Collectors

Collectors must not decide pass or fail. They implement `collect(client) -> dict` so the worker can call them uniformly.

- Contract: [`engine/collectors/base.py`](../../engine/collectors/base.py) (`BaseDataCollector`). PowerShell collectors use [`powershell_base.py`](../../engine/collectors/powershell_base.py).
- How to add one: [`engine/collectors/README.md`](../../engine/collectors/README.md)
- Registry: [`engine/collectors/registry.py`](../../engine/collectors/registry.py)

One collector may feed several controls when they need the same evidence. Prefer adding a field to an existing collector over creating a new authentication path.

## Graph versus PowerShell

**Microsoft Graph** ([`graph_client.py`](../../engine/collectors/graph_client.py)) is used for most Entra and Graph-backed M365 evidence. It authenticates with MSAL application permissions and paginates Graph responses.

**PowerShell** ([`powershell_client.py`](../../engine/collectors/powershell_client.py) → [`engine/powershell/service/`](../../engine/powershell/service/main.py)) is used for Exchange, SharePoint PnP, and Security & Compliance collectors that rely on Microsoft 365 PowerShell cmdlets, including settings that are not available through Graph. The worker calls the PowerShell service over HTTP; that service runs the cmdlet and returns JSON.

The worker chooses a client from the collector ID prefix (see `evaluate_control` in [`tasks.py`](../../engine/worker/tasks.py)):

- PowerShell: `exchange.*` (except `exchange.dns.*`), `compliance.*`, `sharepoint.pnp.*`
- Graph: other prefixes, including Entra collectors

SharePoint tenant settings use PnP through the PowerShell service, not a separate REST SharePoint stack. Setup: [SharePoint local runtime](sharepoint-local-runtime.md). Security & Compliance cmdlets: [Security & Compliance local runtime](compliance-local-runtime.md).

## Metadata, registration, and Rego

[`metadata.json`](../../engine/policies/cis/microsoft-365-foundations/v6.0.0/metadata.json) is the mapping layer the worker actually reads. Typical fields:

| Field | Purpose |
| --- | --- |
| `control_id` | Benchmark identifier |
| `automation_status` | `ready`, `manual`, `deferred`, `blocked`, or `not_started` |
| `data_collector_id` | Key in `DATA_COLLECTORS` |
| `policy_file` | Rego filename for that control |
| `requires_permissions` | Graph or service permissions the collector needs |
| `notes` | Why a control is skipped or limited |

A collector and policy can exist on disk and still never run if metadata is missing, points at the wrong collector ID, or is not `ready`.

OPA receives the collector dict as **root input** (`input.<field>`). The worker builds a package path from framework, benchmark, version, and control ID (hyphens and dots become underscores). For current CIS Microsoft 365 Foundations v6.0.0, control `1.2.2` evaluates `cis/microsoft_365_foundations/v6_0_0/control_1_2_2`.

Rego should return a stable result object (`compliant`, `message`, and useful `details` / `affected_resources`). Handle compliant, non-compliant, and missing evidence. Missing data must not silently pass.

Policy conventions: [`engine/policies/README.md`](../../engine/policies/README.md). Behavioural fixtures: [Compliance engine verification](compliance-engine-verification.md).

## Result states

| State | Meaning |
| --- | --- |
| **Passed** | Evidence was collected; Rego returned `compliant: true` |
| **Failed** | Evidence was collected; Rego returned `compliant: false` |
| **Skipped** | Not evaluated by design (`manual`, `not_started`, `deferred`, `blocked`, or PowerShell controls disabled) |
| **Error** | The Engine could not finish evaluation (unknown collector, permission denied, HTTP failure, retries exhausted) |
| **Pending** | Result row exists but the worker has not written an outcome yet |

PostgreSQL is the source of truth. Celery is not used as the results store.

## Related locations

| Path | Notes |
| --- | --- |
| [`engine/opa_client.py`](../../engine/opa_client.py) | HTTP client to OPA |
| [`engine/tests/`](../../engine/tests/) | Engine test suite, including wiring and policy tests |
| [Control development walkthrough](control-development-walkthrough.md) | CIS 1.2.2 as an example workflow |
| [Manual collector testing](manual-collector-testing.md) | Run a Graph collector against a tenant |
