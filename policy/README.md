# Repository compliance policies

This directory contains Conftest policies for checking AutoAudit's own
repository configuration. The first policy package checks Docker Compose
service resource limits and healthchecks.

## Local verification

Install [Conftest](https://www.conftest.dev/install/), then run the policy unit
tests and the compliant fixture from the repository root:

```powershell
conftest verify --policy policy/compose
conftest test --policy policy/compose policy/fixtures/compose/compliant.yml
```

To inspect the current Compose configuration without failing the command for
known baseline findings, run:

```powershell
conftest test --no-fail --policy policy/compose docker-compose.yml
```

## Scope

The policy requires every Compose service to define both CPU and memory limits,
and a healthcheck with an executable test command. A disabled (`["NONE"]`) or
incomplete healthcheck does not satisfy the requirement. The initial GitHub Actions workflow
verifies the policy and its compliant fixture. It reports, rather than blocks
on, the repository's current Compose findings until the team agrees the
enforcement approach.
