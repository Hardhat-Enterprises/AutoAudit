import os
from pathlib import Path
from typing import Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1])) 
from reports.report_service import generate_pdf
from security.strategies import load_strategies

#------------------------ Import core_ocr.py----------------
from backend.core_ocr import (
    configure_tesseract,
    extract_text_and_preview,
)

#------------------------ Same result and username environment ----------------
RESULTS_DIR  = Path(os.environ.get("AUTOAUDIT_RESULTS", "results"))
REPORTS_DIR  = Path(os.environ.get("AUTOAUDIT_REPORTS", RESULTS_DIR / "reports"))
PREVIEWS_DIR = Path(os.environ.get("AUTOAUDIT_PREVIEWS", RESULTS_DIR / "previews"))
TEMPLATE_PATH = Path(os.environ.get("AUTOAUDIT_TEMPLATE", RESULTS_DIR / "report_template.docx"))
CSV_PATH     = Path(os.environ.get("AUTOAUDIT_CSV", RESULTS_DIR / "scan_report.csv"))

for p in (RESULTS_DIR, REPORTS_DIR, PREVIEWS_DIR):
    p.mkdir(parents=True, exist_ok=True)

def get_username() -> str:
    return os.environ.get("AUTOAUDIT_USER") or (input("Enter your username: ").strip() or "user")

# ----------------------- UI helpers -----------------------
def choose_one(title: str, options: list[str]) -> str:
    """Prompt user to choose exactly one option by number."""
    print(title)
    for i, o in enumerate(options, 1):
        print(f"{i}. {o}")
    while True:
        raw = input("Select ONE option (e.g. 1): ").strip()
        if raw.isdigit():
            i = int(raw)
            if 1 <= i <= len(options):
                return options[i - 1]
        print("Invalid selection. Please enter a single number from the list.")

def list_evidence(folder: Path):
    # Supported evidence types
    image_exts = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
    other_exts = {".pdf", ".txt", ".docx"}
    exts = image_exts | other_exts
    # allow the tool to find files within folders as well 
    return sorted(
        [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in exts],
        key=lambda p: p.as_posix().lower()
    )

def choose_one_evidence(evidence_dir: Path) -> Path | None:
    """
    Show evidence files in evidence/ and prompt for exactly one.
    Also accepts a full path to a file outside the folder.
    """
    files = list_evidence(evidence_dir)
    if files:
        print("\nEvidence files (from ./evidence):")
        for i, p in enumerate(files, 1):
            print(f"{i}. {p.name}")
    else:
        print("No supported files found in ./evidence (you can paste a full file path).")

    while True:
        resp = input("Pick ONE evidence file by number, or paste a full path: ").strip()
        if not resp:
            print("Please choose a number or paste a file path.")
            continue
        if resp.isdigit() and files:
            i = int(resp)
            if 1 <= i <= len(files):
                return files[i - 1]
            print("Number out of range.")
            continue
        pr = Path(resp)
        if pr.exists() and pr.is_file():
            return pr

        print("Invalid selection. Try again.")

# ------------------------ Main --------------------------
def main():
    configure_tesseract() 
    user_id = get_username()

    here = Path(__file__).resolve()
    root = here.parents[1]                      # …/AutoAudit/security
    evidence_dir = root / "evidence"            # …/AutoAudit/security/evidence
    evidence_dir.mkdir(parents=True, exist_ok=True)

    print(f"Looking for evidence in: {evidence_dir}")

    strategies = load_strategies()
    if not strategies:
        print("No strategies found.")
        return

    def desc(s):
        try:
            return s.description()
        except Exception:
            return ""

    names_for_menu = [f"{s.name} — {desc(s)}" for s in strategies]
    chosen_label = choose_one("\nAvailable strategies:", names_for_menu)
    chosen_name = chosen_label.split(" — ")[0]
    chosen_strategy = next((s for s in strategies if s.name == chosen_name), None)
    if not chosen_strategy:
        print("Not a valid selection. Exiting.")
        return

    print(f"\n📋 Strategy selected: {chosen_strategy.name}\n")

    evidence_path = choose_one_evidence(evidence_dir)
    if not evidence_path:
        print("No evidence selected.")
        return

    print(f"\n📄  Evidence: {evidence_path.name}")
    text, preview = extract_text_and_preview(evidence_path, PREVIEWS_DIR)
    preview_text = (text[:300] + "…") if len(text) > 300 else text
    print("📝 Extracted Text:", preview_text)

    generated = []

    try:
        if hasattr(chosen_strategy, "emit_hits"):
            rows = chosen_strategy.emit_hits(text, source_file=evidence_path.name) or []
            if not rows:
                print("No findings for this strategy.")
            for idx, r in enumerate(rows, start=1):
                uid = _safe_uid(f"{user_id}-{chosen_strategy.name}-{evidence_path.stem}-{idx:02d}") # unique file names for multiple findings
                data = {
                    "UniqueID": uid,
                    "UserID": user_id,
                    "Evidence": str(evidence_path),
                    "Evidence Preview": str(preview) if preview else "",
                    "Strategy": chosen_strategy.name,
                    "TestID": r.get("test_id", ""),
                    "Sub-Strategy": r.get("sub_strategy", ""),
                    "ML Level": r.get("detected_level", ""),
                    "Pass/Fail": r.get("pass_fail", ""),
                    "Priority": r.get("priority", ""),
                    "Recommendation": r.get("recommendation", ""),
                    "Evidence Extract": "; ".join(r.get("evidence", [])),
                    "Description": r.get("description", ""),
                    "Confidence": r.get("confidence", ""),
                }
                pdf = generate_pdf(
                    data,
                    template_path=str(TEMPLATE_PATH),
                    output_dir=str(REPORTS_DIR),
                    base_dir="."
                )
                print(f"   ✅ {chosen_strategy.name} → {pdf}")
                generated.append(pdf)
        else:
            hits = chosen_strategy.match(text) or []
            if not hits:
                print("No findings for this strategy.")
            else:
                uid = _safe_uid(f"{user_id}-{chosen_strategy.name}-{evidence_path.stem}-HITS")
                data = {
                    "UniqueID": uid,
                    "UserID": user_id,
                    "Evidence": str(evidence_path),
                    "Evidence Preview": str(preview) if preview else "",
                    "Strategy": chosen_strategy.name,
                    "TestID": "",
                    "Sub-Strategy": "",
                    "ML Level": "",
                    "Pass/Fail": "",
                    "Priority": "",
                    "Recommendation": "",
                    "Evidence Extract": ", ".join(hits),
                }
                pdf = generate_pdf(
                    data,
                    template_path=str(TEMPLATE_PATH),
                    output_dir=str(REPORTS_DIR),
                    base_dir="."
                )
                print(f"   ✅ {chosen_strategy.name} → {pdf}")
                generated.append(pdf)
    except Exception as e:
        print(f"   ❌ {chosen_strategy.name} failed: {e}")

    if generated:
        print("\n📄 Generated reports:")
        for p in generated:
            print(" -", p)
    else:
        print("\nNo findings → no reports generated.")


# -------------------- utilities --------------------
def _safe_uid(s: str) -> str:
    keep = []
    for ch in s:
        if ch.isalnum() or ch in ("-", "_"):
            keep.append(ch)
        else:
            keep.append("-")
    return "".join(keep).strip("-") or "report"


if __name__ == "__main__":
    main()
