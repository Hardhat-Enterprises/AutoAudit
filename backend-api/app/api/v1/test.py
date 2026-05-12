from celery import Celery
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.core.config import get_settings
from app.core.permissions import RoleChecker, require_admin, require_auditor_or_above
from app.models.user import Role, User

settings = get_settings()

router = APIRouter(prefix="/test", tags=["Test"])


# --- Synthetic load lever ---------------------------------------------------
#
# These endpoints exist solely to drive load tests of the scaling stack. They
# are gated by both:
#   * Helm: synthetic.enabled=true (controls whether SYNTHETIC_ENABLED reaches
#     the pod env)
#   * Runtime: APP_ENV != "prod" (so even an accidental flag flip in a prod
#     namespace is still rejected)
# A request that fails either gate gets a 404, not a 403, so probes can't be
# used to detect whether the lever exists.


class SyntheticScanRequest(BaseModel):
    n_graph: int = Field(0, ge=0, le=2000, description="Tasks to enqueue on controls.graph")
    n_powershell: int = Field(
        0, ge=0, le=500, description="Tasks to enqueue on controls.powershell"
    )
    sleep_ms: int = Field(1000, ge=0, le=120000, description="Sleep per task (ms)")
    cpu_burn_ms: int = Field(0, ge=0, le=10000, description="Tight-loop CPU per task (ms)")
    call_powershell_service: bool = Field(
        False,
        description=(
            "If true, controls.powershell tasks call /execute/synthetic on the "
            "powershell-service to drive its HPA in lockstep."
        ),
    )


def _require_synthetic_enabled() -> None:
    if settings.APP_ENV.lower() == "prod" or not settings.SYNTHETIC_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/synthetic-scan", summary="Enqueue synthetic worker tasks for load demos")
async def synthetic_scan(
    request: SyntheticScanRequest,
    _: User = Depends(get_current_user),
):
    """Enqueue N synthetic_evaluate tasks across the worker queues. Gated to
    non-prod environments only; see module docstring."""
    _require_synthetic_enabled()

    # We construct a thin Celery client here rather than importing the worker
    # module (which would pull collector/policy code into the API image).
    client = Celery("autoaudit_synthetic", broker=settings.REDIS_URL)

    common = {"sleep_ms": request.sleep_ms, "cpu_burn_ms": request.cpu_burn_ms}

    for _i in range(request.n_graph):
        client.send_task(
            "worker.tasks.synthetic_evaluate",
            kwargs={**common, "call_powershell_service": False},
            queue="controls.graph",
        )
    for _i in range(request.n_powershell):
        client.send_task(
            "worker.tasks.synthetic_evaluate",
            kwargs={**common, "call_powershell_service": request.call_powershell_service},
            queue="controls.powershell",
        )

    return {
        "queued": {"graph": request.n_graph, "powershell": request.n_powershell},
        "params": common,
    }


@router.get("/public", summary="Test public endpoint")
async def public_endpoint():
    """
    Public endpoint - no authentication required.

    This endpoint is accessible without a valid JWT token.
    """
    return {
        "message": "This is a public endpoint",
        "requires_auth": False,
        "description": "Anyone can access this endpoint without authentication"
    }


@router.get("/protected", summary="Test endpoint that requires authentication only")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    """
    Protected endpoint - requires authentication.

    This endpoint requires a valid JWT token in the Authorization header.
    Returns information about the authenticated user.
    """
    return {
        "message": "This is a protected endpoint",
        "requires_auth": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "is_superuser": current_user.is_superuser,
        },
        "description": "You successfully accessed a protected endpoint!"
    }


@router.get("/protected-admin", summary="Test endpoint that requires authentication AND authorization (admin role)")
async def protected_admin_endpoint(current_user: User = Depends(require_admin)):
    """
    Admin-only endpoint - requires authentication AND admin role.

    This endpoint requires:
    - Valid JWT token in Authorization header
    - User must have 'admin' role

    Returns 403 Forbidden if user is authenticated but not an admin.
    """
    return {
        "message": "This is an admin-only endpoint",
        "requires_auth": True,
        "requires_role": "admin",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
        },
        "description": "You have admin access!",
        "admin_features": [
            "Manage users",
            "View all audit logs",
            "Configure system settings"
        ]
    }


@router.get("/protected-auditor")
async def protected_auditor_endpoint(current_user: User = Depends(require_auditor_or_above)):
    """
    Auditor or Admin endpoint - requires authentication AND auditor/admin role.

    This endpoint requires:
    - Valid JWT token in Authorization header
    - User must have 'auditor' or 'admin' role

    Returns 403 Forbidden if user is authenticated but only has 'viewer' role.
    """
    return {
        "message": "This is an auditor or admin endpoint",
        "requires_auth": True,
        "requires_role": ["auditor", "admin"],
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
        },
        "description": f"You have {current_user.role} access!",
        "auditor_features": [
            "Run compliance scans",
            "Generate audit reports",
            "View scan results"
        ]
    }
