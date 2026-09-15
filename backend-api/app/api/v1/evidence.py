# pylint: disable=line-too-long,missing-function-docstring,broad-exception-caught,too-many-locals,too-many-statements,wrong-import-position,duplicate-code,too-many-arguments,unused-argument
# type: ignore
"""Evidence API Endpoint Handler Module."""
import hashlib
import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("api")

def _find_security_dir() -> Optional[Path]:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "security"
        if candidate.exists():
            return candidate
    return None


SECURITY_DIR = _find_security_dir()
if SECURITY_DIR and str(SECURITY_DIR.parent) not in sys.path:
    sys.path.insert(0, str(SECURITY_DIR.parent))

from security.evidence_ui import app as evidence_ui  # noqa: E402

from app.core.auth import get_current_user  # noqa: E402
from app.db.session import get_async_session  # noqa: E402
from app.ingestion_service import process_ingestion_security_pipeline, validate_file_extension  # noqa: E402
from app.models.evidence_validation import EvidenceValidation  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.encryption import encrypt  # noqa: E402
from app.services.evidence_validator import validate_text  # noqa: E402

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("/strategies")
async def strategies() -> Any:
    return evidence_ui.api_strategies()


@router.get("/health")
async def health() -> Any:
    return evidence_ui.health()


@router.get("/scan-mem")
async def scan_mem() -> Any:
    return evidence_ui.scan_mem_page()


@router.get("/scan-mem-log")
async def scan_mem_log() -> Any:
    return evidence_ui.api_get_scan_mem_log()


@router.get("/recent-scans", include_in_schema=False)
async def recent_scans_redirect() -> RedirectResponse:
    return RedirectResponse(url="/v1/evidence/scan-mem")


@router.get("/scan-log", include_in_schema=False)
async def scan_log_redirect() -> RedirectResponse:
    return RedirectResponse(url="/v1/evidence/scan-mem")


@router.post("/scan")
async def scan(
    evidence: UploadFile = File(...),
    strategy_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    original_filename: str = getattr(evidence, "filename", "") or ""
    _, file_ext = os.path.splitext(original_filename)

    file_ext = file_ext.lower()
    if len(file_ext) > 16 or not validate_file_extension(original_filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Violation: File extension is not permitted or malformed.",
        )

    max_bytes: int = 10 * 1024 * 1024
    total_bytes: int = 0

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:  # nosec B108
        temp_path: str = temp_file.name
        try:
            while chunk := await evidence.read(4096):
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Security Violation: File size exceeds 10 MB limit.",
                    )
                temp_file.write(chunk)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    try:
        is_valid, _file_hash, error_msg = process_ingestion_security_pipeline(temp_path)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    await evidence.seek(0)

    extracted_text: str = ""
    validator_payload: Optional[Dict[str, Any]] = None
    text_hash: Optional[str] = None
    extracted_text_encrypted: Optional[str] = None

    try:
        content_bytes: bytes = await evidence.read()
        await evidence.seek(0)

        extracted_text, _preview_path = evidence_ui.extract_text_and_preview_bytes(
            evidence.filename or "", content_bytes, evidence_ui.PREVIEWS
        )
        validator_payload = validate_text(strategy_name, extracted_text)

        if extracted_text:
            text_hash = hashlib.sha256(extracted_text.encode("utf-8", errors="ignore")).hexdigest()
    except Exception:
        extracted_text = ""
        validator_payload = None
        text_hash = None

    try:
        if extracted_text:
            extracted_text_encrypted = encrypt(extracted_text[:20000])
    except Exception:
        extracted_text_encrypted = None

    scan_result = await evidence_ui.scan(
        evidence=evidence,
        strategy_name=strategy_name,
        user_id=str(current_user.id),
    )

    ok_value: Optional[bool] = None
    if isinstance(scan_result, dict):
        ok_value = bool(scan_result.get("ok")) if "ok" in scan_result else None
        if ok_value is True and validator_payload is not None:
            scan_result["validator"] = validator_payload
    elif isinstance(scan_result, JSONResponse):
        try:
            payload = json.loads((scan_result.body or b"{}").decode("utf-8"))
        except Exception:
            payload = None
        if isinstance(payload, dict):
            ok_value = bool(payload.get("ok")) if "ok" in payload else None
            if ok_value is True and validator_payload is not None:
                payload["validator"] = validator_payload
            scan_result = JSONResponse(payload, status_code=scan_result.status_code)

    try:
        scan_status: str = "success" if ok_value is True else "error"
        if validator_payload is not None:
            record = EvidenceValidation(
                user_id=current_user.id,
                strategy_name=strategy_name,
                source_filename=getattr(evidence, "filename", None),
                text_hash=text_hash,
                extracted_text_encrypted=extracted_text_encrypted,
                matches_json=validator_payload,
                status=scan_status,
            )
            db.add(record)
            await db.commit()
    except Exception:
        try:
            await db.rollback()
        except Exception:  # nosec B110
            logger.debug("Rollback attempt completed.")

    return scan_result


@router.get("/reports/{filename}")
async def download_report(
    filename: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    return evidence_ui.download_report(filename)
