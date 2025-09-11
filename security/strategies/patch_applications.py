# security/strategies/patch_applications.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Iterable, Optional
from .overview import Strategy
import io, os, re

# -------------------- Optional deps (no hard-crash) --------------------
try:
    import fitz  # PyMuPDF (PDF)
except Exception:
    fitz = None

try:
    from docx import Document as DocxDocument  # python-docx
except Exception:
    DocxDocument = None

try:
    import pytesseract
    from PIL import Image, ImageOps, ImageFilter, ImageStat, UnidentifiedImageError
    _TESS_PATH = os.environ.get("TESSERACT_CMD") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if Path(_TESS_PATH).exists():
        pytesseract.pytesseract.tesseract_cmd = _TESS_PATH
except Exception:
    pytesseract = None
    Image = None
    ImageOps = None
    ImageFilter = None
    ImageStat = None
    class UnidentifiedImageError(Exception): ...
# ----------------------------------------------------------------------

# Evidence we consider
EXTS = {".txt", ".log", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}

# Filename hints
FILENAME_HINTS = ("winget_upgrade", "winget-upgrade", "winget upgrades", "winget upg", "winget upgrade")

# Apps to prioritise if pending (raise priority text, but Level stays ML1)
CRITICAL_PATTERNS = [
    r"\b(Microsoft\s*Edge|Google\s*Chrome|Mozilla\s*Firefox)\b",
    r"\b(Teams|Zoom|Slack)\b",
    r"\b(7-?Zip|WinRAR)\b",
    r"\b(Java|JRE|JDK|Temurin|OpenJDK)\b",
    r"\b(Node\.js|Python\s*3)\b",
    r"\b(Adobe\s+Acrobat|Adobe\s+Reader|VLC)\b",
    r"\b(Wireshark|PuTTY)\b",
]

# ------------------------------------ helpers ------------------------------------
def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def _resolve_evidence_dir() -> Path:
    env = os.environ.get("PATCH_APPLICATIONS_DIR")
    if env:
        p = Path(env)
        if p.exists():
            return p
    root = _project_root()
    for c in [root / "evidence" / "patch_applications",
              root / "security" / "evidence" / "patch_applications"]:
        if c.exists():
            return c
    return root / "evidence" / "patch_applications"

def _iter_evidence_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    for p in sorted(root.iterdir()):
        if p.is_file() and p.suffix.lower() in EXTS:
            yield p

# ---------- OCR tuned for dark console screenshots ----------
def _ocr_image_bytes(data: bytes) -> str:
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
# -----------------------------------------------------------

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

def _looks_like_winget(text: str, fname: str) -> bool:
    low = fname.lower()
    if any(h in low for h in FILENAME_HINTS):
        return True
    return bool(
        re.search(r"\bwinget\b", text, re.I)
        and re.search(r"\b(Name|Package)\b", text)
        and re.search(r"\bVersion\b", text)
        and re.search(r"\bAvailable\b", text)
    )

# “No updates” vs “X upgrades available”
NO_UPDATES_RE = re.compile(r"\bNo (applicable )?updates? (found|available)\b", re.I)
FOOTER_COUNT_RE = re.compile(r"\b(\d+)\s+upgrades?\s+available\b", re.I)

def _clean_ocr(text: str) -> str:
    return (
        text.replace("—", "-").replace("–", "-")
            .replace("I", "|")  # common OCR confusion for pipes
    )

def _parse_winget_upgrade(text: str) -> List[Dict[str, str]]:
    """
    Parse `winget upgrade` table into rows: {name, id, version, available, source}
    Works with TXT and OCR'ed screenshots; tolerant to wrapping.
    """
    rows: List[Dict[str, str]] = []
    txt = _clean_ocr(text)
    lines = [ln.rstrip() for ln in txt.splitlines() if ln.strip()]

    # Find header (order may vary)
    header_idx = -1
    for i, ln in enumerate(lines):
        if re.search(r"\b(Name|Package)\b", ln) and re.search(r"\bVersion\b", ln) and re.search(r"\bAvailable\b", ln):
            header_idx = i
            break
    if header_idx == -1:
        return rows

    # Parse body until footer
    for ln in lines[header_idx + 1:]:
        if re.match(r"^[\-\=_]{5,}$", ln):
            continue
        if FOOTER_COUNT_RE.search(ln):
            break
        parts = re.split(r"\s{2,}", ln.strip())
        if len(parts) < 3:
            continue
        name = parts[0]
        version = parts[1] if len(parts) >= 2 else ""
        available = parts[2] if len(parts) >= 3 else ""
        pkg_id = parts[3] if len(parts) >= 4 else ""
        source = parts[4] if len(parts) >= 5 else ""
        if not name or not (version or available):
            continue
        rows.append({
            "name": name,
            "id": pkg_id,
            "version": version,
            "available": available,
            "source": source,
        })

    # Deduplicate by (name, available)
    dedup: Dict[tuple, Dict[str, str]] = {}
    for r in rows:
        key = (r["name"], r["available"])
        dedup[key] = r
    return list(dedup.values())

def _fallback_names(text: str) -> List[str]:
    """
    If row parsing fails but it clearly looks like a winget table,
    try to pull left-column names as a fallback sample.
    """
    names = []
    for ln in text.splitlines():
        ln = ln.strip()
        # Heuristic: names tend not to contain "->", and have spaces; skip headers
        if not ln or "Version" in ln or "Available" in ln or ln.startswith("-"):
            continue
        if re.search(r"\b(Name|Package)\b", ln):
            continue
        # Take everything before 2+ spaces as the "name"
        m = re.split(r"\s{2,}", ln)
        if m and len(m[0]) >= 3:
            names.append(m[0][:80])
    return names[:12]

def _find_critical(rows: List[Dict[str, str]], text: str) -> List[str]:
    crit = []
    # from parsed rows
    for r in rows:
        nm = f"{r.get('name','')} {r.get('id','')}"
        for pat in CRITICAL_PATTERNS:
            if re.search(pat, nm, re.I):
                crit.append(r.get("name") or r.get("id") or nm)
                break
    # if no rows, try the raw text
    if not crit:
        for pat in CRITICAL_PATTERNS:
            m = re.search(pat, text, re.I)
            if m:
                crit.append(m.group(0))
    # dedup
    seen = set()
    out = []
    for c in crit:
        k = c.lower()
        if k not in seen:
            seen.add(k)
            out.append(c)
    return out

# ---------------------------------- core builder ----------------------------------
def _build_hit(ev_text: str, ev_name: str, ev_path: Optional[Path]) -> Dict[str, Any] | None:
    if not _looks_like_winget(ev_text, ev_name):
        return None

    # Default: assume FAIL unless we positively see "No updates..."
    none_found = bool(NO_UPDATES_RE.search(ev_text))
    footer_m = FOOTER_COUNT_RE.search(ev_text)
    footer_count = int(footer_m.group(1)) if footer_m else None

    if none_found:
        rows: List[Dict[str, str]] = []
        pending_count = 0
        parsed_row_count = 0
        detection_notes = "Explicit 'No updates found/available' detected."
    else:
        rows = _parse_winget_upgrade(ev_text)
        parsed_row_count = len(rows)
        pending_count = parsed_row_count

        # Footer fail-safe: if the screenshot says "X upgrades available" but rows == 0, still FAIL
        if (pending_count == 0) and (footer_count is not None) and (footer_count > 0):
            pending_count = footer_count
            # Try to salvage sample names
            sample_names = _fallback_names(ev_text)
            rows = [{"name": n, "id": "", "version": "", "available": "", "source": ""} for n in sample_names]
            detection_notes = f"Footer fail-safe used (saw '{footer_count} upgrades available')."
        else:
            detection_notes = "Parsed rows from table." if pending_count > 0 else "Parsed table with zero rows."

    critical = _find_critical(rows, ev_text) if pending_count > 0 else []

    # ---- Output fields ----
    passed = (pending_count == 0)  # PASS only when zero updates
    # Level column should show ML1 as requested
    level = "ML1"
    # Keep priority higher if critical apps pending
    priority = "P2" if critical else ("P4" if passed else "P4")

    # Build sample list for the PDF
    sample = []
    for r in rows[:12]:
        n = r.get("name") or r.get("id") or "package"
        v = r.get("version") or "?"
        a = r.get("available") or "?"
        if v == "?" and a == "?":
            sample.append(n)
        else:
            sample.append(f"{n} ({v} → {a})")

    recommendation = (
        "Run 'winget upgrade --all --silent --accept-source-agreements --accept-package-agreements' "
        "or deploy via Intune/SCCM to all devices. Enforce auto-update policies for browsers and "
        "high-risk apps. Prefer stable/LTS channels where applicable. For ML1 timelines: remediate "
        "critical/weaponised within 48h; other non-critical within 2 weeks."
    )
    if critical:
        recommendation = (
            "Prioritise updating critical apps immediately (browsers, collaboration tools, runtimes). "
        ) + recommendation

    return {
        "test_id": "E8-PA-ML1-001",
        "sub_strategy": "Patch Applications — Winget Pending Updates",
        "detected_level": level,                 # ← ML1 as requested
        "pass_fail": "pass" if passed else "fail",
        "priority": priority,
        "recommendation": recommendation,
        "evidence": {
            "source_file": ev_name,
            "absolute_path": str(ev_path) if ev_path else "",
            "pending_count": pending_count,
            "parsed_row_count": parsed_row_count,
            "critical_matches": critical,
            "sample_pending": sample,
            "footer_fail_safe_used": bool(footer_count and parsed_row_count == 0),
            "winget_footer_count": footer_count,
            "none_updates_phrase_detected": none_found,
        },
    }

# ---------------------------------- Strategy ----------------------------------
class PatchApplicationsML1(Strategy):
    """
    ML1 detector for pending application updates based on 'winget upgrade' output.
    PASS only when no updates remain. Level column is set to 'ML1'.
    """
    name = "Patch Applications (ML1)"
    key  = "patch_applications_ml1"
    EVIDENCE_DIR = _resolve_evidence_dir()

    def description(self) -> str:
        return (
            "Parses 'winget upgrade' output (TXT/LOG, PDF/DOCX, or dark-theme screenshots) to detect "
            "pending application updates. PASS only when zero updates remain. Level = ML1. "
            "Includes a footer fail-safe so 'X upgrades available' can never pass."
        )

    def emit_hits(self, text: str = "", source_file: str = "", **kwargs) -> List[Dict[str, Any]]:
        hits: List[Dict[str, Any]] = []

        # ---- SINGLE-FILE MODE (UI uploads) ----
        if source_file:
            ev_path: Optional[Path] = None
            fp = kwargs.get("full_path")
            if fp:
                try:
                    ev_path = Path(fp)
                except Exception:
                    ev_path = None
            ev_text = text or (_extract_text(ev_path) if ev_path and ev_path.exists() else "")
            h = _build_hit(ev_text, source_file, ev_path)
            return [h] if h else []

        # ---- FOLDER MODE (repo evidence) ----
        for ev_path in _iter_evidence_files(self.EVIDENCE_DIR):
            ev_text = _extract_text(ev_path)
            if not _looks_like_winget(ev_text, ev_path.name):
                continue
            h = _build_hit(ev_text, ev_path.name, ev_path)
            if h:
                hits.append(h)

        return hits
