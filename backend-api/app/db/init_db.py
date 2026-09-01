"""
Database initialization script for seeding default admin user.

Run this script to create the default admin user:
    python -m app.db.init_db
"""

import asyncio
import os

from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.user import User, Role
from fastapi_users.password import PasswordHelper


async def init_db():
    """
    Database seeding for local/dev environments.

    IMPORTANT:
    - Passwords are stored hashed in the DB.
    - Admin credentials are loaded from environment variables.
    - This script will create or update a default admin user.
    """

    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:
        raise RuntimeError("ADMIN_PASSWORD environment variable is not set")

    password_helper = PasswordHelper()

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.email == admin_email)
        )

        existing_user = result.unique().scalar_one_or_none()

        created = False

        if existing_user:
            admin_user = existing_user
        else:
            created = True
            admin_user = User(email=admin_email)
            session.add(admin_user)

        admin_user.hashed_password = password_helper.hash(admin_password)
        admin_user.role = Role.ADMIN.value
        admin_user.is_active = True
        admin_user.is_superuser = True
        admin_user.is_verified = True

        await session.commit()

        print(
            "[SUCCESS] Created default admin user."
            if created
            else "[SUCCESS] Updated default admin user."
        )

        print(f"  Email: {admin_email}")
        print(f"  Role: {Role.ADMIN.value}")
        print("\nIMPORTANT: Change this password after first login.")


if __name__ == "__main__":
    asyncio.run(init_db())