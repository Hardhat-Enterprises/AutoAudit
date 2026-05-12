"""Health-check endpoints used by Kubernetes probes and load balancers.

`/healthz/live` is the liveness signal — returns OK as long as the process is
running. It must NOT depend on DB / Redis / OPA, because liveness failures
trigger pod restarts and a downstream outage shouldn't cascade into restart
loops.

`/healthz` is the readiness signal — checks that DB, Redis, and OPA are
reachable. A failure here pulls the pod out of the Service endpoint pool but
does not restart it.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Literal

import httpx
import redis.asyncio as redis_async
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import async_session_maker

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


@router.get("/healthz/live", tags=["health"])
async def liveness() -> dict[str, str]:
    """Process-alive signal. Used by Kubernetes livenessProbe."""
    return {"status": "ok"}


async def _check_db(timeout: float = 2.0) -> tuple[Literal["ok", "error"], str | None]:
    try:
        async with async_session_maker() as session:
            await asyncio.wait_for(session.execute(text("SELECT 1")), timeout=timeout)
        return "ok", None
    except Exception as exc:
        logger.warning("healthz: DB check failed: %s", exc)
        return "error", str(exc)


async def _check_redis(timeout: float = 2.0) -> tuple[Literal["ok", "error"], str | None]:
    try:
        client = redis_async.from_url(settings.REDIS_URL, socket_timeout=timeout)
        try:
            await asyncio.wait_for(client.ping(), timeout=timeout)
        finally:
            await client.aclose()
        return "ok", None
    except Exception as exc:
        logger.warning("healthz: Redis check failed: %s", exc)
        return "error", str(exc)


async def _check_opa(timeout: float = 2.0) -> tuple[Literal["ok", "error"], str | None]:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{settings.OPA_URL}/health")
            resp.raise_for_status()
        return "ok", None
    except Exception as exc:
        logger.warning("healthz: OPA check failed: %s", exc)
        return "error", str(exc)


@router.get("/healthz", tags=["health"])
async def readiness() -> JSONResponse:
    """Dependency-aware readiness check. Used by Kubernetes readinessProbe."""
    db_status, db_err = await _check_db()
    redis_status, redis_err = await _check_redis()
    opa_status, opa_err = await _check_opa()

    payload = {
        "status": "ok"
        if db_status == redis_status == opa_status == "ok"
        else "degraded",
        "checks": {
            "db": {"status": db_status, "error": db_err},
            "redis": {"status": redis_status, "error": redis_err},
            "opa": {"status": opa_status, "error": opa_err},
        },
    }

    code = status.HTTP_200_OK if payload["status"] == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(payload, status_code=code)
