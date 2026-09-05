# AutoAudit Report Service

Fills `AutoAudit_Report_Template.docx` with compliance assessment data and
produces a Word document or PDF report.

---

## Files

| File | Purpose |
|------|---------|
| `report_service.py` | The report generator — this is the only file you need to import |
| `AutoAudit_Report_Template.docx` | Word template with `{placeholder}` tokens |
| `generate_report_from_scan.py` | Transforms live API scan results into the dataset schema and generates the report |
| `run_test.py` | Smoke test runner |
| `fake_dataset.json` | Sample dataset for local testing |

---

## Quick start

```python
from report_service import generate_full_report_docx
import json

with open("dataset.json") as f:
    data = json.load(f)

out = generate_full_report_docx(data)
# open out in Word, check layout, export to PDF
```

For headless pipelines:

```python
out = generate_full_report_pdf(data)
```

From the command line:

```bash
python report_service.py dataset.json                        # produces .docx
python report_service.py dataset.json --pdf                  # produces PDF
python report_service.py dataset.json --pdf --keep-docx      # keeps both
python report_service.py convert path/to/report.docx         # convert existing docx
```

---

## Generating a report from a real tenant scan

`generate_report_from_scan.py` connects to the AutoAudit API, fetches real scan
results, transforms them into the dataset schema, and generates the report.
All tenant metadata (name, domain, framework version, dates) is derived
automatically from the scan data — no hardcoded values.

### Prerequisites

1. The full stack must be running (`docker compose --profile all up -d`)
2. You need a valid bearer token (see Authentication below)
3. A completed scan must exist (see Running a scan below)

### Authentication

Register and log in to get a token:

```bash
curl -X POST http://localhost:8000/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email": "you@example.com", "password": "YourPassword1!", "username": "yourname"}'

curl -X POST http://localhost:8000/v1/auth/login \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'username=you@example.com&password=YourPassword1!'
```

Copy the `access_token` from the response and set it:

```bash
export TOKEN="eyJ..."
# or use the env var alternative:
export AUTOAUDIT_TOKEN="eyJ..."
```

### Running a scan

Create an M365 connection using the service principal credentials from Bitwarden:

```bash
curl -X POST http://localhost:8000/v1/m365-connections/ \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "name": "My Tenant",
        "tenant_id": "<tenant_id>",
        "client_id": "<client_id>",
        "client_secret": "<client_secret>"
    }'
```

Trigger a scan (use the `id` returned from the connection step):

```bash
curl -X POST http://localhost:8000/v1/scans/ \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"m365_connection_id": 1, "framework": "cis", "benchmark": "microsoft-365-foundations", "version": "v6.0.0"}'
```

Poll until `status` is `completed`:

```bash
curl http://localhost:8000/v1/scans/1 -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | grep '"status"' | head -1
```

### Live mode (fetches directly from the running API)

```bash
python generate_report_from_scan.py \
    --api-url http://localhost:8000 \
    --token $TOKEN \
    --scan-id 1
```

### Offline mode (from saved JSON files)

First save the scan data:

```bash
curl http://localhost:8000/v1/scans/1 \
    -H "Authorization: Bearer $TOKEN" > scan_meta.json

curl http://localhost:8000/v1/scans/1/results \
    -H "Authorization: Bearer $TOKEN" > scan_results.json
```

Then generate the report:

```bash
python generate_report_from_scan.py \
    --results scan_results.json \
    --meta scan_meta.json
```

### Options

| Flag | Description |
|------|-------------|
| `--api-url URL` | AutoAudit API base URL (live mode) |
| `--token TOKEN` | Bearer token, or set `AUTOAUDIT_TOKEN` env var |
| `--scan-id ID` | Scan ID to fetch and report on (live mode) |
| `--results FILE` | Path to scan results JSON (offline mode) |
| `--meta FILE` | Path to scan metadata JSON (offline mode, optional) |
| `--template FILE` | Path to template .docx (default: `AutoAudit_Report_Template.docx`) |
| `--output DIR` | Output directory (default: `reports_out`) |
| `--pdf` | Also convert output to PDF |
| `--keep-docx` | Keep .docx when `--pdf` is set |
| `--save-dataset` | Save the intermediate transformed JSON for inspection |

### Example output

```
Fetching scan #1 from http://localhost:8000 ...
  Status: completed  |  Pass: 38  |  Fail: 22  |  Score: 63.33%

Transforming 140 control results...
  Tenant  : AutoAudit Sandbox (t8sjf.onmicrosoft.com)
  Score   : 63.3%  |  Risk: HIGH
  Pass: 38  |  Fail: 22  |  Critical: 10  |  High: 11

Generating report...
  Template : AutoAudit_Report_Template.docx
  Output   : reports_out/

✓ Report written to: reports_out/AutoAudit_Sandbox_24May2026_AutoAudit_Report.docx
```

---

## Dataset schema

The service reads these top-level keys:

```json
{
  "tenant":            {},
  "summary":           {},
  "controls":          [],
  "evidence_register": [],
  "remediation_plan":  []
}
```

None are required — missing keys produce empty strings in the output.

Key names are normalised before lookup (lower-cased, underscores/hyphens/slashes
collapsed to spaces), so `"Tenant_Name"`, `"tenant name"`, and `"tenant-name"`
all resolve to the same field.

### tenant

```json
{
  "Tenant_Name":       "Contoso Ltd",
  "Tenant_Domain":     "contoso.com",
  "Assessor_Name":     "Jane Smith",
  "Frameworks_Used":   "CIS M365 v3.0, ISO 27001:2022",
  "Assessment_Period": "April 2025",
  "Assessment_Date":   "30 April 2025",
  "Classification":    "Confidential",
  "Report_Version":    "1.0",
  "Distribution":      "IT Security, Management",
  "Prepared_By":       "Jane Smith",
  "Reviewed_By":       "John Doe",
  "Team_Function":     "GRC",
  "Limitations":       "On-premises AD excluded",
  "Scope_Owner":       "IT Security Manager"
}
```

### summary

```json
{
  "Overall_Score":          "72%",
  "Overall_Risk_Posture":   "Medium",
  "Executive_Summary":      "...",
  "Key_Recommendation":     "...",
  "Total_Controls":         "42",
  "Total_Pass":             "30",
  "Total_Fail":             "12",
  "Total_Critical":         "2",
  "Total_High":             "4",
  "Total_Medium":           "4",
  "Total_Low":              "2",
  "Top_Risk_1":             "DMARC not enforced",
  "Top_Risk_2":             "MFA not required for all users",
  "Top_Risk_3":             "Legacy auth not blocked",
  "Strength_1":             "MFA enabled for admins",
  "Strength_1_Evidence":    "AAD-MFA-001",
  "Cat_1_Pass":             "8",
  "Cat_1_Fail":             "2",
  "Cat_1_Total":            "10",
  "Cat_1_Comment":          "Email security needs attention"
}
```

Category fields run from `Cat_1_*` to `Cat_9_*`. Also supports the nested
shape `summary.categories.Cat_1.Pass` if your dataset uses that instead.

### controls (list)

Each item maps to one finding block in the report. The template has one block
per severity level — Critical, High, Medium, Low — and only the first FAIL at
each level is used.

```json
{
  "UniqueID":             "AAD-DMARC-001",
  "Control_Name":         "Ensure DMARC policy is set to reject or quarantine",
  "CIS_Section":          "1.1.14",
  "ISO_Mapping":          "A.9.4.3",
  "Strategy":             "Email / Exchange Online",
  "Sub_Strategy":         "Email Authentication",
  "Test_id":              "EXO-DMARC-001",
  "Level":                "L1",
  "Compliance_Status":    "Non-Compliant",
  "Risk_Rating":          "High",
  "Priority":             "Within 30 Days",
  "Pass/Fail":            "FAIL",
  "Description":          "DMARC must be configured with p=quarantine or p=reject.",
  "Observations":         "The DMARC TXT record is configured with p=none.",
  "Justification":        "DNS TXT lookup returned: v=DMARC1; p=none; ...",
  "Evidence_Type":        "DNS TXT record",
  "File Name":            "dns_dmarc_contoso_20250430.txt",
  "Extract":              "v=DMARC1; p=none; rua=mailto:dmarc-reports@contoso.com",
  "Confidence":           "High",
  "Evidence_Explanation": "p=none instructs mail servers to take no action on DMARC failures.",
  "Impact":               "Threat actors can send spoofed emails from @contoso.com addresses.",
  "Root_Cause":           "DMARC was deployed in monitoring mode and never moved to enforcement.",
  "Remediation":          "1. Review DMARC aggregate reports. 2. Change p=none to p=quarantine.",
  "Owner":                "IT Security",
  "Target_Date":          "30 May 2025",
  "Remediation_Status":   "Open"
}
```

### evidence_register (list, up to 10 items)

```json
{
  "Evidence_ID":          "EV-001",
  "Evidence_Description": "DNS TXT record for _dmarc.contoso.com",
  "Evidence_Source":      "DNS lookup via MXToolbox",
  "Mapped_Control":       "AAD-DMARC-001",
  "Date_Captured":        "30 April 2025"
}
```

### remediation_plan (list, up to 8 items)

```json
{
  "Remediation_Action":   "Update DMARC policy from p=none to p=quarantine",
  "Owner":                "IT Security",
  "Target_Date":          "30 May 2025",
  "Status":               "Open"
}
```

---

## Adding new template tokens

1. Add `{New_Token}` to the Word template wherever you want the value to appear.
2. In `report_service.py`, add the key to the relevant mapping function:
   - Tenant-level fields → `_map_tenant()`
   - Summary/score fields → `_map_summary()`
   - Per-control fields → `_single_control_mapping()`
3. That's it.

---

## PDF conversion

Tries three methods in order:

1. **docx2pdf** — needs Microsoft Word installed (Windows/macOS only)
2. **LibreOffice headless** — `soffice` must be on PATH
3. **fpdf2 fallback** — text-only, no layout fidelity, last resort

Install dependencies:

```bash
pip install python-docx docx2pdf   # for Word-based conversion
# OR
sudo apt install libreoffice        # for LibreOffice conversion
```

---

## Running the smoke test

```bash
python run_test.py              # generates a .docx from fake_dataset.json
python run_test.py --pdf        # also converts to PDF
```

Expected output:

```
Loading dataset : fake_dataset.json
  Tenant        : Contoso Ltd
  Controls      : 15
  ...
✓ Report generated successfully!
  File : reports_out/Contoso_Ltd_30April2025_AutoAudit_Report.docx
  Size : 245.3 KB
```

---

## Known limitations

- The template has one finding block per severity level (Critical / High /
  Medium / Low). If there are multiple FAILs at the same level, only the first
  one appears in the report. The full list is still included in Appendix B.
- Evidence Register supports up to 10 items, remediation plan up to 8 rows.
  These limits match the template row count — extend the template if you need more.
- PDF conversion quality depends on which converter is available. Always review
  the .docx in Word before distributing the PDF version.
- Fields such as `{ISO_Mapping}`, `{Impact}`, `{Root_Cause}`, and `{Observations}`
  in the detailed findings section require enrichment data from the CIS→ISO mapping
  and GRC pipeline. These are not populated by `generate_report_from_scan.py` as
  that data is not yet wired into the scan results API — this is a separate
  integration task.
