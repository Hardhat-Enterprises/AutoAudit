"""Tests for manual verification CRUD endpoints."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.db.base import Base
from app.db.session import get_async_session
from app.core.auth import get_current_user
from app.models.user import User, Role
from app.models.scan_result import ScanResult
from app.models.compliance import Scan
from app.models.manual_scan_result_detail import ManualScanResultDetail
from app.main import app

# ── Test database setup ──
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ── Fake users ──
def _make_user(user_id: int, email: str) -> User:
    user = object.__new__(User)
    user.id = user_id
    user.email = email
    user.role = Role.ADMIN
    user.is_active = True
    user.is_superuser = False
    user.is_verified = True
    user.hashed_password = "fake"
    return user


user_a = _make_user(1, "alice@test.com")
user_b = _make_user(2, "bob@test.com")
current_test_user = user_a


# ── Dependency overrides ──
async def override_get_session():
    async with TestSession() as session:
        yield session


async def override_get_current_user():
    return current_test_user


app.dependency_overrides[get_async_session] = override_get_session
app.dependency_overrides[get_current_user] = override_get_current_user


# ── Fixtures ──
@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def seed_scan():
    """Create a scan and scan_result for testing."""
    async with TestSession() as session:
        scan = Scan(m365_connection_id=1, status="completed", benchmark_id="cis-m365-v6")
        session.add(scan)
        await session.commit()
        await session.refresh(scan)

        sr1 = ScanResult(scan_id=scan.id, control_id="1.1.2", status="pending")
        session.add(sr1)
        await session.commit()
        await session.refresh(sr1)

        sr2 = ScanResult(scan_id=scan.id, control_id="1.1.3", status="pending")
        session.add(sr2)
        await session.commit()
        await session.refresh(sr2)

        return sr1.id, sr2.id


@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ── Helper to create a verification as a specific user ──
async def _create_as_user(http_client, scan_result_id: int, user: User, comment: str = "Test"):
    """Create a manual verification record as a given user."""
    global current_test_user
    current_test_user = user
    async with http_client as c:
        resp = await c.post("/v1/manual-verification/", json={
            "scan_result_id": scan_result_id,
            "comment": comment,
        })
    return resp


# ── Tests ──

class TestCreateManualVerification:
    """Tests for POST /v1/manual-verification/"""

    @pytest.mark.asyncio
    async def test_create_success(self, client, seed_scan):
        scan_result_id, _ = await seed_scan
        async with client as c:
            response = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id,
                "comment": "Verified in Entra ID admin center",
            })
        assert response.status_code == 201
        data = response.json()
        assert data["scan_result_id"] == scan_result_id
        assert data["user_id"] == user_a.id
        assert data["comment"] == "Verified in Entra ID admin center"

    @pytest.mark.asyncio
    async def test_create_duplicate_scan_result_rejected(self, client, seed_scan):
        scan_result_id, _ = await seed_scan
        async with client as c:
            await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id,
                "comment": "First",
            })
            response = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id,
                "comment": "Duplicate",
            })
        assert response.status_code in (409, 500)


class TestGetManualVerification:
    """Tests for GET /v1/manual-verification/{detail_id}"""

    @pytest.mark.asyncio
    async def test_get_own_record(self, client, seed_scan):
        scan_result_id, _ = await seed_scan
        async with client as c:
            create_resp = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id, "comment": "Test",
            })
            detail_id = create_resp.json()["id"]
            response = await c.get(f"/v1/manual-verification/{detail_id}")
        assert response.status_code == 200
        assert response.json()["id"] == detail_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_404(self, client):
        async with client as c:
            response = await c.get("/v1/manual-verification/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_other_users_record_returns_403(self, client, seed_scan):
        global current_test_user
        scan_result_id, _ = await seed_scan
        resp = await _create_as_user(client, scan_result_id, user_a, "Alice's record")
        detail_id = resp.json()["id"]
        current_test_user = user_b
        new_client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        async with new_client as c:
            response = await c.get(f"/v1/manual-verification/{detail_id}")
        assert response.status_code == 403
        current_test_user = user_a


class TestUpdateManualVerification:
    """Tests for PATCH /v1/manual-verification/{detail_id}"""

    @pytest.mark.asyncio
    async def test_update_own_comment(self, client, seed_scan):
        scan_result_id, _ = await seed_scan
        async with client as c:
            create_resp = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id, "comment": "Original",
            })
            detail_id = create_resp.json()["id"]
            response = await c.patch(f"/v1/manual-verification/{detail_id}", json={
                "comment": "Updated",
            })
        assert response.status_code == 200
        assert response.json()["comment"] == "Updated"

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_404(self, client):
        async with client as c:
            response = await c.patch("/v1/manual-verification/99999", json={"comment": "X"})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_other_users_record_returns_403(self, client, seed_scan):
        global current_test_user
        scan_result_id, _ = await seed_scan
        resp = await _create_as_user(client, scan_result_id, user_a, "Alice's record")
        detail_id = resp.json()["id"]
        current_test_user = user_b
        new_client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        async with new_client as c:
            response = await c.patch(f"/v1/manual-verification/{detail_id}", json={"comment": "Bob"})
        assert response.status_code == 403
        current_test_user = user_a


class TestDeleteManualVerification:
    """Tests for DELETE /v1/manual-verification/{detail_id}"""

    @pytest.mark.asyncio
    async def test_delete_own_record(self, client, seed_scan):
        scan_result_id, _ = await seed_scan
        async with client as c:
            create_resp = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id, "comment": "To delete",
            })
            detail_id = create_resp.json()["id"]
            response = await c.delete(f"/v1/manual-verification/{detail_id}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_404(self, client):
        async with client as c:
            response = await c.delete("/v1/manual-verification/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_other_users_record_returns_403(self, client, seed_scan):
        global current_test_user
        scan_result_id, _ = await seed_scan
        resp = await _create_as_user(client, scan_result_id, user_a, "Alice's record")
        detail_id = resp.json()["id"]
        current_test_user = user_b
        new_client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        async with new_client as c:
            response = await c.delete(f"/v1/manual-verification/{detail_id}")
        assert response.status_code == 403
        current_test_user = user_a