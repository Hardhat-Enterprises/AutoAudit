"""Integration tests for the evidence-scanning endpoints (/v1/evidence/*).

Kept deliberately light on the actual OCR/scan pipeline (security/evidence_ui)
-- that pipeline shells out to pytesseract and does real file-format
detection, which belongs in its own dedicated test suite, not here. What
this file verifies is the integration surface FastAPI is responsible for:
which routes are public vs. auth-gated, and that auth is enforced before
any scan work happens.

The second half of the file covers how POST /scan handles bad, missing and
incomplete evidence (empty, oversized, wrong type, unknown strategy). It uses
small plain-text uploads only, so no OCR is involved. Tests marked xfail
document known gaps and will start failing (strict) once the gap is fixed,
as a reminder to remove the marker.
"""

import pytest
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from httpx import ASGITransport, AsyncClient

from app.api.v1 import evidence as evidence_routes
from app.core.auth import get_current_user
from app.models.user import Role
from tests.conftest import make_user


async def test_strategies_is_public(client):
    """The strategy list backs a dropdown the frontend shows before
    login, so it must not require authentication."""
    resp = await client.get("/v1/evidence/strategies")
    assert resp.status_code == 200, resp.text  # nosec B101


async def test_health_is_public(client):
    resp = await client.get("/v1/evidence/health")
    assert resp.status_code == 200, resp.text  # nosec B101


async def test_scan_requires_auth(client):
    """POST /scan must reject an unauthenticated request. The body is a
    well-formed multipart payload so a 401 can only be coming from the
    get_current_user dependency, not from FastAPI rejecting a malformed
    request body first."""
    resp = await client.post(
        "/v1/evidence/scan",
        files={"evidence": ("test.txt", b"dummy evidence content", "text/plain")},
        data={"strategy_name": "regular_backups"},
    )
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_download_report_requires_auth(client):
    resp = await client.get("/v1/evidence/reports/nonexistent.pdf")
    assert resp.status_code == 401, resp.text  # nosec B101


# ---------------------------------------------------------------------------
# Report ownership (Sprint 1 authz finding F1: cross-tenant report download).
#
# Reports are named "<owner user id>-<strategy>-<stem>-<ts>-<rand>.<ext>"; the
# download route must only serve files whose prefix is the caller's own id.
# A minimal app with just the evidence router is used so the current user can
# be overridden, and evidence_ui.download_report is stubbed so no real report
# files are needed.
# ---------------------------------------------------------------------------

OWNER_REPORT = "12-CIS_Microsoft_365_Audit-policy-1795000799-0123456789abcdef.docx"


@pytest.fixture
def served(monkeypatch):
    """Stub evidence_ui.download_report and record which filenames reach it."""
    calls: list[str] = []

    def fake_download_report(filename: str):
        calls.append(filename)
        return PlainTextResponse(f"report:{filename}")

    monkeypatch.setattr(evidence_routes.evidence_ui, "download_report", fake_download_report)
    return calls


def _client_as(user) -> AsyncClient:
    app = FastAPI()
    app.include_router(evidence_routes.router, prefix="/v1")

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_owner_can_download_own_report(served):
    async with _client_as(make_user(role=Role.AUDITOR.value, user_id=12)) as c:
        resp = await c.get(f"/v1/evidence/reports/{OWNER_REPORT}")
    assert resp.status_code == 200, resp.text  # nosec B101
    assert served == [OWNER_REPORT]  # nosec B101


@pytest.mark.parametrize(
    "role,user_id",
    [
        (Role.AUDITOR.value, 13),  # another tenant
        (Role.VIEWER.value, 14),
        (Role.AUDITOR.value, 1),  # "1-" must not match "12-..."
        (Role.ADMIN.value, 2),  # admins get no cross-user bypass
    ],
)
async def test_other_users_cannot_download_report(served, role, user_id):
    async with _client_as(make_user(role=role, user_id=user_id)) as c:
        resp = await c.get(f"/v1/evidence/reports/{OWNER_REPORT}")
    assert resp.status_code == 404, resp.text  # nosec B101
    assert resp.json()["detail"] == "Report not found"  # nosec B101
    assert served == []  # nosec B101  -- file lookup never attempted


async def test_unprefixed_report_name_is_not_found(served):
    async with _client_as(make_user(role=Role.AUDITOR.value, user_id=12)) as c:
        resp = await c.get("/v1/evidence/reports/report.pdf")
    assert resp.status_code == 404, resp.text  # nosec B101
    assert served == []  # nosec B101


async def _scan(client, filename, content, strategy="Regular Backups"):
    """POST a small in-memory file to /scan; no files are written to disk."""
    return await client.post(
        "/v1/evidence/scan",
        files={"evidence": (filename, content, "application/octet-stream")},
        data={"strategy_name": strategy},
    )


async def test_scan_rejects_empty_file(auth_client):
    resp = await _scan(auth_client, "empty.txt", b"")
    assert resp.status_code == 400, resp.text  # nosec B101
    assert resp.json()["detail"] == "Empty upload"  # nosec B101


async def test_scan_rejects_oversized_file(auth_client):
    resp = await _scan(auth_client, "big.txt", b"0" * (11 * 1024 * 1024))
    assert resp.status_code == 400, resp.text  # nosec B101
    assert "10 MB" in resp.json()["detail"]  # nosec B101


async def test_scan_rejects_disallowed_extension(auth_client):
    resp = await _scan(auth_client, "program.exe", b"MZ fake program")
    assert resp.status_code == 400, resp.text  # nosec B101
    assert "not permitted" in resp.json()["detail"]  # nosec B101


async def test_scan_rejects_unknown_strategy(auth_client):
    resp = await _scan(auth_client, "valid.txt", b"status=success", strategy="nope")
    assert resp.status_code == 400, resp.text  # nosec B101
    assert "Unknown strategy" in resp.json()["detail"]  # nosec B101


async def test_scan_strategy_name_is_exact_match(auth_client):
    """Strategy names are matched exactly, so a slug is not accepted."""
    resp = await _scan(
        auth_client, "valid.txt", b"status=success", strategy="regular_backups"
    )
    assert resp.status_code == 400, resp.text  # nosec B101


async def test_scan_requires_strategy_name(auth_client):
    resp = await auth_client.post(
        "/v1/evidence/scan",
        files={"evidence": ("valid.txt", b"status=success", "text/plain")},
    )
    assert resp.status_code == 422, resp.text  # nosec B101


async def test_scan_requires_file(auth_client):
    resp = await auth_client.post(
        "/v1/evidence/scan", data={"strategy_name": "Regular Backups"}
    )
    assert resp.status_code == 422, resp.text  # nosec B101


async def test_scan_valid_backup_evidence_passes(auth_client):
    resp = await _scan(
        auth_client,
        "valid.txt",
        b"status=success\nbackup_location=offsite\nimmutability=enabled\n",
    )
    assert resp.status_code == 200, resp.text  # nosec B101
    body = resp.json()
    assert body["ok"] is True  # nosec B101
    assert body["findings"], body  # nosec B101
    assert {f["pass_fail"] for f in body["findings"]} == {"PASS"}  # nosec B101


async def test_scan_irrelevant_text_fails_regular_backups(auth_client):
    resp = await _scan(auth_client, "irrelevant.txt", b"hello world, lunch menu")
    assert resp.status_code == 200, resp.text  # nosec B101
    findings = resp.json()["findings"]
    assert findings[0]["pass_fail"] == "FAIL"  # nosec B101


@pytest.mark.xfail(
    strict=True,
    reason="Known gap: an unreadable PDF returns 200 ok=true with no findings "
    "instead of an error.",
)
async def test_scan_corrupt_pdf_is_rejected(auth_client):
    resp = await _scan(auth_client, "corrupt.pdf", b"this is not a real pdf")
    assert resp.status_code >= 400, resp.text  # nosec B101


@pytest.mark.xfail(
    strict=True,
    reason="Known gap: keyword strategies (e.g. CIS) mark text with no bad "
    "keywords as PASS, so irrelevant evidence passes.",
)
async def test_scan_irrelevant_text_does_not_pass_cis(auth_client):
    resp = await _scan(
        auth_client,
        "irrelevant.txt",
        b"hello world, lunch menu",
        strategy="CIS Microsoft 365 Audit",
    )
    assert resp.status_code == 200, resp.text  # nosec B101
    findings = resp.json()["findings"]
    assert all(f["pass_fail"] != "PASS" for f in findings)  # nosec B101


@pytest.mark.xfail(
    strict=True,
    reason="Known gap: GET /scan-mem-log is public and lists user ids and "
    "scan activity.",
)
async def test_scan_mem_log_requires_auth(client):
    resp = await client.get("/v1/evidence/scan-mem-log")
    assert resp.status_code == 401, resp.text  # nosec B101
