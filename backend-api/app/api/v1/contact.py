"""Contact Us API endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_admin
from app.db.session import get_async_session
from app.models.contact import ContactSubmission, SubmissionHistory, SubmissionNote
from app.models.user import User
from app.schemas.contact import (
    ContactSubmissionCreate,
    ContactSubmissionRead,
    ContactSubmissionUpdate,
    SubmissionHistoryRead,
    SubmissionNoteCreate,
    SubmissionNoteRead,
)

router = APIRouter(prefix="/contact", tags=["Contact"])


def _build_history_entry(
    submission_id: UUID,
    admin_user_id: int | None,
    action: str,
    field_name: str | None,
    old_value: str | None,
    new_value: str | None,
) -> SubmissionHistory:
    return SubmissionHistory(
        submission_id=submission_id,
        admin_user_id=admin_user_id,
        action=action,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
    )


@router.post("/", response_model=ContactSubmissionRead, status_code=status.HTTP_201_CREATED)
async def create_contact_submission(
    payload: ContactSubmissionCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> ContactSubmission:
    """Create a new Contact Us submission (public)."""
    submission = ContactSubmission(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        company=payload.company,
        subject=payload.subject,
        message=payload.message,
        source=payload.source,
        ip_address=request.client.host if request.client else None,
    )
    db.add(submission)
    await db.flush()
    db.add(
        _build_history_entry(
            submission_id=submission.id,
            admin_user_id=None,
            action="create",
            field_name=None,
            old_value=None,
            new_value=None,
        )
    )
    await db.commit()
    await db.refresh(submission)
    return submission


@router.get("/submissions", response_model=list[ContactSubmissionRead])
async def list_submissions(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> list[ContactSubmission]:
    """List all contact submissions (admin only)."""
    result = await db.execute(
        select(ContactSubmission).order_by(ContactSubmission.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/submissions/{submission_id}", response_model=ContactSubmissionRead)
async def get_submission(
    submission_id: UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> ContactSubmission:
    """Get a single submission (admin only)."""
    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return submission


@router.patch("/submissions/{submission_id}", response_model=ContactSubmissionRead)
async def update_submission(
    submission_id: UUID,
    payload: ContactSubmissionUpdate,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> ContactSubmission:
    """Update a submission (admin only)."""
    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    history_entries: list[SubmissionHistory] = []

    def track_change(field: str, old: str | None, new: str | None) -> None:
        if old != new:
            history_entries.append(
                _build_history_entry(
                    submission_id=submission.id,
                    admin_user_id=admin_user.id,
                    action="update",
                    field_name=field,
                    old_value=old,
                    new_value=new,
                )
            )

    if "status" in payload.__fields_set__:
        if payload.status is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="status cannot be null")
        track_change("status", submission.status, payload.status)
        submission.status = payload.status
        if payload.status.lower() == "resolved" and submission.resolved_at is None:
            submission.resolved_at = datetime.utcnow()

    if "priority" in payload.__fields_set__:
        if payload.priority is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="priority cannot be null")
        track_change("priority", submission.priority, payload.priority)
        submission.priority = payload.priority

    if "assigned_to" in payload.__fields_set__:
        if payload.assigned_to is not None:
            user_result = await db.execute(
                select(User).where(User.id == payload.assigned_to)
            )
            assigned_user = user_result.scalar_one_or_none()
            if not assigned_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="assigned_to user not found",
                )
        track_change(
            "assigned_to",
            str(submission.assigned_to) if submission.assigned_to is not None else None,
            str(payload.assigned_to) if payload.assigned_to is not None else None,
        )
        submission.assigned_to = payload.assigned_to

    if "resolved_at" in payload.__fields_set__:
        track_change(
            "resolved_at",
            submission.resolved_at.isoformat() if submission.resolved_at else None,
            payload.resolved_at.isoformat() if payload.resolved_at else None,
        )
        submission.resolved_at = payload.resolved_at

    for entry in history_entries:
        db.add(entry)

    await db.commit()
    await db.refresh(submission)
    return submission


@router.delete("/submissions/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission(
    submission_id: UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    """Delete a submission (admin only)."""
    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    await db.delete(submission)
    await db.commit()


@router.get("/submissions/{submission_id}/notes", response_model=list[SubmissionNoteRead])
async def list_notes(
    submission_id: UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> list[SubmissionNote]:
    result = await db.execute(
        select(SubmissionNote)
        .where(SubmissionNote.submission_id == submission_id)
        .order_by(SubmissionNote.created_at.desc())
    )
    return list(result.scalars().all())


@router.post(
    "/submissions/{submission_id}/notes",
    response_model=SubmissionNoteRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_note(
    submission_id: UUID,
    payload: SubmissionNoteCreate,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> SubmissionNote:
    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    note = SubmissionNote(
        submission_id=submission_id,
        admin_user_id=admin_user.id,
        note=payload.note,
        is_internal=payload.is_internal,
    )
    db.add(note)
    db.add(
        _build_history_entry(
            submission_id=submission_id,
            admin_user_id=admin_user.id,
            action="note",
            field_name="note",
            old_value=None,
            new_value=payload.note,
        )
    )
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/submissions/{submission_id}/history", response_model=list[SubmissionHistoryRead])
async def list_history(
    submission_id: UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> list[SubmissionHistory]:
    result = await db.execute(
        select(SubmissionHistory)
        .where(SubmissionHistory.submission_id == submission_id)
        .order_by(SubmissionHistory.created_at.desc())
    )
    return list(result.scalars().all())
