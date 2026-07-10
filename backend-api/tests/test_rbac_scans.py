"""RBAC tests for scan mutation and read endpoints."""

import pytest

from tests.conftest import AUDITOR_FORBIDDEN_DETAIL

SCAN_CREATE_BODY = {
    "m365_connection_id": 1,
    "framework": "cis",
    "benchmark": "microsoft-365-foundations",
    "version": "v3.1.0",
}


@pytest.mark.asyncio
async def test_viewer_cannot_create_scan(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.post("/v1/scans/", json=SCAN_CREATE_BODY)

    assert response.status_code == 403
    assert response.json()["detail"] == AUDITOR_FORBIDDEN_DETAIL


@pytest.mark.asyncio
async def test_viewer_cannot_delete_scan(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.delete("/v1/scans/1")

    assert response.status_code == 403
    assert response.json()["detail"] == AUDITOR_FORBIDDEN_DETAIL


@pytest.mark.asyncio
async def test_viewer_can_list_scans(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.get("/v1/scans/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_viewer_can_get_scan_detail_not_found(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.get("/v1/scans/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Scan 1 not found"


@pytest.mark.asyncio
async def test_admin_passes_rbac_on_create_scan(client_factory, admin_user):
    async with client_factory(admin_user) as client:
        response = await client.post("/v1/scans/", json=SCAN_CREATE_BODY)

    assert response.status_code != 403
