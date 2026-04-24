import os
import sys
from unittest.mock import MagicMock

# Set before any app imports so app/db/base.py creates the engine at module load time
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only")
os.environ.setdefault("ENCRYPTION_KEY", "Ps-HiS3ww5QzQPc_Mdu5-JyA_jCNbdFHMdiwWSlAfgM=")

# Mock optional heavy dependencies from the evidence extra so the app can be imported without the full OCR stack installed
for _mod in [
    "pytesseract",
    "PIL", "PIL.Image", "PIL.UnidentifiedImageError",
    "fitz", "cv2",
    "docx", "docx.shared", "docx.enum", "docx.enum.text",
    "fpdf", "fpdf.FPDF",
    "tabulate",
]:
    sys.modules.setdefault(_mod, MagicMock())

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_async_session
from app.models.user import User
from app.models.oauth_account import OAuthAccount
from app.models.user_settings import UserSettings

# Tables needed for auth tests
_AUTH_TABLES = [User.__table__, OAuthAccount.__table__, UserSettings.__table__]


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: Base.metadata.create_all(c, tables=_AUTH_TABLES))

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_async_session] = override_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    await engine.dispose()
