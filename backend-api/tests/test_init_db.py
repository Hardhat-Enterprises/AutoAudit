"""Unit tests for local admin seed script (no live DB)."""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db import init_db as init_db_mod
from app.models.user import Role, User


def _session_cm(session: AsyncMock):
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=None)
    return cm


def _mock_session(*, existing: User | None) -> AsyncMock:
    session = AsyncMock()
    result = MagicMock()
    result.unique.return_value.scalar_one_or_none.return_value = existing
    session.execute = AsyncMock(return_value=result)
    session.commit = AsyncMock()
    session.add = MagicMock()
    return session


@contextmanager
def _patched_init(session: AsyncMock):
    with patch.object(
        init_db_mod, "async_session_maker", return_value=_session_cm(session)
    ):
        with patch.object(init_db_mod.PasswordHelper, "hash", return_value="hashed"):
            yield


@pytest.mark.asyncio
async def test_init_db_creates_admin_when_missing(capsys) -> None:
    session = _mock_session(existing=None)

    with _patched_init(session):
        await init_db_mod.init_db()

    session.add.assert_called_once()
    added = session.add.call_args[0][0]
    assert isinstance(added, User)
    assert added.email == "admin@example.com"
    assert added.role == Role.ADMIN.value
    assert added.hashed_password == "hashed"
    assert added.is_active is True
    assert added.is_superuser is True
    assert added.is_verified is True
    session.commit.assert_awaited_once()
    assert "Created default admin user" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_init_db_updates_existing_admin(capsys) -> None:
    existing = User(email="admin@example.com")
    existing.hashed_password = "old"
    existing.role = Role.VIEWER.value
    existing.is_active = False
    existing.is_superuser = False
    existing.is_verified = False

    session = _mock_session(existing=existing)

    with _patched_init(session):
        await init_db_mod.init_db()

    session.add.assert_not_called()
    assert existing.hashed_password == "hashed"
    assert existing.role == Role.ADMIN.value
    assert existing.is_active is True
    assert existing.is_superuser is True
    assert existing.is_verified is True
    session.commit.assert_awaited_once()
    assert "Updated default admin user" in capsys.readouterr().out
