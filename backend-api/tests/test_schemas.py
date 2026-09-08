"""Lightweight schema / model coverage for modules not hit by API smoke tests."""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.compliance import Scan
from app.schemas.aws_connection import (
    AWSConnectionCreate,
    AWSConnectionRead,
    AWSConnectionTestResult,
    AWSConnectionUpdate,
)
from app.schemas.azure_connection import (
    AzureConnectionCreate,
    AzureConnectionRead,
    AzureConnectionTestResult,
    AzureConnectionUpdate,
)
from app.schemas.benchmark import BenchmarkRead, ControlRead
from app.schemas.control_verification_template import (
    ControlVerificationTemplateCreate,
    ControlVerificationTemplateRead,
    ControlVerificationTemplateUpdate,
)
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


def test_aws_connection_schemas() -> None:
    created = AWSConnectionCreate(
        name="Prod AWS",
        account_id="123456789012",
        access_key_id="AKIAEXAMPLE",
        secret_access_key="secret",
        region="ap-southeast-2",
    )
    assert created.account_id == "123456789012"
    assert created.region == "ap-southeast-2"

    updated = AWSConnectionUpdate(is_active=False, region="us-west-2")
    assert updated.is_active is False
    assert updated.region == "us-west-2"

    now = datetime.utcnow()
    read = AWSConnectionRead(
        id=1,
        user_id=1,
        name="Prod AWS",
        account_id="123456789012",
        access_key_id="AKIAEXAMPLE",
        region="us-east-1",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    assert read.id == 1
    assert read.user_id == 1

    result = AWSConnectionTestResult(
        success=True,
        message="ok",
        account_alias="prod",
    )
    assert result.success is True
    assert result.account_alias == "prod"


def test_azure_connection_schemas() -> None:
    created = AzureConnectionCreate(
        name="Prod Azure",
        tenant_id="tenant-guid",
        client_id="client-guid",
        subscription_id="sub-guid",
        client_secret="secret",
    )
    assert created.tenant_id == "tenant-guid"

    updated = AzureConnectionUpdate(is_active=False, name="Renamed")
    assert updated.is_active is False
    assert updated.name == "Renamed"

    now = datetime.utcnow()
    read = AzureConnectionRead(
        id=1,
        user_id=1,
        name="Prod Azure",
        tenant_id="tenant-guid",
        client_id="client-guid",
        subscription_id="sub-guid",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    assert read.id == 1

    result = AzureConnectionTestResult(
        success=True,
        message="ok",
        tenant_display_name="Contoso",
    )
    assert result.success is True
    assert result.tenant_display_name == "Contoso"


def test_control_verification_template_schemas() -> None:
    created = ControlVerificationTemplateCreate(
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v6.0.0",
        control_id="CIS-1.1.1",
        title="Manual MFA check",
        instructions="Verify MFA is enforced.",
        keywords=["mfa", "conditional access"],
        severity="high",
        evidence_type="screenshot",
    )
    assert created.control_id == "CIS-1.1.1"
    assert created.severity == "high"

    updated = ControlVerificationTemplateUpdate(
        title="Updated title",
        severity="medium",
        evidence_type="comment_only",
    )
    assert updated.title == "Updated title"
    assert updated.severity == "medium"

    with pytest.raises(ValidationError):
        ControlVerificationTemplateUpdate(title=None)

    now = datetime.utcnow()
    read = ControlVerificationTemplateRead(
        id=1,
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v6.0.0",
        control_id="CIS-1.1.1",
        title="Manual MFA check",
        instructions="Verify MFA is enforced.",
        keywords=["mfa"],
        severity="high",
        evidence_type="screenshot",
        created_at=now,
        updated_at=now,
    )
    assert read.id == 1
    assert read.evidence_type == "screenshot"
