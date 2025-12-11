from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse

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
from security.frontend import ui as evidence_ui

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("/strategies")
async def strategies():
    # delegate to evidence module
    return evidence_ui.api_strategies()


@router.get("/health")
async def health():
    return evidence_ui.health()


@router.get("/scan-mem")
async def scan_mem():
    """Serve the human-friendly recent scans page (HTML)."""
    return evidence_ui.scan_mem_page()


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
    user_id: str = Form("user"),
):
    # delegate to existing implementation
    # Pass the strategy into both fields to avoid FormInfo default overriding it
    return await evidence_ui.scan(
        evidence=evidence,
        strategy_name=strategy_name,
        strategy=strategy_name,
        user_id=user_id,
    )


@router.get("/reports/{filename}")
async def download_report(filename: str):
    # reuse existing download handler
    return evidence_ui.download_report(filename)
