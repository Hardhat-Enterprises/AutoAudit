"""M365 Connection API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.user import User
from app.models.m365_connection import M365Connection
from app.schemas.m365_connection import (
    M365ConnectionCreate,
    M365ConnectionRead,
    M365ConnectionUpdate,
    M365ConnectionTestResult,
)
from app.services.encryption import encrypt, decrypt
from app.services.m365_graph import M365ConnectionError, validate_m365_connection

router = APIRouter(prefix="/m365-connections", tags=["M365 Connections"])


@router.post("/", response_model=M365ConnectionRead, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_data: M365ConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> M365Connection:
    """Create a new M365 connection for the current user."""
    # Validate credentials before saving
    try:
        await validate_m365_connection(
            tenant_id=connection_data.tenant_id,
            client_id=connection_data.client_id,
            client_secret=connection_data.client_secret,
        )
    except M365ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    connection = M365Connection(
        user_id=current_user.id,
        name=connection_data.name,
        tenant_id=connection_data.tenant_id,
        client_id=connection_data.client_id,
        encrypted_client_secret=encrypt(connection_data.client_secret),
    )
    db.add(connection)
    await db.commit()
    await db.refresh(connection)
    return connection


@router.get("/", response_model=list[M365ConnectionRead])
async def list_connections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> list[M365Connection]:
    """List all M365 connections for the current user."""
    result = await db.execute(
        select(M365Connection)
        .where(M365Connection.user_id == current_user.id)
        .order_by(M365Connection.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{connection_id}", response_model=M365ConnectionRead)
async def get_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> M365Connection:
    """Get a specific M365 connection by ID."""
    result = await db.execute(
        select(M365Connection).where(
            M365Connection.id == connection_id,
            M365Connection.user_id == current_user.id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found",
        )
    return connection


@router.put("/{connection_id}", response_model=M365ConnectionRead)
async def update_connection(
    connection_id: int,
    update_data: M365ConnectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> M365Connection:
    """Update an M365 connection."""
    result = await db.execute(
        select(M365Connection).where(
            M365Connection.id == connection_id,
            M365Connection.user_id == current_user.id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found",
        )

    # If tenant_id or client_id changes, require a new secret (can't validate new app without it)
    tenant_changed = update_data.tenant_id is not None and update_data.tenant_id != connection.tenant_id
    client_changed = update_data.client_id is not None and update_data.client_id != connection.client_id
    secret_provided = update_data.client_secret is not None

    if (tenant_changed or client_changed) and not secret_provided:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_secret is required when changing tenant_id or client_id",
        )

    # Validate effective credentials if anything credential-related changed
    should_validate = tenant_changed or client_changed or secret_provided
    if should_validate:
        effective_tenant_id = update_data.tenant_id or connection.tenant_id
        effective_client_id = update_data.client_id or connection.client_id
        effective_secret = (
            update_data.client_secret
            if update_data.client_secret is not None
            else decrypt(connection.encrypted_client_secret)
        )
        try:
            await validate_m365_connection(
                tenant_id=effective_tenant_id,
                client_id=effective_client_id,
                client_secret=effective_secret,
            )
        except M365ConnectionError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    # Update only provided fields (after validation)
    if update_data.name is not None:
        connection.name = update_data.name
    if update_data.tenant_id is not None:
        connection.tenant_id = update_data.tenant_id
    if update_data.client_id is not None:
        connection.client_id = update_data.client_id
    if update_data.client_secret is not None:
        connection.encrypted_client_secret = encrypt(update_data.client_secret)
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
    """Delete an M365 connection (hard delete)."""
    result = await db.execute(
        select(M365Connection).where(
            M365Connection.id == connection_id,
            M365Connection.user_id == current_user.id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found",
        )

    await db.delete(connection)
    await db.commit()


@router.post("/{connection_id}/test", response_model=M365ConnectionTestResult)
async def test_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> M365ConnectionTestResult:
    """Test an M365 connection by attempting to authenticate."""
    result = await db.execute(
        select(M365Connection).where(
            M365Connection.id == connection_id,
            M365Connection.user_id == current_user.id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found",
        )

    # Decrypt credentials
    client_secret = decrypt(connection.encrypted_client_secret)

    try:
        details = await validate_m365_connection(
            tenant_id=connection.tenant_id,
            client_id=connection.client_id,
            client_secret=client_secret,
        )
        #update m365 connection modal with validation attributes (what exact error happened when we tried the api call)
        return M365ConnectionTestResult(
            success=True,
            message="Connection successful",
            tenant_name=details.tenant_display_name,
            tenant_display_name=details.tenant_display_name,
            default_domain=details.default_domain,
            verified_domains=details.verified_domains,
        )
    except M365ConnectionError as e:
        return M365ConnectionTestResult(
            success=False,
            message=str(e),
            tenant_name=None,
            tenant_display_name=None,
            default_domain=None,
            verified_domains=[],
        )
