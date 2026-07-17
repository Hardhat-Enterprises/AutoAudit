"""
Seed local development data after migrations.

Creates (idempotently):
  - Default admin user (via init_db)
  - One M365 connection with placeholder credentials (not valid for Graph)
  - One completed scan with realistic control results (CIS M365 v3.1.0)
  - One failed scan with a notes/error message (for UI testing)

Requires environment variables (see backend-api/.env.example):
  - DATABASE_URL
  - ENCRYPTION_KEY (Fernet key for encrypting the placeholder client secret)
  - POLICIES_DIR pointing at engine policies (e.g. ../engine/policies from backend-api/)

Usage:
    cd backend-api
    uv sync
    uv run alembic upgrade head
    uv run python -m app.db.seed_dev
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Same default as backend-api/.env.example and docker-compose (local dev only).
_DEFAULT_DEV_ENCRYPTION_KEY = "Ps-HiS3ww5QzQPc_Mdu5-JyA_jCNbdFHMdiwWSlAfgM="  # gitleaks:allow

from sqlalchemy import select

from app.core.config import get_settings
from app.db.init_db import init_db
from app.db.session import async_session_maker
from app.models.compliance import Scan
from app.models.m365_connection import M365Connection
from app.models.scan_result import ScanResult
from app.models.user import User
from app.services.benchmark_reader import BenchmarkFileReader
from app.services.encryption import encrypt


SEED_CONNECTION_NAME = "Local Dev (seed)"
SEED_MARKER_COMPLETED = "__AUTOAUDIT_DEV_SEED_COMPLETED__"
FAILED_SEED_NOTES = "Simulated scan failure for local UI testing (seed data)."

# Placeholder Entra app values — not valid for real API calls; UI and PDF export only.
SEED_TENANT_ID = "00000000-0000-0000-0000-000000000001"
SEED_CLIENT_ID = "00000000-0000-0000-0000-000000000002"
SEED_CLIENT_SECRET_PLAINTEXT = "local-dev-placeholder-secret-not-for-production"  # nosec B105


def _metadata_path(policies_dir: Path) -> Path:
    return (
        policies_dir
        / "cis"
        / "microsoft-365-foundations"
        / "v3.1.0"
        / "metadata.json"
    )


def _resolve_policies_dir() -> Path:
    """Prefer POLICIES_DIR from settings; fall back to monorepo engine/policies."""
    configured = Path(get_settings().POLICIES_DIR)
    if _metadata_path(configured).is_file():
        return configured
    repo_root = Path(__file__).resolve().parents[3]
    fallback = repo_root / "engine" / "policies"
    if _metadata_path(fallback).is_file():
        return fallback
    raise FileNotFoundError(
        "Could not find CIS M365 v3.1.0 metadata.json. "
        "Set POLICIES_DIR in backend-api/.env (see .env.example) "
        f"or run from the AutoAudit repo (tried {configured} and {fallback})."
    )


async def _get_admin_user(session) -> User:
    result = await session.execute(select(User).where(User.email == "admin@example.com"))
    user = result.unique().scalar_one_or_none()
    if not user:
        raise RuntimeError(
            "admin@example.com not found after init_db. Run `uv run python -m app.db.init_db` first."
        )
    return user


async def _ensure_seed_connection(session, user_id: int) -> M365Connection:
    result = await session.execute(
        select(M365Connection).where(
            M365Connection.user_id == user_id,
            M365Connection.name == SEED_CONNECTION_NAME,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        print(f"[SKIP] M365 connection already exists: {SEED_CONNECTION_NAME} (id={existing.id})")
        return existing

    conn = M365Connection(
        user_id=user_id,
        name=SEED_CONNECTION_NAME,
        tenant_id=SEED_TENANT_ID,
        client_id=SEED_CLIENT_ID,
        encrypted_client_secret=encrypt(SEED_CLIENT_SECRET_PLAINTEXT),
        is_active=True,
    )
    session.add(conn)
    await session.flush()
    print(f"[OK] Created M365 connection: {SEED_CONNECTION_NAME} (id={conn.id})")
    return conn


async def _ensure_completed_scan(
    session,
    *,
    user_id: int,
    connection_id: int,
    controls: list[dict],
) -> None:
    result = await session.execute(
        select(Scan).where(Scan.user_id == user_id, Scan.notes == SEED_MARKER_COMPLETED)
    )
    if result.scalar_one_or_none():
        print("[SKIP] Completed seed scan already exists")
        return

    if not controls:
        raise RuntimeError("Benchmark returned no controls; check POLICIES_DIR and metadata.json")

    now = datetime.utcnow()
    total = len(controls)
    passed = (total + 1) // 2
    failed = total - passed

    scan = Scan(
        user_id=user_id,
        m365_connection_id=connection_id,
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v3.1.0",
        status="completed",
        started_at=now,
        finished_at=now,
        total_controls=total,
        passed_count=passed,
        failed_count=failed,
        skipped_count=0,
        error_count=0,
        notes=SEED_MARKER_COMPLETED,
    )
    session.add(scan)
    await session.flush()

    for i, control in enumerate(controls):
        cid = str(control.get("control_id", ""))
        title = control.get("title") or cid
        desc = control.get("description")
        status = "passed" if i < passed else "failed"
        scan_result = ScanResult(
            scan_id=scan.id,
            control_id=cid,
            status=status,
            message=None if status == "passed" else "Seeded failure for local development",
            evidence={"title": title, "description": desc} if desc else {"title": title},
        )
        session.add(scan_result)

    print(
        f"[OK] Created completed seed scan id={scan.id} "
        f"({passed} passed, {failed} failed, {total} controls)"
    )


async def _ensure_failed_scan(session, *, user_id: int, connection_id: int) -> None:
    result = await session.execute(
        select(Scan).where(Scan.user_id == user_id, Scan.notes == FAILED_SEED_NOTES)
    )
    if result.scalar_one_or_none():
        print("[SKIP] Failed seed scan already exists")
        return

    now = datetime.utcnow()
    scan = Scan(
        user_id=user_id,
        m365_connection_id=connection_id,
        framework="cis",
        benchmark="microsoft-365-foundations",
        version="v3.1.0",
        status="failed",
        started_at=now,
        finished_at=now,
        total_controls=0,
        passed_count=0,
        failed_count=0,
        skipped_count=0,
        error_count=0,
        notes=FAILED_SEED_NOTES,
    )
    session.add(scan)
    await session.flush()
    print(f"[OK] Created failed seed scan id={scan.id} (for error banner / PDF checks)")


async def seed_dev() -> None:
    if not os.environ.get("ENCRYPTION_KEY"):
        os.environ["ENCRYPTION_KEY"] = _DEFAULT_DEV_ENCRYPTION_KEY
        print(
            "[INFO] ENCRYPTION_KEY was unset; using the dev default from .env.example "
            "so the seed connection secret can be encrypted.",
            file=sys.stderr,
        )

    try:
        policies_dir = _resolve_policies_dir()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    reader = BenchmarkFileReader(policies_dir)
    controls = reader.list_controls("cis", "microsoft-365-foundations", "v3.1.0")

    await init_db()

    async with async_session_maker() as session:
        admin = await _get_admin_user(session)
        conn = await _ensure_seed_connection(session, admin.id)

        await _ensure_completed_scan(
            session,
            user_id=admin.id,
            connection_id=conn.id,
            controls=controls,
        )
        await _ensure_failed_scan(session, user_id=admin.id, connection_id=conn.id)

        await session.commit()

    print("\n[SUCCESS] Dev seed complete. Log in as admin@example.com / admin and open /scans.")


if __name__ == "__main__":
    asyncio.run(seed_dev())
