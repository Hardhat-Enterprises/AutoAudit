"""Unit tests for BackupRestoreDataCollector.

Tests _collect_detected_vendors in isolation using a mocked GraphClient,
since this repo does not have pytest-asyncio installed. Async methods are
run via asyncio.run() inside plain sync test functions rather than using
async def test_... directly, which pytest would not await and would pass
silently without testing anything.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

from collectors.m365.backup_restore import BackupRestoreDataCollector


def _make_client(service_principals: list[dict]) -> AsyncMock:
    """Build a mocked GraphClient whose get_all_pages returns the given
    service principals for any call (only /servicePrincipals is exercised
    by _collect_detected_vendors)."""
    client = AsyncMock()
    client.get_all_pages.return_value = service_principals
    return client


def test_detects_single_known_vendor():
    client = _make_client(
        [
            {"displayName": "Veeam Data Cloud for Microsoft 365"},
            {"displayName": "Some Unrelated App"},
        ]
    )
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector._collect_detected_vendors(client))

    assert result == [
        {
            "vendor": "Veeam",
            "matched_app_name": "Veeam Data Cloud for Microsoft 365",
        }
    ]


def test_detects_multiple_known_vendors():
    client = _make_client(
        [
            {"displayName": "Rubrik Management Enterprise App"},
            {"displayName": "Cloud Backup for Office 365 - Prod (transact)"},
        ]
    )
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector._collect_detected_vendors(client))
    vendors_found = {v["vendor"] for v in result}

    assert vendors_found == {"Rubrik", "AvePoint"}
    assert len(result) == 2


def test_no_vendors_detected_when_none_present():
    client = _make_client(
        [
            {"displayName": "Microsoft Graph"},
            {"displayName": "Some Custom Internal App"},
        ]
    )
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector._collect_detected_vendors(client))

    assert result == []


def test_no_false_positive_on_partial_name_match():
    # A name that merely contains "Veeam" but does not exactly match any
    # known app name should not be treated as a detection. Matching is
    # exact, not substring based, to avoid false positives from unrelated
    # apps that happen to mention a vendor's name.
    client = _make_client(
        [
            {"displayName": "Veeam Data Cloud for Microsoft 365 - Test Copy"},
        ]
    )
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector._collect_detected_vendors(client))

    assert result == []


def test_empty_service_principal_list_returns_empty():
    client = _make_client([])
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector._collect_detected_vendors(client))

    assert result == []


def test_calls_expected_graph_endpoint():
    client = _make_client([])
    collector = BackupRestoreDataCollector()

    asyncio.run(collector._collect_detected_vendors(client))

    client.get_all_pages.assert_awaited_once_with("/servicePrincipals")


# --- _collect_protection_policies ---

def test_collect_protection_policies_parses_service_and_status():
    client = AsyncMock()
    client.get_all_pages.return_value = [
        {"id": "p1", "@odata.type": "#microsoft.graph.exchangeProtectionPolicy", "status": "active"},
        {"id": "p2", "@odata.type": "#microsoft.graph.sharePointProtectionPolicy", "status": "inactive"},
    ]
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector._collect_protection_policies(client))

    assert result == [
        {"id": "p1", "service": "exchangeProtectionPolicy", "status": "active"},
        {"id": "p2", "service": "sharePointProtectionPolicy", "status": "inactive"},
    ]
    client.get_all_pages.assert_awaited_once_with("/solutions/backupRestore/protectionPolicies")


def test_collect_protection_policies_empty_list():
    client = AsyncMock()
    client.get_all_pages.return_value = []
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector._collect_protection_policies(client))

    assert result == []


# --- _collect_recent_restore_points ---

def test_collect_recent_restore_points_maps_protection_unit_type():
    client = AsyncMock()
    client.get_all_pages.return_value = [
        {
            "id": "rp1",
            "protectionDateTime": "2026-08-27T00:00:00Z",
            "expirationDateTime": "2027-08-27T00:00:00Z",
            "protectionUnit": {"@odata.type": "#microsoft.graph.mailboxProtectionUnit"},
        },
    ]
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector._collect_recent_restore_points(client))

    assert result == [
        {
            "id": "rp1",
            "protectionDateTime": "2026-08-27T00:00:00Z",
            "expirationDateTime": "2027-08-27T00:00:00Z",
            "protectionUnitType": "mailboxProtectionUnit",
        }
    ]


def test_collect_recent_restore_points_sends_required_filter_and_expand():
    client = AsyncMock()
    client.get_all_pages.return_value = []
    collector = BackupRestoreDataCollector()

    asyncio.run(collector._collect_recent_restore_points(client))

    args, kwargs = client.get_all_pages.call_args
    assert args[0] == "/solutions/backupRestore/restorePoints"
    assert "$filter" in kwargs["params"]
    assert kwargs["params"]["$expand"] == "protectionUnit"
    assert "protectionDateTime gt" in kwargs["params"]["$filter"]


def test_collect_recent_restore_points_missing_protection_unit_does_not_crash():
    client = AsyncMock()
    client.get_all_pages.return_value = [
        {"id": "rp1", "protectionDateTime": "2026-08-27T00:00:00Z", "expirationDateTime": None}
    ]
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector._collect_recent_restore_points(client))

    assert result[0]["protectionUnitType"] == ""


# --- _collect_restore_sessions ---

def test_collect_restore_sessions_returns_all_without_filtering():
    client = AsyncMock()
    client.get_all_pages.return_value = [
        {"id": "s1", "status": "succeeded", "createdDateTime": "2020-01-01T00:00:00Z"},
        {"id": "s2", "status": "succeeded", "createdDateTime": "2026-06-01T00:00:00Z"},
    ]
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector._collect_restore_sessions(client))

    assert len(result) == 2
    client.get_all_pages.assert_awaited_once_with("/solutions/backupRestore/restoreSessions")


# --- _collect_backup_admin_roles ---

def test_collect_backup_admin_roles_finds_all_three_with_members():
    client = AsyncMock()
    client.get_directory_roles.return_value = [
        {"id": "r1", "displayName": "Microsoft 365 Backup Administrator"},
        {"id": "r2", "displayName": "SharePoint Backup Administrator"},
        {"id": "r3", "displayName": "Exchange Backup Administrator"},
    ]
    client.get_role_members.return_value = [
        {"id": "u1", "userPrincipalName": "a@x.com", "displayName": "A", "@odata.type": "#microsoft.graph.user"},
        {"id": "g1", "@odata.type": "#microsoft.graph.group"},
    ]
    collector = BackupRestoreDataCollector()

    roles, not_found = asyncio.run(collector._collect_backup_admin_roles(client))

    assert len(roles) == 3
    assert not_found == []
    for r in roles:
        assert r["member_count"] == 1
        assert len(r["members"]) == 1
        assert r["members"][0]["id"] == "u1"


def test_collect_backup_admin_roles_reports_roles_not_found():
    client = AsyncMock()
    client.get_directory_roles.return_value = [
        {"id": "r1", "displayName": "Microsoft 365 Backup Administrator"},
    ]
    client.get_role_members.return_value = []
    collector = BackupRestoreDataCollector()

    roles, not_found = asyncio.run(collector._collect_backup_admin_roles(client))

    assert len(roles) == 1
    assert set(not_found) == {
        "SharePoint Backup Administrator",
        "Exchange Backup Administrator",
    }


def test_collect_backup_admin_roles_none_activated():
    client = AsyncMock()
    client.get_directory_roles.return_value = []
    collector = BackupRestoreDataCollector()

    roles, not_found = asyncio.run(collector._collect_backup_admin_roles(client))

    assert roles == []
    assert len(not_found) == 3


# --- full collect() integration ---

def test_collect_returns_all_six_keys():
    client = AsyncMock()
    client.get_all_pages.return_value = []
    client.get_directory_roles.return_value = []
    collector = BackupRestoreDataCollector()

    result = asyncio.run(collector.collect(client))

    assert set(result.keys()) == {
        "protection_policies",
        "recent_restore_points",
        "restore_sessions",
        "backup_admin_roles",
        "roles_not_found",
        "detected_vendors",
    }
