"""CRUD endpoints for ControlVerificationTemplate.

Powers the manual control verification workflow: admins maintain the
templates that auditors see when verifying pending manual controls.

Authorisation:
- POST / PATCH / DELETE: admin only (templates are GRC content; auditors
  consume them but do not author them).
- GET endpoints: any authenticated user (auditors and viewers need read
  access to surface instructions in the UI).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.permissions import require_admin
from app.db.session import get_async_session
from app.models.control_verification_template import ControlVerificationTemplate
from app.models.user import User
from app.schemas.control_verification_template import (
    ControlVerificationTemplateCreate,
    ControlVerificationTemplateRead,
    ControlVerificationTemplateUpdate,
)

router = APIRouter(
    prefix="/verification-templates",
    tags=["Verification Templates"],
)


@router.post(
    "/",
    response_model=ControlVerificationTemplateRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a verification template (admin only)",
)
async def create_template(
    data: ControlVerificationTemplateCreate,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(require_admin),
) -> ControlVerificationTemplate:
    """Create a new verification template for a manual control.

    Returns 409 Conflict if a template for the given control_id already exists.
    """
    result = await db.execute(
        select(ControlVerificationTemplate).where(
            ControlVerificationTemplate.control_id == data.control_id
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Template for control_id '{data.control_id}' already exists",
        )

    template = ControlVerificationTemplate(**data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.get(
    "/",
    response_model=list[ControlVerificationTemplateRead],
    summary="List all verification templates",
)
async def list_templates(
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(get_current_user),
) -> list[ControlVerificationTemplate]:
    """List every verification template, ordered by control_id."""
    result = await db.execute(
        select(ControlVerificationTemplate).order_by(
            ControlVerificationTemplate.control_id
        )
    )
    return list(result.scalars().all())


@router.get(
    "/{control_id}",
    response_model=ControlVerificationTemplateRead,
    summary="Get a verification template by control_id",
)
async def get_template(
    control_id: str,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(get_current_user),
) -> ControlVerificationTemplate:
    """Fetch the verification template for the given control_id."""
    result = await db.execute(
        select(ControlVerificationTemplate).where(
            ControlVerificationTemplate.control_id == control_id
        )
    )
    template = result.scalar_one_or_none()
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template for control_id '{control_id}' not found",
        )
    return template


@router.patch(
    "/{control_id}",
    response_model=ControlVerificationTemplateRead,
    summary="Partially update a verification template (admin only)",
)
async def update_template(
    control_id: str,
    data: ControlVerificationTemplateUpdate,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(require_admin),
) -> ControlVerificationTemplate:
    """Partially update a template. Only fields provided in the body are applied."""
    result = await db.execute(
        select(ControlVerificationTemplate).where(
            ControlVerificationTemplate.control_id == control_id
        )
    )
    template = result.scalar_one_or_none()
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template for control_id '{control_id}' not found",
        )

    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)
    return template


@router.delete(
    "/{control_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a verification template (admin only)",
)
async def delete_template(
    control_id: str,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(require_admin),
) -> None:
    """Delete the verification template for the given control_id."""
    result = await db.execute(
        select(ControlVerificationTemplate).where(
            ControlVerificationTemplate.control_id == control_id
        )
    )
    template = result.scalar_one_or_none()
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template for control_id '{control_id}' not found",
        )

    await db.delete(template)
    await db.commit()