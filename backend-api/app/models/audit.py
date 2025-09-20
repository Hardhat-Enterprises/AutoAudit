from pydantic import BaseModel

class AuditLog(BaseModel):
    timestamp: str
    action: str
    resource: str
    id: str
