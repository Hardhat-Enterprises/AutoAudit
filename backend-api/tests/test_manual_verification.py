"""Unit/API tests for manual verification endpoints (no live server required)."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.models.user import User


def _execute_returning(single=None) -> MagicMock:
    result = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = []
    scalars.one_or_none.return_value = single
    result.scalars.return_value = scalars
    result.unique.return_value = result
    result.scalar_one_or_none.return_value = single
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("get", "/v1/manual-verification/99999", None),
        ("patch", "/v1/manual-verification/99999", {"comment": "x"}),
        ("delete", "/v1/manual-verification/99999", None),
        ("get", "/v1/manual-verification/by-scan-result/99999", None),
    ],
)
async def test_nonexistent_returns_404(
    client_factory,
    mock_db_session: AsyncMock,
    viewer_user: User,
    method: str,
    path: str,
    json_body: dict | None,
) -> None:
    mock_db_session.execute = AsyncMock(return_value=_execute_returning(single=None))

    client: AsyncClient = client_factory(viewer_user)
    async with client:
        kwargs = {"json": json_body} if json_body is not None else {}
        response = await getattr(client, method)(path, **kwargs)

    assert response.status_code == 404
