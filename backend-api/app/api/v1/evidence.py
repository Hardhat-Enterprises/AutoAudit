from fastapi import APIRouter, File, Form, UploadFile

from app.core.errors import NotFound
from app.models.strategy import ScanResponse
from app.services.evidence_extractor import extract_text
from app.services.strategies import get_checker


router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.post("/scan", response_model=ScanResponse)
async def scan_evidence(
    strategy: str = Form(..., description="Strategy name as returned by /strategies"),
    user_id: str | None = Form(None),
    file: UploadFile = File(...),
) -> ScanResponse:
    checker = get_checker(strategy)
    if not checker:
        raise NotFound(f"Unknown strategy '{strategy}'")

    extracted_text, notes = await extract_text(file)
    return checker.run_checks(extracted_text, filename=file.filename, user_id=user_id, notes=notes)
