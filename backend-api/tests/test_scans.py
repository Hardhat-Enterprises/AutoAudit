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

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
import uuid
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.compliance import Scan
from app.models.m365_connection import M365Connection
from app.models.scan_result import ScanResult
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


@pytest_asyncio.fixture
async def auditor_role(db_session, registered_user) -> None:
    """Elevate `registered_user` (and therefore `auth_client`, which logs
    in as that same user) from the default Viewer role to Auditor.

    The scan create/delete endpoints are gated by
    `require_auditor_or_above` (see app/core/permissions.py), so a
    freshly registered user -- Viewer by default -- gets a 403 before
    ever reaching the create/delete logic these tests exercise. There is
    no self-service role-change endpoint, so this updates the row
    directly via `db_session`, mirroring how `m365_connection_id` above
    seeds a connection row directly rather than through the API.
    `get_current_user` re-fetches the user from the DB on every request,
    so the change takes effect immediately -- no re-login required.
    """
    email, _ = registered_user
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.role = "auditor"
    await db_session.commit()


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


async def test_delete_nonexistent_scan_returns_404(auth_client, auditor_role):
    resp = await auth_client.delete("/v1/scans/999999")
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_delete_scan_requires_auth(client):
    resp = await client.delete("/v1/scans/1")
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_create_scan_nonexistent_connection_returns_404(auth_client, auditor_role):
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


async def test_create_scan_happy_path(
    auth_client, m365_connection_id, auditor_role, monkeypatch
):
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
    auth_client, m365_connection_id, auditor_role, monkeypatch
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


def _execute_returning(single=None, items=None, rows=None) -> MagicMock:
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = items or []
    scalars.one_or_none.return_value = single
    result.scalars.return_value = scalars
    result.unique.return_value = result
    result.scalar_one_or_none.return_value = single
    result.all.return_value = rows or []
    return result


def _scan(*, user_id: int = 1) -> Scan:
    now = datetime.utcnow()
    scan = Scan()
    scan.id = 7
    scan.user_id = user_id
    scan.m365_connection_id = 1
    scan.framework = "cis"
    scan.benchmark = "microsoft-365-foundations"
    scan.version = "v3.1.0"
    scan.status = "completed"
    scan.started_at = now
    scan.finished_at = now
    scan.compliance_score = Decimal("90.00")
    scan.total_controls = 2
    scan.passed_count = 1
    scan.failed_count = 1
    scan.skipped_count = 0
    scan.error_count = 0
    scan.indeterminate_count = 0
    scan.not_assessable_count = 0
    scan.results = []
    scan.m365_connection = None
    return scan


async def test_list_scans_supports_filters_and_safe_pagination(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    """Scan history supports filtering and bounded pagination."""

    scan = _scan(user_id=viewer_user.id)

    mock_db_session.execute = AsyncMock(
        return_value=_execute_returning(items=[scan])
    )

    async with client_factory(viewer_user) as client:
        response = await client.get(
            "/v1/scans/",
            params={
                "status": "completed",
                "framework": "cis",
                "benchmark": "microsoft-365-foundations",
                "limit": 10,
                "offset": 5,
            },
        )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "completed"

    mock_db_session.execute.assert_awaited_once()

    statement = mock_db_session.execute.await_args.args[0]

    sql = str(
        statement.compile(
            compile_kwargs={"literal_binds": True}
        )
    )

    assert "completed" in sql
    assert "cis" in sql
    assert "microsoft-365-foundations" in sql
    assert "LIMIT 10" in sql
    assert "OFFSET 5" in sql


@pytest.mark.parametrize(
    "params",
    [
        {"status": "invalid"},
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
    ],
)
async def test_list_scans_rejects_invalid_filter_parameters(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
    params: dict,
) -> None:
    """Invalid scan filtering parameters return validation errors."""

    async with client_factory(viewer_user) as client:
        response = await client.get(
            "/v1/scans/",
            params=params,
        )

    assert response.status_code == 422
    mock_db_session.execute.assert_not_awaited()

async def test_scan_result_status_check_constraint(db_session, registered_user):
    """The DB accepts the new statuses and rejects unknown ones; the worker
    writes with raw SQL, so this constraint is the only shared guard."""
    email, _ = registered_user
    result = await db_session.execute(select(User).where(User.email == email))
    scan = Scan(
        user_id=result.scalar_one().id,
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v6.0.0",
    )
    db_session.add(scan)
    await db_session.flush()

    db_session.add_all(
        [
            ScanResult(scan_id=scan.id, control_id="1.1.1", status="indeterminate"),
            ScanResult(scan_id=scan.id, control_id="1.1.2", status="not_assessable"),
        ]
    )
    await db_session.flush()

    db_session.add(ScanResult(scan_id=scan.id, control_id="1.1.3", status="unknown"))
    with pytest.raises(IntegrityError, match="ck_scan_result_status"):
        await db_session.flush()


async def _user_id_for(db_session, email: str) -> int:
    result = await db_session.execute(select(User).where(User.email == email))
    return result.scalar_one().id


async def _register_other_user(client, db_session) -> int:
    """Register a second, unrelated user and return their id."""
    email = f"other-{uuid.uuid4().hex}@example.com"
    resp = await client.post(
        "/v1/auth/register",
        json={"email": email, "password": "Sup3r-Secret-Test-Pw!"},  # pragma: allowlist secret
    )
    assert resp.status_code == 201, resp.text  # nosec B101
    return await _user_id_for(db_session, email)


async def _make_scan(
    db_session, user_id: int, results: list[tuple[str, str]] | None = None
) -> Scan:
    """Insert a scan owned by `user_id`, with (control_id, status) results."""
    scan = Scan(
        user_id=user_id,
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v6.0.0",
    )
    db_session.add(scan)
    await db_session.flush()
    for control_id, status_ in results or []:
        db_session.add(
            ScanResult(scan_id=scan.id, control_id=control_id, status=status_)
        )
    await db_session.flush()
    await db_session.refresh(scan)
    return scan


@pytest.mark.parametrize(
    "method, suffix",
    [("get", ""), ("get", "/summary"), ("get", "/results"), ("delete", "")],
)
async def test_other_users_scan_returns_404(
    auth_client, auditor_role, db_session, method, suffix
):
    """Scans are scoped to their owner: another user's scan must look like
    it doesn't exist (404), and a delete attempt must not delete it."""
    other_user_id = await _register_other_user(auth_client, db_session)
    scan = await _make_scan(db_session, other_user_id, [("1.1.1", "passed")])

    resp = await getattr(auth_client, method)(f"/v1/scans/{scan.id}{suffix}")

    assert resp.status_code == 404, resp.text  # nosec B101
    still_there = await db_session.execute(select(Scan).where(Scan.id == scan.id))
    assert still_there.scalar_one_or_none() is not None  # nosec B101


async def test_get_own_scan_returns_scan_with_results(
    auth_client, registered_user, db_session
):
    email, _ = registered_user
    user_id = await _user_id_for(db_session, email)
    scan = await _make_scan(
        db_session, user_id, [("1.1.1", "passed"), ("1.1.2", "failed")]
    )

    resp = await auth_client.get(f"/v1/scans/{scan.id}")

    assert resp.status_code == 200, resp.text  # nosec B101
    body = resp.json()
    assert body["id"] == scan.id  # nosec B101
    statuses = {r["control_id"]: r["status"] for r in body["results"]}
    assert statuses == {"1.1.1": "passed", "1.1.2": "failed"}  # nosec B101


async def test_delete_own_scan_removes_scan_and_results(
    auth_client, auditor_role, registered_user, db_session
):
    email, _ = registered_user
    user_id = await _user_id_for(db_session, email)
    scan = await _make_scan(
        db_session, user_id, [("1.1.1", "passed"), ("1.1.2", "failed")]
    )
    scan_id = scan.id

    resp = await auth_client.delete(f"/v1/scans/{scan_id}")

    assert resp.status_code == 204, resp.text  # nosec B101
    remaining_scan = await db_session.execute(select(Scan).where(Scan.id == scan_id))
    assert remaining_scan.scalar_one_or_none() is None  # nosec B101
    remaining_results = await db_session.execute(
        select(ScanResult).where(ScanResult.scan_id == scan_id)
    )
    assert remaining_results.scalars().all() == []  # nosec B101


async def test_summary_category_counts_include_all_statuses(
    auth_client, registered_user, db_session
):
    """The summary groups results by control category and counts every
    status, including indeterminate and not_assessable (added in #437).
    A pending result counts toward the category total but has no bucket."""
    email, _ = registered_user
    user_id = await _user_id_for(db_session, email)
    scan = await _make_scan(
        db_session,
        user_id,
        [
            ("1.1.1", "passed"),
            ("1.1.2", "failed"),
            ("1.2.1", "indeterminate"),
            ("2.1.1", "not_assessable"),
            ("2.1.2", "skipped"),
            ("2.1.3", "error"),
            ("3.1.1", "pending"),
        ],
    )

    resp = await auth_client.get(f"/v1/scans/{scan.id}/summary")

    assert resp.status_code == 200, resp.text  # nosec B101
    categories = {c["category"]: c for c in resp.json()["categories"]}
    assert sorted(categories) == ["1", "2", "3"]  # nosec B101

    one = categories["1"]
    assert (one["total"], one["passed"], one["failed"], one["indeterminate"]) == (  # nosec B101
        3, 1, 1, 1,
    )
    two = categories["2"]
    assert (  # nosec B101
        two["total"], two["not_assessable"], two["skipped"], two["error"]
    ) == (3, 1, 1, 1)
    three = categories["3"]
    assert three["total"] == 1  # nosec B101
    assert three["passed"] == three["failed"] == three["indeterminate"] == 0  # nosec B101


async def test_results_filter_by_status_and_ordering(
    auth_client, registered_user, db_session
):
    email, _ = registered_user
    user_id = await _user_id_for(db_session, email)
    scan = await _make_scan(
        db_session,
        user_id,
        [("1.1.3", "failed"), ("1.1.1", "passed"), ("1.1.2", "failed")],
    )

    everything = await auth_client.get(f"/v1/scans/{scan.id}/results")
    only_failed = await auth_client.get(
        f"/v1/scans/{scan.id}/results", params={"status_filter": "failed"}
    )

    assert everything.status_code == 200, everything.text  # nosec B101
    assert [r["control_id"] for r in everything.json()] == [  # nosec B101
        "1.1.1",
        "1.1.2",
        "1.1.3",
    ]
    assert only_failed.status_code == 200, only_failed.text  # nosec B101
    assert [r["control_id"] for r in only_failed.json()] == [  # nosec B101
        "1.1.2",
        "1.1.3",
    ]