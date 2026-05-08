# AutoAudit Report Service

Fills `AutoAudit_Report_Template.docx` with compliance assessment data and
produces a Word document or PDF report.

---

## Files

| File | Purpose |
|------|---------|
| `report_service.py` | The report generator — this is the only file you need to import |
| `AutoAudit_Report_Template.docx` | Word template with `{placeholder}` tokens |
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

Category fields run from `Cat_1_*` to `Cat_9_*`.  Also supports the nested
shape `summary.categories.Cat_1.Pass` if your dataset uses that instead.

### controls (list)

Each item maps to one finding block in the report.  The template has one block
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
