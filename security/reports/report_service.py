# pylint: disable=line-too-long,broad-exception-caught,too-many-locals,too-many-statements,too-many-branches,too-many-arguments,unused-argument,duplicate-code,import-outside-toplevel
"""Security report generation service module for AutoAudit.

Renders DOCX and PDF audit reports from evidence processing data.
"""

from __future__ import annotations

import os
import subprocess  # nosec B404
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from docx import Document
from docx.shared import Inches
from fpdf import FPDF


def generate_pdf(
    data: Mapping[str, Any],
    *,
    template_path: os.PathLike | str = "templates/report_template.docx",
    output_dir: os.PathLike | str = "reports_out",
    base_dir: os.PathLike | str = ".",
    image_marker: str = "[Embed evidence here]",
    unique_id_override: Optional[str] = None,
) -> Path:
    """Render a single PDF from the in-memory mapping produced by the OCR step."""
    mapping, embed_path, unique_id = _map_to_placeholders(data, Path(base_dir))

    if unique_id_override:
        unique_id = unique_id_override
        mapping["UniqueID"] = unique_id
        mapping["Unique ID"] = unique_id

    tpath = Path(template_path)
    if not tpath.exists():
        raise FileNotFoundError(f"Template not found: {tpath}")

    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    pdf_path = outdir / f"{unique_id}.pdf"
    doc = Document(str(tpath))
    _replace_braced_placeholders_everywhere(doc, mapping)
    _replace_xml_text_everywhere(doc, mapping)
    if embed_path:
        if not _insert_image_at_marker(doc, image_marker, embed_path, width_inches=6.0):
            _insert_image_at_marker(doc, "[Embed screenshot here]", embed_path, width_inches=6.0)
    else:
        _remove_markers_everywhere(doc, ["[Embed evidence here]", "[Embed screenshot here]"])
    filled = pdf_path.with_suffix(".filled.docx")
    doc.save(str(filled))
    _convert_docx_to_pdf(filled, pdf_path)
    try:
        filled.unlink()
    except Exception:
        pass

    return pdf_path


def _normalize_keys(d: Mapping[str, Any]) -> Dict[str, str]:
    """Normalize dictionary keys for consistent field lookup."""
    norm: Dict[str, str] = {}
    for k, v in d.items():
        key = " ".join(str(k).strip().lower().replace("_", " ").replace("-", " ").replace("/", " ").split())
        norm[key] = "" if v is None else str(v)
    return norm


def _pick(norm: Dict[str, str], *names: str) -> str:
    """Select the first matching key value from normalized dictionary."""
    for n in names:
        key = " ".join(n.strip().lower().split())
        if key in norm:
            return norm[key]
    return ""


def _map_to_placeholders(data: Mapping[str, Any], base_dir: Path) -> Tuple[Dict[str, str], Optional[Path], str]:
    """Map OCR dictionary entries to template placeholder fields and evidence paths."""
    n = _normalize_keys(data)

    unique_id = _pick(n, "uniqueid", "unique id", "userid", "user id") or str(uuid.uuid4())
    strategy = _pick(n, "strategy")
    testid = _pick(n, "testid", "test id")
    substrat = _pick(n, "sub-strategy", "sub strategy")
    level = _pick(n, "ml level", "level")
    passfail = _pick(n, "pass/fail", "pass fail")
    priority = _pick(n, "priority")
    rec = _pick(n, "recommendation", "recommendations")
    extract = _pick(n, "evidence extract", "extract")
    descr = _pick(n, "description")
    confidence = _pick(n, "confidence")

    evidence_path_str = _pick(n, "evidence", "evidence path", "file", "file path", "filepath", "image", "screenshot")
    preview_path_str = _pick(n, "evidence preview", "preview", "embed path")

    embed_path: Optional[Path] = None
    file_name = ""
    if evidence_path_str:
        ep = Path(evidence_path_str)
        if not ep.is_absolute():
            ep = base_dir / ep
        file_name = ep.name
    if preview_path_str:
        pp = Path(preview_path_str)
        if not pp.is_absolute():
            pp = base_dir / pp
        if pp.exists():
            embed_path = pp
    else:
        if evidence_path_str:
            ep = Path(evidence_path_str)
            if not ep.is_absolute():
                ep = base_dir / ep
            if ep.exists() and ep.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}:
                embed_path = ep

    mapping: Dict[str, str] = {
        "UniqueID": unique_id,
        "Unique ID": unique_id,
        "UserID": unique_id,
        "Strategy": strategy,
        "Test_id": testid,
        "Sub-Strategy": substrat,
        "level": level,
        "Level": level,
        "Pass/Fail": passfail,
        "Priority": priority,
        "Recommendations": rec,
        "extract": extract,
        "Extract": extract,
        "Description": descr,
        "description": descr,
        "Confidence": confidence or "",
        "file name": file_name,
        "File Name": file_name,
        "Date Generated": datetime.now().strftime("%d %b %Y"),
    }
    _expand_placeholder_variants(mapping)
    return mapping, embed_path, unique_id


def _iter_paragraphs(doc: Any) -> Any:
    """Iterate over all paragraphs in docx body and embedded table cells."""
    for p in doc.paragraphs:
        yield p
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p


def _replace_in_runs(paragraph: Any, mapping: Mapping[str, Any]) -> bool:
    """Replace placeholder tokens directly inside paragraph text runs."""
    changed = False
    for run in paragraph.runs:
        txt = run.text
        new = txt
        for k, v in mapping.items():
            new = new.replace("{" + k + "}", str(v))
        if new != txt:
            run.text = new
            changed = True
    return changed


def _rebuild_paragraph_text(paragraph: Any, mapping: Mapping[str, Any]) -> None:
    """Rebuild paragraph text when placeholder tokens span across multiple runs."""
    full = "".join(run.text for run in paragraph.runs)
    repl = full
    for k, v in mapping.items():
        repl = repl.replace("{" + k + "}", str(v))
    if repl != full:
        for r in paragraph.runs:
            r.text = ""
        paragraph.add_run(repl)


def _replace_braced_placeholders_everywhere(doc: Any, mapping: Mapping[str, Any]) -> None:
    """Replace braced tokens in all document paragraphs and table contents."""
    for p in _iter_paragraphs(doc):
        if not _replace_in_runs(p, mapping):
            _rebuild_paragraph_text(p, mapping)


def _replace_xml_text_everywhere(doc: Any, mapping: Mapping[str, Any]) -> None:
    """Replace {tokens} in all text nodes across main doc, headers, and footers."""
    def replace_in_part(part: Any) -> None:
        """Process XML replacements inside document part."""
        root = part.element
        texts = []
        try:
            ns = getattr(root, "nsmap", None)
            if ns:
                texts = root.xpath(".//w:t", namespaces=ns)
        except TypeError:
            texts = []
        if not texts:
            texts = root.xpath(".//*[local-name()='t']")

        for t in texts:
            old = t.text or ""
            new = old
            for k, v in mapping.items():
                new = new.replace("{" + k + "}", str(v))
            if new != old:
                t.text = new

    replace_in_part(doc.part)
    for section in doc.sections:
        try:
            if section.header:
                replace_in_part(section.header.part)
        except Exception:
            pass
        try:
            if section.footer:
                replace_in_part(section.footer.part)
        except Exception:
            pass


def _insert_image_at_marker(doc: Any, marker: str, image_path: os.PathLike | str, width_inches: float = 6.0) -> bool:
    """Insert an image picture at a designated text marker in the document."""
    ip = Path(image_path)
    if not ip.exists():
        return False
    target = None
    for p in _iter_paragraphs(doc):
        if marker in "".join(run.text for run in p.runs):
            target = p
            break
    if not target:
        return False
    for r in target.runs:
        r.text = r.text.replace(marker, "")
    run = target.add_run()
    try:
        run.add_picture(str(ip), width=Inches(width_inches))
    except AttributeError:
        doc.add_picture(str(ip), width=Inches(width_inches))
    return True


def _convert_docx_to_pdf(input_docx: Path, output_pdf: Path) -> None:
    """Convert DOCX file to PDF using docx2pdf, LibreOffice, or pure-Python FPDF fallback."""
    try:
        from docx2pdf import convert
        convert(str(input_docx), str(output_pdf))
        return
    except Exception:
        pass

    try:
        out_dir = str(output_pdf.parent.resolve())
        subprocess.run(  # nosec B603 B607
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", out_dir, str(input_docx.resolve())],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        expected = output_pdf.with_suffix(".pdf")
        if expected.exists() and expected != output_pdf:
            expected.replace(output_pdf)
        return
    except Exception:
        pass

    if _simple_pdf_from_docx(input_docx, output_pdf):
        return

    raise RuntimeError(
        "PDF conversion failed. Install Microsoft Word for docx2pdf or LibreOffice, or ensure fpdf2 fallback works."
    )


def _simple_pdf_from_docx(input_docx: Path, output_pdf: Path) -> bool:
    """Fallback PDF generator using fpdf2 when external converters are unavailable."""
    try:
        doc = Document(str(input_docx))
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)

        def _safe_text(text: Optional[str]) -> str:
            """Sanitize input text for latin-1 font encoding compatibility."""
            if text is None:
                return ""
            try:
                return text.encode("latin-1").decode("latin-1")
            except Exception:
                return text.encode("ascii", "replace").decode("ascii")

        def _write_line(line: str) -> None:
            """Write individual paragraph line into PDF layout cell."""
            line = _safe_text(line)
            if not line:
                return
            pdf.multi_cell(0, 8, line)
            pdf.ln(1)

        for p in doc.paragraphs:
            text = (p.text or "").strip()
            _write_line(text)

        for tbl in doc.tables:
            for row in tbl.rows:
                row_text = " | ".join((cell.text or "").strip() for cell in row.cells)
                _write_line(row_text)

        pdf.output(str(output_pdf))
        return True
    except Exception:
        return False


def _remove_markers_everywhere(doc: Any, markers: List[str]) -> None:
    """Remove target marker strings from document body, headers, and footers."""
    for p in _iter_paragraphs(doc):
        full = "".join(r.text for r in p.runs)
        new_full = full
        for m in markers:
            new_full = new_full.replace(m, "")
        if new_full != full:
            for r in p.runs:
                r.text = ""
            p.add_run(new_full)

    def scrub_part(part: Any) -> None:
        """Scrub markers from individual XML element part."""
        root = part.element
        texts = []
        try:
            ns = getattr(root, "nsmap", None)
            if ns:
                texts = root.xpath(".//w:t", namespaces=ns)
        except TypeError:
            texts = []
        if not texts:
            texts = root.xpath(".//*[local-name()='t']")
        for t in texts:
            old = t.text or ""
            new = old
            for m in markers:
                new = new.replace(m, "")
            if new != old:
                t.text = new

    scrub_part(doc.part)
    for section in doc.sections:
        try:
            if section.header:
                scrub_part(section.header.part)
        except Exception:
            pass
        try:
            if section.footer:
                scrub_part(section.footer.part)
        except Exception:
            pass


def _expand_placeholder_variants(mapping: Dict[str, str]) -> None:
    """Make token replacement tolerant to dashes, non-ASCII hyphens, and spaces."""
    hyphens = ["-", "\u2010", "\u2011", "\u2013", "\u2014"]
    to_add: Dict[str, str] = {}

    for k, v in list(mapping.items()):
        spaced = f" {k} "
        if spaced not in mapping:
            to_add[spaced] = v
        if "-" in k:
            for h in hyphens:
                if h == "-":
                    continue
                k_dash = k.replace("-", h)
                if k_dash not in mapping:
                    to_add[k_dash] = v
                spaced_dash = f" {k_dash} "
                if spaced_dash not in mapping:
                    to_add[spaced_dash] = v

    mapping.update(to_add)
