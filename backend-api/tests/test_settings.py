"""Tests for /v1/settings user preferences."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.models.user import User
from app.models.user_settings import UserSettings


def _settings(*, user_id: int = 1, confirm_delete_enabled: bool = True) -> UserSettings:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    settings = UserSettings(
        user_id=user_id,
        confirm_delete_enabled=confirm_delete_enabled,
    )
    settings.id = 10
    settings.created_at = now
    settings.updated_at = now
    return settings


def _execute_returning(single=None, items: list | None = None) -> MagicMock:
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = items or []
    scalars.one_or_none.return_value = single
    result.scalars.return_value = scalars
    result.unique.return_value = result
    result.scalar_one_or_none.return_value = single
    return result


@pytest.mark.asyncio
async def test_get_settings_creates_defaults(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/settings/")

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == viewer_user.id
    assert body["confirm_delete_enabled"] is True
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_get_settings_returns_existing(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    existing = _settings(user_id=viewer_user.id, confirm_delete_enabled=False)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=existing))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/settings/")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == existing.id
    assert body["confirm_delete_enabled"] is False
    mock_db_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_update_settings(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    existing = _settings(user_id=viewer_user.id, confirm_delete_enabled=True)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=existing))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.patch(
            "/v1/settings/",
            json={"confirm_delete_enabled": False},
        )

    assert response.status_code == 200
    assert response.json()["confirm_delete_enabled"] is False
    assert existing.confirm_delete_enabled is False
    mock_db_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_get_settings_unauthorized(client_factory) -> None:
    client: AsyncClient = client_factory(None)
    async with client:
        response = await client.get("/v1/settings/")

    assert response.status_code == 401
