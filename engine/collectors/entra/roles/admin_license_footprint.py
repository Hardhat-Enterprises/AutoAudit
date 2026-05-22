"""Admin license footprint collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.1.4

Connection Method: Microsoft Graph API
Required Scopes: User.Read.All, RoleManagement.Read.Directory
Graph Endpoints:
    - /directoryRoles
    - /directoryRoles/{id}/members
    - /users/{id} ($select id,userPrincipalName,displayName)
    - /users/{id}/licenseDetails
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class AdminLicenseFootprintDataCollector(BaseDataCollector):
    """Collects admin account license assignments for CIS compliance evaluation.

    This collector identifies all users holding privileged directory roles and
    checks whether their assigned licenses expose high-footprint application
    service plans such as Exchange Online, Teams, or Office desktop suites.
    """

    ADMIN_ROLE_NAMES = [
        "Global Administrator",
        "Privileged Role Administrator",
        "Privileged Authentication Administrator",
        "Security Administrator",
        "Exchange Administrator",
        "SharePoint Administrator",
        "Intune Administrator",
        "Application Administrator",
        "Cloud Application Administrator",
        "Azure AD Joined Device Local Administrator",
        "Compliance Administrator",
        "Conditional Access Administrator",
        "User Administrator",
    ]

    HIGH_FOOTPRINT_SERVICE_PLANS = frozenset(
        {
            "EXCHANGE_S_STANDARD",
            "EXCHANGE_S_ENTERPRISE",
            "EXCHANGE_S_ARCHIVE_ADDON",
            "EXCHANGE_S_DESKLESS",
            "EXCHANGE_S_FOUNDATION",
            "MCOSTANDARD",
            "MCOEV",
            "OFFICESUBSCRIPTION",
            "SHAREPOINTENTERPRISE",
            "SHAREPOINTSTANDARD",
            "SHAREPOINTW_DEVELOPER",
            "SWAY",
            "YAMMER_ENTERPRISE",
            "PROJECTWORKMANAGEMENT",
            "VISIOONLINE",
            "VISIOCLIENT",
            "INTUNE_A",
        }
    )

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        roles = await client.get_directory_roles()
        admin_roles = [
            role for role in roles if role.get("displayName") in self.ADMIN_ROLE_NAMES
        ]
        admin_users: dict[str, dict[str, Any]] = {}

        for role in admin_roles:
            role_name = role.get("displayName", "Unknown")
            members = await client.get_role_members(role["id"])

            for member in members:
                if member.get("@odata.type") != "#microsoft.graph.user":
                    continue

                user_id = member.get("id")
                if not user_id:
                    continue

                if user_id in admin_users:
                    if role_name not in admin_users[user_id]["admin_roles"]:
                        admin_users[user_id]["admin_roles"].append(role_name)
                    continue

                user_details = await client.get(
                    f"/users/{user_id}",
                    params={"$select": "id,userPrincipalName,displayName"},
                )
                license_details = await client.get_user_license_details(user_id)
                admin_users[user_id] = {
                    "id": user_id,
                    "userPrincipalName": user_details.get("userPrincipalName"),
                    "displayName": user_details.get("displayName"),
                    "admin_roles": [role_name],
                    "license_details": license_details,
                }

        admin_accounts: list[dict[str, Any]] = []
        high_footprint_count = 0

        for data in admin_users.values():
            plans = self._enabled_high_footprint_plans(data["license_details"])
            reduced = len(plans) == 0
            if not reduced:
                high_footprint_count += 1
            admin_accounts.append(
                {
                    "id": data["id"],
                    "userPrincipalName": data["userPrincipalName"],
                    "displayName": data["displayName"],
                    "admin_roles": data["admin_roles"],
                    "sku_part_numbers": sorted(
                        {
                            str(lic.get("skuPartNumber") or "")
                            for lic in data["license_details"]
                            if lic.get("skuPartNumber")
                        }
                    ),
                    "high_footprint_service_plans_enabled": plans,
                    "uses_reduced_license_footprint": reduced,
                }
            )

        return {
            "admin_accounts": admin_accounts,
            "total_admin_accounts": len(admin_accounts),
            "admin_accounts_with_high_footprint_licenses": high_footprint_count,
            "admin_accounts_with_reduced_license_footprint": len(admin_accounts)
            - high_footprint_count,
        }

    @staticmethod
    def _enabled_high_footprint_plans(
        license_details: list[dict[str, Any]],
    ) -> list[str]:
        found: set[str] = set()
        for lic in license_details:
            for sp in lic.get("servicePlans") or []:
                if sp.get("provisioningStatus") != "Success":
                    continue
                if sp.get("appliesTo") != "User":
                    continue
                name = sp.get("servicePlanName") or ""
                if name in AdminLicenseFootprintDataCollector.HIGH_FOOTPRINT_SERVICE_PLANS:
                    found.add(name)
        return sorted(found)
