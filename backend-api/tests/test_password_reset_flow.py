"""Tests for the password reset flow (BE-JN-002).

Covers two things this change introduced:
1. The reset password endpoints are registered on the auth router.
2. The reset token is never written to logs outside a development environment.
"""

import logging
from unittest.mock import AsyncMock

import pytest

from app.api.v1 import auth
from app.core import users as users_module
from app.core.users import UserManager
from tests.conftest import make_user


def _auth_paths() -> set[str]:
    return {getattr(route, "path", None) for route in auth.router.routes}


def test_forgot_password_endpoint_registered():
    assert "/auth/forgot-password" in _auth_paths()


def test_reset_password_endpoint_registered():
    assert "/auth/reset-password" in _auth_paths()


@pytest.mark.asyncio
async def test_reset_token_not_logged_outside_dev(monkeypatch, caplog):
    monkeypatch.setattr(users_module.settings, "APP_ENV", "production", raising=False)
    manager = UserManager(AsyncMock())
    user = make_user(role="admin")

    with caplog.at_level(logging.INFO, logger="api"):
        await manager.on_after_forgot_password(user, "SECRET_TOKEN_VALUE")

    messages = " ".join(record.getMessage() for record in caplog.records)
    assert "SECRET_TOKEN_VALUE" not in messages
    assert "Password reset requested" in messages


@pytest.mark.asyncio
async def test_reset_token_logged_only_in_dev(monkeypatch, caplog):
    monkeypatch.setattr(users_module.settings, "APP_ENV", "dev", raising=False)
    manager = UserManager(AsyncMock())
    user = make_user(role="admin")

    with caplog.at_level(logging.INFO, logger="api"):
        await manager.on_after_forgot_password(user, "DEV_TOKEN_VALUE")

    messages = " ".join(record.getMessage() for record in caplog.records)
    assert "DEV_TOKEN_VALUE" in messages
