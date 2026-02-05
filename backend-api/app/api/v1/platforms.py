"""Platform API endpoints for listing available platform types."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.platform import Platform
from app.models.user import User
from app.schemas.platform import PlatformRead

router = APIRouter(prefix="/platforms", tags=["Platforms"])


@router.get("", response_model=list[PlatformRead])
async def list_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> list[PlatformRead]:
    """List active platforms.

    Returns only platforms where is_active=True (currently only M365).
    """
    result = await db.execute(
        select(Platform).where(Platform.is_active == True).order_by(Platform.name)
    )
    return list(result.scalars().all())


@router.get("/all", response_model=list[PlatformRead])
async def list_all_platforms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> list[PlatformRead]:
    """List all platforms including inactive ones.

    Useful for showing which platforms will be supported in the future.
    """
    result = await db.execute(select(Platform).order_by(Platform.name))
    return list(result.scalars().all())
