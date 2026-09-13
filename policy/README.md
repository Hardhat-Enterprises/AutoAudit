# Repository compliance policies

This directory contains Conftest policies for checking AutoAudit's own
repository configuration. The policy packages currently check Docker Compose
service resource limits and healthchecks, and GitHub Actions permission
declarations.

## Local verification

Install [Conftest](https://www.conftest.dev/install/), then run the policy unit
tests and compliant fixtures from the repository root:

```powershell
conftest verify --policy policy/compose
conftest test --policy policy/compose policy/fixtures/compose/compliant.yml
conftest verify --policy policy/github-actions
conftest test --policy policy/github-actions policy/fixtures/workflows/compliant.yml
```

To inspect the current Compose configuration without failing the command for
known baseline findings, run:

```powershell
conftest test --no-fail --policy policy/compose docker-compose.yml
conftest test --no-fail --policy policy/github-actions .github/workflows
```

## Scope

The Compose policy requires every Compose service to define both CPU and memory limits,
and a healthcheck with an executable test command. A disabled (`["NONE"]`) or
incomplete healthcheck does not satisfy the requirement. The initial GitHub Actions workflow
verifies the policy and its compliant fixture. It reports, rather than blocks
on, the repository's current Compose findings until the team agrees the
enforcement approach.

The GitHub Actions policy requires an explicit `permissions` declaration at the
workflow level or for each job. It reports jobs that rely on repository-default
`GITHUB_TOKEN` permissions, without changing existing workflows or blocking
pull requests.
