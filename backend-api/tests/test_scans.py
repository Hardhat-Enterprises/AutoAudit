"""Integration tests for the scan API endpoints (/v1/scans/*).

Covers auth-gating and 404/not-found behaviour across the whole router.
Deliberately does NOT exercise the create_scan happy path (that needs a
real M365Connection row -- itself needing a valid, encrypted client
secret -- plus benchmark metadata files on disk and a live Celery
worker to pick the task up) or any endpoint that depends on scan results
actually existing. Those are integration surfaces worth covering
separately, with their own fixtures, once this suite's fixture set grows
enough to support them cheaply.
"""


async def test_list_scans_requires_auth(client):
    resp = await client.get("/v1/scans/")
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_list_scans_empty_for_new_user(auth_client):
    """A freshly registered user has created no scans yet."""
    resp = await auth_client.get("/v1/scans/")
    assert resp.status_code == 200, resp.text  # nosec B101
    assert resp.json() == []  # nosec B101


async def test_get_scan_requires_auth(client):
    resp = await client.get("/v1/scans/1")
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_get_nonexistent_scan_returns_404(auth_client):
    resp = await auth_client.get("/v1/scans/999999")
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_get_scan_summary_nonexistent_returns_404(auth_client):
    resp = await auth_client.get("/v1/scans/999999/summary")
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_get_scan_results_nonexistent_returns_404(auth_client):
    resp = await auth_client.get("/v1/scans/999999/results")
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_delete_nonexistent_scan_returns_404(auth_client):
    resp = await auth_client.delete("/v1/scans/999999")
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_delete_scan_requires_auth(client):
    resp = await client.delete("/v1/scans/1")
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_create_scan_nonexistent_connection_returns_404(auth_client):
    """The connection ownership/existence check must run (and fail
    loudly) before any benchmark lookup or Celery task is queued."""
    resp = await auth_client.post(
        "/v1/scans/",
        json={
            "m365_connection_id": 999999,
            "framework": "cis",
            "benchmark": "microsoft-365-foundations",
            "version": "v6.0.0",
        },
    )
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_create_scan_requires_auth(client):
    resp = await client.post(
        "/v1/scans/",
        json={
            "m365_connection_id": 1,
            "framework": "cis",
            "benchmark": "microsoft-365-foundations",
            "version": "v6.0.0",
        },
    )
    assert resp.status_code == 401, resp.text  # nosec B101


async def test_readiness_nonexistent_connection_returns_404(auth_client):
    resp = await auth_client.get(
        "/v1/scans/readiness",
        params={
            "m365_connection_id": 999999,
            "framework": "cis",
            "benchmark": "microsoft-365-foundations",
            "version": "v6.0.0",
        },
    )
    assert resp.status_code == 404, resp.text  # nosec B101


async def test_readiness_requires_auth(client):
    resp = await client.get(
        "/v1/scans/readiness",
        params={
            "m365_connection_id": 1,
            "framework": "cis",
            "benchmark": "microsoft-365-foundations",
            "version": "v6.0.0",
        },
    )
    assert resp.status_code == 401, resp.text  # nosec B101
