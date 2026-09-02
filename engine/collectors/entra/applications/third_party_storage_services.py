"""Third-party storage services collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.7

Connection Method: Microsoft Graph API
Required Scopes: Application.Read.All
Graph Endpoint: /servicePrincipals (v1.0)
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient

# Well-known appId for the "Third Party Storage Services" service principal
# referenced by CIS control 1.3.7 (Microsoft 365 on the web).
THIRD_PARTY_STORAGE_APP_ID = "c1f33bc0-bdb4-4248-ba9b-096807ddb43e"


class ThirdPartyStorageServicesDataCollector(BaseDataCollector):
    """Collects the Third Party Storage Services service principal state.

    This collector retrieves the Entra ID service principal that governs
    whether users can open files stored in third-party storage providers
    (e.g. Dropbox) from Microsoft 365 on the web, to verify it is disabled.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect third-party storage service principal data.

        Returns:
            Dict containing:
            - service_principal_exists: Whether the SP has been created in the tenant
            - account_enabled: The SP's accountEnabled value (None if not found)
            - service_principal: Raw service principal object, if found

        Raises:
            Any exception from the Graph API call is propagated so the worker
            pipeline can retry or mark this control as an evaluation error,
            rather than silently reporting a false non-compliance result.
        """
        service_principal: dict[str, Any] | None = None

        resp = await client.get(
            f"/servicePrincipals?$filter=appId eq '{THIRD_PARTY_STORAGE_APP_ID}'"
        )
        results = resp.get("value") if isinstance(resp, dict) else None
        if isinstance(results, list) and results:
            service_principal = results[0]

        account_enabled = (
            service_principal.get("accountEnabled")
            if isinstance(service_principal, dict)
            else None
        )

        return {
            "service_principal_exists": service_principal is not None,
            "account_enabled": account_enabled,
            "service_principal": service_principal,
        }
    