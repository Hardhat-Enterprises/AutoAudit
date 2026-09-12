# GCP Workload Identity Federation for GitHub Actions

**Workstream 4 (secrets and identity)** — replaces the long-lived `GCP_CREDENTIALS`
service account key used by `ops.collector.yml` with Workload Identity
Federation (WIF), so no GCP service account key ever needs to exist as a
file, in a GitHub secret, or anywhere else.

## Why this was needed

The collector workflow authenticated to GCP using a service account JSON
key stored in the `GCP_CREDENTIALS` GitHub secret. That pattern has two
structural problems, independent of how carefully the key itself is
handled:

- **The key never expires on its own.** If it leaks — which is exactly
  what happened in this repo (`engine/test-sa-key.json`, committed in
  `4fe952c8`, a full copy of a real service account key) — it stays valid
  until someone notices and manually revokes it in GCP IAM.
- **Anyone holding the file can use it**, from anywhere, indefinitely.
  There's no way for GCP to verify the caller is actually a GitHub Actions
  run of this repository rather than, say, someone who found the key in
  git history.

WIF removes the key from the picture entirely. GCP is configured to trust
a signed identity token that GitHub itself issues for each workflow run,
scoped to that one run, valid for minutes. There is nothing to leak.

## How it works

1. A workflow run requests an OIDC token from GitHub's built-in OIDC
   provider (`token.actions.githubusercontent.com`). This requires the
   `id-token: write` permission on the job.
2. The `google-github-actions/auth` action exchanges that token with GCP's
   Security Token Service.
3. GCP checks the token against a **Workload Identity Pool Provider**
   configured to trust GitHub's issuer, but only accepts tokens whose
   `repository` claim exactly matches `Hardhat-Enterprises/AutoAudit` (the
   `attribute-condition` in the setup script). This is the control that
   stops any other GitHub repository from using this trust relationship.
4. If the token passes, GCP lets it impersonate a specific service account
   for the remainder of the job. `google.auth.default()` in Python (or
   equivalent in other languages) picks these credentials up automatically
   - no code needs to know whether it's running against a key file or WIF.

## What changed in this repo

| File | Change |
|---|---|
| `engine/legacy/engine/GCPAccess.py` | `service_account.Credentials.from_service_account_info(json.loads(os.environ["GCP_CREDENTIALS"]))` replaced with `google.auth.default()` |
| `.github/workflows/ops.collector.yml` | Added a `google-github-actions/auth@v2` step and `id-token: write` permission; removed the `GCP_CREDENTIALS` env var |
| `infrastructure/gcp/setup-workload-identity.sh` | New - the one-time `gcloud` setup for the Pool, Provider, and service account |

## What still needs to happen (requires GCP IAM access)

This repository's automated tooling cannot create GCP resources - someone
with IAM admin access on `coastal-stone-470308-a0` needs to:

1. Run `infrastructure/gcp/setup-workload-identity.sh` once.
2. Add the two values it prints as **repository variables** (not
   secrets - they aren't sensitive) under
   `Settings > Secrets and variables > Actions > Variables`:
   - `GCP_WORKLOAD_IDENTITY_PROVIDER`
   - `GCP_SERVICE_ACCOUNT_EMAIL`
3. Confirm `ops.collector.yml` authenticates successfully via
   `workflow_dispatch` with these in place (the job itself stays
   hard-disabled via `if: false` until the point below is also resolved -
   see the comment at the top of the workflow file).
4. **Revoke the old key.** WIF being wired up does not, by itself, revoke
   the existing `GCP_CREDENTIALS` key - that's a separate, still-pending
   action in GCP IAM, and the single most urgent outstanding item from
   the Workstream 4 baseline audit (see `baseline-audit.md`, section 4a).
   Delete the `GCP_CREDENTIALS` GitHub secret once the key is confirmed
   revoked.

## What this does *not* fix

`ops.collector.yml` still auto-commits the data it collects (IAM policy,
network/firewall config, etc.) directly into the git repository as
plaintext JSON. WIF fixes *how the workflow authenticates* - it does
nothing about *what the workflow does once authenticated*. Committing a
live infrastructure snapshot into git history on every run is a separate
problem (broader attack-surface disclosure to anyone with repo/fork
access) that needs its own redesign - for example, uploading as a
short-retention workflow artifact instead of a git commit - before this
workflow's trigger should be restored. That is intentionally out of scope
for this change.

## Service account scope

The new `github-actions-readonly` service account is granted `roles/viewer`
and `roles/iam.securityReviewer` - a best-effort least-privilege set based
on reading the API calls in `GCPAccess.py`, chosen instead of reusing the
old `sa-noperms` account (which held `roles/editor` and whose key had
already leaked). This has not been verified against live API calls, since
preparing this change did not include GCP IAM access. Whoever runs the
setup script should confirm each API call in `GCPAccess.py` succeeds and
narrow the role set further if some part of it turns out to be
unnecessary.
