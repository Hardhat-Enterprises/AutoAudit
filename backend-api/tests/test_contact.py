"""Tests for /v1/contact endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.models.contact import ContactSubmission
from app.models.user import User


VALID_PAYLOAD = {
    "first_name": "Ada",
    "last_name": "Lovelace",
    "email": "ada@example.com",
    "subject": "Question",
    "message": "How do I run a compliance scan?",
}


def _execute_returning(single=None, items: list | None = None) -> MagicMock:
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = items or []
    scalars.one_or_none.return_value = single
    result.scalars.return_value = scalars
    result.unique.return_value = result
    result.scalar_one_or_none.return_value = single
    return result


def _submission() -> ContactSubmission:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    submission = ContactSubmission(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        subject="Question",
        message="How do I run a compliance scan?",
    )
    submission.id = uuid4()
    submission.status = "new"
    submission.priority = "medium"
    submission.assigned_to = None
    submission.created_at = now
    submission.updated_at = now
    submission.resolved_at = None
    return submission


@pytest.mark.asyncio
async def test_create_contact_submission_public(
    client_factory,
    mock_db_session: AsyncMock,
) -> None:
    client: AsyncClient = client_factory(None)
    async with client:
        response = await client.post("/v1/contact/", json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == VALID_PAYLOAD["email"]
    assert body["status"] == "new"
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_create_contact_submission_validation_error(client_factory) -> None:
    client: AsyncClient = client_factory(None)
    async with client:
        response = await client.post(
            "/v1/contact/",
            json={
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "not-an-email",
                "subject": "Question",
                "message": "Hello",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_submissions_admin_ok(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    items = [_submission()]
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(items=items))

    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.get("/v1/contact/submissions")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["email"] == "ada@example.com"


@pytest.mark.asyncio
async def test_list_submissions_forbidden_for_viewer(
    client_factory,
    viewer_user: User,
) -> None:
    client: AsyncClient = client_factory(viewer_user)
    async with client:
        response = await client.get("/v1/contact/submissions")

    assert response.status_code == 403
