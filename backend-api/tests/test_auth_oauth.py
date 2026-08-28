"""Additional coverage for app/api/v1/auth.py (password change + Google OAuth)."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException, status
from httpx import AsyncClient

from app.api.v1.auth import (
    GOOGLE_OAUTH_STATE_COOKIE,
    _frontend_google_callback_url,
    _google_oauth_client,
    _google_redirect_uri,
)
from app.core.config import Settings
from app.core.users import get_user_manager
from app.models.user import User
from tests.conftest import test_app


def _oauth_settings(**overrides) -> Settings:
    data = {
        "GOOGLE_OAUTH_CLIENT_ID": "test-client-id",
        "GOOGLE_OAUTH_CLIENT_SECRET": "test-client-secret",
        "BACKEND_PUBLIC_URL": "http://localhost:8000",
        "FRONTEND_URL": "http://localhost:3000",
        "API_PREFIX": "/v1",
    }
    data.update(overrides)
    return Settings(**data)


# --- helpers -----------------------------------------------------------------


def test_google_redirect_uri() -> None:
    with patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()):
        assert _google_redirect_uri() == "http://localhost:8000/v1/auth/google/callback"


def test_frontend_google_callback_url() -> None:
    with patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()):
        url = _frontend_google_callback_url({"error": "invalid_state"})
    assert url.startswith("http://localhost:3000/auth/google/callback#")
    assert "error=invalid_state" in url


def test_google_oauth_client_requires_config() -> None:
    with patch(
        "app.api.v1.auth.get_settings",
        return_value=_oauth_settings(
            GOOGLE_OAUTH_CLIENT_ID="",
            GOOGLE_OAUTH_CLIENT_SECRET="",
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            _google_oauth_client()
    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_google_oauth_client_builds_client() -> None:
    with patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()):
        client = _google_oauth_client()
    assert client.name == "google"


# --- change password ---------------------------------------------------------


@pytest.mark.asyncio
async def test_change_password_success(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    mock_db_session.get = AsyncMock(return_value=viewer_user)
    password_helper = MagicMock()
    password_helper.verify_and_update.return_value = (True, None)
    password_helper.hash.return_value = "hashed-new-password"
    user_manager = MagicMock()
    user_manager.password_helper = password_helper

    async def fake_session() -> AsyncGenerator[AsyncMock, None]:
        yield mock_db_session

    async def fake_user_manager(_session) -> AsyncGenerator[MagicMock, None]:
        yield user_manager

    with (
        patch("app.db.session.get_async_session", fake_session),
        patch("app.core.users.get_user_manager", fake_user_manager),
    ):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.post(
                "/v1/auth/users/me/change-password",
                json={"current_password": "old", "new_password": "new-secret"},
            )

    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"
    assert viewer_user.hashed_password == "hashed-new-password"
    mock_db_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_change_password_wrong_current(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    mock_db_session.get = AsyncMock(return_value=viewer_user)
    password_helper = MagicMock()
    password_helper.verify_and_update.return_value = (False, None)
    user_manager = MagicMock()
    user_manager.password_helper = password_helper

    async def fake_session() -> AsyncGenerator[AsyncMock, None]:
        yield mock_db_session

    async def fake_user_manager(_session) -> AsyncGenerator[MagicMock, None]:
        yield user_manager

    with (
        patch("app.db.session.get_async_session", fake_session),
        patch("app.core.users.get_user_manager", fake_user_manager),
    ):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.post(
                "/v1/auth/users/me/change-password",
                json={"current_password": "wrong", "new_password": "new-secret"},
            )

    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_user_not_found(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
) -> None:
    mock_db_session.get = AsyncMock(return_value=None)

    async def fake_session() -> AsyncGenerator[AsyncMock, None]:
        yield mock_db_session

    with patch("app.db.session.get_async_session", fake_session):
        client: AsyncClient = client_factory(viewer_user)
        async with client:
            response = await client.post(
                "/v1/auth/users/me/change-password",
                json={"current_password": "old", "new_password": "new-secret"},
            )

    assert response.status_code == 404


# --- Google authorize --------------------------------------------------------


@pytest.mark.asyncio
async def test_google_authorize_not_configured(client_factory) -> None:
    with patch(
        "app.api.v1.auth.get_settings",
        return_value=_oauth_settings(
            GOOGLE_OAUTH_CLIENT_ID="",
            GOOGLE_OAUTH_CLIENT_SECRET="",
        ),
    ):
        client: AsyncClient = client_factory(None)
        async with client:
            response = await client.get("/v1/auth/google/authorize", follow_redirects=False)

    assert response.status_code == 302
    assert "error=oauth_not_configured" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_authorize_redirects_to_google(client_factory) -> None:
    mock_client = AsyncMock()
    mock_client.get_authorization_url = AsyncMock(
        return_value="https://accounts.google.com/o/oauth2/v2/auth?client_id=x"
    )

    with (
        patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()),
        patch("app.api.v1.auth._google_oauth_client", return_value=mock_client),
    ):
        client: AsyncClient = client_factory(None)
        async with client:
            response = await client.get("/v1/auth/google/authorize", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"].startswith("https://accounts.google.com/")
    assert GOOGLE_OAUTH_STATE_COOKIE in response.cookies


# --- Google callback ---------------------------------------------------------


@pytest.mark.asyncio
async def test_google_callback_invalid_state(client_factory) -> None:
    with patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()):
        client: AsyncClient = client_factory(None)
        async with client:
            response = await client.get(
                "/v1/auth/google/callback",
                params={"code": "abc", "state": "one"},
                cookies={GOOGLE_OAUTH_STATE_COOKIE: "two"},
                follow_redirects=False,
            )

    assert response.status_code == 302
    assert "error=invalid_state" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_missing_code(client_factory) -> None:
    with patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()):
        client: AsyncClient = client_factory(None)
        async with client:
            response = await client.get(
                "/v1/auth/google/callback",
                params={"state": "same"},
                cookies={GOOGLE_OAUTH_STATE_COOKIE: "same"},
                follow_redirects=False,
            )

    assert response.status_code == 302
    assert "error=missing_code" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_token_exchange_failed(
    client_factory,
    viewer_user: User,
) -> None:
    mock_client = AsyncMock()
    mock_client.get_access_token = AsyncMock(side_effect=RuntimeError("boom"))

    async def override_user_manager():
        yield MagicMock()

    test_app.dependency_overrides[get_user_manager] = override_user_manager
    try:
        with (
            patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()),
            patch("app.api.v1.auth._google_oauth_client", return_value=mock_client),
        ):
            client: AsyncClient = client_factory(None)
            async with client:
                response = await client.get(
                    "/v1/auth/google/callback",
                    params={"code": "abc", "state": "same"},
                    cookies={GOOGLE_OAUTH_STATE_COOKIE: "same"},
                    follow_redirects=False,
                )
    finally:
        test_app.dependency_overrides.pop(get_user_manager, None)

    assert response.status_code == 302
    assert "error=token_exchange_failed" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_userinfo_failed(
    client_factory,
) -> None:
    mock_client = AsyncMock()
    mock_client.get_access_token = AsyncMock(
        return_value={"access_token": "ya29.token", "expires_at": 123}
    )

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)
    mock_http.get = AsyncMock(side_effect=httpx.HTTPError("network"))

    async def override_user_manager():
        yield MagicMock()

    test_app.dependency_overrides[get_user_manager] = override_user_manager
    try:
        with (
            patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()),
            patch("app.api.v1.auth._google_oauth_client", return_value=mock_client),
            patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_http),
        ):
            client: AsyncClient = client_factory(None)
            async with client:
                response = await client.get(
                    "/v1/auth/google/callback",
                    params={"code": "abc", "state": "same"},
                    cookies={GOOGLE_OAUTH_STATE_COOKIE: "same"},
                    follow_redirects=False,
                )
    finally:
        test_app.dependency_overrides.pop(get_user_manager, None)

    assert response.status_code == 302
    assert "error=userinfo_failed" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_invalid_profile(
    client_factory,
) -> None:
    mock_client = AsyncMock()
    mock_client.get_access_token = AsyncMock(
        return_value={"access_token": "ya29.token", "expires_at": 123}
    )

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"email": "a@example.com"}  # missing sub

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)
    mock_http.get = AsyncMock(return_value=mock_resp)

    async def override_user_manager():
        yield MagicMock()

    test_app.dependency_overrides[get_user_manager] = override_user_manager
    try:
        with (
            patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()),
            patch("app.api.v1.auth._google_oauth_client", return_value=mock_client),
            patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_http),
        ):
            client: AsyncClient = client_factory(None)
            async with client:
                response = await client.get(
                    "/v1/auth/google/callback",
                    params={"code": "abc", "state": "same"},
                    cookies={GOOGLE_OAUTH_STATE_COOKIE: "same"},
                    follow_redirects=False,
                )
    finally:
        test_app.dependency_overrides.pop(get_user_manager, None)

    assert response.status_code == 302
    assert "error=invalid_profile" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_email_not_verified(
    client_factory,
) -> None:
    mock_client = AsyncMock()
    mock_client.get_access_token = AsyncMock(
        return_value={"access_token": "ya29.token", "expires_at": 123}
    )

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "email": "a@example.com",
        "sub": "google-sub",
        "email_verified": False,
    }

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)
    mock_http.get = AsyncMock(return_value=mock_resp)

    async def override_user_manager():
        yield MagicMock()

    test_app.dependency_overrides[get_user_manager] = override_user_manager
    try:
        with (
            patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()),
            patch("app.api.v1.auth._google_oauth_client", return_value=mock_client),
            patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_http),
        ):
            client: AsyncClient = client_factory(None)
            async with client:
                response = await client.get(
                    "/v1/auth/google/callback",
                    params={"code": "abc", "state": "same"},
                    cookies={GOOGLE_OAUTH_STATE_COOKIE: "same"},
                    follow_redirects=False,
                )
    finally:
        test_app.dependency_overrides.pop(get_user_manager, None)

    assert response.status_code == 302
    assert "error=email_not_verified" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_user_link_failed(
    client_factory,
) -> None:
    mock_client = AsyncMock()
    mock_client.get_access_token = AsyncMock(
        return_value={"access_token": "ya29.token", "expires_at": 123}
    )

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "email": "a@example.com",
        "sub": "google-sub",
        "email_verified": True,
    }

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)
    mock_http.get = AsyncMock(return_value=mock_resp)

    user_manager = MagicMock()
    user_manager.oauth_callback = AsyncMock(side_effect=RuntimeError("link failed"))

    async def override_user_manager():
        yield user_manager

    test_app.dependency_overrides[get_user_manager] = override_user_manager
    try:
        with (
            patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()),
            patch("app.api.v1.auth._google_oauth_client", return_value=mock_client),
            patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_http),
        ):
            client: AsyncClient = client_factory(None)
            async with client:
                response = await client.get(
                    "/v1/auth/google/callback",
                    params={"code": "abc", "state": "same"},
                    cookies={GOOGLE_OAUTH_STATE_COOKIE: "same"},
                    follow_redirects=False,
                )
    finally:
        test_app.dependency_overrides.pop(get_user_manager, None)

    assert response.status_code == 302
    assert "error=user_link_failed" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_success(
    client_factory,
    viewer_user: User,
) -> None:
    mock_client = AsyncMock()
    mock_client.get_access_token = AsyncMock(
        return_value={
            "access_token": "ya29.token",
            "expires_at": 123,
            "refresh_token": "refresh",
        }
    )

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "email": viewer_user.email,
        "sub": "google-sub-1",
        "email_verified": True,
    }

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=None)
    mock_http.get = AsyncMock(return_value=mock_resp)

    user_manager = MagicMock()
    user_manager.oauth_callback = AsyncMock(return_value=viewer_user)

    jwt_strategy = MagicMock()
    jwt_strategy.write_token = AsyncMock(return_value="jwt-access-token")

    async def override_user_manager():
        yield user_manager

    test_app.dependency_overrides[get_user_manager] = override_user_manager
    try:
        with (
            patch("app.api.v1.auth.get_settings", return_value=_oauth_settings()),
            patch("app.api.v1.auth._google_oauth_client", return_value=mock_client),
            patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_http),
            patch("app.api.v1.auth.get_jwt_strategy", return_value=jwt_strategy),
        ):
            client: AsyncClient = client_factory(None)
            async with client:
                response = await client.get(
                    "/v1/auth/google/callback",
                    params={"code": "abc", "state": "same"},
                    cookies={GOOGLE_OAUTH_STATE_COOKIE: "same"},
                    follow_redirects=False,
                )
    finally:
        test_app.dependency_overrides.pop(get_user_manager, None)

    assert response.status_code == 302
    location = response.headers["location"]
    assert "access_token=jwt-access-token" in location
    assert "token_type=bearer" in location
    user_manager.oauth_callback.assert_awaited()
