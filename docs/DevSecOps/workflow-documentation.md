# GitHub Actions Workflow Documentation

Reference for anyone picking up the project who wants to understand what runs in `.github/workflows/`, when it runs, and why.

There are fourteen workflow files. This page names all fourteen; if you add one, add it here.

---

## Naming Convention

Workflow files use a prefix to group them by purpose:

| Prefix | Purpose |
|---|---|
| `ci.` | Code quality and security checks on PRs and pushes to main |
| `ops.` | Scheduled or operational jobs not tied to code review |
| `pr.` | PR metadata management |

---

## What runs, and when

| Workflow | Triggers | Path filter |
|---|---|---|
| `ci.backend-api.yml` | push `main`, PR to `main`, weekly | `backend-api/**` |
| `ci.frontend.yml` | push `main`, PR to `main`, weekly | `frontend/**` |
| `ci.engine.yml` | push `main`, PR to `main`, weekly | `engine/**` |
| `ci.security.yml` | push `main`, PR to `main`, weekly | `security/**` |
| `ci.compliance.yml` | push `main`, PR to any branch | `policy/**`, `docker-compose.yml`, `.github/workflows/**` |
| `ci.grype.yml` | push `main`, PR to `main`, weekly | `frontend/**`, `backend-api/**`, `engine/**` |
| `ci.gitleaks.yml` | push and PR on `main` and `staging`, weekly | none |
| `ci.opa-eval.yml` | push `engine-development`, **every** PR, manual | none |
| `ci.validate-alerts.yml` | push on any branch, PR to any branch | `infrastructure/monitoring/alerts/**` |
| `ops.branch-cleanup.yml` | PR to `main` closed | none |
| `ops.collector.yml` | manual only, and **hard-disabled** | none |
| `ops.short-test.yml` | push, but the filter never matches (see below) | `.github/workflows/short-test.yml` |
| `ops.workflow-cleanup.yml` | weekly, manual | none |
| `pr.size-warning.yml` | PR to `main` opened / synchronized / reopened | none |

A path-filtered workflow does not start when a PR touches nothing inside its filter, and does not appear in the Actions tab for that PR. The weekly schedule carries no path filter, so a scheduled run executes regardless of what changed.

Three workflows omit a branch filter on `pull_request`: `ci.compliance.yml` and `ci.validate-alerts.yml`, which are still narrowed by their path filters, and `ci.opa-eval.yml`, which has neither. `ci.opa-eval.yml` therefore runs on every pull request in the repository.

---

## CodeQL and lint workflows

`ci.backend-api.yml`, `ci.frontend.yml`, `ci.engine.yml` and `ci.security.yml` share a shape.

**`analyze`** runs CodeQL static analysis and reports findings to the GitHub Security tab. The backend-api workflow also installs and runs Bandit in the same job, as a Python-specific check.

**`run-lint`** runs Super Linter in `ci.backend-api.yml`, `ci.engine.yml` and `ci.security.yml`, with several linters disabled to keep it focused on the languages used in each area. `ci.frontend.yml` does not use Super Linter: its lint job runs `npm run lint`, which `frontend/package.json` defines as `oxlint`.

**A test job**, in three of the four:

| Workflow | Job | What it runs |
|---|---|---|
| `ci.backend-api.yml` | `test` | `pytest` under `uv`, in `backend-api/` |
| `ci.engine.yml` | `test` | `pytest tests/test_wiring.py` only — structural checks, not the engine suite |
| `ci.frontend.yml` | `build-and-test` | `tsc --noEmit`, `npm test`, `npm run build` |
| `ci.security.yml` | — | no test job |

`ci.engine.yml` runs one test file. The Rego policies under `engine/policies/` are not evaluated by any workflow in this repository — see `ci.opa-eval.yml` below.

### PR status comment

After the other jobs finish, a `report` job posts a table on the PR showing which jobs passed or failed, with a link to the run logs. On subsequent pushes the comment updates in place.

```
analyze  ─┐
run-lint ─┼─→  report
test     ─┘
```

The report job is `if: always() && github.event_name == 'pull_request'`, so it runs whatever the other jobs did, and never on push or schedule. The link to the run logs appears only when something failed.

The comment does not always arrive. `ci.backend-api.yml` and `ci.security.yml` detect a pull request from a fork and skip the comment with a log line; `ci.engine.yml` and `ci.frontend.yml` have no such guard and attempt the write, which a fork's read-only token cannot perform.

### `ci.security.yml`

The `security/` directory contains the TPRM Scanner from T2 2025 and is no longer actively maintained. The workflow is kept so changes to that directory are still scanned but is not expected to trigger under normal development.

---

## Grype Dependency Scan

**`ci.grype.yml`** triggers on PRs and pushes to `main` when files change inside `frontend/**`, `backend-api/**` or `engine/**`, and weekly.

It runs `anchore/scan-action@v6` as a **directory** scan over `path: "."`, checking dependency files (`pyproject.toml`, `requirements.txt`, `package-lock.json`) against public vulnerability databases without needing a built image. Results upload to the GitHub Security tab as a SARIF report.

**`fail-build` is `true`, with `severity-cutoff: critical`.** A critical finding fails the check; anything at high or below is reported and does not. An earlier version of this page said `fail-build` was false — it is not, and a contributor who assumed otherwise would be surprised by a red check. Whether a failing check actually blocks a merge is a branch-protection setting, which is not visible in this repository.

The workflow keeps a commented-out image scan from before Docker Hub was decommissioned. A directory scan cannot see a base image or an OS package layer, so nothing in this repository scans a built image.

Note: the Security tab upload requires GitHub Advanced Security, which is free for public repos and requires a paid plan for private ones.

---

## Secret scanning

**`ci.gitleaks.yml`** runs on pushes and pull requests targeting `main` and `staging`, and weekly on Mondays. It checks out the full history (`fetch-depth: 0`) and scans all of it (`--log-opts="--all"`), so a secret removed in a later commit is still found.

It installs a pinned gitleaks (8.30.1) and verifies the release checksum before using it. Findings are matched against `.gitleaks-baseline.json` at the repository root; anything not in that baseline exits non-zero and **fails the build**. Adding a finding to the baseline is how you accept it, and the baseline is reviewable in the diff.

---

## Compose and workflow policy

**`ci.compliance.yml`** runs Conftest over the Rego policies in `policy/`. It verifies the policy unit tests and the compliant fixtures — those steps gate — and then reports findings against the live `docker-compose.yml` and `.github/workflows/` with `--no-fail`, which do not.

It is the only `ci.` workflow whose `pull_request` trigger has no branch filter beyond its paths, and it watches `.github/workflows/**`, so editing any workflow file runs it.

---

## Other CI workflows

**`ci.opa-eval.yml`** does not evaluate the benchmark policies. It runs `engine/legacy/engine/aggregator.py` and `engine/legacy/engine/json_to_pdf.py` over the legacy engine, and uploads a JSON report and a PDF as artifacts. It does not read `engine/policies/`.

No policy verdict from it can fail the workflow: `aggregator.py` catches a non-zero `opa` exit and records the stderr into the report JSON rather than raising. A crash in either script, or a missing artifact, still fails the job.

Nothing in `.github/workflows/` runs `opa check`, `opa test` or `opa eval` against the CIS or Essential Eight policy corpus.

**`ci.validate-alerts.yml`** validates the Prometheus alerting rules under `infrastructure/monitoring/alerts/`. An earlier version of this page called it a conceptual piece that "does not do anything meaningful"; it does. It runs `infrastructure/monitoring/alerts/tests/promtool_validation.sh`, which is `set -euo pipefail` and calls `promtool check rules`, so a syntax error in a validated rule fails the build.

Three limits are worth knowing:

- The script does not validate the directory. It globs five filename patterns — `*alerts.yaml`, `*_errors.yaml`, `*health.yaml`, `*utilisation.yaml`, `*security.yaml` — non-recursively. Every rule file present today matches one, but a new `custom_rules.yaml` would trigger the workflow and escape validation.
- It installs promtool with `apt-get install -y prometheus`, unpinned, so the tool version is whatever the runner image offers that day.
- `promtool check rules` is a syntax check. It does not test that a threshold fires when it should, and it does not check that an alert reads a metric the application actually emits.

---

## Ops workflows

**`ops.branch-cleanup.yml`** deletes the head branch after a pull request into `main` is merged. It only acts on branches in this repository — not forks — and never on `main`.

**`ops.collector.yml`** is **hard-disabled and runs nothing.** Its push trigger is commented out, leaving only `workflow_dispatch`, and the job itself carries `if: false` so that even a manual run does nothing. Its header records the two conditions for re-enabling it: the `GCP_CREDENTIALS` secret is a long-lived service-account JSON key and must be replaced with Workload Identity Federation, and the workflow auto-commits live GCP infrastructure data — IAM policies, firewall rules, SQL/BigQuery/Dataproc details, DNS zones — into `engine/test-configs/` on every run. Do not restore the trigger before both are addressed.

**`ops.workflow-cleanup.yml`** runs weekly, on Sundays at 00:00 UTC, **as a dry run**: the scheduled step is `node cleanup-workflows.js --dryRun=true`, which reports and deletes nothing. Actual deletion requires a manual `workflow_dispatch` with `dry_run=false` **and** `confirm=DELETE`; without the confirmation the job refuses and exits 1.

**It is not a retention policy.** The workflow passes `RETENTION_DAYS: 30` and the dispatch input is described as "Delete runs older than this many days", but `tools/workflow-cleanup/cleanup-workflows.js` never reads that variable. It selects by how long a run *took*: under 10 seconds is deleted, 10 seconds to 2 minutes is deleted, 2 minutes or more is kept. It also fetches a single page of 20 runs with no pagination.

So a real deletion run would remove recent short runs and keep old long ones, which is not what the input description promises. Nothing here prunes by age, and this workflow should not be cited as evidence that run history is retained for any period.

**`ops.short-test.yml`** is the canary used to check that the cleanup workflow has something to clean. It is meant to trigger only when its own file changes, but its filter names `.github/workflows/short-test.yml` while the file is `.github/workflows/ops.short-test.yml`: commit `155f82aa` applied the `ops.` prefix and left the filter behind. The filter now names a path that does not exist, so editing the workflow does not run it. Anyone who adds a file at the old path would trigger it by accident.

---

## PR workflows

**`pr.size-warning.yml`** flags unusually large pull requests: above 30 changed files or 500 changed lines it emits a `core.warning` annotation and writes a job summary with the numbers. It does **not** post a PR comment, and it does not block the PR. `docs/DevSecOps/pr-size-warning.md` has the reasoning behind the thresholds.

The three `pr.preview-*` workflows — deploy, instructions and teardown — were removed. `git log --diff-filter=D -- .github/workflows/pr.preview-deploy.yml` has the original.

---

## Scheduled runs

| Workflow | Schedule (UTC) | Purpose |
|---|---|---|
| `ci.backend-api.yml` | Saturdays 23:32 | CodeQL and lint scan of backend-api |
| `ci.frontend.yml` | Saturdays 23:32 | CodeQL and lint scan of frontend |
| `ci.engine.yml` | Saturdays 23:32 | CodeQL and lint scan of engine |
| `ci.security.yml` | Saturdays 23:32 | CodeQL and lint scan of security |
| `ci.grype.yml` | Thursdays 20:37 | Dependency vulnerability scan |
| `ci.gitleaks.yml` | Mondays 03:00 | Full-history secret scan |
| `ops.workflow-cleanup.yml` | Sundays 00:00 | Dry run only — reports which of the 20 most recent runs it would delete, and deletes nothing |

Scheduled runs do not post PR comments.
