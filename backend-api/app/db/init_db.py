"""
Database initialization script for seeding default admin user.

Run this script to create the default admin user:
    python -m app.db.init_db
"""
import os
import asyncio
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.user import User, Role
from fastapi_users.password import PasswordHelper


async def init_db():
    """
    Optional database seeding for local/dev environments.

    IMPORTANT:
    - Passwords are stored hashed in the DB (see User.hashed_password).
    - We intentionally avoid hardcoding default credentials in code.
    """
    seed_enabled = os.environ.get("AUTOAUDIT_SEED_USERS", "").strip().lower() in ("1", "true", "yes")
    if not seed_enabled:
        print("Skipping user seed. Set AUTOAUDIT_SEED_USERS=true to enable.")
        return

    admin_email = os.environ.get("AUTOAUDIT_ADMIN_EMAIL", "").strip()
    admin_password = os.environ.get("AUTOAUDIT_ADMIN_PASSWORD", "").strip()
    if not admin_email or not admin_password:
        print(
            "Skipping user seed. Set AUTOAUDIT_ADMIN_EMAIL and AUTOAUDIT_ADMIN_PASSWORD "
            "to create an initial admin user."
        )
        return

    password_helper = PasswordHelper()

    async with async_session_maker() as session:
        # Check if admin user already exists
        result = await session.execute(
            select(User).where(User.email == admin_email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("Seed admin user already exists. Skipping seed.")
            return

        # Create default admin user
        admin_user = User(
            email=admin_email,
            hashed_password=password_helper.hash(admin_password),
            role=Role.ADMIN.value,
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )
        session.add(admin_user)
        await session.commit()

        print("[SUCCESS] Created default admin user with the following details.")
        print(f"  Email: {admin_email}")
        print("  Password: (set via AUTOAUDIT_ADMIN_PASSWORD)")
        print(f"  Role: {Role.ADMIN.value}")
        print("\nIMPORTANT: Ensure the admin password is reset at first login.")


if __name__ == "__main__":
    asyncio.run(init_db())
