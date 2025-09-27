from fastapi import APIRouter
from app.models.exports import ExportRequest, ExportStatusResponse, ExportResponse
from app.services.job_store import create_export_job, get_job_status
from app.core.errors import NotFound 

router = APIRouter(prefix="/exports", tags=["Exports"])

@router.post("/report", response_model=ExportResponse)
def create_report_export(request: ExportRequest):
    job_id = create_export_job(scan_id=request.scan_id, fmt=request.format)
    return {"job_id": job_id, "status": "pending"}

@router.get("/{job_id}", response_model=ExportStatusResponse)
def get_export_status(job_id: str):
    job = get_job_status(job_id)
    if not job:
        raise NotFound(f"Export job {job_id}")
    return job
