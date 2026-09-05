"""
generate_report_from_scan.py
=============================
Transforms AutoAudit API scan results into the dataset schema expected by
report_service.py and generates a compliance report (.docx or PDF).

Works with any tenant — all tenant metadata is derived from the scan data
or supplied via CLI arguments. No hardcoded values.

Usage (two modes):
------------------

1. From saved JSON files (offline):

    python generate_report_from_scan.py \\
        --results  scan_results.json \\
        --meta     scan_meta.json \\
        --template AutoAudit_Report_Template.docx \\
        --output   reports_out

2. Live from API (fetches scan data directly):

    python generate_report_from_scan.py \\
        --api-url  http://localhost:8000 \\
        --token    <bearer_token> \\
        --scan-id  1 \\
        --template AutoAudit_Report_Template.docx \\
        --output   reports_out

Add --pdf to also convert the output to PDF.
Add --save-dataset to save the intermediate transformed JSON for inspection.

Environment variables (alternative to --token):
    AUTOAUDIT_TOKEN   Bearer token for API authentication

Examples:
---------
    # Offline from files
    python generate_report_from_scan.py --results real_scan_results.json --meta scan_meta.json

    # Live from running API
    python generate_report_from_scan.py --api-url http://localhost:8000 --token $TOKEN --scan-id 1

    # Live + PDF output
    python generate_report_from_scan.py --api-url http://localhost:8000 --token $TOKEN --scan-id 1 --pdf
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _api_get(base_url: str, path: str, token: str) -> dict | list:
    """GET request to the AutoAudit API."""
    try:
        import urllib.request
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}{path}",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"ERROR: API request failed for {path}: {e}")
        sys.exit(1)


def fetch_scan_data(api_url: str, token: str, scan_id: int) -> tuple[dict, list]:
    """Fetch scan metadata and results from the API."""
    print(f"Fetching scan #{scan_id} from {api_url} ...")
    meta    = _api_get(api_url, f"/v1/scans/{scan_id}", token)
    results = _api_get(api_url, f"/v1/scans/{scan_id}/results", token)
    print(f"  Status: {meta.get('status')}  |  "
          f"Pass: {meta.get('passed_count')}  |  "
          f"Fail: {meta.get('failed_count')}  |  "
          f"Score: {meta.get('compliance_score')}%")
    return meta, results


# ---------------------------------------------------------------------------
# Severity classification
# ---------------------------------------------------------------------------

# Controls classified as Critical based on CIS M365 benchmark importance
_CRITICAL_CONTROLS = {
    "1.1.3",   # Global admin count
    "5.2.3.4", # MFA registration
    "5.2.3.6", # System-preferred MFA
    "5.1.5.1", # User consent to apps
    "5.1.6.1", # Cross-tenant collaboration
    "5.1.6.3", # Guest invitations
    "5.3.2",   # Guest access reviews
    "5.3.3",   # Privileged role access reviews
    "5.3.4",   # Global admin PIM approval
    "5.3.5",   # Privileged Role Admin PIM approval
}

_HIGH_CONTROLS = {
    "2.1.11",  # Attachment filtering
    "4.1",     # Intune compliance defaults
    "4.2",     # Personal device enrollment
    "5.1.3.1", # Dynamic guest group
    "5.1.4.1", # Device join restriction
    "5.2.3.2", # Custom banned password list
    "5.2.3.3", # On-prem password protection
    "5.2.3.7", # Email OTP
    "6.1.2",   # Mailbox audit actions
    "6.3.1",   # Role assignment policy add-ins
    "5.1.4.6", # BitLocker key access
    "5.1.6.2", # Guest user access (if failed)
    "5.1.5.2", # Admin consent workflow
    "5.2.2.3", # Legacy auth block
    "5.2.3.1", # MFA fatigue protection
}


def _severity(control_id: str, status: str) -> str:
    if status != "failed":
        return "Info"
    if control_id in _CRITICAL_CONTROLS:
        return "Critical"
    if control_id in _HIGH_CONTROLS:
        return "High"
    return "Medium"


# ---------------------------------------------------------------------------
# Core transform
# ---------------------------------------------------------------------------

def transform(results: list, meta: dict | None = None) -> dict:
    """
    Convert AutoAudit API scan data into the report_service.py dataset schema.

    Args:
        results: List of control result dicts from GET /v1/scans/{id}/results
        meta:    Scan metadata dict from GET /v1/scans/{id} (optional but recommended)
    """
    passed  = [r for r in results if r["status"] == "passed"]
    failed  = [r for r in results if r["status"] == "failed"]
    skipped = [r for r in results if r["status"] == "skipped"]
    errored = [r for r in results if r["status"] == "error"]

    total_assessed = len(passed) + len(failed)
    if meta and meta.get("compliance_score"):
        # Use the API's calculated score if available
        score_pct = float(meta["compliance_score"])
        score = f"{score_pct:.1f}%"
    elif total_assessed:
        score_pct = round(len(passed) / total_assessed * 100, 1)
        score = f"{score_pct}%"
    else:
        score_pct = 0
        score = "N/A"

    # Risk posture based on score
    if score_pct < 50:
        risk = "CRITICAL"
    elif score_pct < 70:
        risk = "HIGH"
    elif score_pct < 85:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # Severity counts
    critical_count = sum(1 for r in failed if _severity(r["control_id"], r["status"]) == "Critical")
    high_count     = sum(1 for r in failed if _severity(r["control_id"], r["status"]) == "High")
    medium_count   = sum(1 for r in failed if _severity(r["control_id"], r["status"]) == "Medium")
    low_count      = sum(1 for r in failed if _severity(r["control_id"], r["status"]) == "Low")

    # Dates
    now = datetime.now()
    date_str  = now.strftime("%-d %B %Y")
    date_full = now.strftime("%-d %B %Y %H:%M AEST")

    # Derive tenant info from meta or fall back to scan data
    tenant_name   = "Unknown Tenant"
    tenant_domain = "unknown"
    framework_ver = "v6.0.0"
    started_at    = date_str
    finished_at   = date_str

    if meta:
        tenant_name   = meta.get("connection_name") or tenant_name
        framework_ver = meta.get("version") or framework_ver
        if meta.get("started_at"):
            try:
                dt = datetime.fromisoformat(meta["started_at"].replace("Z", "+00:00"))
                started_at = dt.strftime("%-d %B %Y")
            except Exception:
                pass
        if meta.get("finished_at"):
            try:
                dt = datetime.fromisoformat(meta["finished_at"].replace("Z", "+00:00"))
                finished_at = dt.strftime("%-d %B %Y")
            except Exception:
                pass

    # Try to derive domain from evidence in passed controls
    for r in passed:
        ev = r.get("evidence") or {}
        if isinstance(ev, dict):
            # Domain password policy evidence contains domain names
            domains = ev.get("domains", [])
            if domains and isinstance(domains, list) and domains[0].get("name"):
                tenant_domain = domains[0]["name"]
                break
            # DKIM evidence
            dkim_domains = ev.get("domains_with_dkim_enabled", [])
            if dkim_domains:
                tenant_domain = dkim_domains[0]
                break

    # Build framework string
    frameworks_used = f"CIS Microsoft 365 Foundations Benchmark {framework_ver}"

    # Controls list — all statuses included
    controls = []
    for r in results:
        evidence_str = json.dumps(r["evidence"], indent=2, default=str) if r["evidence"] else "N/A"
        controls.append({
            "Control_ID":   r["control_id"],
            "Control_Name": r["control_id"],  # Name requires benchmark lookup — not in results API
            "Status":       r["status"].upper(),
            "Severity":     _severity(r["control_id"], r["status"]),
            "Description":  r.get("message") or "",
            "Evidence":     evidence_str,
            "Remediation":  (
                f"Review and remediate control {r['control_id']} per {frameworks_used}."
                if r["status"] == "failed" else ""
            ),
        })

    # Sort failed controls by severity for top risks
    sev_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
    sorted_failed = sorted(
        failed,
        key=lambda r: sev_order.get(_severity(r["control_id"], r["status"]), 5)
    )
    top_failed = sorted_failed[:3]

    def risk_text(r: dict) -> str:
        return r.get("message") or f"Control {r['control_id']} failed"

    # Evidence register — passed controls with real evidence (up to 10)
    evidence_register = []
    ev_num = 1
    for r in passed:
        if r.get("evidence") and ev_num <= 10:
            evidence_register.append({
                "Evidence_ID":       f"EV-{ev_num:03d}",
                "Control_Reference": r["control_id"],
                "Description":       r.get("message") or "",
                "Collection_Method": "Automated API scan via AutoAudit Engine",
                "Date_Collected":    finished_at,
            })
            ev_num += 1

    # Remediation plan — failed controls sorted by severity (up to 8)
    remediation_plan = []
    for i, r in enumerate(sorted_failed[:8], 1):
        sev = _severity(r["control_id"], r["status"])
        remediation_plan.append({
            "Item":       i,
            "Control_ID": r["control_id"],
            "Finding":    r.get("message") or "",
            "Action":     f"Remediate control {r['control_id']} per {frameworks_used} guidance.",
            "Priority":   sev,
            "Owner":      "IT Security Team",
        })

    # Key recommendation
    if critical_count > 0:
        key_rec = (
            f"{tenant_name} has {critical_count} Critical finding(s) requiring immediate remediation. "
            f"The tenant scored {score} against {frameworks_used}. "
            f"Critical findings represent unacceptable risk and must be addressed before the next assessment cycle."
        )
    else:
        key_rec = (
            f"{tenant_name} scored {score} against {frameworks_used}. "
            f"{len(failed)} control(s) failed and require remediation. "
            f"Priority should be given to High severity findings."
        )

    top_action = remediation_plan[0]["Action"] if remediation_plan else ""

    dataset = {
        "tenant": {
            "Tenant_Name":       tenant_name,
            "Tenant_Domain":     tenant_domain,
            "Assessor_Name":     "AutoAudit Platform",
            "Frameworks_Used":   frameworks_used,
            "Assessment_Date":   finished_at,
            "Assessment_Period": f"{started_at} \u2013 {finished_at}",
            "Generated_Date":    date_full,
            "Date_Generated":    date_full,
            "Classification":    "Confidential",
            "Report_Version":    "v1.0",
            "Distribution":      "IT Security Team",
            "Prepared_By":       "AutoAudit Engine",
            "Reviewed_By":       "AutoAudit Platform",
            "Team_Function":     "Information Security",
            "Scope_Owner":       "IT Security Team",
            "Limitations": (
                "Assessment conducted using read-only API access to Microsoft 365 and Entra ID. "
                f"{len(skipped)} control(s) were skipped due to API limitations, manual verification "
                "requirements, or incomplete collector implementation. "
                f"{len(errored)} control(s) returned errors during evaluation."
                if errored else
                "Assessment conducted using read-only API access to Microsoft 365 and Entra ID. "
                f"{len(skipped)} control(s) were skipped due to API limitations or manual verification requirements."
            ),
        },
        "summary": {
            "Overall_Score":          score,
            "Overall_Risk_Posture":   risk,
            "Total_Controls":         len(results),
            "Total_Pass":             len(passed),
            "Total_Fail":             len(failed),
            "Total_Critical":         critical_count,
            "Total_High":             high_count,
            "Total_Medium":           medium_count,
            "Total_Low":              low_count,
            "Top_Risk_1":             risk_text(top_failed[0]) if len(top_failed) > 0 else "",
            "Top_Risk_2":             risk_text(top_failed[1]) if len(top_failed) > 1 else "",
            "Top_Risk_3":             risk_text(top_failed[2]) if len(top_failed) > 2 else "",
            "Strength_1":             passed[0].get("message", "") if len(passed) > 0 else "",
            "Strength_1_Evidence":    "EV-001",
            "Strength_2":             passed[1].get("message", "") if len(passed) > 1 else "",
            "Strength_2_Evidence":    "EV-002",
            "Strength_3":             passed[2].get("message", "") if len(passed) > 2 else "",
            "Strength_3_Evidence":    "EV-003",
            "Strength_4":             passed[3].get("message", "") if len(passed) > 3 else "",
            "Strength_4_Evidence":    "EV-004",
            "Strength_5":             passed[4].get("message", "") if len(passed) > 4 else "",
            "Strength_5_Evidence":    "EV-005",
            "Top_Remediation_Action": top_action,
            "Key_Recommendation":     key_rec,
            "categories":             {},
        },
        "controls":          controls,
        "evidence_register": evidence_register,
        "remediation_plan":  remediation_plan,
    }

    return dataset


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate an AutoAudit compliance report from scan results.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From saved JSON files
  python generate_report_from_scan.py --results scan_results.json --meta scan_meta.json

  # Live from running API
  python generate_report_from_scan.py --api-url http://localhost:8000 --token $TOKEN --scan-id 1

  # Live + save dataset + PDF
  python generate_report_from_scan.py --api-url http://localhost:8000 --token $TOKEN --scan-id 1 --pdf --save-dataset
        """,
    )

    # Input: offline mode
    offline = p.add_argument_group("Offline mode (from saved JSON files)")
    offline.add_argument("--results", "-r", metavar="FILE",
                         help="Path to scan results JSON (from GET /v1/scans/{id}/results)")
    offline.add_argument("--meta", "-m", metavar="FILE",
                         help="Path to scan metadata JSON (from GET /v1/scans/{id}), optional")

    # Input: live mode
    live = p.add_argument_group("Live mode (fetch directly from API)")
    live.add_argument("--api-url", metavar="URL",
                      help="AutoAudit API base URL (e.g. http://localhost:8000)")
    live.add_argument("--token", metavar="TOKEN",
                      help="Bearer token (or set AUTOAUDIT_TOKEN env var)")
    live.add_argument("--scan-id", metavar="ID", type=int,
                      help="Scan ID to fetch and report on")

    # Output
    out = p.add_argument_group("Output options")
    out.add_argument("--template", "-t", metavar="FILE",
                     default="AutoAudit_Report_Template.docx",
                     help="Path to report template .docx (default: AutoAudit_Report_Template.docx)")
    out.add_argument("--output", "-o", metavar="DIR",
                     default="reports_out",
                     help="Output directory for generated report (default: reports_out)")
    out.add_argument("--pdf", action="store_true",
                     help="Also convert the report to PDF")
    out.add_argument("--keep-docx", action="store_true",
                     help="Keep .docx when --pdf is set (default: delete after conversion)")
    out.add_argument("--save-dataset", action="store_true",
                     help="Save the intermediate transformed JSON dataset for inspection")

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    results: list | None = None
    meta: dict | None    = None

    # --- Determine input mode ---
    if args.api_url or args.scan_id:
        # Live mode
        if not args.api_url or not args.scan_id:
            parser.error("--api-url and --scan-id are both required for live mode.")
        token = args.token or os.environ.get("AUTOAUDIT_TOKEN")
        if not token:
            parser.error("Provide --token or set the AUTOAUDIT_TOKEN environment variable.")
        meta, results = fetch_scan_data(args.api_url, token, args.scan_id)

    elif args.results:
        # Offline mode
        results_path = Path(args.results)
        if not results_path.exists():
            print(f"ERROR: Results file not found: {results_path}")
            sys.exit(1)
        print(f"Loading results from: {results_path}")
        with open(results_path) as f:
            results = json.load(f)

        if args.meta:
            meta_path = Path(args.meta)
            if not meta_path.exists():
                print(f"WARNING: Meta file not found: {meta_path} — tenant name will be generic.")
            else:
                print(f"Loading metadata from: {meta_path}")
                with open(meta_path) as f:
                    meta = json.load(f)
    else:
        parser.error("Provide either --results (offline) or --api-url + --scan-id (live).")

    # --- Validate template ---
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"ERROR: Template not found: {template_path}")
        print("Ensure AutoAudit_Report_Template.docx is in the current directory or pass --template.")
        sys.exit(1)

    # --- Transform ---
    print(f"\nTransforming {len(results)} control results...")
    dataset = transform(results, meta)

    passed_n = dataset["summary"]["Total_Pass"]
    failed_n = dataset["summary"]["Total_Fail"]
    score    = dataset["summary"]["Overall_Score"]
    risk     = dataset["summary"]["Overall_Risk_Posture"]
    tenant   = dataset["tenant"]["Tenant_Name"]
    domain   = dataset["tenant"]["Tenant_Domain"]

    print(f"  Tenant  : {tenant} ({domain})")
    print(f"  Score   : {score}  |  Risk: {risk}")
    print(f"  Pass: {passed_n}  |  Fail: {failed_n}  |  "
          f"Critical: {dataset['summary']['Total_Critical']}  |  "
          f"High: {dataset['summary']['Total_High']}")

    # --- Optionally save dataset ---
    if args.save_dataset:
        if args.results:
            dataset_out = Path(args.results).stem + "_dataset.json"
        else:
            dataset_out = f"scan_{args.scan_id}_dataset.json"
        with open(dataset_out, "w") as f:
            json.dump(dataset, f, indent=2, default=str)
        print(f"\nDataset saved to: {dataset_out}")

    # --- Generate report ---
    print(f"\nGenerating report...")
    print(f"  Template : {template_path}")
    print(f"  Output   : {args.output}/")

    sys.path.insert(0, str(Path(__file__).parent))
    try:
        import report_service as svc
    except ImportError:
        print("ERROR: report_service.py not found. Place this script in the same folder.")
        sys.exit(1)

    try:
        if args.pdf:
            out = svc.generate_full_report_pdf(
                dataset,
                template_path=str(template_path),
                output_dir=args.output,
                keep_docx=args.keep_docx,
            )
            print(f"\n✓ PDF written to: {out}")
        else:
            out = svc.generate_full_report_docx(
                dataset,
                template_path=str(template_path),
                output_dir=args.output,
            )
            print(f"\n✓ Report written to: {out}")
            print(f"  Convert to PDF: python {Path(__file__).name} "
                  f"--results {args.results or f'scan_{args.scan_id}_results.json'} --pdf")

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"ERROR during report generation: {e}")
        traceback.print_exc()
        sys.exit(1)

    out_path = Path(out)
    if not out_path.exists():
        print("ERROR: generation completed but no file was written.")
        sys.exit(1)

    size_kb = out_path.stat().st_size / 1024
    if size_kb < 1:
        print(f"WARNING: output is only {size_kb:.1f} KB — check the template path is correct.")


if __name__ == "__main__":
    main()