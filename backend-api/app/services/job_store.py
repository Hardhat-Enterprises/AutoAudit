from uuid import uuid4
from datetime import datetime

jobs = {}

def create_export_job(scan_id: str, fmt: str) -> str:
    job_id = str(uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "scan_id": scan_id,
        "format": fmt,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "url": None
    }
    # Simulate immediate completion as a test
    jobs[job_id]["status"] = "completed"
    jobs[job_id]["url"] = f"http://localhost:3000/downloads/{scan_id}.{fmt}"
    return job_id

def get_job_status(job_id: str):
    return jobs.get(job_id)
