"""SharePoint Online collectors.

These collectors use the SharePoint REST API instead of PowerShell because
SharePoint Online PowerShell does not support client secret authentication
for app-only scenarios.

NOTE: If certificate authentication is adopted in the future, these collectors
should be updated to use PowerShell cmdlets (Get-SPOTenant, Get-SPOSite, etc.)
for consistency with other collectors.
"""
