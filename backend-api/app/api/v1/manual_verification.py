"""Manual scan result detail API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.user import User
from app.models.manual_scan_result_detail import ManualScanResultDetail
from app.schemas.manual_scan_result_detail import (
    ManualScanResultDetailCreate,
    ManualScanResultDetailRead,
    ManualScanResultDetailUpdate,
)

router = APIRouter(prefix="/manual-verification", tags=["Manual Verification"])


@router.post("/", response_model=ManualScanResultDetailRead, status_code=status.HTTP_201_CREATED)
async def create_manual_verification(
    data: ManualScanResultDetailCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Submit a manual verification for a scan result."""
    detail = ManualScanResultDetail(
        scan_result_id=data.scan_result_id,
        user_id=current_user.id,
        comment=data.comment,
    )
    db.add(detail)
    await db.commit()
    await db.refresh(detail)
    return detail


@router.get("/{detail_id}", response_model=ManualScanResultDetailRead)
async def get_manual_verification(
    detail_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get a manual verification by ID."""
    result = await db.execute(
        select(ManualScanResultDetail).where(ManualScanResultDetail.id == detail_id)
    )
    detail = result.scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=404, detail="Manual verification not found")
    return detail


@router.get("/by-scan-result/{scan_result_id}", response_model=ManualScanResultDetailRead)
async def get_manual_verification_by_scan_result(
    scan_result_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get a manual verification by scan result ID."""
    result = await db.execute(
        select(ManualScanResultDetail).where(
            ManualScanResultDetail.scan_result_id == scan_result_id
        )
    )
    detail = result.scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=404, detail="Manual verification not found for this scan result")
    return detail


@router.patch("/{detail_id}", response_model=ManualScanResultDetailRead)
async def update_manual_verification(
    detail_id: int,
    update: ManualScanResultDetailUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Update a manual verification comment."""
    result = await db.execute(
        select(ManualScanResultDetail).where(ManualScanResultDetail.id == detail_id)
    )
    detail = result.scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=404, detail="Manual verification not found")

    if update.comment is not None:
        detail.comment = update.comment

    await db.commit()
    await db.refresh(detail)
    return detail


@router.delete("/{detail_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_manual_verification(
    detail_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Delete a manual verification."""
    result = await db.execute(
        select(ManualScanResultDetail).where(ManualScanResultDetail.id == detail_id)
    )
    detail = result.scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=404, detail="Manual verification not found")

    await db.delete(detail)
    await db.commit()