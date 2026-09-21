from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.health import router as health_router
from app.db.session import get_async_session


health_app = FastAPI()
health_app.include_router(health_router)

client = TestClient(health_app)


class HealthySession:
    async def execute(self, statement):
        return None


class FailingSession:
    async def execute(self, statement):
        raise ConnectionError("Database unavailable")


async def healthy_session():
    yield HealthySession()


async def failing_session():
    yield FailingSession()


def test_readiness_when_database_available():
    health_app.dependency_overrides[get_async_session] = healthy_session

    try:
        response = client.get("/readiness")

        assert response.status_code == 200
        assert response.json() == {"status": "ready"}
    finally:
        health_app.dependency_overrides.clear()


def test_readiness_when_database_unavailable():
    health_app.dependency_overrides[get_async_session] = failing_session

    try:
        response = client.get("/readiness")

        assert response.status_code == 503
        assert response.json() == {"status": "not_ready"}
    finally:
        health_app.dependency_overrides.clear()