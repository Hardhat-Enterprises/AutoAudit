"""Administrative license footprint collector.

CIS Microsoft 365 Foundations Benchmark Control:
    v6.0.0: 1.1.4

Purpose:
    Enumerate administrative accounts and report their assigned licenses to
    identify over-provisioning for admin users.

Notes:
    - Uses Microsoft Graph (application) via GraphClient.
    - Requires RoleManagement.Read.Directory, User.Read.All, Directory.Read.All,
      and access to license details.
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class AdminLicenseFootprintDataCollector(BaseDataCollector):
    """Collect admin accounts and their assigned licenses."""

    ADMIN_ROLE_NAMES = {
        "Global Administrator",
        "Privileged Role Administrator",
        "Privileged Authentication Administrator",
        "Security Administrator",
        "Exchange Administrator",
        "SharePoint Administrator",
        "Teams Administrator",
        "Teams Communications Administrator",
        "Intune Administrator",
        "Application Administrator",
        "Cloud Application Administrator",
        "Conditional Access Administrator",
        "User Administrator",
    }

    async def _get_admin_users(self, client: GraphClient) -> list[dict[str, Any]]:
        """Return unique admin user objects with their roles."""
        roles = await client.get_directory_roles()
        admin_roles = [r for r in roles if r.get("displayName") in self.ADMIN_ROLE_NAMES]

        admins: dict[str, dict[str, Any]] = {}
        for role in admin_roles:
            members = await client.get_role_members(role["id"])
            role_name = role.get("displayName", "Unknown")
            for member in members:
                if member.get("@odata.type") != "#microsoft.graph.user":
                    continue
                user_id = member.get("id")
                if not user_id:
                    continue
                user = admins.setdefault(
                    user_id,
                    {
                        "id": user_id,
                        "userPrincipalName": member.get("userPrincipalName"),
                        "displayName": member.get("displayName"),
                        "roles": [],
                    },
                )
                user["roles"].append(role_name)
        return list(admins.values())

    async def _get_sku_map(self, client: GraphClient) -> dict[str, str]:
        """Map skuId -> human-readable name."""
        skus = await client.get("/subscribedSkus")
        sku_map: dict[str, str] = {}
        for sku in skus.get("value", []):
            sku_id = sku.get("skuId")
            name = sku.get("skuPartNumber") or sku.get("prepaidUnits", {}).get("enabled")
            if sku_id:
                sku_map[str(sku_id).lower()] = name or "unknown"
        return sku_map

    async def _get_license_details(self, client: GraphClient, user_id: str) -> list[dict[str, Any]]:
        """Fetch license details for a user."""
        resp = await client.get(f"/users/{user_id}/licenseDetails")
        return resp.get("value", [])

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect admin license footprint data."""
        admins = await self._get_admin_users(client)
        sku_map = await self._get_sku_map(client)

        enriched = []
        sku_counter: dict[str, int] = {}
        licensed_admins = 0

        for admin in admins:
            details = await self._get_license_details(client, admin["id"])
            assigned = []
            for lic in details:
                sku_id = str(lic.get("skuId", "")).lower()
                sku_name = sku_map.get(sku_id, sku_id)
                assigned.append({
                    "skuId": lic.get("skuId"),
                    "skuName": sku_name,
                    "servicePlans": [sp.get("servicePlanName") for sp in lic.get("servicePlans", [])],
                })
                sku_counter[sku_name] = sku_counter.get(sku_name, 0) + 1

            licensed_admins += 1 if assigned else 0

            enriched.append({
                "userPrincipalName": admin.get("userPrincipalName"),
                "displayName": admin.get("displayName"),
                "roles": admin.get("roles", []),
                "licenses": assigned,
            })

        return {
            "admins": enriched,
            "summary": {
                "total_admins": len(admins),
                "licensed_admins": licensed_admins,
                "skus": sku_counter,
            },
        }
