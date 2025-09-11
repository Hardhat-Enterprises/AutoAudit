import os
import csv
from pathlib import Path
from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1])) 
from strategies import load_strategies  

#------------------------ Import core_ocr.py----------------
from backend.core_ocr import extract_text_and_preview, SUPPORTED_ALL_EXTS

#------------------------ Same result and username environment ----------------
RESULTS_DIR = Path(os.environ.get("AUTOAUDIT_RESULTS", "results"))
PREVIEWS    = Path(os.environ.get("AUTOAUDIT_PREVIEWS", RESULTS_DIR / "previews"))
CSV_PATH    = Path(os.environ.get("AUTOAUDIT_CSV", RESULTS_DIR / "scan_report.csv"))

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PREVIEWS.mkdir(parents=True, exist_ok=True)

def get_username() -> str:
    return os.environ.get("AUTOAUDIT_USER") or (input("Enter your username: ").strip() or "user")

# ---------- Folder mapping for the 8 Essential Eight strategies ----------
STRAT_DIR_MAP = {
    "application control": "application_control",
    "restrict admin privileges": "restrict_admin_privileges",
    "patch applications": "patch_applications",
    "patch operating systems": "patch_operating_systems",
    "configure microsoft office macro settings": "configure_macro_settings",
    "multi-factor authentication": "multi_factor_authentication",
    "regular backups": "regular_backups",
    "user application hardening": "user_application_hardening",
}

# ---------- UI helpers ----------
def choose_from_menu(title: str, options: List[str]) -> List[str]:
    print(title)
    for i, o in enumerate(options, 1):
        print(f"{i}. {o}")
    raw = input("Select the strategy by number(s) e.g. 1,3,5 for multiple strategies: ")
    idxs = []
    for tok in raw.split(","):
        tok = tok.strip()
        if tok.isdigit() and 1 <= int(tok) <= len(options):
            idxs.append(int(tok) - 1)
    return [options[i] for i in idxs]

# ---------- Content extraction ----------
def read_text_file(path: Path) -> str:
    """Read small text-like files into a single string."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        try:
            return path.read_text(errors="ignore")
        except Exception:
            return ""

def extract_text(path: Path) -> str:
    text, _ = extract_text_and_preview(path, PREVIEWS)
    return text or ""
    
def list_supported_files(folder: Path) -> List[Path]:
    if not folder.exists():
        return []
    out = []
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_ALL_EXTS:
            out.append(p)
    return sorted(out, key=lambda x: x.name.lower())

# ---------- Main ----------
def main():
    # 1) user id that was keyed in 
    user_id = get_username()

    # 2) load strategies
    strategies = load_strategies()
    if not strategies:
        print("No strategies found")
        return

    # 3) pick strategies
    names_for_menu = [f"{s.name} — {s.description()}" for s in strategies]
    chosen_menu = choose_from_menu("\nAvailable strategies:", names_for_menu)

    chosen_names = {n.split(" — ")[0] for n in chosen_menu}
    chosen_strategies = [s for s in strategies if s.name in chosen_names]

    if not chosen_strategies:
        print("Not a valid selection. Exiting the application.")
        return

    print("\n📋 Scanning using strategies:", ", ".join(s.name for s in chosen_strategies), "\n")

    # 4) where evidence/files live
    base_dir = Path(os.environ.get("AUTOAUDIT_INPUT_DIR", "evidence"))

    # 5) CSV header
    report_rows = [(
        "UserID", "Image", "Strategy", "TestID", "Sub-Strategy",
        "ML Level", "Pass/Fail", "Priority", "Recommendation", "Evidence Extract"
    )]

    # 6) scan per strategy
    for strat in chosen_strategies:
        strat_key = strat.name.lower().strip()
        strat_sub = STRAT_DIR_MAP.get(strat_key, None)
        preferred = (base_dir / strat_sub) if strat_sub else base_dir
        fallback  = base_dir

        files = list_supported_files(preferred)
        using_dir = preferred
        if not files:
            files = list_supported_files(fallback)
            using_dir = fallback

        if not files:
            print(f"⚠️  No files found for '{strat.name}' in '{preferred}' or '{fallback}'. Skipping.")
            continue

        print(f"\n🔎 Strategy: {strat.name}")
        print(f"   Using inputs from: {using_dir}")

        for fpath in files:
            print(f"📄 {fpath.name}:")
            raw_text = extract_text(fpath)

            if not raw_text.strip():
                print("   (no readable text found)\n")
                # record a row so you see the file in the CSV
                report_rows.append((
                    user_id, fpath.name, strat.name, "", "", "",
                    "NO_TEXT", "Low",
                    "OCR could not read this file. Try a clearer screenshot.",
                    ""
                ))
                continue

            preview = (raw_text[:200] + "…") if len(raw_text) > 200 else raw_text
            print("📝 Extracted:", preview.replace("\n", " ")[:200], "\n")

            rows_added = 0  # track whether any hits were written

            if hasattr(strat, "emit_hits"):
                rows = strat.emit_hits(raw_text, source_file=fpath.name)
                for r in rows:
                    report_rows.append((
                        user_id,
                        fpath.name,
                        strat.name,
                        r.get("test_id", ""),
                        r.get("sub_strategy", ""),
                        r.get("detected_level", ""),
                        r.get("pass_fail", ""),
                        r.get("priority", ""),
                        r.get("recommendation", ""),
                        "; ".join(r.get("evidence", [])),
                    ))
                    rows_added += 1
            else:
                hits = strat.match(raw_text)
                if hits:
                    report_rows.append((
                        user_id, fpath.name, strat.name, "", "", "",
                        "HIT", "Medium",
                        "Heuristic match.",
                        ", ".join(hits)
                    ))
                    rows_added += 1

            # If no matches, write a NO_MATCH row so the file appears in the report
            if rows_added == 0:
                report_rows.append((
                    user_id, fpath.name, strat.name, "", "", "",
                    "NO_MATCH", "Low",
                    "No rule matched this file.",
                    ""
                ))

    # 7) save
    try:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(report_rows)
        print(f"\n ✅ Report has been saved as: {CSV_PATH}")
    except PermissionError:
        temp_name = "scan_report_temp.csv"
        with open(temp_name, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(report_rows)
        print(f"\n  'scan_report.csv' was locked. Saved as: {temp_name}")

if __name__ == "__main__":
    main()
