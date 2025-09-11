# security/strategies/patch_operating_systems.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Iterable, Optional, Tuple
from .overview import Strategy
from datetime import datetime, timedelta
import io, os, re

# -------------------- Optional deps (no hard-crash) --------------------
try:
    import fitz  # PyMuPDF for PDF text extraction
except Exception:
    fitz = None

try:
    from docx import Document as DocxDocument  # python-docx
except Exception:
    DocxDocument = None

try:
    import pytesseract
    from PIL import Image, ImageOps, ImageFilter, ImageStat, UnidentifiedImageError
    _TESS = os.environ.get("TESSERACT_CMD") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if Path(_TESS).exists():
        pytesseract.pytesseract.tesseract_cmd = _TESS
except Exception:
    pytesseract = None
    Image = None
    ImageOps = None
    ImageFilter = None
    ImageStat = None
    class UnidentifiedImageError(Exception): ...
# -------------------------------------------------------------------------

# Evidence we consider
EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".pdf", ".docx", ".txt", ".log"}

# Filename hints typical for OS patch/build evidence
FILENAME_HINTS = (
    "winupdate_home", "winupdate_history",
    "system_about", "settings_about",
    "os_build", "winver",
    "update_status", "update_settings",
)

# OS patching/build signals
KEYWORDS = [
    r"\bWindows Update\b",
    r"\b(Cumulative|Feature)\s+update\b",
    r"\bKB\d{6,}\b",
    r"\bInstalled on\b|\bLast checked\b|\bCheck for updates\b|\bYou'?re up to date\b",
    r"\bWindows (10|11)\b",
    r"\bVersion\s+(?:21H\d|22H\d|23H\d|24H\d)\b",
    r"\bOS Build\b|\bBuild\s+\d{4,}(?:\.\d+)?\b",
    r"\bfailed\b|\berror\b|\bpending\b|\brestart required\b|\binstall now\b|\bpause updates\b",
]

# Max allowable age for Last checked / Installed on (days)
MAX_LAST_CHECK_DAYS = int(os.environ.get("PATCH_OS_MAX_LAST_CHECK_DAYS", "14"))

# Date parsing formats
_DATE_FORMATS = [
    "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d",
    "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y",
    "%d-%m-%Y", "%m-%d-%Y",
]
_LAST_CHECK_RE   = re.compile(r"Last\s*checked\s*:?\s*([^\r\n]+)", re.I)
_INSTALLED_ON_RE = re.compile(r"Installed\s*on\s*:?\s*([^\r\n]+)", re.I)

# -------------------- helpers --------------------
def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def _resolve_evidence_dir() -> Path:
    env = os.environ.get("PATCH_OS_DIR")
    if env:
        p = Path(env)
        if p.exists():
            return p
    root = _project_root()
    for c in [root / "evidence" / "patch_operating_systems",
              root / "security" / "evidence" / "patch_operating_systems"]:
        if c.exists():
            return c
    return root / "evidence" / "patch_operating_systems"

def _iter_evidence_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    for p in sorted(root.iterdir()):
        if p.is_file() and p.suffix.lower() in EXTS:
            yield p

def _ocr_image_bytes(data: bytes) -> str:
    """OCR tuned for dark Windows Settings UI."""
    if not pytesseract or not Image:
        return ""
    try:
        with Image.open(io.BytesIO(data)) as img:
            img = img.convert("L")
            if ImageStat:
                mean_luma = ImageStat.Stat(img).mean[0]
                if mean_luma < 80:  # dark theme → invert
                    img = ImageOps.invert(img)
            img = ImageOps.autocontrast(img)
            w, h = img.size
            img = img.resize((int(w * 1.5), int(h * 1.5)))
            if ImageFilter:
                img = img.filter(ImageFilter.SHARPEN)
            return pytesseract.image_to_string(img, config="--psm 6 --oem 3")
    except UnidentifiedImageError:
        return ""
    except Exception:
        return ""

def _extract_text(path: Optional[Path]) -> str:
    if not path:
        return ""
    s = path.suffix.lower()
    try:
        if s in {".txt", ".log"}:
            return path.read_text(errors="ignore")
        if s == ".pdf" and fitz:
            out = []
            with fitz.open(path) as doc:
                for page in doc:
                    out.append(page.get_text() or "")
            return "\n".join(out)
        if s == ".docx" and DocxDocument:
            d = DocxDocument(str(path))
            return "\n".join(p.text for p in d.paragraphs)
        if s in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}:
            return _ocr_image_bytes(path.read_bytes())
        return path.read_text(errors="ignore")
    except Exception:
        return ""

def _matched_patterns(text: str) -> List[str]:
    return [pat for pat in KEYWORDS if re.search(pat, text, re.I)]

def _filename_hinted(name: str) -> bool:
    low = name.lower()
    return any(h in low for h in FILENAME_HINTS)

def _parse_rel_or_fmt(token: str) -> Optional[datetime]:
    token = token.strip()
    now = datetime.now()
    low = token.lower()
    # support "Today, 3:27 PM" / "Yesterday, 10:15 AM"
    if low.startswith("today"):
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if low.startswith("yesterday"):
        d = now - timedelta(days=1)
        return d.replace(hour=0, minute=0, second=0, microsecond=0)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(token, fmt)
        except Exception:
            pass
    m = re.search(r"\b(\d{1,2})\s+([A-Za-z]{3,})\s+(\d{4})\b", token)
    if m:
        for fmt in ("%d %B %Y", "%d %b %Y"):
            try:
                return datetime.strptime(m.group(0), fmt)
            except Exception:
                pass
    return None

def _extract_date_info(text: str) -> Tuple[Optional[str], Optional[str], Optional[int], str]:
    """
    Return (raw_label, iso_date, age_days, which_label) using Last checked OR Installed on (prefer Last checked).
    """
    now = datetime.now()
    raw = iso = None
    age_days = None
    which = ""

    m = _LAST_CHECK_RE.search(text)
    if not m:
        m = _INSTALLED_ON_RE.search(text)
        which = "Installed on" if m else ""
    else:
        which = "Last checked"

    if m:
        raw_val = m.group(1).strip()
        dt = _parse_rel_or_fmt(raw_val)
        if dt:
            iso = dt.strftime("%Y-%m-%d")
            age_days = (now.date() - dt.date()).days
        raw = raw_val
    return raw, iso, age_days, which

def _has_failure_indicators(text: str) -> bool:
    return bool(re.search(r"\b(failed|error|pending|restart required|install now|pause updates)\b", text, re.I))

def _pass_signal(text: str, fname: str, age_days: Optional[int]) -> bool:
    """
    PASS if:
      - "You're up to date" AND date age <= threshold, OR
      - KB/update or Build/Version evidence AND filename hint AND date age <= threshold.
    """
    up_to_date = re.search(r"\bYou'?re up to date\b", text, re.I) is not None
    kb_or_update = re.search(r"\b(KB\d{6,}|(Cumulative|Feature)\s+update)\b", text, re.I)
    build_or_ver = re.search(r"\b(OS Build|Version\s+(?:21H\d|22H\d|23H\d|24H\d)|Windows (10|11))\b", text, re.I)

    if up_to_date and age_days is not None:
        return age_days <= MAX_LAST_CHECK_DAYS
    if (kb_or_update or build_or_ver) and _filename_hinted(fname) and age_days is not None:
        return age_days <= MAX_LAST_CHECK_DAYS
    return False

# -------- core builder --------
def _build_hit_for_text(ev_text: str, ev_name: str, ev_path: Optional[Path]) -> Dict[str, Any] | None:
    patterns = _matched_patterns(ev_text)
    hinted   = _filename_hinted(ev_name)
    if not (patterns or hinted):
        return None

    raw_date, iso_date, age_days, which_label = _extract_date_info(ev_text)
    passed = _pass_signal(ev_text, ev_name, age_days)
    fail_indicators = _has_failure_indicators(ev_text)

    # ---- Level/priority/recommendation ----
    level = "ML1"  # <-- fixed per requirement
    stale_or_missing = (age_days is None) or (age_days > MAX_LAST_CHECK_DAYS)
    priority = "P2" if (stale_or_missing or fail_indicators or not passed) else "P4"

    base_rec = (
        f"Maintain OS update/build evidence. Ensure Windows Update checks are recent (≤ {MAX_LAST_CHECK_DAYS} days). "
        "For ML1 timelines: apply critical/weaponised updates within 48h; apply other updates within 2 weeks for online "
        "services and within 1 month for other applications; remove unsupported OS versions."
    )
    fix_rec = (
        " Turn on automatic Windows Update (Settings → Windows Update), keep “Get the latest updates as soon as they’re "
        "available” enabled, click “Check for updates”, and schedule required restarts. Ensure the Windows Update service "
        "is running and updates are not paused."
    )
    recommendation = base_rec + ("" if passed and not stale_or_missing and not fail_indicators else fix_rec)

    return {
        "test_id": "E8-POS-ML1-001",
        "sub_strategy": "Patch Operating Systems — Update/Build Evidence (Date-Checked)",
        "detected_level": level,                       # <-- ML1
        "pass_fail": "pass" if passed else "fail",
        "priority": priority,
        "recommendation": recommendation,
        "evidence": {
            "source_file": ev_name,
            "absolute_path": str(ev_path) if ev_path else "",
            "filename_hinted": hinted,
            "keyword_patterns_matched": patterns,
            "date_field_used": which_label or "",
            "last_checked_raw": raw_date,
            "last_checked_iso": iso_date,
            "last_checked_age_days": age_days,
            "max_last_check_days": MAX_LAST_CHECK_DAYS,
            "up_to_date_string_found": bool(re.search(r"\bYou'?re up to date\b", ev_text, re.I)),
            "failure_indicators_found": fail_indicators,
        },
    }

# -------------------- Strategy --------------------
class PatchOperatingSystemsML1(Strategy):
    name = "Patch Operating Systems (ML1)"
    key  = "patch_operating_systems_ml1"
    EVIDENCE_DIR = _resolve_evidence_dir()

    def description(self) -> str:
        return (
            "Validates Windows Update status and recency of 'Last checked/Installed on'. "
            "Pass requires up-to-date state with a recent check (≤ threshold). Level = ML1. "
            "Supports single-file uploads and folder scans."
        )

    def emit_hits(self, text: str = "", source_file: str = "", **kwargs) -> List[Dict[str, Any]]:
        hits: List[Dict[str, Any]] = []

        # ---- SINGLE-FILE MODE (UI upload) ----
        if source_file:
            ev_path: Optional[Path] = None
            fp = kwargs.get("full_path")
            if fp:
                try:
                    ev_path = Path(fp)
                except Exception:
                    ev_path = None
            ev_text = text or (_extract_text(ev_path) if ev_path and ev_path.exists() else "")
            h = _build_hit_for_text(ev_text, source_file, ev_path)
            return [h] if h else []

        # ---- FOLDER MODE ----
        for ev_path in _iter_evidence_files(self.EVIDENCE_DIR):
            ev_text = _extract_text(ev_path)
            h = _build_hit_for_text(ev_text, ev_path.name, ev_path)
            if h:
                hits.append(h)

        return hits
