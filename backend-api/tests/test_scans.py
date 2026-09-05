"""Integration tests for the scan API endpoints (/v1/scans/*).

Covers auth-gating and 404/not-found behaviour across the whole router,
plus the create_scan happy path: a real M365Connection row is inserted
directly via `db_session` (with a Fernet-encrypted fake client secret,
matching how the app stores real ones), and the request runs against the
real benchmark metadata checked into engine/policies/ (see
conftest.py's POLICIES_DIR default) -- so control counts, ScanResult
seeding, and the response shape are all exercised for real.

The one thing that's stubbed out is the actual Celery dispatch:
`queue_scan` talks to a Redis broker that isn't part of this suite's test
infrastructure (only Postgres is), and a live broker/worker is Celery's
concern, not this endpoint's -- create_scan's own job is to validate the
connection, create the Scan/ScanResult rows, and queue the task, and it's
that behaviour (not Celery's delivery of the message) this test verifies.
`queue_scan` is monkeypatched to a stand-in that mimics the small part of
its return value (`AsyncResult.id`) the endpoint actually reads.
"""

import pytest_asyncio
from sqlalchemy import select

from app.models.m365_connection import M365Connection
from app.models.user import User
from app.services.encryption import encrypt


class _FakeAsyncResult:
    """Stand-in for the celery.result.AsyncResult that queue_scan()
    returns. create_scan() only ever reads `.id` off of it (to report the
    task ID back to the caller), so that's the only thing faked here."""

    id = "fake-task-id-for-tests"


@pytest_asyncio.fixture
async def m365_connection_id(db_session, registered_user) -> int:
    """Insert a real, usable M365Connection row for the registered test
    user directly via db_session -- Fernet-encrypted secret included, the
    same as a real saved connection would look at rest -- so create_scan's
    connection-ownership check has something genuine to find."""
    email, _ = registered_user
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    connection = M365Connection(
        user_id=user.id,
        name="Test Tenant",
        tenant_id="11111111-1111-1111-1111-111111111111",
        client_id="22222222-2222-2222-2222-222222222222",
        encrypted_client_secret=encrypt("not-a-real-secret"),  # pragma: allowlist secret
    )
    db_session.add(connection)
    await db_session.commit()
    await db_session.refresh(connection)
    return connection.id


async def test_list_scans_requires_auth(client):
    resp = await client.get("/v1/scans/")
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_list_scans_empty_for_new_user(auth_client):
    """A freshly registered user has created no scans yet."""
    resp = await auth_client.get("/v1/scans/")
    assert resp.status_code == 200, resp.text  # nosec B101
    assert resp.json() == []  # nosec B101


async def test_get_scan_requires_auth(client):
    resp = await client.get("/v1/scans/1")
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_get_nonexistent_scan_returns_404(auth_client):
    resp = await auth_client.get("/v1/scans/999999")
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_get_scan_summary_nonexistent_returns_404(auth_client):
    resp = await auth_client.get("/v1/scans/999999/summary")
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_get_scan_results_nonexistent_returns_404(auth_client):
    resp = await auth_client.get("/v1/scans/999999/results")
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_delete_nonexistent_scan_returns_404(auth_client):
    resp = await auth_client.delete("/v1/scans/999999")
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_delete_scan_requires_auth(client):
    resp = await client.delete("/v1/scans/1")
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_create_scan_nonexistent_connection_returns_404(auth_client):
    """The connection ownership/existence check must run (and fail
    loudly) before any benchmark lookup or Celery task is queued."""
    resp = await auth_client.post(
        "/v1/scans/",
        json={
            "m365_connection_id": 999999,
            "framework": "cis",
            "benchmark": "microsoft-365-foundations",
            "version": "v6.0.0",
        },
    )
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_create_scan_requires_auth(client):
    resp = await client.post(
        "/v1/scans/",
        json={
            "m365_connection_id": 1,
            "framework": "cis",
            "benchmark": "microsoft-365-foundations",
            "version": "v6.0.0",
        },
    )
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_readiness_nonexistent_connection_returns_404(auth_client):
    resp = await auth_client.get(
        "/v1/scans/readiness",
        params={
            "m365_connection_id": 999999,
            "framework": "cis",
            "benchmark": "microsoft-365-foundations",
            "version": "v6.0.0",
        },
    )
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_readiness_requires_auth(client):
    resp = await client.get(
        "/v1/scans/readiness",
        params={
            "m365_connection_id": 1,
            "framework": "cis",
            "benchmark": "microsoft-365-foundations",
            "version": "v6.0.0",
        },
    )
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_create_scan_happy_path(auth_client, m365_connection_id, monkeypatch):
    """A valid, active connection plus a real benchmark on disk should
    create the scan, seed every control as a pending ScanResult, and
    queue it -- the full path the frontend relies on after the user picks
    a connection and clicks "Run scan"."""
    monkeypatch.setattr(
        "app.api.v1.scans.queue_scan", lambda scan_id: _FakeAsyncResult()
    )

    resp = await auth_client.post(
        "/v1/scans/",
        json={
            "m365_connection_id": m365_connection_id,
            "framework": "cis",
            "benchmark": "microsoft-365-foundations",
            "version": "v6.0.0",
        },
    )
    assert resp.status_code == 201, resp.text  # nosec B101
    body = resp.json()
    assert body["status"] == "pending"  # nosec B101
    assert "Task ID" in body["message"]  # nosec B101
    scan_id = body["id"]

    get_resp = await auth_client.get(f"/v1/scans/{scan_id}")
    assert get_resp.status_code == 200, get_resp.text  # nosec B101
    scan = get_resp.json()
    assert scan["framework"] == "cis"  # nosec B101
    assert scan["benchmark"] == "microsoft-365-foundations"  # nosec B101
    assert scan["status"] == "pending"  # nosec B101
    assert scan["skipped_count"] == 0  # nosec B101
    # Every control in the real, on-disk benchmark metadata should have
    # been seeded as its own ScanResult, all still pending (nothing has
    # actually run -- queue_scan is mocked out above).
    assert scan["total_controls"] > 0  # nosec B101
    assert scan["total_controls"] == len(scan["results"])  # nosec B101
    assert all(r["status"] == "pending" for r in scan["results"])  # nosec B101

    list_resp = await auth_client.get("/v1/scans/")
    assert list_resp.status_code == 200, list_resp.text  # nosec B101
    assert any(item["id"] == scan_id for item in list_resp.json())  # nosec B101


async def test_create_scan_with_control_ids_skips_the_rest(
    auth_client, m365_connection_id, monkeypatch
):
    """Requesting specific control_ids should still seed a ScanResult for
    every control in the benchmark (so category totals in the summary
    stay accurate) but mark everything outside the requested set as
    `skipped` rather than `pending`."""
    monkeypatch.setattr(
        "app.api.v1.scans.queue_scan", lambda scan_id: _FakeAsyncResult()
    )

    resp = await auth_client.post(
        "/v1/scans/",
        json={
            "m365_connection_id": m365_connection_id,
            "framework": "cis",
            "benchmark": "microsoft-365-foundations",
            "version": "v6.0.0",
            "control_ids": ["1.1.1"],
        },
    )
    assert resp.status_code == 201, resp.text  # nosec B101
    scan_id = resp.json()["id"]

    results_resp = await auth_client.get(f"/v1/scans/{scan_id}/results")
    assert results_resp.status_code == 200, results_resp.text  # nosec B101
    results = results_resp.json()
    by_control = {r["control_id"]: r["status"] for r in results}
    assert len(results) > 1, "expected the whole benchmark's controls, not just the selected one"  # nosec B101
    assert by_control["1.1.1"] == "pending"  # nosec B101
    skipped = [s for s in by_control.values() if s == "skipped"]
    assert len(skipped) == len(results) - 1  # nosec B101
