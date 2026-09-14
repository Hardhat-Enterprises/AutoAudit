"""Unit tests for PatchApplicationsDataCollector.

Tests _collect_protection_states and _collect_software_inventory in
isolation using mocked clients, since this repo does not have
pytest-asyncio installed. Async methods are run via asyncio.run() inside
plain sync test functions, matching test_backup_restore_collector.py.

collect() now takes a dict of clients ({"graph": ..., "dvm": ...}),
built and injected by tasks.py based on required_clients. Tests use
plain mocks for both, no need to patch DVMClient at the class level
since it's no longer built internally.
"""


from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

from collectors.m365.patch_applications import PatchApplicationsDataCollector


def _make_graph_client(devices: list[dict]) -> AsyncMock:
    client = AsyncMock()
    client.get_all_pages.return_value = devices
    client.tenant_id = "test-tenant"
    client.client_id = "test-client"
    client.client_secret = "test-secret"
    return client


# --- _collect_protection_states ---


def test_collect_protection_states_parses_fields():
    client = _make_graph_client(
        [
            {
                "id": "d1",
                "deviceName": "Device1",
                "windowsProtectionState": {
                    "signatureUpdateOverdue": False,
                    "realTimeProtectionEnabled": True,
                    "signatureVersion": "1.2.3",
                    "engineVersion": "4.5.6",
                    "lastReportedDateTime": "2026-08-30T00:00:00Z",
                },
            }
        ]
    )
    collector = PatchApplicationsDataCollector()

    result = asyncio.run(collector._collect_protection_states(client))

    assert result == [
        {
            "device_id": "d1",
            "device_name": "Device1",
            "signatureUpdateOverdue": False,
            "realTimeProtectionEnabled": True,
            "signatureVersion": "1.2.3",
            "engineVersion": "4.5.6",
            "lastReportedDateTime": "2026-08-30T00:00:00Z",
        }
    ]


def test_collect_protection_states_missing_windows_protection_state_does_not_crash():
    client = _make_graph_client([{"id": "d1", "deviceName": "Device1"}])
    collector = PatchApplicationsDataCollector()

    result = asyncio.run(collector._collect_protection_states(client))

    assert result[0]["signatureUpdateOverdue"] is None
    assert result[0]["realTimeProtectionEnabled"] is None


def test_collect_protection_states_empty_list():
    client = _make_graph_client([])
    collector = PatchApplicationsDataCollector()

    result = asyncio.run(collector._collect_protection_states(client))

    assert result == []


def test_collect_protection_states_sends_expand_param():
    client = _make_graph_client([])
    collector = PatchApplicationsDataCollector()

    asyncio.run(collector._collect_protection_states(client))

    args, kwargs = client.get_all_pages.call_args
    assert args[0] == "/deviceManagement/managedDevices"
    assert kwargs["params"]["$expand"] == "windowsProtectionState"


# --- _collect_software_inventory ---


def _make_dvm_client(software: list[dict]) -> AsyncMock:
    client = AsyncMock()
    client.get_software_inventory.return_value = software
    return client


def test_collect_software_inventory_filters_to_covered_categories():
    client = _make_dvm_client(
        [
            {"softwareName": "Google Chrome", "numberOfWeaknesses": 0},
            {"softwareName": "Some Internal Tool", "numberOfWeaknesses": 0},
            {"softwareName": "Adobe Acrobat Reader", "numberOfWeaknesses": 2},
        ]
    )
    collector = PatchApplicationsDataCollector()

    result = asyncio.run(collector._collect_software_inventory(client))

    names = {item["softwareName"] for item in result}
    assert names == {"Google Chrome", "Adobe Acrobat Reader"}


def test_collect_software_inventory_parses_fields():
    client = _make_dvm_client(
        [
            {
                "deviceId": "d1",
                "softwareName": "Microsoft Word",
                "softwareVendor": "Microsoft",
                "softwareVersion": "16.0",
                "numberOfWeaknesses": 1,
                "endOfSupportStatus": "Supported",
                "endOfSupportDate": None,
            }
        ]
    )
    collector = PatchApplicationsDataCollector()

    result = asyncio.run(collector._collect_software_inventory(client))

    assert result == [
        {
            "device_id": "d1",
            "softwareName": "Microsoft Word",
            "softwareVendor": "Microsoft",
            "softwareVersion": "16.0",
            "numberOfWeaknesses": 1,
            "endOfSupportStatus": "Supported",
            "endOfSupportDate": None,
        }
    ]


def test_collect_software_inventory_empty_list():
    client = _make_dvm_client([])
    collector = PatchApplicationsDataCollector()

    result = asyncio.run(collector._collect_software_inventory(client))

    assert result == []


def test_collect_software_inventory_no_covered_software_returns_empty():
    client = _make_dvm_client(
        [{"softwareName": "Random Internal App", "numberOfWeaknesses": 5}]
    )
    collector = PatchApplicationsDataCollector()

    result = asyncio.run(collector._collect_software_inventory(client))

    assert result == []


def test_collect_software_inventory_machine_id_fallback():
    # Some DVM responses may use machineId instead of deviceId - UNVERIFIED,
    # test documents the fallback behaviour either way.
    client = _make_dvm_client(
        [{"machineId": "m1", "softwareName": "Mozilla Firefox", "numberOfWeaknesses": 0}]
    )
    collector = PatchApplicationsDataCollector()

    result = asyncio.run(collector._collect_software_inventory(client))

    assert result[0]["device_id"] == "m1"


# --- full collect() integration ---


def _make_dvm_client_mock(software: list[dict]) -> AsyncMock:
    client = AsyncMock()
    client.get_software_inventory.return_value = software
    return client


def test_collect_returns_all_four_keys():
    graph_client = _make_graph_client([])
    dvm_client = _make_dvm_client_mock([])

    collector = PatchApplicationsDataCollector()
    result = asyncio.run(collector.collect({"graph": graph_client, "dvm": dvm_client}))

    assert set(result.keys()) == {
        "protection_states",
        "software_inventory",
        "recent_window_hours",
        "weakness_threshold",
    }
    assert result["recent_window_hours"] == 24
    assert result["weakness_threshold"] == 0


def test_collect_uses_the_clients_it_was_given():
    # Confirms collect() uses the injected graph/dvm clients directly,
    # not building its own internally (that was the old behaviour,
    # replaced by BaseMultiClientCollector).
    graph_client = _make_graph_client(
        [{"id": "d1", "deviceName": "Device1", "windowsProtectionState": {}}]
    )
    dvm_client = _make_dvm_client_mock(
        [{"softwareName": "Google Chrome", "numberOfWeaknesses": 0}]
    )

    collector = PatchApplicationsDataCollector()
    result = asyncio.run(collector.collect({"graph": graph_client, "dvm": dvm_client}))

    graph_client.get_all_pages.assert_called_once()
    dvm_client.get_software_inventory.assert_called_once()
    assert len(result["protection_states"]) == 1
    assert len(result["software_inventory"]) == 1


def test_required_clients_declares_graph_and_dvm():
    assert PatchApplicationsDataCollector.required_clients == ("graph", "dvm")
