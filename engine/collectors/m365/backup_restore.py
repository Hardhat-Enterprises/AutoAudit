"""Microsoft 365 Backup Storage collector.

E8-BAK-1.1: Regular Backups (ASD Essential Eight, ML1)
Checks whether Exchange, SharePoint, and OneDrive for Business are covered
by an active protection policy, whether a recent restore point exists per
service, whether a recent restore session exists, whether access to backup
administration is restricted to the dedicated backup admin roles, and
detects known third-party backup vendor service principals as supporting
evidence for the third-party offline backup limitation. Vendor detection is
supporting evidence only and does not affect the compliant/non-compliant
result.

Data sources:
- Microsoft Graph, solutions/backupRestore/protectionPolicies
  Required permission: BackupRestore-Configuration.Read.All (confirmed
  against Microsoft's own docs for this specific endpoint)
- Microsoft Graph, solutions/backupRestore/restorePoints
  Required permission: UNCONFIRMED for this specific endpoint, likely
  also BackupRestore-Configuration.Read.All or BackupRestore-Restore.Read.All,
  needs checking against Microsoft's docs for restorePoints specifically
- Microsoft Graph, solutions/backupRestore/restoreSessions
  Required permission: BackupRestore-Restore.Read.All (confirmed, this
  permission "allows the app to read restore sessions")
- Microsoft Entra ID directory roles and role membership
  Required permission: RoleManagement.Read.Directory
- Microsoft Entra ID service principals
  Required permission: Application.Read.All
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient

# Confirmed display names of enterprise applications these vendors register
# in a customer's Entra tenant, sourced from each vendor's own documentation.
# Other known top-3 M365 backup vendors (e.g. Cohesity) were checked but
# excluded, their setup process does not use a fixed, predictable vendor
# branded app name, so they cannot be reliably detected this way.
KNOWN_BACKUP_VENDOR_APP_NAMES = {
    "Veeam": [
        "Veeam Data Cloud for Microsoft 365",
        "Veeam Data Cloud for MS 365",
        "Veeam Data Cloud Registration [EMEA, AMER, APJ]",
        "Veeam Data Cloud [EMEA, AMER, APJ]",
    ],
    "AvePoint": [
        "Cloud Backup for Office 365 - Prod (transact)",
    ],
    "Rubrik": [
        "Rubrik Management Enterprise App",
    ],
}


class BackupRestoreDataCollector(BaseDataCollector):
    """Collects M365 Backup Storage protection, restore, and admin role data."""

    # restorePoints requires both $expand and $filter, confirmed against
    # Microsoft's own API reference. Filtering for anything newer than this
    # window approximates "does a recent restore point exist" without
    # having to enumerate every protection unit individually.
    RECENT_WINDOW_HOURS = 24

    BACKUP_ROLE_NAMES = [
        "Microsoft 365 Backup Administrator",
        "SharePoint Backup Administrator",
        "Exchange Backup Administrator",
    ]

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect protection policy, restore, admin role, and vendor data.

        Returns:
            Dict with:
            - protection_policies: list of policy summaries (service, status)
            - recent_restore_points: restore points newer than the recency window
            - restore_sessions: list of restore session summaries
            - backup_admin_roles: membership of the three backup admin roles
            - roles_not_found: names of any of the three roles not present
              (a role only exists in directoryRoles once it has been activated)
            - detected_vendors: known third-party backup vendor apps found in
              the tenant, supporting evidence only, not a compliance factor
        """
        protection_policies = await self._collect_protection_policies(client)
        recent_restore_points = await self._collect_recent_restore_points(client)
        restore_sessions = await self._collect_restore_sessions(client)
        backup_admin_roles, roles_not_found = await self._collect_backup_admin_roles(
            client
        )
        detected_vendors = await self._collect_detected_vendors(client)

        return {
            "protection_policies": protection_policies,
            "recent_restore_points": recent_restore_points,
            "restore_sessions": restore_sessions,
            "backup_admin_roles": backup_admin_roles,
            "roles_not_found": roles_not_found,
            "detected_vendors": detected_vendors,
        }

    async def _collect_protection_policies(
        self, client: GraphClient
    ) -> list[dict[str, Any]]:
        policies = await client.get_all_pages(
            "/solutions/backupRestore/protectionPolicies"
        )

        return [
            {
                "id": p.get("id"),
                "service": p.get("@odata.type", "").rsplit(".", 1)[-1],
                "status": p.get("status"),
            }
            for p in policies
        ]

    async def _collect_recent_restore_points(
        self, client: GraphClient
    ) -> list[dict[str, Any]]:
        cutoff = (
            datetime.now(timezone.utc) - timedelta(hours=self.RECENT_WINDOW_HOURS)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        # NOTE: $expand and $filter are both required by this endpoint.
        # Filtering for protectionDateTime gt <cutoff> and expanding
        # protectionUnit gives which service each recent restore point
        # belongs to, without needing per-policy traversal. The exact
        # response shape for this filter direction (gt vs lt in Microsoft's
        # own examples) should be confirmed against a live tenant before
        # this is relied on.
        restore_points_raw = await client.get_all_pages(
            "/solutions/backupRestore/restorePoints",
            params={
                "$filter": f"protectionDateTime gt {cutoff}",
                "$expand": "protectionUnit",
            },
        )

        return [
            {
                "id": rp.get("id"),
                "protectionDateTime": rp.get("protectionDateTime"),
                "expirationDateTime": rp.get("expirationDateTime"),
                "protectionUnitType": (rp.get("protectionUnit") or {})
                .get("@odata.type", "")
                .rsplit(".", 1)[-1],
            }
            for rp in restore_points_raw
        ]

    async def _collect_restore_sessions(
        self, client: GraphClient
    ) -> list[dict[str, Any]]:
        # Recency (last 12 months) is checked in the Rego policy, not here,
        # since this endpoint has no required filter and returning
        # everything keeps the recency threshold configurable in one place.
        restore_sessions_raw = await client.get_all_pages(
            "/solutions/backupRestore/restoreSessions"
        )

        return [
            {
                "id": s.get("id"),
                "status": s.get("status"),
                "createdDateTime": s.get("createdDateTime"),
            }
            for s in restore_sessions_raw
        ]

    async def _collect_backup_admin_roles(
        self, client: GraphClient
    ) -> tuple[list[dict[str, Any]], list[str]]:
        directory_roles = await client.get_directory_roles()
        roles_by_name = {r.get("displayName"): r for r in directory_roles}

        backup_admin_roles = []
        roles_not_found = []

        for role_name in self.BACKUP_ROLE_NAMES:
            role = roles_by_name.get(role_name)

            if not role:
                # Directory roles only appear once activated in the tenant.
                # Not finding one here means it has never been activated,
                # which is itself relevant: no one can hold a role that
                # hasn't been activated.
                roles_not_found.append(role_name)
                continue

            members = await client.get_role_members(role["id"])

            member_details = [
                {
                    "id": m.get("id"),
                    "userPrincipalName": m.get("userPrincipalName"),
                    "displayName": m.get("displayName"),
                }
                for m in members
                if m.get("@odata.type") == "#microsoft.graph.user"
            ]

            backup_admin_roles.append(
                {
                    "role_name": role_name,
                    "member_count": len(member_details),
                    "members": member_details,
                }
            )

        return backup_admin_roles, roles_not_found

    async def _collect_detected_vendors(
        self, client: GraphClient
    ) -> list[dict[str, Any]]:
        service_principals = await client.get_all_pages("/servicePrincipals")
        principal_names = {sp.get("displayName") for sp in service_principals}

        return [
            {"vendor": vendor, "matched_app_name": app_name}
            for vendor, app_names in KNOWN_BACKUP_VENDOR_APP_NAMES.items()
            for app_name in app_names
            if app_name in principal_names
        ]
