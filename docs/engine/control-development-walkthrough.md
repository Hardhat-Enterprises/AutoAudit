# Control development walkthrough

This walkthrough uses **CIS Microsoft 365 Foundations 1.2.2** (Ensure sign-in to shared mailboxes is blocked) as a worked example.

It is **one workflow**, not the only supported pattern. Graph-only Entra controls, SharePoint PnP tenant settings, and Essential Eight device policies follow the same ideas (evidence → collector → registry → Rego → metadata → tests → live scan) but different clients and folders. For SharePoint, use [SharePoint control development](sharepoint-control-development.md) instead of copying the Exchange cmdlets below.

Architecture and result states: [Engine architecture](architecture.md). Hub: [Engine onboarding](README.md).

## 1. Read the requirement

Start from the CIS (or other benchmark) text, not from an existing file name.

For 1.2.2 the security intent is: shared mailboxes must not allow direct sign-in. People should reach them through their own accounts with delegated access.

Write down:

- the compliant setting
- the evidence that proves it
- the API or cmdlet that can return that evidence
- the minimum permissions

Confirm the intent with the team that owns the benchmark if the wording is ambiguous.

## 2. Read metadata before writing code

Open the benchmark [`metadata.json`](../../engine/policies/cis/microsoft-365-foundations/v6.0.0/metadata.json) for the control.

For 1.2.2 that file is the wiring the worker uses: `control_id`, `automation_status`, `data_collector_id`, and `policy_file`.

This step shows whether a collector already exists, whether a policy is already linked, and whether the control is still `not_started`. It avoids duplicating work and keeps `ready` from being set too early.

`metadata.json` is the current source of automation status. Do not mark `ready` until collector, policy, and tests are complete.

## 3. Select or extend a collector

Inspect the assigned collector, if any. For 1.2.2 that is [`exchange.mailbox.mailboxes`](../../engine/collectors/exchange/mailbox/mailboxes.py), registered in [`registry.py`](../../engine/collectors/registry.py).

This control needs Exchange Online PowerShell (`Get-EXOMailbox`, `Get-User`), not Microsoft Graph. The worker routes `exchange.*` collectors (except `exchange.dns.*`) to the PowerShell client. See [architecture](architecture.md#graph-versus-powershell).

Run or inspect the collector **before** writing Rego:

- If no collector exists, create one (see [`engine/collectors/README.md`](../../engine/collectors/README.md)).
- If a collector exists, confirm it returns every field the policy needs.
- Extend it only when a required field is missing.

For 1.2.2, listing shared mailboxes was not enough. Sign-in blocked is represented as the associated user’s `AccountDisabled` flag, which required `Get-User` in addition to `Get-EXOMailbox`.

Use representative tenant data where you can. An empty mailbox list cannot prove the sign-in check works.

Graph collectors can be exercised with [Manual collector testing](manual-collector-testing.md). PowerShell/PnP collectors are validated through the Worker and PowerShell service on the local stack.

## 4. Normalise evidence

Return a small, stable dictionary. Do not dump the raw cmdlet object into OPA.

The 1.2.2 collector returns:

```json
{
  "shared_mailboxes": [
    {
      "display_name": "...",
      "user_principal_name": "...",
      "external_directory_object_id": "...",
      "account_disabled": true
    }
  ],
  "total_shared_mailboxes": 1
}
```

OPA sees this dict at the **root** of `input`. Policies must read `input.shared_mailboxes`, not a nested wrapper the collector does not send.

Keep collectors free of pass/fail logic. A collector may report `account_disabled: false`; only Rego decides that this fails the control.

## 5. Register the collector

If you added a class, import it and add a `DATA_COLLECTORS` entry in [`registry.py`](../../engine/collectors/registry.py). The ID must match `data_collector_id` in metadata.

1.2.2 uses `exchange.mailbox.mailboxes` → `MailboxesDataCollector`. Unknown IDs fail at scan time with an error, not a skip.

## 6. Write Rego

Add the policy next to the other files for that benchmark version, for example [`1.2.2_shared_mailbox_signin_blocked.rego`](../../engine/policies/cis/microsoft-365-foundations/v6.0.0/1.2.2_shared_mailbox_signin_blocked.rego).

Package names must match what the worker derives from framework, benchmark, version, and control ID (see [architecture](architecture.md#metadata-registration-and-rego)).

Cover at least:

- compliant evidence
- non-compliant evidence
- missing or null fields (fail closed; do not pass)

The 1.2.2 policy treats `account_disabled == false` as non-compliant and `null` as unknown, and it defaults to non-compliant when evaluation cannot complete.

More convention notes: [`engine/policies/README.md`](../../engine/policies/README.md). Optional behavioural fixtures: [Compliance engine verification](compliance-engine-verification.md).

## 7. Add unit tests

Add focused tests for compliant, non-compliant, empty, null, and mixed inputs. 1.2.2 uses [`engine/tests/test_cis_1_2_2_shared_mailbox_signin.rego`](../../engine/tests/test_cis_1_2_2_shared_mailbox_signin.rego).

Unit tests check policy logic without a live tenant. They do **not** replace a full scan.

From `engine/`, also run the Engine pytest suite (see [`engine/pyproject.toml`](../../engine/pyproject.toml) `testpaths`). Wiring tests catch metadata and registry mistakes that a single Rego file will not.

## 8. Wire metadata last

Only after collector output, Rego, and tests look right, update `metadata.json`:

- `data_collector_id` — registry ID
- `policy_file` — Rego filename
- `automation_status` — `ready`
- permissions and notes as needed

Setting `ready` too early dispatches a half-finished control into live scans.

## 9. Validate locally and with a live scan

1. Engine pytest from `engine/`.
2. OPA tests for the new `.rego` test file.
3. Rebuild the Worker if you changed Python collectors (image-baked). Restart OPA if you changed bind-mounted policies.
4. Run a scan for the target framework in the local UI.

How to bring the stack up: [Getting Started](../GETTING_STARTED.md). SharePoint-specific runtime: [SharePoint local runtime](sharepoint-local-runtime.md).

## 10. Tenant failure versus runtime error

| Outcome | Meaning |
| --- | --- |
| **Passed** | Policy ran; tenant matches the requirement |
| **Failed** | Policy ran; tenant does not match. This is successful automation |
| **Skipped** | Control was not dispatched (`not_started`, `manual`, and similar) |
| **Error** | Collection or evaluation broke (auth, unknown collector, HTTP 403, crash) |

A failed 1.2.2 result because a shared mailbox still allows sign-in is a tenant finding. An error because Exchange PowerShell could not run is an implementation or runtime problem.

Confirm the dashboard (or scan API) shows the same status the worker wrote. Passing unit tests alone does not prove the Worker, OPA, and UI are using your files.

## Recommended sequence

Understand the control → review metadata → inspect the collector → test or extend the collector → normalise output → register if new → implement Rego → unit tests → update metadata to `ready` → pytest / OPA → live scan → confirm UI.

## Related patterns

- Graph Entra collectors: [`engine/collectors/README.md`](../../engine/collectors/README.md) and [Manual collector testing](manual-collector-testing.md)
- SharePoint PnP: [SharePoint control development](sharepoint-control-development.md)
- PR readiness checklist: [Engine onboarding hub](README.md#before-submitting-a-pr)
