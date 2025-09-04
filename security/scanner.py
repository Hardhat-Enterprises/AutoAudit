import os
import csv
from pathlib import Path
from typing import List
import pytesseract
from pytesseract import TesseractNotFoundError
from PIL import Image, UnidentifiedImageError

# If PATH sometimes fails, uncomment and set your path explicitly:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Optional but recommended for better OCR
try:
    import cv2
    _HAS_CV2 = True
except Exception:
    _HAS_CV2 = False

from strategies import load_strategies  # your plugin loader

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

# ---------- File type support ----------
SUPPORTED_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp")
SUPPORTED_TEXT_EXTS  = (".txt", ".log", ".reg", ".csv", ".ini", ".json", ".xml", ".htm", ".html")

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

# ---------- OCR helpers ----------
def _ocr_with_pillow(path: Path) -> str:
    """Plain PIL -> pytesseract (fallback)."""
    try:
        with Image.open(path) as img:
            return pytesseract.image_to_string(img, config="--psm 6")
    except (UnidentifiedImageError, OSError, TesseractNotFoundError):
        return ""

def _ocr_with_cv2(path: Path) -> str:
    """OpenCV preprocessing for clearer OCR."""
    if not _HAS_CV2:
        return _ocr_with_pillow(path)

    try:
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None:
            return ""

        # Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Upscale a bit to help OCR on UI screenshots
        gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

        # Boost contrast/brightness
        gray = cv2.convertScaleAbs(gray, alpha=2.0, beta=15)

        # Binarize adaptively to handle uneven backgrounds
        thr = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 35, 11
        )

        return pytesseract.image_to_string(thr, config="--psm 6")
    except TesseractNotFoundError:
        return ""
    except Exception:
        # Last-ditch fallback
        return _ocr_with_pillow(path)

def run_ocr(path: Path) -> str:
    """Try OpenCV pre-processing first, then fallback to plain OCR."""
    text = _ocr_with_cv2(path)
    if text and text.strip():
        return text
    return _ocr_with_pillow(path)

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
    """Choose OCR for images, direct read for text files."""
    ext = path.suffix.lower()
    if ext in SUPPORTED_IMAGE_EXTS:
        return run_ocr(path)
    if ext in SUPPORTED_TEXT_EXTS:
        return read_text_file(path)
    return ""  # unsupported

def list_supported_files(folder: Path) -> List[Path]:
    """Recursively gather supported files under folder."""
    if not folder.exists():
        return []
    out = []
    for p in folder.rglob("*"):  # RECURSIVE now
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in SUPPORTED_IMAGE_EXTS or ext in SUPPORTED_TEXT_EXTS:
            out.append(p)
    return sorted(out, key=lambda x: x.name.lower())

# ---------- Main ----------
def main():
    # 1) user id
    user_id = input("Enter your username: ").strip()

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
    # Put files in: evidence/<mapped_subdir>/...
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
        with open("scan_report.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(report_rows)
        print("\n✅ Report saved as: scan_report.csv")
    except PermissionError:
        temp_name = "scan_report_temp.csv"
        with open(temp_name, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(report_rows)
        print(f"\n⚠️  'scan_report.csv' was locked. Saved as: {temp_name}")

if __name__ == "__main__":
    # Helpful check: print tesseract path/version once
    try:
        ver = pytesseract.get_tesseract_version()
        print(f"(i) Tesseract found: {ver}")
    except Exception:
        print("(i) Tesseract not detected by pytesseract. Ensure the Tesseract OCR engine is installed and on PATH.")
    main()
