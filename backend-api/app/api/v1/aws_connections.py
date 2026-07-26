"""AWS Connection API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.aws_connection import AWSConnection
from app.models.user import User
from app.schemas.aws_connection import (
    AWSConnectionCreate,
    AWSConnectionRead,
    AWSConnectionTestResult,
    AWSConnectionUpdate,
)
from app.services.encryption import decrypt, encrypt

router = APIRouter(prefix="/aws-connections", tags=["AWS Connections"])


@router.post("/", response_model=AWSConnectionRead, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_data: AWSConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> AWSConnection:
    """Create a new AWS connection for the current user."""
    connection = AWSConnection(
        user_id=current_user.id,
        name=connection_data.name,
        account_id=connection_data.account_id,
        access_key_id=connection_data.access_key_id,
        encrypted_secret_access_key=encrypt(connection_data.secret_access_key),
        region=connection_data.region,
    )
    db.add(connection)
    await db.commit()
    await db.refresh(connection)
    return connection


@router.get("/", response_model=list[AWSConnectionRead])
async def list_connections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> list[AWSConnection]:
    """List all AWS connections for the current user."""
    result = await db.execute(
        select(AWSConnection)
        .where(AWSConnection.user_id == current_user.id)
        .order_by(AWSConnection.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{connection_id}", response_model=AWSConnectionRead)
async def get_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> AWSConnection:
    """Get a specific AWS connection by ID."""
    result = await db.execute(
        select(AWSConnection).where(
            AWSConnection.id == connection_id,
            AWSConnection.user_id == current_user.id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found",
        )
    return connection


@router.put("/{connection_id}", response_model=AWSConnectionRead)
async def update_connection(
    connection_id: int,
    update_data: AWSConnectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> AWSConnection:
    """Update an AWS connection."""
    result = await db.execute(
        select(AWSConnection).where(
            AWSConnection.id == connection_id,
            AWSConnection.user_id == current_user.id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found",
        )

    # Update only provided fields
    if update_data.name is not None:
        connection.name = update_data.name
    if update_data.account_id is not None:
        connection.account_id = update_data.account_id
    if update_data.access_key_id is not None:
        connection.access_key_id = update_data.access_key_id
    if update_data.secret_access_key is not None:
        connection.encrypted_secret_access_key = encrypt(update_data.secret_access_key)
    if update_data.region is not None:
        connection.region = update_data.region
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
    """Delete an AWS connection (hard delete)."""
    result = await db.execute(
        select(AWSConnection).where(
            AWSConnection.id == connection_id,
            AWSConnection.user_id == current_user.id,
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


@router.post("/{connection_id}/test", response_model=AWSConnectionTestResult)
async def test_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> AWSConnectionTestResult:
    """Test an AWS connection by verifying the credentials are valid."""
    result = await db.execute(
        select(AWSConnection).where(
            AWSConnection.id == connection_id,
            AWSConnection.user_id == current_user.id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection {connection_id} not found",
        )

    # Decrypt credentials
    secret_access_key = decrypt(connection.encrypted_secret_access_key)

    # Placeholder: AWS credential validation will be implemented
    # when the AWS SDK (boto3) integration is added.
    # For now, return a success response confirming the connection is stored.
    return AWSConnectionTestResult(
        success=True,
        message="AWS connection credentials are stored. Live validation requires boto3 integration.",
        account_alias=None,
    )
