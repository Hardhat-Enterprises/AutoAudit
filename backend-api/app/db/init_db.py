"""
Database initialization script for seeding default admin user.

Run this script to create the default admin user:
    python -m app.db.init_db
"""
import asyncio
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.user import User, Role
from fastapi_users.password import PasswordHelper


async def init_db():
    """Initialize database with default admin user."""
    password_helper = PasswordHelper()

    async with async_session_maker() as session:
        # Check if admin user already exists
        result = await session.execute(
            select(User).where(User.email == "admin@example.com")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("Admin user already exists. Skipping seed.")
            return

        # Create default admin user
        admin_user = User(
            email="admin@example.com",
            hashed_password=password_helper.hash("admin"),
            role=Role.ADMIN.value,
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )

        session.add(admin_user)
        await session.commit()

        print("[SUCCESS] Created default admin user with the following details.")
        print(f"  Email: admin@example.com")
        print(f"  Password: admin")
        print(f"  Role: {Role.ADMIN.value}")
        print("\nIMPORTANT: We need to make sure the default password is reset at first login.")


if __name__ == "__main__":
    asyncio.run(init_db())
