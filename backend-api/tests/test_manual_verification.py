"""Expanded API tests for manual verification endpoints."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from app.models.compliance import Scan
from app.models.manual_scan_result_detail import ManualScanResultDetail
from app.models.scan_result import ScanResult
from app.models.user import User


def _execute_returning(single=None) -> MagicMock:
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = []
    scalars.one_or_none.return_value = single
    result.scalars.return_value = scalars
    result.unique.return_value = result
    result.scalar_one_or_none.return_value = single
    return result


def _detail(*, user_id: int = 1, comment: str = "ok") -> ManualScanResultDetail:
    now = datetime.utcnow()
    detail = ManualScanResultDetail()
    detail.id = 10
    detail.scan_result_id = 5
    detail.user_id = user_id
    detail.comment = comment
    detail.created_at = now
    detail.updated_at = now
    return detail


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("get", "/v1/manual-verification/99999", None),
        ("patch", "/v1/manual-verification/99999", {"comment": "x"}),
        ("delete", "/v1/manual-verification/99999", None),
        ("get", "/v1/manual-verification/by-scan-result/99999", None),
    ],
)
async def test_nonexistent_returns_404(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
    method: str,
    path: str,
    json_body: dict | None,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        kwargs = {"json": json_body} if json_body is not None else {}
        response = await getattr(client, method)(path, **kwargs)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_forbidden_for_other_user(
    client_factory, mock_db_session: AsyncMock, viewer_user: User
) -> None:
    mock_db_session.execute = AsyncMock(
        return_value=_execute_returning(single=_detail(user_id=99))
    )
    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/manual-verification/10")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_and_by_scan_result_ok(
    client_factory, mock_db_session: AsyncMock, viewer_user: User
) -> None:
    detail = _detail(user_id=viewer_user.id)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=detail))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        by_id = await client.get("/v1/manual-verification/10")
        by_scan = await client.get("/v1/manual-verification/by-scan-result/5")

    assert by_id.status_code == 200
    assert by_id.json()["comment"] == "ok"
    assert by_scan.status_code == 200
    assert by_scan.json()["scan_result_id"] == 5


@pytest.mark.asyncio
async def test_patch_and_delete_ok(
    client_factory, mock_db_session: AsyncMock, viewer_user: User
) -> None:
    detail = _detail(user_id=viewer_user.id)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=detail))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        patched = await client.patch(
            "/v1/manual-verification/10", json={"comment": "updated"}
        )
        deleted = await client.delete("/v1/manual-verification/10")

    assert patched.status_code == 200
    assert detail.comment == "updated"
    assert deleted.status_code == 204
    mock_db_session.delete.assert_awaited()


@pytest.mark.asyncio
async def test_create_paths(
    client_factory, mock_db_session: AsyncMock, viewer_user: User
) -> None:
    scan_result = ScanResult()
    scan_result.id = 5
    scan_result.scan_id = 1

    owned_scan = Scan()
    owned_scan.id = 1
    owned_scan.user_id = viewer_user.id

    foreign_scan = Scan()
    foreign_scan.id = 1
    foreign_scan.user_id = 99

    # 404 when scan result missing
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))
    client: AsyncClient = client_factory(viewer_user)
    async with client:
        missing = await client.post(
            "/v1/manual-verification/",
            json={"scan_result_id": 5, "comment": "x"},
        )
    assert missing.status_code == 404

    # 403 when scan owned by someone else
    mock_db_session.execute = AsyncMock(
        side_effect=[
            _execute_returning(single=scan_result),
            _execute_returning(single=foreign_scan),
        ]
    )
    async with client_factory(viewer_user) as client:
        forbidden = await client.post(
            "/v1/manual-verification/",
            json={"scan_result_id": 5, "comment": "x"},
        )
    assert forbidden.status_code == 403

    # 201 happy path
    mock_db_session.execute = AsyncMock(
        side_effect=[
            _execute_returning(single=scan_result),
            _execute_returning(single=owned_scan),
        ]
    )
    async with client_factory(viewer_user) as client:
        created = await client.post(
            "/v1/manual-verification/",
            json={"scan_result_id": 5, "comment": "verified"},
        )
    assert created.status_code == 201
    assert created.json()["scan_result_id"] == 5

    # 409 on IntegrityError
    mock_db_session.execute = AsyncMock(
        side_effect=[
            _execute_returning(single=scan_result),
            _execute_returning(single=owned_scan),
        ]
    )
    mock_db_session.commit = AsyncMock(side_effect=IntegrityError("stmt", {}, None))
    async with client_factory(viewer_user) as client:
        conflict = await client.post(
            "/v1/manual-verification/",
            json={"scan_result_id": 5, "comment": "dup"},
        )
    assert conflict.status_code == 409
