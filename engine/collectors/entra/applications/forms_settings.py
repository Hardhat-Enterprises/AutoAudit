"""Forms settings collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.5

Connection Method: Microsoft Graph API
Required Scopes: OrgSettings-Forms.Read.All
Graph Endpoint: /admin/forms/settings
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class FormsSettingsDataCollector(BaseDataCollector):
    """Collects Microsoft Forms settings for CIS compliance evaluation.

    This collector retrieves Microsoft Forms configuration including
    phishing protection settings for compliance evaluation.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Forms settings data.

        Returns:
            Dict containing:
            - forms_settings: Microsoft Forms configuration
            - internal_phishing_protection_enabled: Phishing protection status
            - external_sharing_enabled: External sharing status
        """
        # Get Microsoft Forms admin settings
        try:
            settings = await client.get("/admin/forms/settings", beta=True)
        except Exception:
            settings = {}

        return {
            "forms_settings": settings,
            "internal_phishing_protection_enabled": settings.get(
                "isInternalPhishingProtectionEnabled"
            ),
            "external_sharing_enabled": settings.get("isExternalSharingEnabled"),
            "external_send_form_enabled": settings.get("isExternalSendFormEnabled"),
            "external_share_collaborating_enabled": settings.get(
                "isExternalShareCollaborationEnabled"
            ),
            "external_share_template_enabled": settings.get(
                "isExternalShareTemplateEnabled"
            ),
            "external_share_result_enabled": settings.get(
                "isExternalShareResultEnabled"
            ),
            "bing_search_enabled": settings.get("isBingSearchEnabled"),
            "record_identity_by_default_enabled": settings.get(
                "isRecordIdentityByDefaultEnabled"
            ),
        }
