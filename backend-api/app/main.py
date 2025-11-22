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

    # Allow the React dev server (localhost:3000/3001) and other frontends to call the API.
    # In production, set ALLOWED_ORIGINS via env to restrict as needed.
    allowed_origins = getattr(settings, "ALLOWED_ORIGINS", []) or [
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    # Starlette disallows allow_credentials=True with "*" origins. If the user really
    # wants "*", we turn off credentials but keep the open origin for dev convenience.
    allow_credentials = "*" not in allowed_origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
