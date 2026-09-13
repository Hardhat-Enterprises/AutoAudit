"""CRUD endpoints for ControlVerificationTemplate.
 
Powers the manual control verification workflow: admins maintain the
templates that auditors see when verifying pending manual controls.
 
Identity:
    Each template is uniquely identified by the
    (framework, benchmark, version, control_id) tuple. This matches the
    same tuple Scan already uses (see app/api/v1/scans.py) so the lookup
    pattern is consistent end-to-end and the same control_id can carry
    different instructions across benchmark versions and across frameworks.
 
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
 
 
# ── Internal helpers ────────────────────────────────────────────────────
 
 
async def _get_template_or_404(
    db: AsyncSession,
    framework: str,
    benchmark: str,
    version: str,
    control_id: str,
) -> ControlVerificationTemplate:
    """Fetch the template for the given tuple or raise 404."""
    result = await db.execute(
        select(ControlVerificationTemplate).where(
            ControlVerificationTemplate.framework == framework,
            ControlVerificationTemplate.benchmark == benchmark,
            ControlVerificationTemplate.version == version,
            ControlVerificationTemplate.control_id == control_id,
        )
    )
    template = result.scalar_one_or_none()
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Template for {framework}/{benchmark}/{version}/{control_id} not found"
            ),
        )
    return template
 
 
# ── Endpoints ───────────────────────────────────────────────────────────
 
 
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
 
    Returns 409 Conflict if a template for the given
    (framework, benchmark, version, control_id) tuple already exists.
    """
    result = await db.execute(
        select(ControlVerificationTemplate).where(
            ControlVerificationTemplate.framework == data.framework,
            ControlVerificationTemplate.benchmark == data.benchmark,
            ControlVerificationTemplate.version == data.version,
            ControlVerificationTemplate.control_id == data.control_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Template for {data.framework}/{data.benchmark}/"
                f"{data.version}/{data.control_id} already exists"
            ),
        )
 
    template = ControlVerificationTemplate(**data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template
 
 
@router.get(
    "/",
    response_model=list[ControlVerificationTemplateRead],
    summary="List verification templates",
)
async def list_templates(
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(get_current_user),
    framework: str | None = None,
    benchmark: str | None = None,
    version: str | None = None,
) -> list[ControlVerificationTemplate]:
    """List verification templates, optionally filtered by framework/benchmark/version.
 
    Sorted by (framework, benchmark, version, control_id) so output is stable
    across calls. Phase 2 seeding scripts can pass the tuple to fetch only
    the templates for a single benchmark version.
    """
    query = select(ControlVerificationTemplate)
    if framework is not None:
        query = query.where(ControlVerificationTemplate.framework == framework)
    if benchmark is not None:
        query = query.where(ControlVerificationTemplate.benchmark == benchmark)
    if version is not None:
        query = query.where(ControlVerificationTemplate.version == version)
    query = query.order_by(
        ControlVerificationTemplate.framework,
        ControlVerificationTemplate.benchmark,
        ControlVerificationTemplate.version,
        ControlVerificationTemplate.control_id,
    )
 
    result = await db.execute(query)
    return list(result.scalars().all())
 
 
@router.get(
    "/{framework}/{benchmark}/{version}/{control_id}",
    response_model=ControlVerificationTemplateRead,
    summary="Get a verification template by (framework, benchmark, version, control_id)",
)
async def get_template(
    framework: str,
    benchmark: str,
    version: str,
    control_id: str,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(get_current_user),
) -> ControlVerificationTemplate:
    """Fetch the verification template for the given tuple."""
    return await _get_template_or_404(db, framework, benchmark, version, control_id)
 
 
@router.patch(
    "/{framework}/{benchmark}/{version}/{control_id}",
    response_model=ControlVerificationTemplateRead,
    summary="Partially update a verification template (admin only)",
)
async def update_template(
    framework: str,
    benchmark: str,
    version: str,
    control_id: str,
    data: ControlVerificationTemplateUpdate,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(require_admin),
) -> ControlVerificationTemplate:
    """Partially update a template. Only fields provided in the body are applied.
 
    Explicit null values for non-nullable fields are rejected by the schema
    validator (422), not allowed through to the DB.
    """
    template = await _get_template_or_404(db, framework, benchmark, version, control_id)
 
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(template, field, value)
 
    await db.commit()
    await db.refresh(template)
    return template
 
 
@router.delete(
    "/{framework}/{benchmark}/{version}/{control_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a verification template (admin only)",
)
async def delete_template(
    framework: str,
    benchmark: str,
    version: str,
    control_id: str,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(require_admin),
) -> None:
    """Delete the verification template for the given tuple."""
    template = await _get_template_or_404(db, framework, benchmark, version, control_id)
    await db.delete(template)
    await db.commit()