"""AutoAudit FastAPI Application Entry Point."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import NotFound, not_found_handler
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.users import current_active_superuser
from app.db.session import get_async_session
from app.schemas.health import ReadinessResponse

settings = get_settings()


class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce maximum payload size limit on incoming requests."""

    def __init__(self, app, max_upload_size: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_upload_size:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Security Violation: File size exceeds 10 MB limit."},
                )
        return await call_next(request)


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="AutoAudit API", version="0.1.0")

    # Enforce 10 MB payload size limit middleware
    app.add_middleware(LimitUploadSizeMiddleware)

    # RequestLoggingMiddleware must be added before CORSMiddleware
    # (middleware executes in reverse order - last added runs first)
    app.add_middleware(RequestLoggingMiddleware)

    # Allow the configured frontend to make credentialed API requests.
    # Expose X-Request-ID so the frontend can use it when reporting errors.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL.rstrip("/")],  # Explicit origin required when credentials are True
        allow_credentials=True,                               # Must be True to allow HttpOnly auth cookies
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

    # Initialize Prometheus Instrumentator and expose the /metrics endpoint.
    # Restricted to superusers: this exposes internal request/latency data
    # (endpoint paths, traffic volume, timing) that shouldn't be public.
    Instrumentator().instrument(app).expose(
        app, dependencies=[Depends(current_active_superuser)]
    )

    return app


app = create_app()
