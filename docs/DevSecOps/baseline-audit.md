# AutoAudit Baseline Security Audit — Week 4/5

**Workstream 4 (lead), Workstream 1 (partial)**

## 1. Hardcoded credentials in docker-compose.yml

A line-by-line review of docker-compose.yml identified three credentials stored in plain text:

- **Line 32** — `POSTGRES_PASSWORD: autoaudit_dev_password`. Carries a `# pragma: allowlist secret` comment, which suppresses detect-secrets from flagging it despite being a real password.
- **Line 107** — `SECRET_KEY=dev-secret-key-change-in-production`, the JWT signing key for backend-api.
- **Line 126** — `ENCRYPTION_KEY=Ps-HiS3ww5QzQPc_Mdu5-JyA_jCNbdFHMdiwWSlAfgM=`. Unlike the other two, this is not a placeholder — it is an active Fernet key encrypting stored M365/AWS/Azure/GCP credentials. It is repeated at **line 166** in the worker service, since both services require the same key to decrypt shared data.

The Postgres password additionally appears embedded in the `DATABASE_URL` connection string at lines 104 and 157, so a fix limited to the standalone `POSTGRES_PASSWORD` line alone would be incomplete. This class of finding is addressed by the [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html) and the [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker), both of which recommend externalizing secrets from configuration files rather than hardcoding them.

## 2. Repository hygiene

`git ls-files` confirms both `.DS_Store` and `output.json` remain tracked at the repository root. `.DS_Store` is listed in `.gitignore`, but this only prevents new commits from reintroducing it — since it was committed before the rule existed, it remains tracked and requires an explicit `git rm --cached` to remove. `output.json` is not covered by `.gitignore` at all.

## 3. Workflows missing a top-level permissions block

A review of all 15 workflow files under `.github/workflows` found seven with no top-level `permissions:` block, meaning they run with default token permissions rather than an explicit minimal grant, contrary to [GitHub's documented guidance on securing GITHUB_TOKEN permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token):

`ci.backend-api.yml`, `ci.engine.yml`, `ci.frontend.yml`, `ci.security.yml`, `ci.validate-alerts.yml`, `ops.collector.yml`, `ops.short-test.yml`

## 4. No scanning of full commit history for secrets

Pre-commit's [detect-secrets](https://github.com/Yelp/detect-secrets) only evaluates staged diffs at commit time and has no visibility into content already merged into history. A credential such as the one at line 126 could therefore remain in history indefinitely without detection.

A full-history scan using [gitleaks](https://github.com/gitleaks/gitleaks) (`--log-opts="--all"`), run on 2026-08-16, returned 31 findings. The raw scan output is retained locally rather than attached to this document, since several findings contain live key material. No equivalent check currently runs in CI.

Separately, `.secrets.baseline` is documented in CONTRIBUTING.md as containing 7 known findings, but its `results` field is currently empty, indicating the file is either stale or was regenerated incorrectly.

## 4a. Critical finding — live GCP service account private key in history

`engine/test-sa-key.json`, added in commit `4fe952c8` (2025-09-03, "added code in collecter to extract compute networks config"), contains a full unencrypted RSA private key for a GCP service account. This is a live credential, not a placeholder, and has been present in a public repository for approximately one year. Revocation requires GCP IAM access outside the scope of this document or its associated pull request, and remains the most urgent outstanding item from this audit.

## 5. Related finding — ops.collector.yml (tracked separately)

`ops.collector.yml` uses a long-lived `GCP_CREDENTIALS` secret to retrieve live GCP infrastructure data (IAM policy, network and firewall configuration) and commit it into `engine/test-configs/` on every push to `engine-development`. This is a long-lived-credential exposure within Workstream 4's scope, already addressed in PR #327.

## Next steps

This document is descriptive rather than corrective; no code changes are included, consistent with the Week 4–5 audit-only scope. Planned follow-up work:

1. Confirm revocation of the credential described in section 4a and record the outcome here.
2. Replace the three docker-compose.yml credentials with environment-variable references and a local `.env` file (PR #330).
3. Add a CI job running gitleaks against full commit history on every push.
4. Evaluate GCP Workload Identity Federation as a replacement for long-lived service account credentials. Code-side change and setup script prepared (see `docs/DevSecOps/workload-identity-federation.md`); still pending someone with GCP IAM access running the setup script and confirming the old key is revoked.
