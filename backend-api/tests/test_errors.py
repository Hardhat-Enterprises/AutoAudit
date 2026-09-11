"""Unit tests for Problem Details helpers and NotFound handler."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.core.errors import NotFound, not_found_handler, problem


def test_problem_without_detail() -> None:
    response = problem(status=400, title="Bad Request")
    assert response.status_code == 400
    assert response.body  # JSONResponse
    payload = response.body.decode()
    assert "Bad Request" in payload
    assert "detail" not in payload


def test_problem_with_detail() -> None:
    response = problem(status=404, title="Not Found", detail="gone")
    assert response.status_code == 404
    assert b"gone" in response.body


def test_not_found_exception_sets_detail() -> None:
    exc = NotFound("Widget")
    assert exc.status_code == 404
    assert exc.detail == "Widget not found"
    assert exc.resource == "Widget"


@pytest.mark.asyncio
async def test_not_found_handler() -> None:
    request = MagicMock()
    response = await not_found_handler(request, NotFound("Scan"))
    assert response.status_code == 404
    assert b"Scan not found" in response.body
