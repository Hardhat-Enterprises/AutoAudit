"""Integration tests for the manual-verification endpoints.

Rewritten to run in-process against the ASGI app via the shared
`auth_client` fixture (see conftest.py) instead of raw synchronous
`httpx` calls against a live server on localhost:8000. The previous
version assumed a server was already running outside pytest and posted
to `/auth/login` expecting a JSON `access_token` body -- but the app's
real auth backend is cookie-based (fastapi-users `CookieTransport`),
so login actually returns `204 No Content` with a `Set-Cookie` header,
never a JSON access token. Whatever was listening on port 8000 during a
manual run of the old file also 303-redirected to `/en-US/v1/auth/login`
(most likely a stray frontend dev server, not the backend at all) --
another sign this file was never actually exercised against the current
auth system. Routing it through the same in-process `auth_client` used
by test_auth.py removes the live-server dependency entirely, which is
also required for this suite to run unattended in CI.
"""


async def test_get_nonexistent_returns_404(auth_client):
    resp = await auth_client.get("/v1/manual-verification/99999")
    assert resp.status_code == 404, resp.text


async def test_patch_nonexistent_returns_404(auth_client):
    resp = await auth_client.patch(
        "/v1/manual-verification/99999",
        json={"comment": "x"},
    )
    assert resp.status_code == 404, resp.text


async def test_delete_nonexistent_returns_404(auth_client):
    resp = await auth_client.delete("/v1/manual-verification/99999")
    assert resp.status_code == 404, resp.text


async def test_get_by_scan_result_nonexistent_returns_404(auth_client):
    resp = await auth_client.get("/v1/manual-verification/by-scan-result/99999")
    assert resp.status_code == 404, resp.text


async def test_endpoints_require_auth(client):
    """Without a logged-in session, every route in this router should
    reject with 401 rather than leaking a 404 (which would happen if
    auth were silently skipped and the lookup just failed to find the
    record)."""
    get_resp = await client.get("/v1/manual-verification/99999")
    assert get_resp.status_code == 401, get_resp.text

    patch_resp = await client.patch(
        "/v1/manual-verification/99999",
        json={"comment": "x"},
    )
    assert patch_resp.status_code == 401, patch_resp.text

    delete_resp = await client.delete("/v1/manual-verification/99999")
    assert delete_resp.status_code == 401, delete_resp.text
