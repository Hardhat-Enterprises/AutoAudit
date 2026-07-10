"""RBAC tests for M365 connection mutation and read endpoints."""

import pytest

from tests.conftest import AUDITOR_FORBIDDEN_DETAIL

CONNECTION_CREATE_BODY = {
    "name": "Test Connection",
    "tenant_id": "00000000-0000-0000-0000-000000000001",
    "client_id": "00000000-0000-0000-0000-000000000002",
    "client_secret": "secret",
}

CONNECTION_UPDATE_BODY = {"name": "Updated Connection"}


@pytest.mark.asyncio
async def test_viewer_cannot_create_connection(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.post("/v1/m365-connections/", json=CONNECTION_CREATE_BODY)

    assert response.status_code == 403
    assert response.json()["detail"] == AUDITOR_FORBIDDEN_DETAIL


@pytest.mark.asyncio
async def test_viewer_cannot_update_connection(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.put(
            "/v1/m365-connections/1",
            json=CONNECTION_UPDATE_BODY,
        )

    assert response.status_code == 403
    assert response.json()["detail"] == AUDITOR_FORBIDDEN_DETAIL


@pytest.mark.asyncio
async def test_viewer_cannot_delete_connection(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.delete("/v1/m365-connections/1")

    assert response.status_code == 403
    assert response.json()["detail"] == AUDITOR_FORBIDDEN_DETAIL


@pytest.mark.asyncio
async def test_viewer_cannot_test_connection(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.post("/v1/m365-connections/1/test")

    assert response.status_code == 403
    assert response.json()["detail"] == AUDITOR_FORBIDDEN_DETAIL


@pytest.mark.asyncio
async def test_viewer_can_list_connections(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.get("/v1/m365-connections/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_viewer_can_get_connection_not_found(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.get("/v1/m365-connections/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Connection 1 not found"


@pytest.mark.asyncio
async def test_admin_passes_rbac_on_update_connection(client_factory, admin_user):
    async with client_factory(admin_user) as client:
        response = await client.put(
            "/v1/m365-connections/1",
            json=CONNECTION_UPDATE_BODY,
        )

    assert response.status_code != 403
