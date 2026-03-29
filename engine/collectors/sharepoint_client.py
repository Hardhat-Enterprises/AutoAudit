"""Microsoft Graph client for SharePoint and OneDrive tenant controls.

This module uses Microsoft Graph application permissions with client-secret
authentication only. It replaces the older SharePoint REST/admin API flow so
SharePoint collectors can run without a tenant-specific SharePoint token.
"""

from typing import Any
from urllib.parse import urlparse

from collectors.graph_client import GraphClient


class SharePointClient(GraphClient):
    """Graph-backed client for SharePoint Online tenant data."""

    async def get_tenant_settings(self) -> dict[str, Any]:
        """Get SharePoint/OneDrive tenant settings from Microsoft Graph."""
        response = await self.get("/admin/sharepoint/settings")
        if not isinstance(response, dict):
            raise TypeError("Unexpected Graph sharePointSettings response shape")
        return response

    async def search_sites(
        self,
        *,
        include_personal_sites: bool = True,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        """Enumerate SharePoint sites using Microsoft Graph."""
        response = await self.get("/sites/getAllSites")

        sites: list[dict[str, Any]] = []
        next_link = response.get("@odata.nextLink")
        page_items = response.get("value", [])

        while True:
            for item in page_items:
                if not isinstance(item, dict):
                    continue

                web_url = item.get("webUrl")
                if not isinstance(web_url, str) or not web_url:
                    continue

                is_personal_site = "-my.sharepoint.com/" in web_url.lower()
                if not include_personal_sites and is_personal_site:
                    continue

                sites.append(
                    {
                        "title": item.get("displayName") or item.get("name"),
                        "url": web_url,
                        "site_id": item.get("id"),
                        "web_template": item.get("webTemplate"),
                        "content_class": "STS_Web" if is_personal_site else "STS_Site",
                    }
                )

                if len(sites) >= limit:
                    return sites

            if not next_link:
                break

            next_page = await self._request("GET", next_link.replace(self.GRAPH_BASE_URL, ""))
            if not isinstance(next_page, dict):
                raise TypeError("Unexpected Graph sites pagination response shape")
            page_items = next_page.get("value", [])
            next_link = next_page.get("@odata.nextLink")

        return sites

    async def get_site_properties(self, site_url: str) -> dict[str, Any]:
        """Get basic site properties for a SharePoint site via Microsoft Graph."""
        parsed = urlparse(site_url)
        hostname = parsed.netloc
        relative_path = parsed.path.rstrip("/")

        if not hostname:
            raise ValueError(f"Invalid SharePoint site URL: {site_url}")

        endpoint = f"/sites/{hostname}:{relative_path}" if relative_path else f"/sites/{hostname}"
        site_info = await self.get(
            endpoint,
            params={"$select": "id,displayName,name,webUrl,siteCollection,createdDateTime"},
        )

        if not isinstance(site_info, dict):
            raise TypeError("Unexpected Graph site response shape")

        return {
            "site": {
                "Id": site_info.get("id"),
                "Url": site_info.get("webUrl"),
            },
            "web": {
                "Id": site_info.get("id"),
                "Title": site_info.get("displayName") or site_info.get("name"),
                "Url": site_info.get("webUrl"),
                "WebTemplate": site_info.get("webTemplate"),
            },
        }

    async def get_sync_client_restriction(self) -> dict[str, Any]:
        """Get OneDrive sync client restriction settings from tenant settings."""
        tenant_settings = await self.get_tenant_settings()

        allowed_domain_guids = tenant_settings.get("allowedDomainGuidsForSyncApp")
        if allowed_domain_guids is None:
            allowed_domain_guids = tenant_settings.get("AllowedDomainList")
        if allowed_domain_guids is None:
            allowed_domain_guids = tenant_settings.get("allowedDomainList")

        excluded_file_extensions = tenant_settings.get("excludedFileExtensionsForSyncApp")
        if excluded_file_extensions is None:
            excluded_file_extensions = tenant_settings.get("ExcludedFileExtensions")
        if excluded_file_extensions is None:
            excluded_file_extensions = tenant_settings.get("excludedFileExtensions")

        return {
            "TenantRestrictionEnabled": tenant_settings.get(
                "isUnmanagedSyncAppForTenantRestricted",
                tenant_settings.get(
                    "TenantRestrictionEnabled",
                    tenant_settings.get("tenantRestrictionEnabled"),
                ),
            ),
            "AllowedDomainList": self._normalize_list(allowed_domain_guids),
            "BlockMacSync": (
                tenant_settings.get("BlockMacSync", tenant_settings.get("blockMacSync"))
                if "isMacSyncAppEnabled" not in tenant_settings
                else not bool(tenant_settings["isMacSyncAppEnabled"])
            ),
            "GrooveBlockOption": tenant_settings.get(
                "GrooveBlockOption",
                tenant_settings.get("grooveBlockOption"),
            ),
            "ExcludedFileExtensions": self._normalize_list(excluded_file_extensions),
        }

    @staticmethod
    def _normalize_list(value: Any) -> list[Any]:
        """Normalize Graph list-like payloads to plain Python lists."""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, str):
            if not value.strip():
                return []
            return [item.strip() for item in value.split(",") if item.strip()]
        return [value]
