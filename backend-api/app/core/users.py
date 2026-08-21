"""
FastAPI Users configuration for authentication.

This file follows the official FastAPI Users setup pattern for SQLAlchemy with async support.
Official documentation: https://fastapi-users.github.io/fastapi-users/

Key components:
- UserManager: Handles user lifecycle events (registration, password reset, etc.)
- Authentication backend: JWT-based authentication with Bearer tokens
- Dependencies: get_user_db, get_user_manager for dependency injection
"""

import logging
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_async_session
from app.models.user import User
from app.models.oauth_account import OAuthAccount

settings = get_settings()
logger = logging.getLogger("api")


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """User manager for handling user operations."""

    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Called after user registration."""
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after a password reset is requested.

        The reset token is a credential and must never be written to logs in a
        deployed environment. In production it should be delivered to the user
        out of band, for example by email. Until an email integration exists,
        the token is only surfaced in a development environment so the flow can
        be tested end to end.
        """
        logger.info("Password reset requested for user %s", user.id)
        if settings.APP_ENV == "dev":
            # Development only: allows local testing of the reset flow.
            logger.info("DEV ONLY reset token for user %s: %s", user.id, token)
        # TODO: deliver the reset token to the user's email once mail sending exists.

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after an email verification is requested.

        Like the reset token, the verification token is a credential and must
        not be written to logs in a deployed environment. It is only surfaced in
        a development environment for local testing.
        """
        logger.info("Email verification requested for user %s", user.id)
        if settings.APP_ENV == "dev":
            # Development only.
            logger.info("DEV ONLY verification token for user %s: %s", user.id, token)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Dependency for getting the user database."""
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Dependency for getting the user manager."""
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """Get JWT strategy for authentication."""
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# Bearer transport for JWT tokens
bearer_transport = BearerTransport(tokenUrl="api/v1/auth/login")

# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Dependencies for getting current user
current_active_user = fastapi_users.current_user(active=True)
