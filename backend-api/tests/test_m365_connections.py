"""API tests for M365 connection endpoints beyond RBAC smoke checks."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.models.m365_connection import M365Connection
from app.models.user import User
from app.services.m365_graph import M365ConnectionError, TenantDetails


def _execute_returning(single=None, items=None) -> MagicMock:
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = items or []
    scalars.one_or_none.return_value = single
    result.scalars.return_value = scalars
    result.unique.return_value = result
    result.scalar_one_or_none.return_value = single
    return result


def _connection(*, user_id: int = 2) -> M365Connection:
    now = datetime.utcnow()
    conn = M365Connection()
    conn.id = 1
    conn.user_id = user_id
    conn.name = "Prod"
    conn.tenant_id = "tenant"
    conn.client_id = "client"
    conn.encrypted_client_secret = "enc"
    conn.is_active = True
    conn.created_at = now
    conn.updated_at = now
    return conn


CREATE_BODY = {
    "name": "Prod",
    "tenant_id": "tenant",
    "client_id": "client",
    "client_secret": "secret",
}


@pytest.mark.asyncio
async def test_create_connection_validation_error(
    client_factory, mock_db_session: AsyncMock, auditor_user: User
) -> None:
    with patch(
        "app.api.v1.m365_connections.validate_m365_connection",
        new=AsyncMock(side_effect=M365ConnectionError("invalid")),
    ):
        client: AsyncClient = client_factory(auditor_user)
        async with client:
            response = await client.post("/v1/m365-connections/", json=CREATE_BODY)
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid"


@pytest.mark.asyncio
async def test_create_connection_success(
    client_factory, mock_db_session: AsyncMock, auditor_user: User
) -> None:
    with patch(
        "app.api.v1.m365_connections.validate_m365_connection",
        new=AsyncMock(return_value=None),
    ), patch("app.api.v1.m365_connections.encrypt", return_value="enc"):
        client: AsyncClient = client_factory(auditor_user)
        async with client:
            response = await client.post("/v1/m365-connections/", json=CREATE_BODY)
    assert response.status_code == 201
    assert response.json()["name"] == "Prod"


@pytest.mark.asyncio
async def test_get_update_delete_and_test_connection(
    client_factory, mock_db_session: AsyncMock, auditor_user: User
) -> None:
    conn = _connection(user_id=auditor_user.id)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=conn))

    details = TenantDetails(
        tenant_display_name="Contoso",
        default_domain="contoso.com",
        verified_domains=["contoso.com"],
    )

    with patch("app.api.v1.m365_connections.decrypt", return_value="secret"), patch(
        "app.api.v1.m365_connections.validate_m365_connection",
        new=AsyncMock(return_value=details),
    ), patch("app.api.v1.m365_connections.encrypt", return_value="enc2"):
        client: AsyncClient = client_factory(auditor_user)
        async with client:
            got = await client.get("/v1/m365-connections/1")
            updated = await client.put(
                "/v1/m365-connections/1",
                json={"name": "Renamed", "client_secret": "new"},
            )
            tested = await client.post("/v1/m365-connections/1/test")
            deleted = await client.delete("/v1/m365-connections/1")

    assert got.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["name"] == "Renamed"
    assert tested.status_code == 200
    assert tested.json()["success"] is True
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_test_connection_failure_result(
    client_factory, mock_db_session: AsyncMock, auditor_user: User
) -> None:
    conn = _connection(user_id=auditor_user.id)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=conn))

    with patch("app.api.v1.m365_connections.decrypt", return_value="secret"), patch(
        "app.api.v1.m365_connections.validate_m365_connection",
        new=AsyncMock(side_effect=M365ConnectionError("nope")),
    ):
        client: AsyncClient = client_factory(auditor_user)
        async with client:
            response = await client.post("/v1/m365-connections/1/test")

    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["message"] == "nope"


@pytest.mark.asyncio
async def test_update_requires_secret_when_ids_change(
    client_factory, mock_db_session: AsyncMock, auditor_user: User
) -> None:
    conn = _connection(user_id=auditor_user.id)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=conn))

    client: AsyncClient = client_factory(auditor_user)
    async with client:
        response = await client.put(
            "/v1/m365-connections/1",
            json={"tenant_id": "new-tenant"},
        )
    assert response.status_code == 400
