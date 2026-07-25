"""
Database initialization script for seeding default admin user.

Run this script to create the default admin user:
    python -m app.db.init_db
"""

import asyncio

from fastapi_users.password import PasswordHelper
from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.user import Role, User


async def init_db():
    """
    Database seeding for local/dev environments.

    IMPORTANT:
    - Passwords are stored hashed in the DB (see User.hashed_password).
    - This script will create or update a default admin user for local development.
    """
    admin_email = "admin@example.com"
    admin_password = "admin"  # pragma: allowlist secret  # nosec B105

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
        print("  Default development credentials have been configured.")
        print("\nIMPORTANT: Change the default password after first login.")


if __name__ == "__main__":
    asyncio.run(init_db())