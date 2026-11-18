"""API tests for AWS connection endpoints: invalid input, missing resources and auth."""

import pytest
from pydantic import ValidationError
from app.schemas.aws_connection import AWSConnectionCreate

VALID_CREATE_BODY = {
    "name": "Test AWS",
    "account_id": "123456789012",
    "access_key_id": "test-access-key-id",
    "secret_access_key": "test-secret",  # pragma: allowlist secret
    "region": "us-east-1",
}


@pytest.mark.asyncio
async def test_get_nonexistent_connection_returns_404(client_factory, auditor_user):
    async with client_factory(auditor_user) as client:
        response = await client.get("/v1/aws-connections/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_connection_with_non_integer_id_returns_422(client_factory, auditor_user):
    async with client_factory(auditor_user) as client:
        response = await client.get("/v1/aws-connections/abc")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_nonexistent_connection_returns_404(client_factory, auditor_user):
    async with client_factory(auditor_user) as client:
        response = await client.put("/v1/aws-connections/99999", json={"name": "New name"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_connection_returns_404(client_factory, auditor_user):
    async with client_factory(auditor_user) as client:
        response = await client.delete("/v1/aws-connections/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_test_endpoint_nonexistent_connection_returns_404(client_factory, auditor_user):
    async with client_factory(auditor_user) as client:
        response = await client.post("/v1/aws-connections/99999/test")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "missing_field", ["name", "account_id", "access_key_id", "secret_access_key"]
)
async def test_create_connection_missing_required_field_returns_422(
    client_factory, auditor_user, missing_field
):
    body = {k: v for k, v in VALID_CREATE_BODY.items() if k != missing_field}
    async with client_factory(auditor_user) as client:
        response = await client.post("/v1/aws-connections/", json=body)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("name", ""),
        ("account_id", "123"),
        ("account_id", "1" * 21),
        ("access_key_id", ""),
        ("secret_access_key", ""),
        ("region", ""),
    ],
)
async def test_create_connection_invalid_value_returns_422(
    client_factory, auditor_user, field, bad_value
):
    body = {**VALID_CREATE_BODY, field: bad_value}
    async with client_factory(auditor_user) as client:
        response = await client.post("/v1/aws-connections/", json=body)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method, path, body",
    [
        ("get", "/v1/aws-connections/", None),
        ("get", "/v1/aws-connections/1", None),
        ("post", "/v1/aws-connections/", VALID_CREATE_BODY),
        ("put", "/v1/aws-connections/1", {"name": "x"}),
        ("delete", "/v1/aws-connections/1", None),
        ("post", "/v1/aws-connections/1/test", None),
    ],
)
async def test_aws_endpoints_require_authentication(client_factory, method, path, body):
    async with client_factory(None) as client:
        response = await getattr(client, method)(path, **({"json": body} if body else {}))
    assert response.status_code == 401

@pytest.mark.xfail(
    strict=True,
    reason="account_id is described as a 12-digit number but the schema only enforces length 12-20",
)
def test_account_id_must_be_numeric():
    with pytest.raises(ValidationError):
        AWSConnectionCreate(**{**VALID_CREATE_BODY, "account_id": "abcdefghijkl"})    