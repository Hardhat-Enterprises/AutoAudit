from fastapi import APIRouter
from app.api.v1 import exports, audit, auth, test

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router)

# Test routes
api_router.include_router(test.router)

# Existing routes
api_router.include_router(exports.router)
api_router.include_router(audit.router)
