"""Integration tests for the evidence-scanning endpoints (/v1/evidence/*).

Kept deliberately light on the actual OCR/scan pipeline (security/evidence_ui)
-- that pipeline shells out to pytesseract and does real file-format
detection, which belongs in its own dedicated test suite, not here. What
this file verifies is the integration surface FastAPI is responsible for:
which routes are public vs. auth-gated, and that auth is enforced before
any scan work happens.
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
