import hashlib
import json

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure the monorepo /security package is importable both locally and inside Docker
import sys
from pathlib import Path


def _find_security_dir() -> Path | None:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "security"
        if candidate.exists():
            return candidate
    return None


SECURITY_DIR = _find_security_dir()
if SECURITY_DIR and str(SECURITY_DIR.parent) not in sys.path:
    sys.path.insert(0, str(SECURITY_DIR.parent))

# Reuse existing evidence logic from security package
from security.evidence_ui import app as evidence_ui

from app.core.auth import get_current_user
from app.db.session import get_async_session
from app.models.evidence_validation import EvidenceValidation
from app.models.user import User
from app.services.encryption import encrypt
from app.services.evidence_validator import validate_text

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("/strategies")
async def strategies():
    """
    Backend API: list available evidence strategies for the frontend dropdown.

    Used by frontend/src/pages/Evidence.js via:
      - frontend/src/api/client.js -> getEvidenceStrategies()
      - GET /v1/evidence/strategies
    """
    # Delegate to the existing evidence UI module (security/evidence_ui/app.py).
    return evidence_ui.api_strategies()


@router.get("/health")
async def health():
    """Backend API: health/debug endpoint for evidence scanning stack."""
    return evidence_ui.health()


@router.get("/scan-mem")
async def scan_mem():
    """Serve the human-friendly recent scans page (HTML)."""
    return evidence_ui.scan_mem_page()


@router.get("/scan-mem-log")
async def scan_mem_log():
    """Return recent scans as JSON for the frontend."""
    return evidence_ui.api_get_scan_mem_log()


@router.get("/recent-scans", include_in_schema=False)
async def recent_scans_redirect():
    return RedirectResponse(url="/v1/evidence/scan-mem")


@router.get("/scan-log", include_in_schema=False)
async def scan_log_redirect():
    return RedirectResponse(url="/v1/evidence/scan-mem")


@router.post("/scan")
async def scan(
    evidence: UploadFile = File(...),
    strategy_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Backend API: run an evidence scan.

    Used by frontend/src/pages/Evidence.js via:
      - frontend/src/api/client.js -> scanEvidence()
      - POST /v1/evidence/scan (multipart/form-data)

    Responsibilities in this layer:
    - (Best-effort) extract text + run validator pre-pass
    - Delegate the actual scanning to security/evidence_ui/app.py
    - (Best-effort) store validator output in DB (evidence_validation table)
    - Return the original scan response shape so the frontend can render it
    """
    # --- Validator pre-pass (best-effort) ---
    extracted_text = ""
    validator_payload: dict | None = None
    text_hash: str | None = None
    extracted_text_encrypted: str | None = None

    try:
        content_bytes = await evidence.read()
        await evidence.seek(0)

        extracted_text, _preview_path = evidence_ui.extract_text_and_preview_bytes(
            evidence.filename or "", content_bytes, evidence_ui.PREVIEWS
        )
        validator_payload = validate_text(strategy_name, extracted_text)

        if extracted_text:
            text_hash = hashlib.sha256(extracted_text.encode("utf-8", errors="ignore")).hexdigest()
    except Exception:
        # Do not block scan if validator pre-pass fails.
        extracted_text = ""
        validator_payload = None
        text_hash = None

    # Store only a capped excerpt of extracted text to reduce DB bloat.
    # If encryption isn't configured, skip encryption but do not break scanning.
    try:
        if extracted_text:
            extracted_text_encrypted = encrypt(extracted_text[:20000])
    except Exception:
        extracted_text_encrypted = None

    # delegate to existing implementation
    # NOTE: evidence_ui.scan is the "real" scanner implementation.
    # We keep this router thin and focused on integration concerns.
    scan_result = await evidence_ui.scan(
        evidence=evidence,
        strategy_name=strategy_name,
        user_id=str(current_user.id),
    )

    # --- Append validator to response (without changing existing keys) ---
    ok_value: bool | None = None
    response_payload: dict | None = None

    if isinstance(scan_result, dict):
        response_payload = scan_result
        ok_value = bool(response_payload.get("ok")) if "ok" in response_payload else None
        if ok_value is True and validator_payload is not None:
            response_payload["validator"] = validator_payload
    elif isinstance(scan_result, JSONResponse):
        try:
            payload = json.loads((scan_result.body or b"{}").decode("utf-8"))
        except Exception:
            payload = None
        if isinstance(payload, dict):
            response_payload = payload
            ok_value = bool(payload.get("ok")) if "ok" in payload else None
            if ok_value is True and validator_payload is not None:
                payload["validator"] = validator_payload
            # Return a new JSONResponse to include validator payload.
            scan_result = JSONResponse(payload, status_code=scan_result.status_code)

    # --- Persist validator output (best-effort; never blocks scan) ---
    try:
        status = "success" if ok_value is True else "error"
        if validator_payload is not None:
            record = EvidenceValidation(
                user_id=current_user.id,
                strategy_name=strategy_name,
                source_filename=getattr(evidence, "filename", None),
                text_hash=text_hash,
                extracted_text_encrypted=extracted_text_encrypted,
                matches_json=validator_payload,
                status=status,
            )
            db.add(record)
            await db.commit()
    except Exception:
        try:
            await db.rollback()
        except Exception:
            pass

    return scan_result


@router.get("/reports/{filename}")
async def download_report(filename: str):
    """
    Backend API: download a generated report file.

    The frontend links to this URL using:
      - frontend/src/api/client.js -> getEvidenceReportUrl()
      - GET /v1/evidence/reports/{filename}
    """
    # Reuse existing download handler in security/evidence_ui/app.py
    return evidence_ui.download_report(filename)
