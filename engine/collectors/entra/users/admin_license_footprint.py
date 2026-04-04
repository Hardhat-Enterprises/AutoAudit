"""Admin license footprint collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.1.4

Connection Method: Microsoft Graph API
Required Scopes: Directory.Read.All, User.Read.All
Graph Endpoints: /directoryRoles, /directoryRoles/{id}/members, /users/{id}, /subscribedSkus
"""

from __future__ import annotations

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class AdminLicenseFootprintDataCollector(BaseDataCollector):
    """Collects license assignments for administrative accounts.

    This collector identifies users with directory roles (admin accounts),
    fetches their assigned licenses, and maps SKU IDs to SKU part numbers.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        # Fetch directory roles and members
        roles = await client.get_directory_roles()

        admin_users: dict[str, dict[str, Any]] = {}
        for role in roles:
            role_id = role.get("id")
            role_name = role.get("displayName")
            if not role_id:
                continue

            members = await client.get_role_members(role_id)
            for member in members:
                if member.get("@odata.type") != "#microsoft.graph.user":
                    continue
                user_id = member.get("id")
                if not user_id:
                    continue

                entry = admin_users.setdefault(
                    user_id,
                    {
                        "id": user_id,
                        "displayName": member.get("displayName"),
                        "userPrincipalName": member.get("userPrincipalName"),
                        "roles": [],
                    },
                )
                entry["roles"].append(role_name)

        # Map SKU IDs to readable names
        sku_response = await client.get("/subscribedSkus")
        sku_map = {
            sku.get("skuId"): {
                "skuPartNumber": sku.get("skuPartNumber"),
                "prepaidUnits": sku.get("prepaidUnits"),
            }
            for sku in sku_response.get("value", [])
            if sku.get("skuId")
        }

        admin_license_details: list[dict[str, Any]] = []
        for user_id, info in admin_users.items():
            user_detail = await client.get(
                f"/users/{user_id}",
                params={
                    "$select": "id,displayName,userPrincipalName,assignedLicenses,accountEnabled",
                },
            )
            assigned = user_detail.get("assignedLicenses", [])
            license_skus = [lic.get("skuId") for lic in assigned if lic.get("skuId")]

            admin_license_details.append(
                {
                    "id": user_id,
                    "displayName": info.get("displayName") or user_detail.get("displayName"),
                    "userPrincipalName": info.get("userPrincipalName")
                    or user_detail.get("userPrincipalName"),
                    "accountEnabled": user_detail.get("accountEnabled"),
                    "roles": info.get("roles", []),
                    "assignedLicenses": assigned,
                    "assignedSkuIds": license_skus,
                }
            )

        return {
            "admin_users_count": len(admin_users),
            "admin_users": admin_license_details,
            "sku_map": sku_map,
        }
