from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import NotFound, not_found_handler
from app.core.health import database_ready
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware

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

    @app.get("/readiness", tags=["Health"])
    async def readiness_check():
        """
        Check whether the API and database are ready to serve requests.
        """
        if not await database_ready():
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not_ready",
                    "checks": {
                        "database": "unavailable",
                    },
                },
            )

        return {
            "status": "ready",
            "checks": {
                "database": "ok",
            },
        }

    return app


app = create_app()