# Evidence Handling: Findings (26T3-BAC-RG-002)

Findings from investigating how the backend handles evidence uploads (`POST /v1/evidence/scan`), including missing and incomplete evidence, and how it supports the Essential Eight Macro Settings controls E8-MAC-3.2, 3.5 and 3.6.

## Contents

1. [What I investigated](#1-what-i-investigated)
2. [Current implementation](#2-current-implementation)
3. [Testing in Swagger](#3-testing-in-swagger)
4. [Gaps identified](#4-gaps-identified)
5. [Macro Settings evidence (E8-MAC-3.2, 3.5, 3.6)](#5-macro-settings-evidence-e8-mac-32-35-36)
6. [Recommendations / next steps](#6-recommendations--next-steps)
7. [Related pull requests](#7-related-pull-requests)

## 1. What I investigated

- How an uploaded file moves through `evidence.py`, `ingestion_service.py` and `security/evidence_ui/app.py`.
- How the API behaves with a valid scan, and with empty, corrupt, oversized and wrong-type files.
- How it behaves with an unknown or missing strategy, and with irrelevant evidence.
- Whether the existing macro strategy can support the manual controls E8-MAC-3.2, 3.5 and 3.6.

## 2. Current implementation

**`evidence.py`:** I have read evidence.py as this is the API endpoint that receives all the uploaded evidence from `POST /v1/evidence/scan`, and to upload evidence you must be logged in. It then checks the file extension and the file must be less than 10 MB. It also runs additional security checks and saves the results to the database. Most errors return a 400 response.

**`ingestion_service.py`:** this is the file gatekeeper. It holds the list of allowed file types and rejects anything over 10 MB, and creates a SHA-256 of the file. It also returns a success or failure message. At the time of the investigation the allowed types were `.txt .pdf .png .jpg .jpeg .json .csv`. `.docx` has since been added (see [Related pull requests](#7-related-pull-requests)).

**`security/evidence_ui/app.py`:** it extracts text from the file (OCR for images, PDF and .docx readers, plain text for the rest). It looks up the selected strategy, runs its rules over the text, and generates a PDF report. It rejects empty files and unknown strategies, and returns "no readable text" if extraction finds nothing.

## 3. Testing in Swagger

### Setup and login

First I ran the docker images and created their containers. I then ran the backend and ensured the backend was ready to go. I then went to `localhost:8000/docs`, which allowed me to view the Swagger documentation. Being able to navigate to this page I could begin testing and verifying the backend API functionality.

I first wanted to confirm that the Authentication section worked via `POST /v1/auth/login`. I used the seeded development admin account and it returned a 204, logging me in correctly.

I then tested the API call `GET /v1/evidence/strategies` and it showed all the different strategies the application can run tests on.

### Valid scan (Regular Backups)

Next I ran a valid scan for Regular Backups. I used an input of `status=success`, `backup_location=offsite`, `immutability=enabled`. I used this format because Regular Backups only understands this format. This was imported as a txt file and then I specified the scan I wanted to run.

The scan returned a 200:

```json
{
  "ok": true,
  "findings": [
    {
      "test_id": "ML1-RB-01",
      "sub_strategy": "Backups configured and recent",
      "detected_level": "ML1",
      "pass_fail": "PASS",
      "priority": "High",
      "recommendation": "Maintain regular backups and monitor success.",
      "evidence": [
        "status=success\nbackup_location=offsite\nimmutability=enabled\n"
      ]
    },
    {
      "test_id": "ML1-RB-02",
      "sub_strategy": "Offsite or immutable backups",
      "detected_level": "ML1",
      "pass_fail": "PASS",
      "priority": "Medium",
      "recommendation": "Maintain offsite backups and/or immutability for backup storage.",
      "evidence": [
        "status=success\nbackup_location=offsite\nimmutability=enabled\n"
      ]
    }
  ],
  "reports": [
    "1-Regular_Backups-valid_backup_evidence-1794817568.docx",
    "1-Regular_Backups-valid_backup_evidence-1794817568.docx"
  ],
  "note": "PDF converter not available or file was locked; generated a DOCX/TXT fallback.",
  "validator": {
    "matched": [],
    "missing": [],
    "summary": {
      "matchedCount": 0,
      "totalTerms": 0
    }
  }
}
```

I logged in to Swagger as the seeded admin, listed the available strategies, and uploaded a valid evidence file. The scan returned 200 with `ok: true` and two PASS findings. The response said a DOCX report was generated instead of a PDF because no PDF converter is available. That is worth noting, but it isn't a failure. I also found that a plain-sentence file returns FAIL for Regular Backups, because the strategy only recognises key=value evidence. This is useful context for the missing and incomplete evidence tests.

### Empty, corrupt, oversized and wrong-type files

| Test case | File | What it is | Expected status | Expected message | Verdict |
|---|---|---|---|---|---|
| 1 | `empty.txt` | 0 bytes text file | 400 | Empty upload | Correct |
| 2 | `corrupt.pdf` | Text pretending to be a PDF | 200 | `ok: true`, `findings: []`, "No readable text found in evidence." | **Problem:** a broken file looks like a clean scan |
| 3 | `big.txt` | 11 MB, over the 10 MB limit | 400 | Security Violation: File size exceeds 10 MB limit | Correct |
| 4 | `wrong.exe` | Disallowed file type | 400 | Security Violation: File extension is not permitted or malformed. | Correct |

I uploaded four invalid files to `POST /v1/evidence/scan` using the Regular Backups strategy. The empty file (400 "Empty upload"), the oversized 11 MB file (400, 10 MB limit) and the `.exe` file (400, extension not permitted) were all rejected correctly. The corrupt PDF returned 200 with `ok: true` and no findings, so an unreadable file is reported as a success. This is a gap and a candidate fix. No 500 errors occurred in these four tests.

### Unknown strategy and irrelevant evidence

I have checked with the team and we have agreed that `.docx` should be allowed as a file type as AutoAudit can analyse this file type.

I uploaded an unknown strategy name (400 "Unknown strategy"), an empty one (422) and a wrong-case name `regular_backups` (400). All were rejected correctly. I then uploaded irrelevant text. Regular Backups correctly returned FAIL, but CIS Microsoft 365 Audit returned PASS even though the validator showed all expected terms missing. The keyword checker treats "no bad keyword found" as PASS, so irrelevant evidence is reported as compliant. I tested Regular Backups and CIS Microsoft 365 Audit.

### Why the CIS result is wrong

I traced it to `security/strategies/custom_benchmarks.py`. The keyword checker marks a finding FAIL if a bad phrase appears, such as "no mfa" or "legacy auth". Otherwise it marks PASS. A file that says nothing about MFA gets a PASS, and the validator in the same response shows none of the expected evidence was found.

The NIST, ISO, SOC 2 and GDPR strategies use the same checker. I only tested CIS, so I can't say for certain that they behave the same way.

The macro handover calls this "the worst kind of bug this project can ship". It's a strong candidate for the "fix 1-2 issues" step.

### 500 errors

There were no 500 errors in my testing.

## 4. Gaps identified

| # | Gap | Where |
|---|---|---|
| 1 | A corrupt or unreadable PDF returns 200 with `ok: true` and no findings, so it looks like a clean scan | `POST /v1/evidence/scan` |
| 2 | Keyword strategies (CIS tested; NIST, ISO, SOC 2 and GDPR likely) mark text with no bad keywords as PASS, so irrelevant evidence is reported as compliant | `security/strategies/custom_benchmarks.py` |
| 3 | `.docx` was supported by the text extractor but blocked by the upload allowlist (fixed, see below) | `ingestion_service.py` |
| 4 | When no PDF converter is available the report falls back to DOCX/TXT (not a failure, but worth noting) | `security/evidence_ui/app.py` |

## 5. Macro Settings evidence (E8-MAC-3.2, 3.5, 3.6)

For the backend the uploading works but nothing stores or presents the evidence as belonging to those controls yet. The three controls are manual, as the E8 handover says, so the backend's job is to take the evidence, store it and show it for review, not mark it PASS or FAIL.

- `/v1/evidence/scan` handles uploads (type check, 10 MB limit, SHA-256 hash, text extraction).
- With PR [#447](https://github.com/Hardhat-Enterprises/AutoAudit/pull/447), Word `.docx` files are accepted, which suits procedure documents (3.5) and review records (3.6).
- PR [#442](https://github.com/Hardhat-Enterprises/AutoAudit/pull/442) adds tests for empty, oversized, wrong-type and unknown-strategy uploads.

**Gaps:** Our existing macro strategy can't assess these controls. When I ran it on sample evidence for 3.2, 3.5 and 3.6, each one returned FAIL "Macro evidence missing". It also reports `ML1-OM-xx` IDs that don't map to the platform's `E8-MAC-x.y` IDs, and has no "pending review" result for manual controls. `ML1-OM-03` is also too loose, because it passes any text containing "from the internet". I haven't confirmed how a scan result is linked to a specific control in the database.

## 6. Recommendations / next steps

- I believe the best approach is to keep 3.2, 3.5 and 3.6 manual.
- I think we should add a "pending review" status for manual control evidence.
- We should also tighten `ML1-OM-03`.
- Lastly we should consult GRC on which evidence is acceptable for each control.

For the gaps in section 4:

- Reject an unreadable PDF with a 400 error instead of returning 200 (the xfail test `test_scan_corrupt_pdf_is_rejected` in `backend-api/tests/test_evidence.py` documents this).
- Change the keyword strategies so that evidence with none of the expected terms is not reported as PASS (xfail test `test_scan_irrelevant_text_does_not_pass_cis`).

## 7. Related pull requests

- [#442](https://github.com/Hardhat-Enterprises/AutoAudit/pull/442): endpoint tests for `POST /v1/evidence/scan`, including expected-failure (xfail) tests that record the known gaps.
- [#447](https://github.com/Hardhat-Enterprises/AutoAudit/pull/447): allows `.docx` files as evidence uploads (the macro-enabled `.docm` stays blocked).
