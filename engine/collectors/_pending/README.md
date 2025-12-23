# Pending Collectors

This directory contains collectors that have been implemented but cannot currently
be used due to authentication or API limitations.

## Compliance Collectors

**Issue:** Security & Compliance PowerShell (IPPSSession) does not support client
secret authentication for app-only access.

**Reference:** https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell

| Collector | CIS Controls | Required Cmdlet |
|-----------|--------------|-----------------|
| `dlp_compliance_policy` | 3.2.1, 3.2.2 | Get-DlpCompliancePolicy |
| `label_policy` | 3.3.1 | Get-LabelPolicy |

**To Enable:** Implement certificate-based authentication in `PowerShellClient`,
then move these collectors back to `collectors/compliance/` and register them.

## Teams Collectors

**Issue:** MicrosoftTeams PowerShell module's `-AccessTokens` parameter returns
"Not supported tenant type" error for certain tenant configurations. This is a
known bug in the module.

**Reference:** https://techcommunity.microsoft.com/discussions/teamsdeveloper/authenticating-with-an-access-token-connect-microsoftteams/2233794

| Collector | CIS Controls | Required Cmdlet |
|-----------|--------------|-----------------|
| `external_access_policy` | 8.2.1, 8.2.2, 8.2.3 | Get-CsExternalAccessPolicy |
| `teams_client_config` | 8.1.1, 8.1.2 | Get-CsTeamsClientConfiguration |
| `teams_meeting_policy` | 8.5.1-8.5.9 | Get-CsTeamsMeetingPolicy |
| `teams_messaging_policy` | 8.6.1 | Get-CsTeamsMessagingPolicy |
| `tenant_federation_config` | 8.2.1-8.2.4 | Get-CsTenantFederationConfiguration |

**To Enable:** Either wait for Microsoft to fix the module, or implement
certificate-based authentication. Then move these collectors back to
`collectors/teams/` and register them.
