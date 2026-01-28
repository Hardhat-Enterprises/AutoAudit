from fastapi import Depends
from app.core.users import current_active_user
from app.models.user import User


async def get_current_user(user: User = Depends(current_active_user)) -> User:
    """
    Dependency for getting the current authenticated user.

    Usage:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user": user.email}
    """
    return user
