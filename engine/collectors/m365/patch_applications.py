"""Patch Applications collector.

E8-PA-1.1: Patch Applications (ASD Essential Eight, ML1)
Checks whether Microsoft Defender's signature is current and real time
protection is active on each device, and whether covered category
software (office productivity, browser, email client, PDF) installed on
each device carries known weaknesses or is past its vendor end of
support date. Security products are covered by windowsProtectionState
rather than the DVM software inventory filter, so they are not checked
twice.

This control needs two separate API clients: Microsoft Graph for
windowsProtectionState, and DVM for software inventory. It uses
BaseMultiClientCollector (see collectors/multi_client_base.py) rather
than building a second client internally: tasks.py builds both clients
and passes them in as a dict, keyed by "graph" and "dvm".

** DEPENDS ON `collectors/multi_client_base.py` and the multi-client
support in `worker/tasks.py`. This collector will not run until those
exist in the codebase. **

DVM credentials are assumed SEPARATE from Graph's, matching report
26T2-SEC-EG-003 which states DVM "requires its own Entra app
registration and permissions... distinct from the app registration
AutoAudit's existing collectors use." UNVERIFIED against the live
tenant, see the "dvm" branch in tasks.py for where those credentials
are sourced (settings.DVM_TENANT_ID etc., which do not exist yet).

Data sources:
- Microsoft Graph, deviceManagement/managedDevices (windowsProtectionState)
  Required permission: DeviceManagementManagedDevices.Read.All
- Microsoft Defender Vulnerability Management, software inventory
  Required permission: Confirmed as "Vulnerability.Read.All", application
  type, under the WindowsDefenderATP API (confirmed against Microsoft's
  own docs, not the E8-PA-1.1 report, which did not specify a name).
  Not yet tested against the live t8sjf tenant.
"""

from typing import Any

from collectors.dvm_client import DVMClient
from collectors.graph_client import GraphClient
from collectors.multi_client_base import BaseMultiClientCollector

# ACSC covered categories for Patch Applications at ML1: office
# productivity, browser, email client, PDF software. Security products
# are covered separately via windowsProtectionState, so they are not
# checked twice here. DVM's software inventory endpoint cannot filter
# by category server-side, so all installed software is retrieved and
# category filtering happens here. This is broader than ACSC's exact
# category list but avoids maintaining an app-name allowlist.
# UNVERIFIED against a live DVM response shape.
COVERED_CATEGORY_KEYWORDS = [
    "office", "word", "excel", "powerpoint", "outlook",
    "chrome", "firefox", "edge", "safari",
    "acrobat", "reader", "pdf",
]


class PatchApplicationsDataCollector(BaseMultiClientCollector):
    """Collects Defender protection state and DVM software inventory data."""

    required_clients = ("graph", "dvm")

    # Matches AutoAudit's existing default recency threshold, same value
    # used in backup_restore.py (RECENT_WINDOW_HOURS). Recency itself is
    # checked in the Rego policy, not here, consistent with how Backups
    # keeps the threshold configurable in one place.
    RECENT_WINDOW_HOURS = 24

    # Judgement call reasoned from the ACSC ML1 wording (patches applied
    # within two weeks = no known weakness should sit unaddressed). Not
    # from any codebase precedent or ACSC-published number. Confirm with
    # team before relying on this.
    WEAKNESS_THRESHOLD = 0

    async def collect(self, clients: dict[str, Any]) -> dict[str, Any]:
        """Collect windowsProtectionState and DVM software inventory data.

        Args:
            clients: dict with "graph" -> GraphClient and "dvm" -> DVMClient,
                built and injected by tasks.py based on required_clients.

        Returns:
            Dict with:
            - protection_states: per-device signature/real-time protection status
            - software_inventory: per-device covered category software with
              weakness counts and end of support status
            - recent_window_hours: the recency threshold, for the policy to apply
            - weakness_threshold: the weakness threshold, for the policy to apply
        """
        graph_client: GraphClient = clients["graph"]
        dvm_client: DVMClient = clients["dvm"]

        protection_states = await self._collect_protection_states(graph_client)
        software_inventory = await self._collect_software_inventory(dvm_client)

        return {
            "protection_states": protection_states,
            "software_inventory": software_inventory,
            "recent_window_hours": self.RECENT_WINDOW_HOURS,
            "weakness_threshold": self.WEAKNESS_THRESHOLD,
        }

    async def _collect_protection_states(
        self, client: GraphClient
    ) -> list[dict[str, Any]]:
        # UNVERIFIED endpoint shape, based on report 26T2-SEC-EG-003
        # reference 4 (windowsProtectionState resource type). Confirm
        # against a live tenant before relying on this.
        devices = await client.get_all_pages(
            "/deviceManagement/managedDevices",
            params={"$expand": "windowsProtectionState"},
        )

        results = []
        for device in devices:
            protection = device.get("windowsProtectionState") or {}
            results.append(
                {
                    "device_id": device.get("id"),
                    "device_name": device.get("deviceName"),
                    "signatureUpdateOverdue": protection.get("signatureUpdateOverdue"),
                    "realTimeProtectionEnabled": protection.get(
                        "realTimeProtectionEnabled"
                    ),
                    "signatureVersion": protection.get("signatureVersion"),
                    "engineVersion": protection.get("engineVersion"),
                    "lastReportedDateTime": protection.get("lastReportedDateTime"),
                }
            )

        return results

    async def _collect_software_inventory(
        self, client: DVMClient
    ) -> list[dict[str, Any]]:
        # UNVERIFIED endpoint and response shape, based on report
        # 26T2-SEC-EG-003 reference 5. Confirm against a live tenant.
        software_raw = await client.get_software_inventory()

        covered = []
        for item in software_raw:
            software_name = (item.get("softwareName") or "").lower()
            if not any(kw in software_name for kw in COVERED_CATEGORY_KEYWORDS):
                continue

            covered.append(
                {
                    "device_id": item.get("deviceId") or item.get("machineId"),
                    "softwareName": item.get("softwareName"),
                    "softwareVendor": item.get("softwareVendor"),
                    "softwareVersion": item.get("softwareVersion"),
                    "numberOfWeaknesses": item.get("numberOfWeaknesses"),
                    "endOfSupportStatus": item.get("endOfSupportStatus"),
                    "endOfSupportDate": item.get("endOfSupportDate"),
                }
            )

        return covered
