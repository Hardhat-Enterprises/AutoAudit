# GitHub Actions Workflow Documentation

Reference for anyone picking up the project who wants to understand what runs in `.github/workflows/`, when it runs, and why.

---

## Naming Convention

Workflow files use a prefix to group them by purpose:

| Prefix | Purpose |
|---|---|
| `ci.` | Code quality checks on PRs and pushes to main |
| `ops.` | Scheduled or operational jobs not tied to code review |
| `pr.` | PR metadata management |

---

## CI Workflows

| Workflow | Watches |
|---|---|
| `ci.backend-api.yml` | `backend-api/**` |
| `ci.frontend.yml` | `frontend/**` |
| `ci.engine.yml` | `engine/**` |
| `ci.security.yml` | `security/**` |

### When they run

Each workflow triggers on pull requests and pushes to `main`, but only when files inside its watched directory changed. If a PR only touches `frontend/`, the backend, engine, and security workflows never start and do not appear in the Actions tab.

The weekly schedule bypasses path filtering and runs everything regardless.

### Jobs

When triggered, two jobs run in parallel:

**`analyze`** runs CodeQL static analysis and reports findings to the GitHub Security tab. The backend-api workflow also runs Bandit inside the same job as a Python-specific check.

**`run-lint`** runs Super Linter across changed files. Several linters are disabled to keep it focused on the languages used in each area.

### PR status comment

After both jobs finish, a `report` job posts a table on the PR showing which jobs passed or failed with a link to the run logs. On subsequent pushes the comment updates in place.

```
analyze  ─┐
           ├─→  report
run-lint ─┘
```

The report job only runs on PR events, not on push or schedule.

### `ci.security.yml`

The `security/` directory contains the TPRM Scanner from T2 2025 and is no longer actively maintained. The workflow is kept so changes to that directory are still scanned but is not expected to trigger under normal development.

---

## Grype Dependency Scan

**`ci.grype.yml`** triggers on PRs and pushes to `main` when files change inside `frontend/**`, `backend-api/**`, or `engine/**`, and on a weekly schedule.

Grype walks the repo and checks dependency files (`pyproject.toml`, `requirements.txt`, `package-lock.json`) against public vulnerability databases without needing a Docker build. Results upload to the GitHub Security tab as a SARIF report.

`fail-build` is false so findings are surfaced for review rather than blocking merges.

Note: the Security tab upload requires GitHub Advanced Security, which is free for public repos and requires a paid plan for private ones.

---

## Ops Workflows

**`ops.collector.yml`** runs the audit engine collector on the `engine-development` branch when changes are pushed there.

**`ops.workflow-cleanup.yml`** runs on a schedule to delete old workflow run history.

**`ops.short-test.yml`** a minimal workflow used to verify cleanup is working. Only triggers when its own file changes.

---

## Other CI Workflows

**`ci.opa-eval.yml`** evaluates OPA policies used by the audit engine. Runs on `engine-development` and on any pull request.

**`ci.validate-alerts.yml`** was intended to validate Prometheus alerting rules under `infrastructure/monitoring/alerts/`. It was left by a previous team member as a conceptual piece and does not do anything meaningful in its current state. Left in place for reference.

---

## Weekly Scheduled Scans

| Workflow | Schedule | Purpose |
|---|---|---|
| `ci.backend-api.yml` | Saturdays 23:32 UTC | CodeQL and lint scan of backend-api |
| `ci.frontend.yml` | Saturdays 23:32 UTC | CodeQL and lint scan of frontend |
| `ci.engine.yml` | Saturdays 23:32 UTC | CodeQL and lint scan of engine |
| `ci.security.yml` | Saturdays 23:32 UTC | CodeQL and lint scan of security |
| `ci.grype.yml` | Thursdays 20:37 UTC | Dependency vulnerability scan |
| `ops.workflow-cleanup.yml` | Saturdays 23:32 UTC | Cleans up old workflow run history |

Scheduled runs do not post PR comments.
