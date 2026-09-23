"""Unit tests for async session dependency."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db import session as session_mod


@pytest.mark.asyncio
async def test_get_async_session_yields_session() -> None:
    fake_session = AsyncMock()
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=fake_session)
    cm.__aexit__ = AsyncMock(return_value=None)

    with patch.object(session_mod, "async_session_maker", return_value=cm):
        agen = session_mod.get_async_session()
        yielded = await agen.__anext__()
        assert yielded is fake_session
        with pytest.raises(StopAsyncIteration):
            await agen.__anext__()
