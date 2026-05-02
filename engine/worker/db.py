"""Database access for the Celery worker.

Uses synchronous SQLAlchemy since Celery tasks are synchronous.
For async operations within tasks, use asyncio.run().

---
Extending for other cloud providers
---

Right now this module only handles M365 connections. The backend schema already
has tables for azure_connection, gcp_connection, and aws_connection - we just
haven't built the credential storage for those yet.

When you add a new provider, you'll need to:

1. Add a get_<provider>_credentials() function that queries the relevant table
   and decrypts any secrets. Look at how get_scan() joins to m365_connection
   for the pattern.

2. Update get_scan() to also pull from the new connection table. The scan table
   has nullable FKs for each provider (azure_connection_id, gcp_connection_id,
   aws_connection_id) - only one will be non-null per scan.

3. Add a collector in /engine/collectors/<provider>/ that knows how to use
   those credentials to call the provider's APIs.

4. The task in tasks.py will need a branch to pick the right collector based on
   which connection ID is populated on the scan.

The encryption approach is the same across all providers - Fernet symmetric
encryption with the key from ENCRYPTION_KEY env var. See decrypt() below.
"""

import json
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Generator

from cryptography.fernet import Fernet
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from worker.config import settings

# Convert async URL to sync URL for worker
sync_database_url = settings.DATABASE_URL.replace(
    "postgresql+asyncpg://", "postgresql://"
)

# Create sync engine and session factory
engine = create_engine(sync_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get a database session context manager."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Fernet instance for decryption
_fernet: Fernet | None = None


def get_fernet() -> Fernet:
    """Get or create Fernet instance for credential decryption."""
    global _fernet
    if _fernet is None:
        if not settings.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY environment variable is required")
        _fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return _fernet


def decrypt(ciphertext: str) -> str:
    """Decrypt a ciphertext string."""
    if not ciphertext:
        return ""
    return get_fernet().decrypt(ciphertext.encode()).decode()


def get_scan(session: Session, scan_id: int) -> dict | None:
    """Get scan details by ID.

    Returns a dict with scan data including the M365 connection credentials.
    For other providers, you'd add similar joins here - see module docstring.
    """
    result = session.execute(
        text("""
            SELECT s.id, s.user_id,
                   s.m365_connection_id, s.azure_connection_id,
                   s.gcp_connection_id, s.aws_connection_id,
                   s.framework, s.benchmark, s.version,
                   s.status, s.started_at, s.finished_at,
                   s.compliance_score, s.total_controls, s.passed_count,
                   s.failed_count, s.skipped_count, s.error_count, s.notes,
                   c.tenant_id, c.client_id, c.encrypted_client_secret
            FROM scan s
            LEFT JOIN m365_connection c ON s.m365_connection_id = c.id
            WHERE s.id = :scan_id
        """),
        {"scan_id": scan_id},
    )
    row = result.fetchone()
    if not row:
        return None

    return {
        "id": row.id,
        "user_id": row.user_id,
        # Connection IDs - only one of these should be set per scan
        "m365_connection_id": row.m365_connection_id,
        "azure_connection_id": row.azure_connection_id,
        "gcp_connection_id": row.gcp_connection_id,
        "aws_connection_id": row.aws_connection_id,
        # What we're scanning against
        "framework": row.framework,
        "benchmark": row.benchmark,
        "version": row.version,
        # Status and timing
        "status": row.status,
        "started_at": row.started_at,
        "finished_at": row.finished_at,
        # Results
        "compliance_score": row.compliance_score,
        "total_controls": row.total_controls,
        "passed_count": row.passed_count,
        "failed_count": row.failed_count,
        "skipped_count": row.skipped_count,
        "error_count": row.error_count,
        "notes": row.notes,
        # M365 credentials (decrypted) - add similar blocks for other providers
        "tenant_id": row.tenant_id,
        "client_id": row.client_id,
        "client_secret": decrypt(row.encrypted_client_secret) if row.encrypted_client_secret else None,
    }


def get_pending_scan_results(session: Session, scan_id: int) -> list[dict]:
    """Get all scan results with status='pending' for a scan.

    Returns list of dicts with result details including control metadata.
    """
    result = session.execute(
        text("""
            SELECT id, scan_id, control_id, status, message, evidence
            FROM scan_result
            WHERE scan_id = :scan_id AND status = 'pending'
            ORDER BY control_id
        """),
        {"scan_id": scan_id},
    )
    rows = result.fetchall()
    return [
        {
            "id": row.id,
            "scan_id": row.scan_id,
            "control_id": row.control_id,
            "status": row.status,
            "message": row.message,
            "evidence": row.evidence,
        }
        for row in rows
    ]


def update_scan_status(
    session: Session,
    scan_id: int,
    status: str,
    finished_at: datetime | None = None,
    total_controls: int | None = None,
    passed_count: int | None = None,
    failed_count: int | None = None,
    skipped_count: int | None = None,
    error_count: int | None = None,
    compliance_score: Decimal | None = None,
    notes: str | None = None,
) -> None:
    """Update scan status and optionally other fields."""
    updates = ["status = :status"]
    params = {"scan_id": scan_id, "status": status}

    if finished_at is not None:
        updates.append("finished_at = :finished_at")
        params["finished_at"] = finished_at
    if total_controls is not None:
        updates.append("total_controls = :total_controls")
        params["total_controls"] = total_controls
    if passed_count is not None:
        updates.append("passed_count = :passed_count")
        params["passed_count"] = passed_count
    if failed_count is not None:
        updates.append("failed_count = :failed_count")
        params["failed_count"] = failed_count
    if skipped_count is not None:
        updates.append("skipped_count = :skipped_count")
        params["skipped_count"] = skipped_count
    if error_count is not None:
        updates.append("error_count = :error_count")
        params["error_count"] = error_count
    if compliance_score is not None:
        updates.append("compliance_score = :compliance_score")
        params["compliance_score"] = compliance_score
    if notes is not None:
        updates.append("notes = :notes")
        params["notes"] = notes

    session.execute(
        text(f"UPDATE scan SET {', '.join(updates)} WHERE id = :scan_id"),
        params,
    )


def increment_scan_progress(
    session: Session,
    scan_id: int,
    passed: bool,
) -> None:
    """Increment the passed or failed count for a scan."""
    if passed:
        session.execute(
            text("UPDATE scan SET passed_count = passed_count + 1 WHERE id = :scan_id"),
            {"scan_id": scan_id},
        )
    else:
        session.execute(
            text("UPDATE scan SET failed_count = failed_count + 1 WHERE id = :scan_id"),
            {"scan_id": scan_id},
        )


def increment_scan_error_count(session: Session, scan_id: int) -> None:
    """Increment the error count for a scan."""
    session.execute(
        text("UPDATE scan SET error_count = error_count + 1 WHERE id = :scan_id"),
        {"scan_id": scan_id},
    )


def increment_scan_skipped_count(session: Session, scan_id: int, amount: int = 1) -> None:
    """Increment the skipped count for a scan."""
    session.execute(
        text("UPDATE scan SET skipped_count = skipped_count + :amount WHERE id = :scan_id"),
        {"scan_id": scan_id, "amount": amount},
    )


def update_scan_result(
    session: Session,
    result_id: int,
    status: str,
    message: str | None = None,
    evidence: dict | None = None,
) -> None:
    """Update a scan result record.

    Args:
        session: Database session
        result_id: The scan_result.id to update
        status: New status (passed, failed, error)
        message: Human-readable result message
        evidence: Details from OPA evaluation
    """
    updates = ["status = :status", "updated_at = now()"]
    params = {"result_id": result_id, "status": status}

    if message is not None:
        updates.append("message = :message")
        params["message"] = message

    if evidence is not None:
        updates.append("evidence = CAST(:evidence AS jsonb)")
        params["evidence"] = json.dumps(evidence)

    session.execute(
        text(f"UPDATE scan_result SET {', '.join(updates)} WHERE id = :result_id"),
        params,
    )


def finalize_scan_if_complete(session: Session, scan_id: int) -> bool:
    """Check if all controls are evaluated and finalize scan if complete.

    This function uses SELECT FOR UPDATE to prevent race conditions when
    multiple tasks complete simultaneously.

    Args:
        session: Database session
        scan_id: The scan ID to check

    Returns:
        True if scan was finalized, False if still pending controls
    """
    # Check if there are any pending controls remaining
    result = session.execute(
        text("""
            SELECT COUNT(*) as pending_count
            FROM scan_result
            WHERE scan_id = :scan_id AND status = 'pending'
        """),
        {"scan_id": scan_id},
    )
    pending_count = result.scalar()

    if pending_count > 0:
        # Still have pending controls
        return False

    # All controls complete - finalize the scan
    # Use SELECT FOR UPDATE to prevent race condition
    result = session.execute(
        text("""
            SELECT id, status, passed_count, failed_count
            FROM scan
            WHERE id = :scan_id
            FOR UPDATE
        """),
        {"scan_id": scan_id},
    )
    row = result.fetchone()

    if not row or row.status == "completed":
        # Already finalized by another task
        return False

    # Calculate compliance score
    passed = row.passed_count or 0
    failed = row.failed_count or 0
    total = passed + failed

    if total > 0:
        compliance_score = Decimal(str(round(passed / total * 100, 2)))
    else:
        compliance_score = Decimal("0.00")

    # Update scan to completed
    session.execute(
        text("""
            UPDATE scan
            SET status = 'completed',
                finished_at = now(),
                compliance_score = :compliance_score
            WHERE id = :scan_id
        """),
        {"scan_id": scan_id, "compliance_score": compliance_score},
    )

    return True
