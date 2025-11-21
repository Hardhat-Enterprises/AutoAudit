from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path
from typing import List, Tuple

from fastapi import UploadFile


MAX_TEXT_LENGTH = 200_000  # soft guardrail to avoid returning extremely large payloads


def _extract_pdf(content: bytes, notes: List[str]) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover - dependency missing at runtime
        notes.append(f"PDF extraction skipped: pypdf not available ({exc}).")
        return ""

    try:
        reader = PdfReader(io.BytesIO(content))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as exc:  # pragma: no cover - defensive
        notes.append(f"PDF extraction failed: {exc}")
        return ""


def _extract_image(content: bytes, notes: List[str]) -> str:
    try:
        from PIL import Image  # type: ignore
    except Exception as exc:  # pragma: no cover
        notes.append(f"OCR skipped: Pillow not available ({exc}).")
        return ""

    try:
        import pytesseract  # type: ignore
    except Exception as exc:  # pragma: no cover
        notes.append(f"OCR skipped: pytesseract not available ({exc}).")
        return ""

    try:
        image = Image.open(io.BytesIO(content))
        return pytesseract.image_to_string(image)
    except Exception as exc:  # pragma: no cover - OCR might fail if tesseract binary is missing
        notes.append(f"OCR failed: {exc}")
        return ""


def _extract_docx(content: bytes, notes: List[str]) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            # rudimentary tag strip; good enough for inline text
            text = re.sub(r"<[^>]+>", " ", xml)
            return re.sub(r"\s+", " ", text)
    except Exception as exc:  # pragma: no cover
        notes.append(f"DOCX extraction failed: {exc}")
        return ""


def _extract_plain_text(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


async def extract_text(upload_file: UploadFile) -> Tuple[str, List[str]]:
    """
    Extract textual content from an uploaded evidence file.

    Returns a tuple of (text, notes). `notes` carries non-fatal warnings that the
    caller can surface to the user (e.g., OCR unavailable, extraction failure).
    """

    data = await upload_file.read()
    suffix = Path(upload_file.filename or "evidence").suffix.lower()
    notes: List[str] = []
    text = ""

    if suffix == ".pdf":
        text = _extract_pdf(data, notes)
    elif suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}:
        text = _extract_image(data, notes)
    elif suffix in {".docx"}:
        text = _extract_docx(data, notes)
    else:
        # treat as plain text-ish content (txt, log, csv, json, xml, ini, reg, html, etc.)
        text = _extract_plain_text(data)

    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
        notes.append("Extracted text truncated to 200k characters to keep the response lightweight.")

    return text.strip(), notes
