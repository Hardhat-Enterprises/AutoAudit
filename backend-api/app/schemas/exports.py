from pydantic import BaseModel, Field

class ExportRequest(BaseModel):
    scan_id: str = Field(..., example="s-001")
    format: str = Field(..., pattern="^(csv|pdf)$", example="csv")

class ExportResponse(BaseModel):
    job_id: str
    status: str

class ExportStatusResponse(BaseModel):
    job_id: str
    scan_id: str
    format: str
    status: str
    created_at: str
    url: str | None = None
