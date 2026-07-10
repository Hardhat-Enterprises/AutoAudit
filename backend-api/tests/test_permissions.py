"""Unit tests for RBAC permission dependencies."""

import pytest
from fastapi import HTTPException

from app.core.permissions import (
    RoleChecker,
    require_admin,
    require_auditor_or_above,
    require_viewer_or_above,
)
from app.models.user import Role
from tests.conftest import make_user


def test_require_auditor_or_above_allows_admin():
    user = make_user(role=Role.ADMIN.value)

    result = require_auditor_or_above(user=user)

    assert result is user


def test_require_auditor_or_above_allows_auditor():
    user = make_user(role=Role.AUDITOR.value)

    result = require_auditor_or_above(user=user)

    assert result is user


def test_require_auditor_or_above_rejects_viewer():
    user = make_user(role=Role.VIEWER.value)

    with pytest.raises(HTTPException) as exc_info:
        require_auditor_or_above(user=user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Auditor or Admin access required"


def test_require_admin_allows_admin():
    user = make_user(role=Role.ADMIN.value)

    result = require_admin(user=user)

    assert result is user


def test_require_admin_rejects_auditor():
    user = make_user(role=Role.AUDITOR.value)

    with pytest.raises(HTTPException) as exc_info:
        require_admin(user=user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Admin access required"


def test_require_viewer_or_above_allows_viewer():
    user = make_user(role=Role.VIEWER.value)

    result = require_viewer_or_above(user=user)

    assert result is user


def test_role_checker_allows_listed_roles():
    checker = RoleChecker([Role.ADMIN, Role.AUDITOR])
    auditor = make_user(role=Role.AUDITOR.value)

    result = checker(user=auditor)

    assert result is auditor


def test_role_checker_rejects_unlisted_role():
    checker = RoleChecker([Role.ADMIN])
    viewer = make_user(role=Role.VIEWER.value)

    with pytest.raises(HTTPException) as exc_info:
        checker(user=viewer)

    assert exc_info.value.status_code == 403
    assert "Insufficient permissions" in exc_info.value.detail
