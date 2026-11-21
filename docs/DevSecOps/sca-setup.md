# Dependency checks and automatic updates

Our code relies on third-party packages. Software composition analysis (SCA)
checks those packages for known vulnerabilities. Grype scans the repository,
dependency review checks changes in a pull request (PR), and Dependabot opens
PRs to update dependencies.

## What runs and when

| Tool | What it checks | When it runs | What fails the check |
|---|---|---|---|
| Grype | Packages it can detect in the repository | PRs targeting `main` and pushes to `main` that change `frontend/**`, `backend-api/**`, or `engine/**`; also Thursdays at 20:37 UTC | A known **critical** vulnerability |
| Dependency review | Dependency changes introduced by a PR | When a PR is opened, reopened, or receives new commits; all target branches and paths | An introduced dependency with a known **high or critical** vulnerability |
| Dependabot | Available package and Docker image updates | See the schedules below | It opens update PRs rather than passing or failing a scan |

A red check can also mean a tool, API, or upload failed. Start with the failed
step's logs to find out which problem you have.

## Grype: check the repository's dependencies

Configuration: [ci.grype.yml](../../.github/workflows/ci.grype.yml).

Look for **Grype Dependency Vulnerability Scan** in Actions, then **Scan
dependencies for vulnerabilities**. It uses `anchore/scan-action@v6` with
`path: "."` to scan from the repository root. It does not build a Docker image.
It can only check packages and versions it detects.

The folders in the table decide when a PR or push starts Grype. Once started,
it scans the repository. Changes only under `docs/`, `security/`, or `.github/`
do not start it. The weekly run scans the default branch regardless of changed
paths. There is no manual-run trigger.

The settings `fail-build: true` and `severity-cutoff: critical` mean a critical
finding fails the scan. Lower-severity findings are reported but do not fail this
policy. Grype can flag an existing package even if your PR did not change it.

Results go into `grype-report.sarif`, a report GitHub displays under **Security →
Code scanning**. **Upload vulnerability report** uses `if: always()`, so it tries
to upload even after a failed scan. If the scanner stopped before writing the
file, the upload can fail too. There is no separate Actions artifact to download.

## Dependency review: check what a PR introduces

Configuration: [ci.dependency-review.yml](../../.github/workflows/ci.dependency-review.yml).

The **Dependency Review** workflow runs the **Dependency review** check. It uses
GitHub's dependency graph and security advisories without installing packages or
running the app. It runs on PRs only, with no path filter or schedule.

It checks runtime, development, and unknown dependency scopes. High and critical
findings fail the check; low and moderate findings do not fail this policy.
License checking is off. GitHub needs to recognise the dependency files and have
the dependency data for the comparison.

The logs and Actions job summary list affected packages, advisories, and patched
versions where available. The workflow also tries to comment on failures for PRs
from this repository, if its token allows it. It skips comments for fork PRs and
runs started by `dependabot[bot]`. Check the logs even when there is no comment.

For more detail, see [Dependency review](dependency-review.md).

## Dependabot: propose dependency updates

Configuration: [dependabot.yml](../../.github/dependabot.yml).

| Package manager | Directories | Schedule | Routine version-update PRs |
|---|---|---|---|
| `uv` | `/backend-api`, `/engine` | Weekly | Paused: `open-pull-requests-limit: 0` |
| `pip` | `/security` | Weekly | Paused: limit `0` |
| `npm` | `/frontend` | Weekly | Paused: limit `0` |
| `github-actions` | `/` | Weekly | Paused: limit `0` |
| `docker` | `/backend-api`, `/engine`, `/frontend`, `/security` | Monthly | Enabled in this file; uses the default PR limit |

Each Docker entry allows the default five open version-update PRs. Monthly checks
run on the first day of the month; this file sets no exact time. Dependabot opens
a PR when it finds an eligible update and has room under the limit.

Setting the limit to zero pauses routine version-update PRs for that entry.
Dependabot alerts and security-update PRs are separate features. Zero does not
disable security updates; ask a maintainer whether those are enabled in GitHub.
See GitHub's [Dependabot options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#open-pull-requests-limit).

Review Dependabot PRs like any other change: read the version changes and release
notes, and check the CI results. This file does not set up automatic merging.

## What actually blocks merging?

GitHub blocks a PR when a failed check is required by the target branch's
protection rules or ruleset, unless a permitted bypass is used. The workflow
files do not tell us which checks are required. Ask a maintainer to confirm the
rules for your target branch. A failed weekly or push run reports a problem on
that branch; it does not itself decide whether a PR can merge. See GitHub's
[required status checks guidance](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging).

## How to read and fix a failure

1. Open the PR's **Checks** tab or the run under **Actions**. Find the first
   failed step and read its logs.
2. For a vulnerability, note the package, installed version, severity, advisory
   ID (CVE or GHSA), and fixed version if listed. Grype results also appear under
   **Security → Code scanning** if the upload succeeded.
3. Update or remove the package, then regenerate the lockfile with the project's
   package manager. If another package pulls it in, try updating that parent
   package. Discuss options with maintainers if there is no safe fix.
4. Run the affected component's tests, review the diff, and push the fix to your
   PR branch. The applicable checks will run again.

A new **high** finding can fail dependency review while staying below Grype's
**critical** cutoff. An unchanged package with a **critical** finding can fail
Grype even if dependency review finds no new problem.

| What you see | What to check next |
|---|---|
| Dependency graph unavailable or an API error | Read the dependency-review logs. Ask a maintainer to check GitHub feature access and permissions. |
| Grype download or vulnerability-database error | Read the scan logs. Retry once a temporary service problem is resolved. |
| SARIF upload denied or report file missing | Check whether the scan wrote the report, then check code-scanning access. A failed upload does not mean the scan passed. |
| Dependabot cannot open an update PR | Open **Insights → Dependency graph → Dependabot → Recent update jobs**. Check for registry access or dependency resolution errors, or a reached PR limit. Ask a maintainer if you cannot access the logs. |

GitHub provides [instructions for viewing Dependabot job logs](https://docs.github.com/en/code-security/how-tos/view-and-interpret-data/view-dependabot-logs).

Include the advisory or error in the PR discussion so reviewers can follow the
fix. Changes to thresholds or exceptions need maintainer review.

Update this page when the automation changes. For action settings, see
[Anchore](https://github.com/anchore/scan-action/tree/v6) and
[GitHub dependency review](https://github.com/actions/dependency-review-action).
