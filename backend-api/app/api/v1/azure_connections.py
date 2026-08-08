"""Azure Connection API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.azure_connection import AzureConnection
from app.models.user import User
from app.schemas.azure_connection import (
    AzureConnectionCreate,
    AzureConnectionRead,
    AzureConnectionTestResult,
    AzureConnectionUpdate,
)
from app.services.encryption import decrypt, encrypt

router = APIRouter(prefix="/azure-connections", tags=["Azure Connections"])


async def _get_user_connection(
    connection_id: int,
    user_id: int,
    db: AsyncSession,
) -> AzureConnection:
    """Fetch an Azure connection by ID scoped to the given user, or raise 404."""
    result = await db.execute(
        select(AzureConnection).where(
            AzureConnection.id == connection_id,
            AzureConnection.user_id == user_id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found",
        )
    return connection


@router.post("/", response_model=AzureConnectionRead, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_data: AzureConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> AzureConnection:
    """Create a new Azure connection for the current user."""
    connection = AzureConnection(
        user_id=current_user.id,
        name=connection_data.name,
        tenant_id=connection_data.tenant_id,
        client_id=connection_data.client_id,
        encrypted_client_secret=encrypt(connection_data.client_secret),
        subscription_id=connection_data.subscription_id,
    )
    db.add(connection)
    await db.commit()
    await db.refresh(connection)
    return connection


@router.get("/", response_model=list[AzureConnectionRead])
async def list_connections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> list[AzureConnection]:
    """List all Azure connections for the current user."""
    result = await db.execute(
        select(AzureConnection)
        .where(AzureConnection.user_id == current_user.id)
        .order_by(AzureConnection.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{connection_id}", response_model=AzureConnectionRead)
async def get_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> AzureConnection:
    """Get a specific Azure connection by ID."""
    return await _get_user_connection(connection_id, current_user.id, db)


@router.put("/{connection_id}", response_model=AzureConnectionRead)
async def update_connection(
    connection_id: int,
    update_data: AzureConnectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> AzureConnection:
    """Update an Azure connection."""
    connection = await _get_user_connection(connection_id, current_user.id, db)

    if update_data.name is not None:
        connection.name = update_data.name
    if update_data.tenant_id is not None:
        connection.tenant_id = update_data.tenant_id
    if update_data.client_id is not None:
        connection.client_id = update_data.client_id
    if update_data.client_secret is not None:
        connection.encrypted_client_secret = encrypt(update_data.client_secret)
    if update_data.subscription_id is not None:
        connection.subscription_id = update_data.subscription_id
    if update_data.is_active is not None:
        connection.is_active = update_data.is_active

    await db.commit()
    await db.refresh(connection)
    return connection


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    """Delete an Azure connection (hard delete)."""
    connection = await _get_user_connection(connection_id, current_user.id, db)
    await db.delete(connection)
    await db.commit()


@router.post("/{connection_id}/test", response_model=AzureConnectionTestResult)
async def test_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> AzureConnectionTestResult:
    """Test an Azure connection by verifying stored credentials."""
    connection = await _get_user_connection(connection_id, current_user.id, db)

    # Decrypt credentials — Azure SDK integration to be added for live validation
    _client_secret = decrypt(connection.encrypted_client_secret)

    return AzureConnectionTestResult(
        success=True,
        message="Azure connection credentials are stored. Live validation requires Azure SDK integration.",
        tenant_display_name=None,
    )
