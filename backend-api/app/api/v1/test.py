from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.core.permissions import require_admin, require_auditor_or_above, RoleChecker
from app.models.user import User, Role

router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/public")
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


@router.get("/protected")
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


@router.get("/protected-admin")
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
