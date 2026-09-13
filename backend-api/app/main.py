# pylint: disable=line-too-long,missing-function-docstring,broad-exception-caught
"""AutoAudit Backend API Application Entry Point."""

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import NotFound, not_found_handler
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.db.session import get_async_session
from app.schemas.health import ReadinessResponse

settings = get_settings()


class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    """Rejects payload requests exceeding max_upload_size before FastAPI spools files."""

    def __init__(self, app, max_upload_size: int = 12 * 1024 * 1024):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "POST" and "/evidence/scan" in request.url.path:
            content_length = request.headers.get("content-length")
            transfer_encoding = request.headers.get("transfer-encoding", "").lower()

            if content_length and int(content_length) > self.max_upload_size:
                return Response(
                    content="Security Violation: File size exceeds 10 MB limit.",
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )

            if transfer_encoding == "chunked" and not content_length:
                return Response(
                    content="Security Violation: Chunked transfers without Content-Length not permitted for scans.",
                    status_code=status.HTTP_411_LENGTH_REQUIRED,
                )

        return await call_next(request)


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="AutoAudit API", version="0.1.0")

    app.add_middleware(LimitUploadSizeMiddleware, max_upload_size=12 * 1024 * 1024)
    app.add_middleware(RequestLoggingMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL.rstrip("/")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    app.include_router(api_router, prefix=settings.API_PREFIX)
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

    return app


app = create_app()
