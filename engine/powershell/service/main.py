"""FastAPI service for PowerShell cmdlet execution."""

import asyncio
import os
import time

from fastapi import FastAPI, HTTPException, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from schemas import ExecuteRequest, ExecuteResponse, HealthResponse
from executor import execute_cmdlet, PowerShellExecutionError
from metrics import (
    pwsh_active_subprocesses,
    pwsh_execution_duration_seconds,
    pwsh_executions_total,
)

app = FastAPI(
    title="PowerShell Service",
    description="HTTP service for executing M365 PowerShell cmdlets",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    """Prometheus scrape endpoint. Drives the scaling dashboard and (eventually)
    HPA's custom-metrics path via Prometheus Adapter."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# --- Synthetic load lever ---------------------------------------------------


class SyntheticExecuteRequest(BaseModel):
    sleep_ms: int = Field(1000, ge=0, le=120000)
    cpu_burn_ms: int = Field(0, ge=0, le=10000)


def _synthetic_enabled() -> bool:
    return os.environ.get("SYNTHETIC_ENABLED", "").lower() in {"1", "true", "yes"}


@app.post("/execute/synthetic", include_in_schema=False)
async def execute_synthetic(request: SyntheticExecuteRequest):
    """Synthetic load lever — simulates a pwsh execution without spawning one.

    Reuses the same metrics as real executions (`pwsh_active_subprocesses`,
    `pwsh_execution_duration_seconds`, `pwsh_executions_total`) so HPA and
    Grafana panels see the same shape under demo load as they would under
    real load. Gated to non-prod via SYNTHETIC_ENABLED.
    """
    if not _synthetic_enabled():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    pwsh_active_subprocesses.inc()
    start = time.monotonic()
    try:
        if request.cpu_burn_ms > 0:
            deadline = time.monotonic() + request.cpu_burn_ms / 1000.0
            while time.monotonic() < deadline:
                pass
        if request.sleep_ms > 0:
            await asyncio.sleep(request.sleep_ms / 1000.0)
        return {"ok": True, "sleep_ms": request.sleep_ms, "cpu_burn_ms": request.cpu_burn_ms}
    finally:
        pwsh_active_subprocesses.dec()
        pwsh_execution_duration_seconds.labels(module="synthetic").observe(
            time.monotonic() - start
        )
        pwsh_executions_total.labels(module="synthetic", outcome="success").inc()


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """Execute a PowerShell cmdlet.

    Args:
        request: Execution request with module, cmdlet, params, and auth

    Returns:
        ExecuteResponse with success status and data or error
    """
    try:
        result = execute_cmdlet(
            module=request.module,
            cmdlet=request.cmdlet,
            params=request.params,
            tenant_id=request.tenant_id,
            token=request.token,
            graph_token=request.graph_token,
        )
        return ExecuteResponse(success=True, data=result)
    except ValueError as e:
        # Invalid request (e.g., Teams without graph_token)
        raise HTTPException(status_code=400, detail=str(e))
    except PowerShellExecutionError as e:
        # PowerShell execution failed
        return ExecuteResponse(success=False, error=str(e))
    except Exception as e:
        # Unexpected error
        return ExecuteResponse(success=False, error=f"Unexpected error: {e}")
