"""Tests for /v1/platforms endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.models.platform import Platform
from app.models.user import User


def _execute_returning(items: list | None = None) -> MagicMock:
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = items or []
    scalars.one_or_none.return_value = None
    result.scalars.return_value = scalars
    result.unique.return_value = result
    result.scalar_one_or_none.return_value = None
    return result


def _platform(*, platform_id: int, name: str, active: bool) -> Platform:
    platform = Platform()
    platform.id = platform_id
    platform.name = name
    platform.display_name = name.upper()
    platform.is_active = active
    return platform


@pytest.mark.asyncio
async def test_list_active_platforms(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    active = _platform(platform_id=1, name="m365", active=True)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(items=[active]))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/platforms")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "m365"
    assert body[0]["is_active"] is True


@pytest.mark.asyncio
async def test_list_all_platforms(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    platforms = [
        _platform(platform_id=1, name="m365", active=True),
        _platform(platform_id=2, name="gcp", active=False),
    ]
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(items=platforms))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/platforms/all")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_list_platforms_unauthorized(client_factory) -> None:
    client: AsyncClient = client_factory(None)
    async with client:
        response = await client.get("/v1/platforms")

    assert response.status_code == 401
