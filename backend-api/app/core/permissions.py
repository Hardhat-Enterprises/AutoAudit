"""
Role-based access control (RBAC) dependencies.

These dependencies check if the current user has the required role.
"""
from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user
from app.models.user import User, Role


class RoleChecker:
    """Dependency class for checking user roles."""

    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        """Check if user has one of the allowed roles."""
        if user.role not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {[r.value for r in self.allowed_roles]}"
            )
        return user


# Convenience functions for common role checks
def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require user to be an admin."""
    if user.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


def require_auditor_or_above(user: User = Depends(get_current_user)) -> User:
    """Require user to be auditor or admin."""
    if user.role not in [Role.ADMIN.value, Role.AUDITOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auditor or Admin access required"
        )
    return user


def require_viewer_or_above(user: User = Depends(get_current_user)) -> User:
    """Require user to be viewer, auditor, or admin (i.e., any authenticated user)."""
    # All authenticated users are at least viewers
    return user
