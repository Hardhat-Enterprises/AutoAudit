from fastapi import APIRouter
from app.api.v1 import exports, audit, evidence  

api_router = APIRouter()
api_router.include_router(exports.router)
api_router.include_router(audit.router)
api_router.include_router(evidence.router)
