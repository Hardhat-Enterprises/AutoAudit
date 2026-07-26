from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import NotFound, not_found_handler
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.db.session import get_async_session
from app.schemas.health import ReadinessResponse

settings = get_settings()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="AutoAudit API", version="0.1.0")

    # RequestLoggingMiddleware must be added before CORSMiddleware
    # (middleware executes in reverse order - last added runs first)
    app.add_middleware(RequestLoggingMiddleware)

    # Allow the configured frontend to make credentialed API requests.
    # Expose X-Request-ID so the frontend can use it when reporting errors.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL.rstrip("/")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Error handler
    app.add_exception_handler(NotFound, not_found_handler)

    @app.get("/")
    def root():
        return {
            "status": "ok",
            "message": "AutoAudit API running",
        }

    @app.get("/liveness")
    def health_check():
        return {
            "status": "healthy",
        }

    @app.get(
        "/readiness",
        response_model=ReadinessResponse,
        tags=["Health"],
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

    @app.get("/liveness")
    def liveness():
        return {"status": "healthy"}

    @app.get("/version")
    def version():
        return {
            "version": app.version,
            "name": app.title,
        }

    return app


app = create_app()
