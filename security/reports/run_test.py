"""
run_test.py — smoke test for the AutoAudit report generator

Place this file in the same folder as:

    report_service.py
    AutoAudit_Report_Template.docx
    fake_dataset.json

Usage:

    python run_test.py                 # generates a .docx
    python run_test.py --pdf           # converts to PDF as well
    python run_test.py --pdf --keep-docx
"""

import json
import sys
from pathlib import Path

DATASET_PATH  = "fake_dataset.json"
TEMPLATE_PATH = "AutoAudit_Report_Template.docx"
OUTPUT_DIR    = "reports_out"


def main() -> None:
    args      = sys.argv[1:]
    to_pdf    = "--pdf"       in args
    keep_docx = "--keep-docx" in args

    missing = [p for p in [DATASET_PATH, TEMPLATE_PATH] if not Path(p).exists()]
    if missing:
        for p in missing:
            print(f"ERROR: {p} not found — check you're running from the right directory.")
        sys.exit(1)

    with open(DATASET_PATH) as f:
        data = json.load(f)

    tenant = data.get("tenant", {}).get("Tenant_Name", "unknown")
    print(f"Dataset : {DATASET_PATH}")
    print(f"  Tenant            : {tenant}")
    print(f"  Controls          : {len(data.get('controls', []))}")
    print(f"  Evidence items    : {len(data.get('evidence_register', []))}")
    print(f"  Remediation items : {len(data.get('remediation_plan', []))}")

    try:
        import report_service as svc
    except ImportError as e:
        print(f"\nERROR: {e}")
        print("report_service.py must be in the same directory.")
        sys.exit(1)

    fmt = "PDF + docx" if to_pdf and keep_docx else "PDF" if to_pdf else "docx"
    print(f"\nTemplate : {TEMPLATE_PATH}")
    print(f"Output   : {OUTPUT_DIR}/  ({fmt})")
    print()

    try:
        if to_pdf:
            out = svc.generate_full_report_pdf(
                data,
                template_path=TEMPLATE_PATH,
                output_dir=OUTPUT_DIR,
                keep_docx=keep_docx,
            )
        else:
            out = svc.generate_full_report_docx(
                data,
                template_path=TEMPLATE_PATH,
                output_dir=OUTPUT_DIR,
            )
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

    out = Path(out)
    if not out.exists():
        print("ERROR: generation returned a path but no file was written.")
        sys.exit(1)

    size_kb = out.stat().st_size / 1024
    if size_kb < 1:
        print(f"WARNING: output is only {size_kb:.1f} KB — something may have gone wrong.")

    print(f"✓  {out.resolve()}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()