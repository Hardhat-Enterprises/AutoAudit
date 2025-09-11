from fastapi import FastAPI
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.core.config import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="AutoAudit API", version="0.1.0")
    app.include_router(api_router, prefix=settings.API_PREFIX)
    return app


app = create_app()
