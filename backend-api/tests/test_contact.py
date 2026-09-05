"""Tests for /v1/contact endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.models.contact import ContactSubmission, SubmissionHistory, SubmissionNote
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


def _submission(**overrides) -> ContactSubmission:
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
    for key, value in overrides.items():
        setattr(submission, key, value)
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


@pytest.mark.asyncio
async def test_get_submission_ok(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    submission = _submission()
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=submission))

    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.get(f"/v1/contact/submissions/{submission.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(submission.id)


@pytest.mark.asyncio
async def test_get_submission_not_found(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.get(f"/v1/contact/submissions/{uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_submission_status_to_resolved(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    submission = _submission()
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=submission))

    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.patch(
            f"/v1/contact/submissions/{submission.id}",
            json={"status": "resolved", "priority": "high"},
        )

    assert response.status_code == 200
    assert submission.status == "resolved"
    assert submission.priority == "high"
    assert submission.resolved_at is not None
    mock_db_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_update_submission_clears_resolved_at(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    submission = _submission(status="resolved", resolved_at=now)
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=submission))

    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.patch(
            f"/v1/contact/submissions/{submission.id}",
            json={"status": "open"},
        )

    assert response.status_code == 200
    assert submission.status == "open"
    assert submission.resolved_at is None


@pytest.mark.asyncio
async def test_update_submission_not_found(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.patch(
            f"/v1/contact/submissions/{uuid4()}",
            json={"status": "open"},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_submission_ok(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    submission = _submission()
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=submission))

    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.delete(f"/v1/contact/submissions/{submission.id}")

    assert response.status_code == 204
    mock_db_session.delete.assert_awaited()
    mock_db_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_delete_submission_not_found(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.delete(f"/v1/contact/submissions/{uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_and_add_notes(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    submission = _submission()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    note = SubmissionNote(
        submission_id=submission.id,
        admin_user_id=admin_user.id,
        note="Follow up",
        is_internal=True,
    )
    note.id = uuid4()
    note.created_at = now
    note.updated_at = now

    mock_db_session.execute = AsyncMock(
        side_effect=[
            _execute_returning(items=[note]),  # list_notes
            _execute_returning(single=submission),  # add_note lookup
        ]
    )

    client: AsyncClient = client_factory(admin_user)
    async with client:
        listed = await client.get(f"/v1/contact/submissions/{submission.id}/notes")
        assert listed.status_code == 200
        assert listed.json()[0]["note"] == "Follow up"

        created = await client.post(
            f"/v1/contact/submissions/{submission.id}/notes",
            json={"note": "New note", "is_internal": False},
        )

    assert created.status_code == 201
    assert created.json()["note"] == "New note"
    mock_db_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_add_note_submission_not_found(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.post(
            f"/v1/contact/submissions/{uuid4()}/notes",
            json={"note": "Missing", "is_internal": True},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_history(
    client_factory,
    mock_db_session: AsyncMock,
    admin_user: User,
) -> None:
    submission = _submission()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    history = SubmissionHistory(
        submission_id=submission.id,
        admin_user_id=admin_user.id,
        action="update",
        field_name="status",
        old_value="new",
        new_value="open",
    )
    history.id = uuid4()
    history.created_at = now
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(items=[history]))

    client: AsyncClient = client_factory(admin_user)
    async with client:
        response = await client.get(f"/v1/contact/submissions/{submission.id}/history")

    assert response.status_code == 200
    assert response.json()[0]["action"] == "update"
