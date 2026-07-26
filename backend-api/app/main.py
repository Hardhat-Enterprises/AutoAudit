from fastapi import FastAPI
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.middleware import RequestLoggingMiddleware
from app.core.errors import not_found_handler, NotFound

settings = get_settings()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="AutoAudit API", version="0.1.0")

    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # error handler
    app.add_exception_handler(NotFound, not_found_handler)

    @app.get("/")
    def root():
        return {"status": "ok", "message": "AutoAudit API running"}

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
