"""FastAPI service for PowerShell cmdlet execution."""

from fastapi import FastAPI, HTTPException

from schemas import ExecuteRequest, ExecuteResponse, HealthResponse
from executor import execute_cmdlet, PowerShellExecutionError

app = FastAPI(
    title="PowerShell Service",
    description="HTTP service for executing M365 PowerShell cmdlets",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


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
