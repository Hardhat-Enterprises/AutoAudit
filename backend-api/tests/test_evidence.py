"""Integration tests for the evidence-scanning endpoints (/v1/evidence/*).

Kept deliberately light on the actual OCR/scan pipeline (security/evidence_ui)
-- that pipeline shells out to pytesseract and does real file-format
detection, which belongs in its own dedicated test suite, not here. What
this file verifies is the integration surface FastAPI is responsible for:
which routes are public vs. auth-gated, and that auth is enforced before
any scan work happens.
"""


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
