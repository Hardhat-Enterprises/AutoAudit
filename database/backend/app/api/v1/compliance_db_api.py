# backend/app/api/v1/compliance_db_api.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...models.compliance_models import Scan, Issue
from ...schemas import compliance as compliance_schemas
from app.deps import get_current_user, get_db

router = APIRouter(prefix="/db", tags=["ComplianceDB"])

@router.post("/scan", response_model=compliance_schemas.ScanOut)
def create_scan(
    payload: compliance_schemas.ScanIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # create scan record
    scan = Scan(
        tenant_id=payload.tenant_id,
        status=payload.status or "completed",
        compliance_score=payload.compliance_score,
        total_controls=payload.total_controls,
        passed_count=payload.passed_count,
        failed_count=payload.failed_count,
        not_tested_count=payload.not_tested_count,
        notes=payload.notes
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # add issues if any
    for i in payload.issues or []:
        issue = Issue(
            scan_id=scan.id,
            rule_id=i.rule_id,
            priority=i.priority,
            title=i.title,
            description=i.description,
            result=i.result,
            evidence=i.evidence
        )
        db.add(issue)

    db.commit()
    db.refresh(scan)
    return scan

@router.get("/scan/latest", response_model=compliance_schemas.ScanReportOut)
def latest_scan(db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = db.query(Scan).order_by(Scan.id.desc()).first()
    if not s:
        raise HTTPException(status_code=404, detail="No scans found")
    # gather issues
    issues = db.query(Issue).filter(Issue.scan_id == s.id).all()
    return {"scan": s, "issues": issues}
