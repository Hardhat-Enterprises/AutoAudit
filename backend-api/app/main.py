from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.middleware import RequestLoggingMiddleware
from app.core.errors import not_found_handler, NotFound

settings = get_settings()
#builds the project using uvicorn and fastapi

def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="AutoAudit API", version="0.1.0")

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # error handler
    app.add_exception_handler(NotFound, not_found_handler)

    @app.get("/")
    def root():
        return {"status": "ok", "message": "AutoAudit API running"}

    return app

app = create_app()
