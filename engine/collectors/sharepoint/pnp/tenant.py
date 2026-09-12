"""PnP SharePoint tenant collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 7.2.1, 7.2.2, 7.2.4, 7.2.5, 7.2.7, 7.2.9, 7.2.10, 7.3.1

Control Descriptions:
    7.2.1 - Ensure modern authentication for SharePoint applications is required
    7.2.2 - Ensure SharePoint and OneDrive integration with Azure AD B2B is enabled
    7.2.4 - Ensure OneDrive content sharing is restricted
    7.2.5 - Ensure SharePoint guest users cannot share items they don't own
    7.2.7 - Ensure link sharing is restricted in SharePoint and OneDrive
    7.2.9 - Ensure guest access to a site or OneDrive will expire automatically
    7.2.10 - Ensure reauthentication with verification code is restricted
    7.3.1 - Ensure Office 365 SharePoint infected files are disallowed for download

Connection Method: SharePoint Online PowerShell (via PowerShell HTTP service)
Required Cmdlets: Get-PnPTenant
Required Permissions: SharePoint.Admin
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class PnpTenantDataCollector(BasePowerShellCollector):
    """Collects SharePoint tenant settings via Get-PnPTenant.

    This collector retrieves tenant-wide SharePoint settings. CIS 7.2.1
    evaluates LegacyAuthProtocolsEnabled; CIS 7.2.2 evaluates
    EnableAzureADB2BIntegration; CIS 7.2.4
    evaluates SharingCapability; CIS 7.2.5 evaluates
    PreventExternalUsersFromResharing; CIS 7.2.9 evaluates
    ExternalUserExpirationRequired and ExternalUserExpireInDays; CIS 7.2.10
    evaluates EmailAttestationRequired and EmailAttestationReAuthDays; CIS
    7.3.1 evaluates DisallowInfectedFileDownload. Later controls can reuse
    the same tenant evidence.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect SharePoint tenant data.

        Returns:
            Dict containing:
            - tenant: Full Get-PnPTenant result
            - legacy_auth_protocols_enabled: Legacy auth protocol status (CIS 7.2.1)
            - azure_ad_b2b_integration_enabled: Azure AD B2B integration status (CIS 7.2.2)
            - sharing_capability: External sharing capability (CIS 7.2.4)
            - prevent_external_users_from_resharing: Guest resharing restriction status (CIS 7.2.5)
            - external_user_expiration_required: Guest access expiration requirement (CIS 7.2.9)
            - external_user_expire_in_days: Guest access expiration period in days (CIS 7.2.9)
            - email_attestation_required: Verification code reauthentication requirement (CIS 7.2.10)
            - email_attestation_reauth_days: Verification code reauthentication period in days (CIS 7.2.10)
            - disallow_infected_file_download: Infected-file download status (CIS 7.3.1)
        """
        tenant = await client.run_cmdlet("SharePointOnline", "Get-PnPTenant")

        return {
            "tenant": tenant,
            "sharing_capability": tenant.get("SharingCapability"),
            "legacy_auth_protocols_enabled": tenant.get(
                "LegacyAuthProtocolsEnabled"
            ),
            "disallow_infected_file_download": tenant.get(
                "DisallowInfectedFileDownload"
            ),
            "azure_ad_b2b_integration_enabled": tenant.get(
                "EnableAzureADB2BIntegration"
            ),
            "prevent_external_users_from_resharing": tenant.get(
                "PreventExternalUsersFromResharing"
            ),
            "external_user_expiration_required": tenant.get(
                "ExternalUserExpirationRequired"
            ),
            "external_user_expire_in_days": tenant.get(
                "ExternalUserExpireInDays"
            ),
            "default_sharing_link_type": tenant.get(
                "DefaultSharingLinkType"
            ),
            "restrict_external_domain_sharing":tenant.get(
                "SharingDomainRestrictionMode"
            ),
            "email_attestation_required": tenant.get(
                "EmailAttestationRequired"
            ),
            "email_attestation_reauth_days": tenant.get(
                "EmailAttestationReAuthDays"
            ),
        }