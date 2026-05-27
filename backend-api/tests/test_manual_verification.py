"""Integration tests for manual verification endpoints."""
import httpx

BASE = "http://localhost:8000/v1"


def token():
    r = httpx.post(
        f"{BASE}/auth/login",
        data={"username": "admin@example.com", "password": "admin"},
        timeout=10,
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth(t):
    return {"Authorization": f"Bearer {t}"}


def test_get_nonexistent_returns_404():
    t = token()
    r = httpx.get(f"{BASE}/manual-verification/99999", headers=auth(t))
    assert r.status_code == 404, r.text


def test_patch_nonexistent_returns_404():
    t = token()
    r = httpx.patch(
        f"{BASE}/manual-verification/99999",
        json={"comment": "x"},
        headers=auth(t),
    )
    assert r.status_code == 404, r.text


def test_delete_nonexistent_returns_404():
    t = token()
    r = httpx.delete(f"{BASE}/manual-verification/99999", headers=auth(t))
    assert r.status_code == 404, r.text


def test_get_by_scan_result_nonexistent_returns_404():
    t = token()
    r = httpx.get(
        f"{BASE}/manual-verification/by-scan-result/99999",
        headers=auth(t),
    )
    assert r.status_code == 404, r.text