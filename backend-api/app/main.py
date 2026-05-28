from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import health
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import NotFound, not_found_handler
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware

settings = get_settings()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="AutoAudit API", version="0.1.0")

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

    # Health endpoints live at the root, not under the /v1 API prefix, so probes
    # and load balancers can hit them with a single static path regardless of
    # API version evolution.
    app.include_router(health.router)

    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Prometheus instrumentation. Exposes /metrics with RED-style HTTP metrics
    # (request count, request duration histogram, in-progress requests). Mounted
    # at the root path; PodMonitor scrapes it directly. Excludes /metrics and
    # /healthz routes from being instrumented (they'd dominate the cardinality).
    Instrumentator(
        excluded_handlers=["/metrics", "/healthz", "/healthz/live"],
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

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
