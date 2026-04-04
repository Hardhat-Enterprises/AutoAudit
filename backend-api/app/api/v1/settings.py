"""User settings API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.user_settings import UserSettingsRead, UserSettingsUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])


async def _get_or_create_settings(
    db: AsyncSession,
    user_id: int,
) -> UserSettings:
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == user_id))
    settings = result.scalar_one_or_none()
    if settings:
        return settings

    settings = UserSettings(user_id=user_id)
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    return settings


@router.get("/", response_model=UserSettingsRead)
async def get_my_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> UserSettings:
    """Get settings for the current user (creates defaults on first access)."""
    return await _get_or_create_settings(db, current_user.id)


@router.patch("/", response_model=UserSettingsRead)
async def update_my_settings(
    update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> UserSettings:
    """Update settings for the current user."""
    settings = await _get_or_create_settings(db, current_user.id)

    if update.confirm_delete_enabled is not None:
        settings.confirm_delete_enabled = update.confirm_delete_enabled

    await db.commit()
    await db.refresh(settings)
    return settings

