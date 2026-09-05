"""Lightweight schema / model coverage for modules not hit by API smoke tests."""

from datetime import datetime
from decimal import Decimal

from app.models.compliance import Scan
from app.schemas.benchmark import BenchmarkRead, ControlRead
from app.schemas.m365_connection import (
    M365ConnectionCreate,
    M365ConnectionRead,
    M365ConnectionTestResult,
    M365ConnectionUpdate,
)
from app.schemas.scan import (
    ControlCategoryBreakdown,
    ScanCreate,
    ScanCreatedResponse,
    ScanListItem,
    ScanRead,
    ScanReadinessCheck,
    ScanReadinessResponse,
    ScanResultRead,
    ScanSummary,
)


def test_benchmark_schemas() -> None:
    bench = BenchmarkRead(
        framework="cis",
        slug="microsoft-365-foundations",
        version="v3.1.0",
        name="CIS M365",
        platform="m365",
        control_count=1,
    )
    assert bench.slug == "microsoft-365-foundations"
    control = ControlRead(
        control_id="CIS-1.1.1",
        title="MFA",
        level="L1",
        is_manual=False,
        benchmark_audit_type="Automated",
        automation_status="ready",
    )
    assert control.control_id == "CIS-1.1.1"


def test_m365_connection_schemas() -> None:
    created = M365ConnectionCreate(
        name="Prod",
        tenant_id="tenant",
        client_id="client",
        client_secret="secret",
    )
    assert created.name == "Prod"
    updated = M365ConnectionUpdate(is_active=False)
    assert updated.is_active is False
    now = datetime.utcnow()
    read = M365ConnectionRead(
        id=1,
        user_id=1,
        name="Prod",
        tenant_id="tenant",
        client_id="client",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    assert read.id == 1
    result = M365ConnectionTestResult(success=True, message="ok", tenant_name="Contoso")
    assert result.success is True


def test_scan_schemas() -> None:
    create = ScanCreate(
        m365_connection_id=1,
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v3.1.0",
    )
    assert create.framework == "cis"
    now = datetime.utcnow()
    result = ScanResultRead(
        id=1,
        scan_id=1,
        control_id="CIS-1.1.1",
        status="passed",
        message=None,
        evidence=None,
        created_at=now,
        updated_at=now,
    )
    scan = ScanRead(
        id=1,
        user_id=1,
        m365_connection_id=1,
        azure_connection_id=None,
        gcp_connection_id=None,
        aws_connection_id=None,
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v3.1.0",
        status="completed",
        started_at=now,
        finished_at=now,
        compliance_score=Decimal("90.0"),
        total_controls=10,
        passed_count=9,
        failed_count=1,
        skipped_count=0,
        error_count=0,
        notes=None,
        results=[result],
    )
    assert scan.passed_count == 9
    listed = ScanListItem(
        id=1,
        user_id=1,
        m365_connection_id=1,
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v3.1.0",
        status="completed",
        started_at=now,
        finished_at=now,
        compliance_score=Decimal("90.0"),
        total_controls=10,
        passed_count=9,
        failed_count=1,
        skipped_count=0,
        error_count=0,
    )
    assert listed.id == 1
    created = ScanCreatedResponse(id=1, status="pending", message="queued")
    assert created.status == "pending"
    summary = ScanSummary(
        id=1,
        status="completed",
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v3.1.0",
        started_at=now,
        finished_at=now,
        compliance_score=Decimal("90.0"),
        total_controls=10,
        passed_count=9,
        failed_count=1,
        skipped_count=0,
        error_count=0,
        categories=[
            ControlCategoryBreakdown(
                category="1",
                total=10,
                passed=9,
                failed=1,
                skipped=0,
                error=0,
            )
        ],
    )
    assert summary.categories[0].passed == 9
    readiness = ScanReadinessResponse(
        ready=True,
        summary="ok",
        required_permissions=["User.Read"],
        missing_permissions=[],
        unverified_permissions=[],
        checks=[
            ScanReadinessCheck(
                key="perms",
                label="Permissions",
                status="pass",
                severity="critical",
                message="ok",
            )
        ],
    )
    assert readiness.ready is True


def test_scan_connection_name_property() -> None:
    scan = Scan()
    scan.m365_connection = None
    assert scan.connection_name is None

    from app.models.m365_connection import M365Connection

    connection = M365Connection()
    connection.name = "Contoso M365"
    object.__setattr__(scan, "m365_connection", connection)
    assert scan.connection_name == "Contoso M365"
