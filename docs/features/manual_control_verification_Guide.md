# Manual Control Verification - User Guide

**Feature owner:** Aaron Alijani (backend/DevOps)  

---

## Overview

AutoAudit scans Microsoft 365 tenants against the CIS M365 Foundations Benchmark
and writes a pass, fail, or pending result for each control. Most controls are
resolved automatically through the Microsoft Graph API. However, 14 controls
cannot be checked programmatically, either because Microsoft provides no API
for the setting or because the required API is not yet integrated into AutoAudit.

This feature gives auditors a structured, consistent workflow for handling those
14 pending controls manually, and lays the backend foundation for semi-automated
verification in Phase 2.

---

## The 14 Manual Controls

Not all 14 controls are manual for the same reason. They fall into two groups.

### Truly manual- no API exists

These controls have no public Microsoft API and are only reachable through internal
Microsoft APIs that app registrations cannot access, or require a human judgment
call that cannot be expressed as a configuration value. They will remain manual
until Microsoft exposes the relevant API surface.

| Control ID | Severity | Service  | Why manual                                                                                                   |
| ---------- | -------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| 1.1.2      | High     | Entra ID | Which accounts are designated as break-glass is an organisational policy decision; no API can read this      |
| 1.3.8      | Medium   | Sway     | Microsoft provides no API for Sway external sharing settings                                                 |
| 2.2.1      | High     | Entra ID | Defining which accounts to monitor is a human decision; no API can confirm it is set up correctly            |
| 2.4.3      | Medium   | Defender | MCAS configuration must be verified through the security portal; no stable API exposes its enabled state     |
| 5.1.2.1    | Medium   | Entra ID | The relevant endpoint only exists in the Microsoft Graph beta API, which is not stable enough for production |
| 5.1.2.4    | Medium   | Entra ID | Only accessible through an internal Azure API, not available to app registrations                            |
| 5.1.2.5    | Low      | Entra ID | Microsoft does not expose this setting through the Graph API                                                 |
| 5.1.2.6    | Low      | Entra ID | Same as 5.1.2.4, internal Azure API only                                                                     |
| 5.1.8.1    | High     | Entra ID | Verifying password hash sync requires checking on-premises AD Connect directly, no cloud API exists          |
| 5.2.4.1    | Medium   | Entra ID | SSPR settings are not exposed through the Graph API                                                          |
| 8.4.1      | Medium   | Teams    | Teams app permission policy configuration is only accessible through the Teams admin portal                  |

### Automation candidates- manual for now

These controls can eventually be automated once outstanding blockers are resolved.

| Control ID   | Severity | Service    | Blocker                                                                                           | When it can be automated                                                                                        |
| ------------ | -------- | ---------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 7.2.8        | Medium   | SharePoint | The `sharepoint.spo_tenant` collector exists in the codebase but raises `NotImplementedError`     | Once the collector implementation is completed, no other changes are needed.                                    |
| 9.1.1–9.1.12 | Medium   | Fabric     | AutoAudit has not yet confirmed that app-only authentication works against Fabric admin endpoints | Once Fabric app-only auth is validated, all 12 controls can be automated in one go. |

---

## How it works - the two database tables

The feature is split across two tables that work together.

### `manual_scan_result_detail` (PR #166)

This is the **record-keeping** side. When an auditor manually verifies a pending
control, this table records that they did it.

| Field                       | Purpose                                                                      |
| --------------------------- | ---------------------------------------------------------------------------- |
| `scan_result_id`            | Links one-to-one to the existing `scan_result` row for this control          |
| `user_id`                   | Which auditor performed the verification                                     |
| `comment`                   | An optional free-text note that the auditor leaves explaining their decision |
| `created_at` / `updated_at` | Timestamps                                                                   |

`scan_result` remains the single source of truth for the outcome (pass/fail/pending).
This table only adds the manual-specific fields that `scan_result` does not have.

**Ownership rule:** An auditor can only read, update, or delete their own verification
records. Attempting to access another user's record returns HTTP 403.

### `control_verification_template` (PR #229)

This is the **instruction** side. For each of the 14 manual controls, this table
stores what the auditor needs to check and what compliant evidence looks like.

| Field           | Purpose                                                                     |
| --------------- | --------------------------------------------------------------------------- |
| `framework`     | e.g. `CIS`                                                                  |
| `benchmark`     | e.g. `CIS M365 Foundations`                                                 |
| `version`       | e.g. `v6.0.0`                                                               |
| `control_id`    | e.g. `1.1.2` - matches `scan_result.control_id`                             |
| `title`         | Human-readable control title from the benchmark                             |
| `instructions`  | Numbered, portal-specific steps telling the auditor where to look           |
| `keywords`      | JSONB list of terms expected to appear in compliant evidence                |
| `severity`      | `high`, `medium`, or `low`- drives confidence scoring thresholds in Phase 2 |
| `evidence_type` | Expected evidence format: `screenshot`, `pdf_export`, or `comment_only`     |

The combination of `(framework, benchmark, version, control_id)` is unique. This
means the same control ID can carry different instructions across the CIS benchmark
versions (e.g. `1.1.2` in v3.1.0 versus v6.0.0) without collision. When Phase 2
seed the 14 templates, this design prevents unique constraint failures.

---

## End-to-end flow

**Step 1 : Scan runs**  
AutoAudit runs a benchmark scan against the tenant. For each of the 14
manual controls, a row is written to `scan_result` with status `pending`.
Automated controls resolve immediately; these 14 wait for an auditor.

**Step 2: Auditor opens a pending control**  
The auditor sees the pending controls in the frontend. When they open one,
the frontend calls
`GET /v1/verification-templates/{framework}/{benchmark}/{version}/{control_id}`
to fetch the template for that control.

**Step 3 : Instructions displayed**  
The template returns the numbered portal-specific instructions and the
keyword list for that control. The auditor sees exactly where to go in the
M365 admin portal and what compliant evidence should contain.

**Step 4: Auditor uploads screenshot**  
The auditor follows the instructions, navigates to the relevant M365 portal
screen, captures a screenshot or PDF export, and uploads it as evidence.

**Step 5: OCR extracts text**  
The existing evidence scanner in `/security` runs OCR on the uploaded file
and extracts the text content.

**Step 6: Auditor reviews and confirms**  
The auditor records their verdict via `POST /v1/manual-verification/` — pass
or fail, with an optional comment. Phase 2 will add confidence scoring here:
the scanner matches the extracted text against the template keywords and
suggests a verdict with a confidence score before the auditor confirms.

**Step 7: Status propagation**  
The backend updates `scan_result.status` from `pending` to `pass` or `fail`.
The `finalize_scan_if_complete` function fires to check whether all controls
in the scan are now resolved.

**Step 8: Scan completes**  
Once all 14 manual controls have a verdict, the scan reaches completed state.

---

## API endpoints

All endpoints require a valid JWT bearer token. Obtain one via `POST /v1/auth/login`.

### Manual Verification - `/v1/manual-verification`

| Method | Path                                                      | Description                                    | Auth required           |
| ------ | --------------------------------------------------------- | ---------------------------------------------- | ----------------------- |
| POST   | `/v1/manual-verification/`                                | Submit a manual verification for a scan result | Auditor (own scan only) |
| GET    | `/v1/manual-verification/{id}`                            | Get a verification by ID                       | Owner only              |
| GET    | `/v1/manual-verification/by-scan-result/{scan_result_id}` | Get a verification by scan result              | Owner only              |
| PATCH  | `/v1/manual-verification/{id}`                            | Update the comment on a verification           | Owner only              |
| DELETE | `/v1/manual-verification/{id}`                            | Delete a verification record                   | Owner only              |

### Verification Templates - `/v1/verification-templates`

| Method | Path                                                                        | Description                    | Auth required          |
| ------ | --------------------------------------------------------------------------- | ------------------------------ | ---------------------- |
| POST   | `/v1/verification-templates/`                                               | Create a template (admin only) | Admin                  |
| GET    | `/v1/verification-templates/`                                               | List all templates             | Any authenticated user |
| GET    | `/v1/verification-templates/{framework}/{benchmark}/{version}/{control_id}` | Get a specific template        | Any authenticated user |
| PATCH  | `/v1/verification-templates/{framework}/{benchmark}/{version}/{control_id}` | Update a template (admin only) | Admin                  |
| DELETE | `/v1/verification-templates/{framework}/{benchmark}/{version}/{control_id}` | Delete a template (admin only) | Admin                  |

All endpoints are visible in Swagger at `http://localhost:8000/docs` under the
**Verification Templates** section.

---

## Confidence scoring - how Phase 2 will suggest verdicts

When an auditor uploads evidence in Phase 2, the existing evidence scanner
(OCR + keyword matching in `/security`) will extract text from the file and check
How many of the template's keywords appear in it? The match percentage is turned
into a verdict suggestion based on the severity of the control.

### Base thresholds

| Match % | Suggestion      | Meaning                                                      |
| ------- | --------------- | ------------------------------------------------------------ |
| ≥ 80%   | Suggest pass    | Enough keywords found: compliant evidence likely captured    |
| 50–79%  | Flag for review | Some keywords matched, but not enough to be confident        |
| < 50%   | Suggest fail    | Too few keywords : evidence does not clearly show compliance |

### Thresholds adjusted by severity

Higher-severity controls demand more keyword matches before suggesting pass,
because getting them wrong in the pass direction has serious real-world consequences.

| Severity | Suggest pass | Flag for review | Suggest fail |
| -------- | ------------ | --------------- | ------------ |
| Critical | ≥ 90%        | 60–89%          | < 60%        |
| High     | ≥ 80%        | 50–79%          | < 50%        |
| Medium   | ≥ 70%        | 40–69%          | < 40%        |
| Low      | ≥ 60%        | 30–59%          | < 30%        |

**Example : why severity matters:**

Control `1.1.2` (high) checks that two emergency break-glass accounts exist.
If the algorithm wrongly suggests pass when no break-glass accounts are configured,
the tenant has no fallback if all primary admin accounts are locked out. The higher
threshold exists to guard against this.

Control `5.1.2.5` (low) checks whether the "stay signed in" prompt is hidden on
the login page. If the algorithm wrongly flags it as failed, an admin spends a few
minutes double-checking a low-risk setting. A lower threshold is appropriate here.

Confidence scoring thresholds are implemented in
`backend-api/app/services/confidence_scorer.py` in the `PASS_THRESHOLDS` and
`REVIEW_THRESHOLDS` dictionaries. If the team adjusts any values after testing,
update both the code and this document at the same time.

The auditor always has final say, the system suggests a verdict, the auditor
confirms or overrides.

---

## Delivery phases

### Phase 1 - Backend foundation (this trimester, complete)

- `control_verification_template` table and CRUD API (PR #229)
- `manual_scan_result_detail` table and CRUD API (PR #166)
- Composite unique key enabling multi-version benchmark support
- Confidence scoring threshold design documented (see above)

### Phase 2 - Semi-automated verification

- Connect evidence uploads to `scan_result` for manual controls
- Run the evidence scanner against template keywords
- Return a confidence score and verdict suggestion to the auditor UI
- Auditor confirms or overrides the suggestion

### Phase 3 - Status propagation and scan finalisation

- Auditor verdict updates `scan_result.status` from pending to pass or fail
- Scan finalisation logic: a benchmark scan is only complete when all pending
  Manual controls have been resolved
- Reporting: manual verdicts included in compliance reports alongside automated results

---

## Related files

| File                                                      | Purpose                                 |
| --------------------------------------------------------- | --------------------------------------- |
| `backend-api/app/models/control_verification_template.py` | SQLAlchemy model - PR #229              |
| `backend-api/app/models/manual_scan_result_detail.py`     | SQLAlchemy model - PR #166              |
| `backend-api/app/api/v1/verification_templates.py`        | API endpoints - PR #229                 |
| `backend-api/app/api/v1/manual_verification.py`           | API endpoints - PR #166                 |
| `backend-api/alembic/versions/8a7b91ea95d9_*.py`          | Migration - PR #229                     |
| `backend-api/alembic/versions/ccf7645372fc_*.py`          | Migration - PR #166                     |
| `backend-api/app/services/confidence_scorer.py`           | Confidence scoring thresholds - Phase 2 |
| `docs/grc/manual_control_classification.md`               | Classification of the 14 controls       |
| `docs/grc/confidence_threshold_justification.md`          | Threshold justification per severity    |
