"""Benchmark and control discovery API endpoints.

These endpoints read from metadata.json files in the policies directory
to allow the frontend to discover available benchmarks and controls.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.benchmark import BenchmarkRead, ControlRead
from app.services.benchmark_reader import get_file_reader

router = APIRouter(prefix="/benchmarks", tags=["Benchmarks"])


@router.get("", response_model=list[BenchmarkRead])
async def list_benchmarks(
    current_user: User = Depends(get_current_user),
) -> list[BenchmarkRead]:
    """List all available benchmarks.

    Scans the policies directory for metadata.json files and returns
    information about each available benchmark.
    """
    file_reader = get_file_reader()
    benchmarks_data = file_reader.list_benchmarks()

    result = []
    for data in benchmarks_data:
        controls = data.get("controls", [])
        result.append(
            BenchmarkRead(
                framework=data.get("framework", ""),
                slug=data.get("slug", ""),
                version=data.get("version", ""),
                name=data.get("benchmark", ""),
                platform=data.get("platform", ""),
                release_date=data.get("release_date"),
                source_url=data.get("source_url"),
                control_count=len(controls),
            )
        )
    return result


@router.get("/{framework}/{slug}/{version}", response_model=BenchmarkRead)
async def get_benchmark(
    framework: str,
    slug: str,
    version: str,
    current_user: User = Depends(get_current_user),
) -> BenchmarkRead:
    """Get details for a specific benchmark."""
    file_reader = get_file_reader()

    try:
        data = file_reader.get_benchmark_metadata(framework, slug, version)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark {framework}/{slug}/{version} not found",
        )

    controls = data.get("controls", [])
    return BenchmarkRead(
        framework=data.get("framework", framework),
        slug=data.get("slug", slug),
        version=data.get("version", version),
        name=data.get("benchmark", ""),
        platform=data.get("platform", ""),
        release_date=data.get("release_date"),
        source_url=data.get("source_url"),
        control_count=len(controls),
    )


@router.get("/{framework}/{slug}/{version}/controls", response_model=list[ControlRead])
async def list_controls(
    framework: str,
    slug: str,
    version: str,
    current_user: User = Depends(get_current_user),
) -> list[ControlRead]:
    """List all controls for a specific benchmark."""
    file_reader = get_file_reader()

    try:
        controls_data = file_reader.list_controls(framework, slug, version)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark {framework}/{slug}/{version} not found",
        )

    result = []
    for control in controls_data:
        result.append(
            ControlRead(
                control_id=control.get("control_id", ""),
                title=control.get("title", ""),
                description=control.get("description"),
                severity=control.get("severity"),
                service=control.get("service"),
                data_collector_id=control.get("data_collector_id", ""),
                policy_file=control.get("policy_file", ""),
                requires_permissions=control.get("requires_permissions"),
            )
        )
    return result


@router.get(
    "/{framework}/{slug}/{version}/controls/{control_id}",
    response_model=ControlRead,
)
async def get_control(
    framework: str,
    slug: str,
    version: str,
    control_id: str,
    current_user: User = Depends(get_current_user),
) -> ControlRead:
    """Get details for a specific control."""
    file_reader = get_file_reader()

    try:
        control = file_reader.get_control_metadata(framework, slug, version, control_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark {framework}/{slug}/{version} not found",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Control {control_id} not found in {framework}/{slug}/{version}",
        )

    return ControlRead(
        control_id=control.get("control_id", ""),
        title=control.get("title", ""),
        description=control.get("description"),
        severity=control.get("severity"),
        service=control.get("service"),
        data_collector_id=control.get("data_collector_id", ""),
        policy_file=control.get("policy_file", ""),
        requires_permissions=control.get("requires_permissions"),
    )
