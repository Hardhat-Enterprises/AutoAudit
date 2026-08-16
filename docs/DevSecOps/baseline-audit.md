# AutoAudit Baseline Security Audit - Week 4/5

**Workstream 4 (lead), Workstream 1 (partial)**

## 1. Hardcoded credentials in docker-compose.yml

I went through docker-compose.yml line by line and found three real credentials sitting in plain text:

- **Line 32** - `POSTGRES_PASSWORD: autoaudit_dev_password`. It has a `# pragma: allowlist secret` comment next to it, which tells detect-secrets to ignore it, so it won't get flagged even though it's a real password sitting in the file.
- **Line 107** - `SECRET_KEY=dev-secret-key-change-in-production`. This is the JWT signing key for backend-api.
- **Line 126** - `ENCRYPTION_KEY=Ps-HiS3ww5QzQPc_Mdu5-JyA_jCNbdFHMdiwWSlAfgM=`. This one's worse than the other two because it's not a placeholder - it's an actual Fernet key currently being used to encrypt stored M365/AWS/Azure/GCP credentials. It's also repeated on **line 166** in the worker service, since both services need the same key to decrypt the same data.

It is also worth noting that the Postgres password isn't just sitting in one place either it's baked into the `DATABASE_URL` connection string on lines 104 and 157 as well, so fixing the standalone `POSTGRES_PASSWORD` line alone wouldn't be enough.

## 2. Repo hygiene

Ran `git ls-files` and confirmed both `.DS_Store` and `output.json` are still tracked at the repo root. `.DS_Store` is actually already in `.gitignore`, but that only stops *new* commits from adding it back since it was committed before the ignore rule existed, it's still sitting in the repo and needs an explicit `git rm --cached` to actually remove it. `output.json` isn't in `.gitignore` at all, so it'll keep coming back if it's ever regenerated locally.

## 3. Workflows with no permissions block

Checked all 15 workflow files under `.github/workflows` for a top-level `permissions:` block. Seven don't have one, which means they're running with whatever the default token permissions are instead of something explicit and minimal:

`ci.backend-api.yml`, `ci.engine.yml`, `ci.frontend.yml`, `ci.security.yml`, `ci.validate-alerts.yml`, `ops.collector.yml`, `ops.short-test.yml`

## 4. Nothing scans full commit history for secrets

Pre-commit's `detect-secrets` only looks at what's staged when you commit, it has no visibility into anything already merged. So a key like the one on line 126 could sit in the repo's history indefinitely and nothing would catch it.

I ran gitleaks locally against the full history (`--log-opts="--all"`) on 2026-08-16 and it came back with 31 findings, log kept locally, not attached to this doc since some of the findings contain live key material. There's currently no equivalent check running in CI, so this only exists because I ran it manually.

Also worth flagging: `.secrets.baseline` is supposed to document known findings (CONTRIBUTING.md says there are 7), but when I opened the file its `results` section is completely empty. Either it's out of date or something regenerated it incorrectly, either way it's not doing what the docs say it's doing.

## 4a. Critical finding - live GCP service account private key in history

`engine/test-sa-key.json`, added in commit `4fe952c` (2025-09-03, "added code in collecter to extract compute networks config"), contains a full unencrypted RSA private key for a GCP service account. Unlike the docker-compose credentials, this isn't a placeholder, it's a real key that's been sitting in a public repo for close to a year. **This has not yet been escalated for revocation as of 2026-08-16.** Flagging it here as the single most urgent action item from this audit — it needs to be raised with whoever has GCP admin access as soon as possible, independent of this doc's review timeline.

## 5. One more thing I found, but isn't mine to fix

While going through workflows I came across `ops.collector.yml`, it uses a long-lived `GCP_CREDENTIALS` secret to pull live GCP infrastructure data (IAM policy, network and firewall config) and auto-commit it into `engine/test-configs/` on every push to `engine-development`. That's a long-lived-secret problem directly in Workstream 4's territory, but Irusha already found it independently and has a PR up to disable it and clean up the exposed data. Flagging it here for the record since it's relevant, not because I'm picking it up.

## What's next

This audit doesn't change any code. Once it's merged, here's what I'm doing with it:

1. Raise the GCP service account key in 4a for revocation, flagging it in the next team meeting, and will update this doc once it's confirmed revoked.
2. Pull the three docker-compose secrets out into a `.env` file the repo never sees, and rotate the Fernet key since it's already been exposed.
3. Add a gitleaks job to CI that scans full history on every push, not just pre-commit.
4. Write up a design for using GCP Workload Identity Federation instead of long-lived keys, there's no GCP CI pipeline built yet, so this is about getting the pattern right before one exists, not migrating something that's already there.