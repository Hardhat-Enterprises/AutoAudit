"""Password policy data collector.

CIS-1.3.1: Ensure password expiration policy is set to never expire.
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class PasswordPolicyDataCollector(BaseDataCollector):
    """Collects domain password expiration policy settings."""

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect password policy for all domains.

        Returns:
            Dict with domains list containing password policy details.
        """
        domains = await client.get_all_pages("/domains")

        domain_data = []
        for domain in domains:
            # Federated domains return null for password properties
            is_managed = domain.get("authenticationType") == "Managed"

            domain_data.append({
                "domain_name": domain.get("id"),
                "is_default": domain.get("isDefault", False),
                "is_managed": is_managed,
                "authentication_type": domain.get("authenticationType"),
                "password_validity_days": domain.get("passwordValidityPeriodInDays"),
                "password_notification_days": domain.get("passwordNotificationWindowInDays"),
            })

        return {
            "domains": domain_data,
            "total_domains": len(domain_data),
            "managed_domains_count": sum(1 for d in domain_data if d["is_managed"]),
        }
