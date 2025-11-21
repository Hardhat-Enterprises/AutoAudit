from fastapi import APIRouter

from app.api.v1 import audit, evidence, exports, strategies

api_router = APIRouter()
api_router.include_router(strategies.router)
api_router.include_router(evidence.router)
api_router.include_router(exports.router)
api_router.include_router(audit.router)
