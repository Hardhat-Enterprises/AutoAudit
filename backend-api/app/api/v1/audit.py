from fastapi import APIRouter, Query
from app.models.audit import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit"])

# Mock audit log store
logs = [
    {"timestamp": "2025-09-18T02:00:00Z", "action": "scan_started", "resource": "scan", "id": "s-001"},
    {"timestamp": "2025-09-18T02:01:00Z", "action": "scan_completed", "resource": "scan", "id": "s-001"}
]

@router.get("/logs", response_model=list[AuditLog])
def get_audit_logs(resource: str, id: str, limit: int = Query(100, le=500)):
    filtered = [log for log in logs if log["resource"] == resource and log["id"] == id]
    return filtered[:limit]
