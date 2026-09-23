"""Application health endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.health import ReadinessResponse

router = APIRouter(tags=["Health"])


@router.get("/liveness")
def liveness_check():
    return {"status": "healthy"}


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    summary="Check whether the API is ready to serve requests",
    responses={
        503: {
            "model": ReadinessResponse,
            "description": "Required dependency is unavailable",
        }
    },
)
async def readiness_check(
    db: AsyncSession = Depends(get_async_session),
):
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready"},
        )

    return ReadinessResponse(status="ready")