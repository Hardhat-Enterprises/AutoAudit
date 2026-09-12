"""
Integration tests for the authentication endpoints (/v1/auth/*).

These exercise the real HTTP surface end-to-end -- registration, login,
the current-user dependency, profile updates, and password changes --
against a real (test) Postgres database, through the actual FastAPI app,
with nothing in the auth stack mocked. Only the transport is replaced
(httpx's ASGI transport talks to the app in-process instead of over a
socket); password hashing, JWT signing, cookie handling, and the SQL
queries are all the real thing.
"""


async def test_register_creates_user(client):
    import uuid

    email = f"test-{uuid.uuid4().hex}@example.com"
    resp = await client.post(
        "/v1/auth/register",
        json={"email": email, "password": "Sup3r-Secret-Test-Pw!"},  # nosec B105
    )
    assert resp.status_code == 201, resp.text  # nosec B101
    body = resp.json()
    assert body["email"] == email  # nosec B101
    assert body["role"] == "viewer"  # nosec B101


async def test_register_duplicate_email_rejected(client, registered_user):
    email, _ = registered_user
    resp = await client.post(
        "/v1/auth/register",
        json={"email": email, "password": "Another-Pw!23"},  # nosec B105
    )
    assert resp.status_code == 400, resp.text  # nosec B101


async def test_login_sets_httponly_cookie(client, registered_user):
    email, password = registered_user
    resp = await client.post(
        "/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert resp.status_code == 204, resp.text  # nosec B101
    assert "autoaudit_jwt" in resp.cookies  # nosec B101


async def test_login_rejects_wrong_password(client, registered_user):
    email, _ = registered_user
    resp = await client.post(
        "/v1/auth/login",
        data={"username": email, "password": "definitely-wrong"},  # nosec B105
    )
    assert resp.status_code == 400, resp.text  # nosec B101


async def test_get_current_user_requires_auth(client):
    resp = await client.get("/v1/auth/users/me")
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_get_current_user_returns_profile(auth_client, registered_user):
    email, _ = registered_user
    resp = await auth_client.get("/v1/auth/users/me")
    assert resp.status_code == 200, resp.text  # nosec B101
    assert resp.json()["email"] == email  # nosec B101


async def test_logout_clears_session(auth_client):
    resp = await auth_client.post("/v1/auth/logout")
    assert resp.status_code == 204, resp.text  # nosec B101
    resp = await auth_client.get("/v1/auth/users/me")
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_update_profile(auth_client):
    resp = await auth_client.patch(
        "/v1/auth/users/me",
        json={"first_name": "Pratiyush", "organization_name": "Hardhat"},
    )
    assert resp.status_code == 200, resp.text  # nosec B101
    body = resp.json()
    assert body["first_name"] == "Pratiyush"  # nosec B101
    assert body["organization_name"] == "Hardhat"  # nosec B101


async def test_change_password_wrong_current_password_rejected(auth_client):
    resp = await auth_client.post(
        "/v1/auth/users/me/change-password",
        json={"current_password": "not-the-real-password", "new_password": "New-Pw!234"},  # nosec B105
    )
    assert resp.status_code == 400, resp.text  # nosec B101


async def test_change_password_then_relogin(client, registered_user):
    email, old_password = registered_user
    login = await client.post("/v1/auth/login", data={"username": email, "password": old_password})
    assert login.status_code == 204, login.text  # nosec B101

    new_password = "Brand-New-Pw!456"  # nosec B105
    changed = await client.post(
        "/v1/auth/users/me/change-password",
        json={"current_password": old_password, "new_password": new_password},
    )
    assert changed.status_code == 200, changed.text  # nosec B101

    relog_old = await client.post("/v1/auth/login", data={"username": email, "password": old_password})
    assert relog_old.status_code == 400, relog_old.text  # nosec B101

    relog_new = await client.post("/v1/auth/login", data={"username": email, "password": new_password})
    assert relog_new.status_code == 204, relog_new.text  # nosec B101