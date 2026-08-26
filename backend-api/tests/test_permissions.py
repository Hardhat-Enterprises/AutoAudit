"""Unit tests for RBAC permission helpers."""

import pytest
from fastapi import HTTPException

from app.core.permissions import (
    RoleChecker,
    require_admin,
    require_auditor_or_above,
    require_viewer_or_above,
)
from app.models.user import Role, User
from tests.conftest import make_user


def test_require_admin_allows_admin(admin_user: User) -> None:
    assert require_admin(admin_user) is admin_user


def test_require_admin_rejects_viewer(viewer_user: User) -> None:
    with pytest.raises(HTTPException) as exc:
        require_admin(viewer_user)
    assert exc.value.status_code == 403


def test_require_auditor_or_above_allows_auditor(auditor_user: User) -> None:
    assert require_auditor_or_above(auditor_user) is auditor_user


def test_require_auditor_or_above_rejects_viewer(viewer_user: User) -> None:
    with pytest.raises(HTTPException) as exc:
        require_auditor_or_above(viewer_user)
    assert exc.value.status_code == 403


def test_require_viewer_or_above_allows_any_authenticated(viewer_user: User) -> None:
    assert require_viewer_or_above(viewer_user) is viewer_user


def test_role_checker_allows_matching_role(admin_user: User) -> None:
    checker = RoleChecker([Role.ADMIN])
    assert checker(admin_user) is admin_user


def test_role_checker_rejects_non_matching_role(viewer_user: User) -> None:
    checker = RoleChecker([Role.ADMIN])
    with pytest.raises(HTTPException) as exc:
        checker(viewer_user)
    assert exc.value.status_code == 403


def test_make_user_defaults() -> None:
    user = make_user(role=Role.VIEWER.value)
    assert user.email.endswith("@example.com")
    assert user.is_active is True
