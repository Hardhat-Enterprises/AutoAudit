import logging
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.errors import NotFound
from app.services import evidence as evidence_service

router = APIRouter(prefix="/evidence", tags=["Evidence"])
logger = logging.getLogger("api")


@router.get("/strategies")
def get_strategies():
    return evidence_service.list_strategy_options()


@router.post("/scan")
async def scan_evidence(
    strategy_name: str = Form(...),
    user_id: str = Form("user"),
    evidence: UploadFile = File(...),
):
    content = await evidence.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty evidence upload")
    try:
        result = evidence_service.scan_evidence(
            filename=evidence.filename or "evidence",
            data=content,
            strategy_name=strategy_name,
            user_id=user_id or "user",
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - runtime safeguards
        logger.exception("Scan failed")
        raise HTTPException(status_code=500, detail="Scan failed") from exc


@router.get("/reports/{filename}")
def download_report(filename: str):
    path = evidence_service.resolve_report_path(filename)
    if not path.exists():
        raise NotFound(f"Report {filename}")

    media_type = (
        "application/pdf"
        if filename.lower().endswith(".pdf")
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if filename.lower().endswith(".docx")
        else "text/plain"
    )
    return FileResponse(str(path), media_type=media_type, filename=path.name)
