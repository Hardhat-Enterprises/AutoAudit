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

#Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


#Fake users
def make_user(id: int, email: str) -> User:
    user = User.__new__(User)
    user.id = id
    user.email = email
    user.role = Role.ADMIN
    user.is_active = True
    user.is_superuser = False
    user.is_verified = True
    user.hashed_password = "fake"
    return user


user_a = make_user(1, "alice@test.com")
user_b = make_user(2, "bob@test.com")
current_test_user = user_a


#Dependency overrides
async def override_get_session():
    async with TestSession() as session:
        yield session


async def override_get_current_user():
    return current_test_user


app.dependency_overrides[get_async_session] = override_get_session
app.dependency_overrides[get_current_user] = override_get_current_user


#Fixtures
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
        scan = Scan(
            m365_connection_id=1,
            status="completed",
            benchmark_id="cis-m365-v6",
        )
        session.add(scan)
        await session.commit()
        await session.refresh(scan)

        scan_result = ScanResult(
            scan_id=scan.id,
            control_id="1.1.2",
            status="pending",
        )
        session.add(scan_result)
        await session.commit()
        await session.refresh(scan_result)

        # Create a second scan_result for duplicate tests
        scan_result_2 = ScanResult(
            scan_id=scan.id,
            control_id="1.1.3",
            status="pending",
        )
        session.add(scan_result_2)
        await session.commit()
        await session.refresh(scan_result_2)

        return scan_result.id, scan_result_2.id


@pytest.fixture
def client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )


#Tests

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
                "comment": "First verification",
            })
            response = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id,
                "comment": "Duplicate attempt",
            })
        assert response.status_code in (409, 500)  # unique constraint violation


class TestGetManualVerification:
    """Tests for GET /v1/manual-verification/{detail_id}"""

    @pytest.mark.asyncio
    async def test_get_own_record(self, client, seed_scan):
        scan_result_id, _ = await seed_scan
        async with client as c:
            create_resp = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id,
                "comment": "Test",
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

        # Create as user_a
        current_test_user = user_a
        async with client as c:
            create_resp = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id,
                "comment": "Alice's verification",
            })
            detail_id = create_resp.json()["id"]

        # Try to read as user_b
        current_test_user = user_b
        async with client as c:
            response = await c.get(f"/v1/manual-verification/{detail_id}")
        assert response.status_code == 403

        current_test_user = user_a  # reset


class TestUpdateManualVerification:
    """Tests for PATCH /v1/manual-verification/{detail_id}"""

    @pytest.mark.asyncio
    async def test_update_own_comment(self, client, seed_scan):
        scan_result_id, _ = await seed_scan
        async with client as c:
            create_resp = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id,
                "comment": "Original comment",
            })
            detail_id = create_resp.json()["id"]
            response = await c.patch(f"/v1/manual-verification/{detail_id}", json={
                "comment": "Updated comment",
            })
        assert response.status_code == 200
        assert response.json()["comment"] == "Updated comment"

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_404(self, client):
        async with client as c:
            response = await c.patch("/v1/manual-verification/99999", json={
                "comment": "Doesn't matter",
            })
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_other_users_record_returns_403(self, client, seed_scan):
        global current_test_user
        scan_result_id, _ = await seed_scan

        # Create as user_a
        current_test_user = user_a
        async with client as c:
            create_resp = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id,
                "comment": "Alice's verification",
            })
            detail_id = create_resp.json()["id"]

        # Try to update as user_b
        current_test_user = user_b
        async with client as c:
            response = await c.patch(f"/v1/manual-verification/{detail_id}", json={
                "comment": "Bob trying to edit",
            })
        assert response.status_code == 403

        current_test_user = user_a  # reset


class TestDeleteManualVerification:
    """Tests for DELETE /v1/manual-verification/{detail_id}"""

    @pytest.mark.asyncio
    async def test_delete_own_record(self, client, seed_scan):
        scan_result_id, _ = await seed_scan
        async with client as c:
            create_resp = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id,
                "comment": "To be deleted",
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

        # Create as user_a
        current_test_user = user_a
        async with client as c:
            create_resp = await c.post("/v1/manual-verification/", json={
                "scan_result_id": scan_result_id,
                "comment": "Alice's verification",
            })
            detail_id = create_resp.json()["id"]

        # Try to delete as user_b
        current_test_user = user_b
        async with client as c:
            response = await c.delete(f"/v1/manual-verification/{detail_id}")
        assert response.status_code == 403

        current_test_user = user_a  # reset