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
    ScanReadinessCheck,
    ScanReadinessResponse,
    ScanRead,
    ScanResultRead,
)
from app.services.benchmark_reader import get_file_reader
from app.services.celery_client import queue_scan
from app.services.encryption import decrypt
from app.services.scan_readiness import (
    evaluate_scan_readiness,
    extract_required_permissions,
)

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

# Get scan readiness status for a given M365 connection and benchmark. This is used by the frontend before starting a scan to validate the connection and provide feedback on any issues that might cause the scan to fail or have incomplete results.
@router.get("/readiness", response_model=ScanReadinessResponse)
async def get_scan_readiness(
    m365_connection_id: int,
    framework: str,
    benchmark: str,
    version: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> ScanReadinessResponse:
    """Validate whether a scan can run successfully before queueing it."""
    # Readiness uses the saved M365 connection exactly as the user configured it.
    result = await db.execute(
        select(M365Connection).where(
            M365Connection.id == m365_connection_id,
            M365Connection.user_id == current_user.id,
            M365Connection.is_active == True,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"M365 connection {m365_connection_id} not found or inactive",
        )

    # Benchmark metadata is the source of truth for which controls are runnable and which permissions those controls declare.
    file_reader = get_file_reader()
    try:
        metadata = file_reader.get_benchmark_metadata(framework, benchmark, version)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark {framework}/{benchmark}/{version} not found",
        )

    if metadata.get("platform", "").lower() != "m365":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark platform '{metadata.get('platform')}' does not match M365 connection",
        )

    # The API layer only prepares inputs here. The actual readiness logic lives in scan_readiness.py so the route stays thin.
    required_permissions = extract_required_permissions(metadata.get("controls", []))
    readiness = await evaluate_scan_readiness(
        tenant_id=connection.tenant_id,
        client_id=connection.client_id,
        client_secret=decrypt(connection.encrypted_client_secret),
        required_permissions=required_permissions,
    )

    # Convert the service result into the response model returned to the frontend.
    return ScanReadinessResponse(
        ready=readiness.ready,
        summary=readiness.summary,
        required_permissions=readiness.required_permissions,
        missing_permissions=readiness.missing_permissions,
        unverified_permissions=readiness.unverified_permissions,
        checks=[
            ScanReadinessCheck(
                key=check.key,
                label=check.label,
                status=check.status,
                severity=check.severity,
                message=check.message,
            )
            for check in readiness.checks
        ],
    )


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
    """Delete a scan (hard delete) and its results."""
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found",
        )

    # Delete dependent results first (FK is not ON DELETE CASCADE).
    await db.execute(delete(ScanResult).where(ScanResult.scan_id == scan_id))
    await db.delete(scan)
    await db.commit()
