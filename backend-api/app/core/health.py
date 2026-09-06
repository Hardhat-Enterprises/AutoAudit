"""Health-check helpers for the AutoAudit backend."""

from sqlalchemy import text

from app.db.base import engine


async def database_ready() -> bool:
    """
    Check whether the backend can communicate with the database.

    A lightweight SELECT 1 query is used so the readiness check
    does not read or modify application data.
    """
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        return True

    except Exception:  # pylint: disable=broad-exception-caught
        return False