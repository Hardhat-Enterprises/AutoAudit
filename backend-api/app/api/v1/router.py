from fastapi import APIRouter
from app.api.v1 import (
    auth,
    benchmarks,
    contact,
    evidence,
    m365_connections,
    platforms,
    scans,
    settings,
    test,
)

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router)

# Test routes
api_router.include_router(test.router)

# Platform routes (list available platforms)
api_router.include_router(platforms.router)

# Cloud connection routes
api_router.include_router(m365_connections.router)

# Scan routes
api_router.include_router(scans.router)

# Benchmark discovery routes
api_router.include_router(benchmarks.router)

# Evidence routes
api_router.include_router(evidence.router)

# Contact routes
api_router.include_router(contact.router)

# User settings routes
api_router.include_router(settings.router)
