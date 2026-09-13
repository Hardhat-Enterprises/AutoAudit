"""API tests for scan endpoints beyond RBAC smoke checks."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.models.compliance import Scan
from app.models.m365_connection import M365Connection
from app.models.scan_result import ScanResult
from app.models.user import User
from app.services.scan_readiness import ReadinessCheck, ReadinessResult


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
    scan.results = []
    scan.m365_connection = None
    return scan


def _connection(*, user_id: int = 1) -> M365Connection:
    conn = M365Connection()
    conn.id = 1
    conn.user_id = user_id
    conn.name = "Prod"
    conn.tenant_id = "tenant"
    conn.client_id = "client"
    conn.encrypted_client_secret = "enc"
    conn.is_active = True
    return conn


CREATE_BODY = {
    "m365_connection_id": 1,
    "framework": "cis",
    "benchmark": "microsoft-365-foundations",
    "version": "v3.1.0",
    "control_ids": ["CIS-1.1.1"],
}


@pytest.mark.asyncio
async def test_create_scan_success(
    client_factory, mock_db_session: AsyncMock, auditor_user: User
) -> None:
    conn = _connection(user_id=auditor_user.id)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=conn))

    reader = MagicMock()
    reader.list_controls.return_value = [
        {"control_id": "CIS-1.1.1"},
        {"control_id": "CIS-1.1.2"},
    ]
    reader.get_benchmark_metadata.return_value = {"platform": "m365"}
    task = MagicMock()
    task.id = "task-1"

    with patch("app.api.v1.scans.get_file_reader", return_value=reader), patch(
        "app.api.v1.scans.queue_scan", return_value=task
    ):
        client: AsyncClient = client_factory(auditor_user)
        async with client:
            response = await client.post("/v1/scans/", json=CREATE_BODY)

    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    assert "task-1" in response.json()["message"]


@pytest.mark.asyncio
async def test_create_scan_connection_missing(
    client_factory, mock_db_session: AsyncMock, auditor_user: User
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))
    client: AsyncClient = client_factory(auditor_user)
    async with client:
        response = await client.post("/v1/scans/", json=CREATE_BODY)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_scan_benchmark_errors(
    client_factory, mock_db_session: AsyncMock, auditor_user: User
) -> None:
    conn = _connection(user_id=auditor_user.id)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=conn))

    reader = MagicMock()
    reader.list_controls.side_effect = FileNotFoundError("missing")
    with patch("app.api.v1.scans.get_file_reader", return_value=reader):
        async with client_factory(auditor_user) as client:
            missing = await client.post("/v1/scans/", json=CREATE_BODY)
    assert missing.status_code == 404

    reader = MagicMock()
    reader.list_controls.return_value = [{"control_id": "CIS-1.1.1"}]
    reader.get_benchmark_metadata.return_value = {"platform": "aws"}
    with patch("app.api.v1.scans.get_file_reader", return_value=reader):
        async with client_factory(auditor_user) as client:
            bad_platform = await client.post("/v1/scans/", json=CREATE_BODY)
    assert bad_platform.status_code == 400


@pytest.mark.asyncio
async def test_get_summary_results_delete_and_readiness(
    client_factory, mock_db_session: AsyncMock, auditor_user: User
) -> None:
    scan = _scan(user_id=auditor_user.id)
    conn = _connection(user_id=auditor_user.id)

    result_rows = [("CIS-1.1.1", "passed"), ("CIS-1.1.2", "failed")]
    scan_results = [ScanResult()]
    scan_results[0].id = 1
    scan_results[0].scan_id = 7
    scan_results[0].control_id = "CIS-1.1.1"
    scan_results[0].status = "passed"
    scan_results[0].message = None
    scan_results[0].evidence = None
    scan_results[0].created_at = datetime.utcnow()
    scan_results[0].updated_at = datetime.utcnow()

    readiness = ReadinessResult(
        ready=True,
        summary="Ready to start scan.",
        required_permissions=["User.Read.All"],
        missing_permissions=[],
        unverified_permissions=[],
        checks=[
            ReadinessCheck(
                key="connection_auth",
                label="auth",
                status="pass",
                severity="critical",
                message="ok",
            )
        ],
    )

    mock_db_session.execute = AsyncMock(
        side_effect=[
            _execute_returning(single=scan),  # get scan
            _execute_returning(single=scan),  # summary scan
            _execute_returning(rows=result_rows),  # summary rows
            _execute_returning(single=scan),  # results ownership
            _execute_returning(items=scan_results),  # results list
            _execute_returning(single=scan),  # delete lookup
            _execute_returning(),  # delete results
            _execute_returning(single=conn),  # readiness connection
        ]
    )

    reader = MagicMock()
    reader.get_benchmark_metadata.return_value = {
        "platform": "m365",
        "controls": [
            {
                "automation_status": "ready",
                "requires_permissions": ["User.Read.All"],
            }
        ],
    }

    with patch("app.api.v1.scans.get_file_reader", return_value=reader), patch(
        "app.api.v1.scans.decrypt", return_value="secret"
    ), patch(
        "app.api.v1.scans.evaluate_scan_readiness",
        new=AsyncMock(return_value=readiness),
    ):
        client: AsyncClient = client_factory(auditor_user)
        async with client:
            detail = await client.get("/v1/scans/7")
            summary = await client.get("/v1/scans/7/summary")
            results = await client.get("/v1/scans/7/results")
            deleted = await client.delete("/v1/scans/7")
            ready = await client.get(
                "/v1/scans/readiness",
                params={
                    "m365_connection_id": 1,
                    "framework": "cis",
                    "benchmark": "microsoft-365-foundations",
                    "version": "v3.1.0",
                },
            )

    assert detail.status_code == 200
    assert summary.status_code == 200
    assert summary.json()["categories"]
    assert results.status_code == 200
    assert deleted.status_code == 204
    assert ready.status_code == 200
    assert ready.json()["ready"] is True
