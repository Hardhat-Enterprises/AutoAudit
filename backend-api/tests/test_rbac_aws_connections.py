"""RBAC tests for AWS connection endpoints.

These mirror tests/test_rbac_m365_connections.py. The M365 endpoints require
auditor-or-above for create/update/delete/test and return 403 to viewers.
The AWS endpoints currently only require an authenticated user, so viewers
are not blocked. The tests describing the M365-consistent behaviour are marked
xfail(strict=True): they document the gap now, and will fail loudly (forcing
removal of the marker) once the endpoints enforce the role check.
"""

import pytest

from tests.conftest import AUDITOR_FORBIDDEN_DETAIL

CREATE_BODY = {
    "name": "Test AWS",
    "account_id": "123456789012",
    "access_key_id": "test-access-key-id",
    "secret_access_key": "test-secret",  # pragma: allowlist secret
    "region": "us-east-1",
}


@pytest.mark.xfail(
    strict=True,
    reason="AWS endpoints do not enforce auditor-or-above yet (M365 endpoints do)",
)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method, path, body",
    [
        ("post", "/v1/aws-connections/", CREATE_BODY),
        ("put", "/v1/aws-connections/1", {"name": "Updated"}),
        ("delete", "/v1/aws-connections/1", None),
        ("post", "/v1/aws-connections/1/test", None),
    ],
)
async def test_viewer_cannot_modify_aws_connections(
    client_factory, viewer_user, method, path, body
):
    async with client_factory(viewer_user) as client:
        response = await getattr(client, method)(path, **({"json": body} if body else {}))

    assert response.status_code == 403
    assert response.json()["detail"] == AUDITOR_FORBIDDEN_DETAIL


@pytest.mark.asyncio
async def test_viewer_can_list_aws_connections(client_factory, viewer_user):
    async with client_factory(viewer_user) as client:
        response = await client.get("/v1/aws-connections/")

    assert response.status_code == 200
    assert response.json() == []