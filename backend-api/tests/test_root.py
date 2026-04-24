async def test_root_returns_ok(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_public_endpoint_accessible(client):
    response = await client.get("/v1/test/public")
    assert response.status_code == 200
    assert response.json()["requires_auth"] is False


async def test_protected_endpoint_requires_auth(client):
    response = await client.get("/v1/test/protected")
    assert response.status_code == 401
