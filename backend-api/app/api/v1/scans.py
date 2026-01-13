"""Scan API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.compliance import Scan
from app.models.m365_connection import M365Connection
from app.models.scan_result import ScanResult
from app.models.user import User
from app.schemas.scan import (
    ScanCreate,
    ScanCreatedResponse,
    ScanListItem,
    ScanRead,
    ScanResultRead,
)
from app.services.benchmark_reader import get_file_reader
from app.services.celery_client import queue_scan

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("/", response_model=ScanCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ScanCreatedResponse:
    """Create a new compliance scan.

    Creates a scan record with all ScanResult records and queues a Celery task.
    The scan runs asynchronously - poll GET /scans/{id} for status.
    """
    # Verify the connection exists and belongs to the user
    result = await db.execute(
        select(M365Connection).where(
            M365Connection.id == scan_data.m365_connection_id,
            M365Connection.user_id == current_user.id,
            M365Connection.is_active == True,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"M365 connection {scan_data.m365_connection_id} not found or inactive",
        )

    # Load benchmark metadata to get all controls
    file_reader = get_file_reader()
    try:
        all_controls = file_reader.list_controls(
            scan_data.framework, scan_data.benchmark, scan_data.version
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark {scan_data.framework}/{scan_data.benchmark}/{scan_data.version} not found",
        )

    # Validate platform matches (benchmark must be for m365)
    metadata = file_reader.get_benchmark_metadata(
        scan_data.framework, scan_data.benchmark, scan_data.version
    )
    if metadata.get("platform", "").lower() != "m365":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark platform '{metadata.get('platform')}' does not match M365 connection",
        )

    # Create scan record
    scan = Scan(
        user_id=current_user.id,
        m365_connection_id=scan_data.m365_connection_id,
        framework=scan_data.framework,
        benchmark=scan_data.benchmark,
        version=scan_data.version,
        status="pending",
        total_controls=len(all_controls),
    )
    db.add(scan)
    await db.flush()  # Get scan.id

    # Create ScanResult records for ALL controls
    selected_ids = set(scan_data.control_ids) if scan_data.control_ids else None
    skipped = 0
    for control in all_controls:
        is_selected = selected_ids is None or control["control_id"] in selected_ids
        result_status = "pending" if is_selected else "skipped"
        if result_status == "skipped":
            skipped += 1
        scan_result = ScanResult(
            scan_id=scan.id,
            control_id=control["control_id"],
            status=result_status,
        )
        db.add(scan_result)

    scan.skipped_count = skipped
    await db.commit()
    await db.refresh(scan)

    # Queue Celery task
    task = queue_scan(scan.id)

    return ScanCreatedResponse(
        id=scan.id,
        status="pending",
        message=f"Scan queued successfully. Task ID: {task.id}",
    )


@router.get("/", response_model=list[ScanListItem])
async def list_scans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    limit: int = 50,
    offset: int = 0,
) -> list[Scan]:
    """List scans for the current user."""
    result = await db.execute(
        select(Scan)
        .options(selectinload(Scan.m365_connection))
        .where(Scan.user_id == current_user.id)
        .order_by(Scan.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


@router.get("/{scan_id}", response_model=ScanRead)
async def get_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Scan:
    """Get scan details by ID including results."""
    result = await db.execute(
        select(Scan)
        .options(selectinload(Scan.results), selectinload(Scan.m365_connection))
        .where(Scan.id == scan_id, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found",
        )
    return scan


@router.get("/{scan_id}/results", response_model=list[ScanResultRead])
async def get_scan_results(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    status_filter: str | None = None,
) -> list[ScanResult]:
    """Get results for a scan.

    Optionally filter by status (pending, passed, failed, error, skipped).
    """
    # Verify scan exists and user has access
    scan_result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == current_user.id)
    )
    scan = scan_result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found",
        )

    # Build query
    query = select(ScanResult).where(ScanResult.scan_id == scan_id)
    if status_filter:
        query = query.where(ScanResult.status == status_filter)
    query = query.order_by(ScanResult.control_id)

    results = await db.execute(query)
    return list(results.scalars().all())


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    """Delete a scan and its results.

    Only allow deleting scans that are no longer running to avoid race conditions
    with in-flight Celery tasks updating scan results.
    """
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found",
        )
#prevent this from the ui itself by hiding/disabling the button when the scanning is happening
    if scan.status in {"pending", "running"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a scan while it is pending or running",
        )

    # Explicitly delete child rows to avoid relying on DB-level cascades.
    await db.execute(delete(ScanResult).where(ScanResult.scan_id == scan_id))
    await db.delete(scan)
    await db.commit()
    return None
