import pytest

REGISTER_PAYLOAD = {"email": "test@example.com", "password": "TestPassword123!"}
LOGIN_FORM = {"username": "test@example.com", "password": "TestPassword123!"}


async def _register_and_login(client):
    await client.post("/v1/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post(
        "/v1/auth/login",
        data=LOGIN_FORM,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()["access_token"]


async def test_register_creates_user(client):
    response = await client.post("/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]


async def test_register_duplicate_email_rejected(client):
    await client.post("/v1/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post("/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 400


async def test_login_returns_access_token(client):
    await client.post("/v1/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post(
        "/v1/auth/login",
        data=LOGIN_FORM,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password_rejected(client):
    await client.post("/v1/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post(
        "/v1/auth/login",
        data={"username": REGISTER_PAYLOAD["email"], "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400


async def test_me_without_token_returns_401(client):
    response = await client.get("/v1/auth/users/me")
    assert response.status_code == 401


async def test_me_with_valid_token_returns_user(client):
    token = await _register_and_login(client)
    response = await client.get(
        "/v1/auth/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]


async def test_protected_endpoint_with_token(client):
    token = await _register_and_login(client)
    response = await client.get(
        "/v1/test/protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["requires_auth"] is True


async def test_admin_endpoint_returns_403_for_viewer(client):
    token = await _register_and_login(client)
    response = await client.get(
        "/v1/test/protected-admin",
        headers={"Authorization": f"Bearer {token}"},
    )
    # Default role is viewer (admin endpoint should deny)
    assert response.status_code == 403
