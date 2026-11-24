"""Tests that POST /v1/evidence/scan accepts Word (.docx) evidence.

.docx was approved as an evidence type. The scanner already extracts its
text; only the upload extension allowlist blocked it. Macro-enabled .docm
files remain rejected.
"""

import io

import pytest

pytest.importorskip("docx")  # python-docx comes with the 'evidence' extra

from docx import Document


def _docx_bytes(*lines: str) -> bytes:
    doc = Document()
    for line in lines:
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


async def _scan(client, filename, content):
    return await client.post(
        "/v1/evidence/scan",
        files={"evidence": (filename, content, "application/octet-stream")},
        data={"strategy_name": "Regular Backups"},
    )


async def test_scan_accepts_docx_evidence(auth_client):
    content = _docx_bytes(
        "status=success", "backup_location=offsite", "immutability=enabled"
    )
    resp = await _scan(auth_client, "evidence.docx", content)
    assert resp.status_code == 200, resp.text  # nosec B101
    body = resp.json()
    assert body["ok"] is True  # nosec B101
    assert body["findings"], body  # nosec B101


async def test_scan_still_rejects_docm(auth_client):
    resp = await _scan(auth_client, "macro.docm", b"PK fake macro document")
    assert resp.status_code == 400, resp.text  # nosec B101
    assert "not permitted" in resp.json()["detail"]  # nosec B101
