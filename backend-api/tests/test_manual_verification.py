"""Unit/API tests for manual verification endpoints (no live server required)."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

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


@pytest.mark.asyncio
async def test_get_nonexistent_returns_404(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/manual-verification/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_nonexistent_returns_404(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.patch(
            "/v1/manual-verification/99999",
            json={"comment": "x"},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_returns_404(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.delete("/v1/manual-verification/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_by_scan_result_nonexistent_returns_404(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/manual-verification/by-scan-result/99999")

    assert response.status_code == 404
