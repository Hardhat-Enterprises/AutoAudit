from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import NotFound, not_found_handler
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware

settings = get_settings()


class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    """Rejects payload requests exceeding max_upload_size via Content-Length header before spooling."""

    def __init__(self, app, max_upload_size: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "POST" and "/evidence/scan" in request.url.path:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_upload_size:
                return Response(
                    content="Security Violation: File size exceeds 10 MB limit.",
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
        return await call_next(request)


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="AutoAudit API", version="0.1.0")

    # Add ASGI upload cap middleware before request logging
    app.add_middleware(LimitUploadSizeMiddleware, max_upload_size=10 * 1024 * 1024)

    # RequestLoggingMiddleware must be added before CORSMiddleware
    # (middleware executes in reverse order - last added runs first)
    app.add_middleware(RequestLoggingMiddleware)

    # Allow frontend (localhost:3000 and others) to call the API during development.
    # CORS must be added last so it runs first and wraps all responses including errors.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # permissive for dev; adjust in prod
        allow_credentials=False,  # must be False when using wildcard origins
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # error handler
    app.add_exception_handler(NotFound, not_found_handler)

    @app.get("/")
    def root():
        return {"status": "ok", "message": "AutoAudit API running"}

    @app.get("/liveness")
    def health_check():
        return {
            "status": "healthy",
        }

    return app


app = create_app()
