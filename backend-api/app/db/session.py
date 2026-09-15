from collections.abc import AsyncGenerator

from app.db.base import engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with async_session_maker() as session:
        yield session
