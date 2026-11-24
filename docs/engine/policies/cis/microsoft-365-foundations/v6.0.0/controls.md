# CIS Microsoft 365 Foundations Benchmark v6.0.0 - Control Status

This document provides a comprehensive overview of all 140 controls in the CIS Microsoft 365 Foundations Benchmark v6.0.0, including their automation status and implementation progress.

*Last Updated: 2026-11-24*

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Controls** | 140 |
| **CIS Automated** | 117 |
| **CIS Manual** | 23 |

### Our Implementation Status

| Our Audit Type | Count | Description |
|----------------|-------|-------------|
| Automated | 88 | Fully automatable with current collectors |
| Deferred | 8 | Collector works but needs "compliant with review" capability |
| Blocked | 33 | Collector exists but authentication issues prevent execution |
| Manual | 11 | No API available, truly requires manual verification |
| Not Started | 0 | No collector implemented yet |
    
---

## Legend

**Our Audit Type:**
- **Automated** - We can fully automate pass/fail determination
- **Deferred** - Collector works but requires user involvement to verify exclusions/gaps
- **Blocked** - Collector exists but authentication issues prevent execution
- **Manual** - No API available, truly requires manual verification

**Status:**
- **Implemented** - Collector exists and is registered
- **Pending** - Collector exists but blocked/not registered
- **Not Started** - No collector implemented yet
- **N/A** - Truly manual, no collector needed

---

## Section 1: Microsoft 365 Admin Center

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 1.1.1 | L1 | Ensure Administrative accounts are cloud-only | Automated | Automated | `entra.roles.cloud_only_admins` | Implemented | |
| 1.1.2 | L1 | Ensure two emergency access accounts have been defined | Manual | Manual | | N/A | Organizational policy; requires human designation of accounts |
| 1.1.3 | L1 | Ensure that between two and four global admins are designated | Automated | Automated | `entra.roles.privileged_roles` | Implemented | |
| 1.1.4 | L1 | Ensure administrative accounts use licenses with a reduced application footprint | Automated | Automated | `entra.roles.admin_license_footprint` | Implemented | Graph `licenseDetails` per admin; sample `{"admin_accounts":[{"userPrincipalName":"admin@contoso.com","uses_reduced_license_footprint":true,"high_footprint_service_plans_enabled":[],"sku_part_numbers":["AAD_PREMIUM_P2"]}]}` |
| 1.2.1 | L2 | Ensure that only organizationally managed/approved public groups exist | Automated | Automated | `entra.groups.groups` | Implemented | Uses Microsoft Graph /groups to identify groups with Public visibility. The Rego policy passes when no public groups exist and flags existing public groups for organisational review. The automated check does not establish whether a public group is approved |
| 1.2.2 | L1 | Ensure sign-in to shared mailboxes is blocked | Automated | Automated | `exchange.mailbox.mailboxes` | Implemented | Collector and Rego policy implemented; OPA tests present |
| 1.3.1 | L1 | Ensure the 'Password expiration policy' is set to 'Set passwords to never expire (recommended)' | Automated | Automated | `entra.domains.password_policy` | Implemented | |
| 1.3.2 | L2 | Ensure 'Idle session timeout' is set to '3 hours (or less)' for unmanaged devices | Automated | Automated | `entra.policies.activity_based_timeout` | Implemented | Uses Microsoft Graph /policies/activityBasedTimeoutPolicies to collect idle timeout evidence. The Rego policy checks for a timeout greater than zero and no more than 180 minutes. Six policy tests passed using OPA 1.13.1-debug. Live tenant validation has not been confirmed in this review |
| 1.3.3 | L2 | Ensure 'External sharing' of calendars is not available | Automated | Automated | `exchange.organization.sharing_policy` | Implemented | Uses Exchange Online Get-SharingPolicy evidence to flag enabled external-sharing policies and an enabled Default Sharing Policy. Current Rego behaviour treats absent policy evidence as compliant; missing-evidence handling requires review |
| 1.3.4 | L1 | Ensure 'User owned apps and services' is restricted | Automated | Automated | `entra.applications.apps_and_services_settings` | Implemented | |
| 1.3.5 | L1 | Ensure internal phishing protection for Forms is enabled | Automated | Automated | `entra.applications.forms_settings` | Implemented | |
| 1.3.6 | L2 | Ensure the customer lockbox feature is enabled | Automated | Automated | `exchange.organization.organization_config` | Implemented | |
| 1.3.7 | L2 | Ensure 'third-party storage services' are restricted in 'Microsoft 365 on the web' | Automated | Automated | `entra.applications.third_party_storage_services` | Implemented | Queries Microsoft Graph for the Third Party Storage Services service principal by app ID. The Rego policy reports compliance when the service principal exists and accountEnabled is false. Graph request exceptions propagate to the worker |
| 1.3.8 | L2 | Ensure that Sways cannot be shared with people outside of your organization | Manual | Manual | | N/A | No API available for Sway settings |
| 1.3.9 | L1 | Ensure shared bookings pages are restricted to select users | Automated | Automated | `exchange.organization.owa_mailbox_policy` | Implemented | Uses Exchange Online Get-OwaMailboxPolicy and Get-OrganizationConfig evidence. When the default OWA Bookings creation setting is a Boolean, the policy reports compliance if that setting is false or tenant-wide BookingsEnabled is false. A missing or null default OWA setting returns an unable-to-determine result |

---

## Section 2: Microsoft Defender for Office 365

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 2.1.1 | L2 | Ensure Safe Links for Office Applications is Enabled | Automated | Automated | `exchange.protection.safe_links_policy` | Implemented | |
| 2.1.2 | L1 | Ensure the Common Attachment Types Filter is enabled | Automated | Automated | `exchange.protection.malware_filter_policy` | Implemented | |
| 2.1.3 | L1 | Ensure notifications for internal users sending malware is Enabled | Automated | Automated | `exchange.protection.malware_filter_policy` | Implemented | |
| 2.1.4 | L2 | Ensure Safe Attachments policy is enabled | Automated | Automated | `exchange.protection.safe_attachment_policy` | Implemented | |
| 2.1.5 | L2 | Ensure Safe Attachments for SharePoint, OneDrive, and Microsoft Teams is Enabled | Automated | Automated | `exchange.protection.atp_policy_o365` | Implemented | |
| 2.1.6 | L1 | Ensure Exchange Online Spam Policies are set to notify administrators | Automated | Automated | `exchange.protection.hosted_outbound_spam_filter` | Implemented | |
| 2.1.7 | L2 | Ensure that an anti-phishing policy has been created | Automated | Automated | `exchange.protection.anti_phish_policy` | Implemented | |
| 2.1.8 | L1 | Ensure that SPF records are published for all Exchange Domains | Automated | Automated | `exchange.dns.dns_security_records` | Implemented | DNS lookup for SPF TXT records |
| 2.1.9 | L1 | Ensure that DKIM is enabled for all Exchange Online Domains | Automated | Automated | `exchange.authentication.dkim_signing_config` | Implemented | |
| 2.1.10 | L1 | Ensure DMARC Records for all Exchange Online domains are published | Automated | Automated | `exchange.dns.dns_security_records` | Implemented | DNS lookup for DMARC TXT records |
| 2.1.11 | L2 | Ensure comprehensive attachment filtering is applied | Automated | Automated | `exchange.protection.malware_filter_policy` | Implemented | |
| 2.1.12 | L1 | Ensure the connection filter IP allow list is not used | Automated | Automated | `exchange.protection.hosted_connection_filter` | Implemented | |
| 2.1.13 | L1 | Ensure the connection filter safe list is off | Automated | Automated | `exchange.protection.hosted_connection_filter` | Implemented | |
| 2.1.14 | L1 | Ensure inbound anti-spam policies do not contain allowed domains | Automated | Automated | `exchange.protection.hosted_content_filter` | Implemented | |
| 2.1.15 | L1 | Ensure outbound anti-spam message limits are in place | Automated | Automated | `exchange.protection.hosted_outbound_spam_filter` | Implemented | |
| 2.2.1 | L1 | Ensure emergency access account activity is monitored | Manual | Manual | | N/A | Organizational policy; requires defining which accounts to monitor |
| 2.4.1 | L1 | Ensure Priority account protection is enabled and configured | Automated | Blocked | `exchange.protection.priority_account_protection_config` | Blocked | IPPSSession requires certificate auth |
| 2.4.2 | L1 | Ensure Priority accounts have 'Strict protection' presets applied | Automated | Automated | `exchange.protection.priority_account_protection` | Implemented | |
| 2.4.3 | L2 | Ensure Microsoft Defender for Cloud Apps is enabled and configured | Manual | Manual | | N/A | MCAS configuration requires portal verification |
| 2.4.4 | L1 | Ensure Zero-hour auto purge for Microsoft Teams is on | Automated | Automated | `exchange.protection.teams_protection_policy` | Implemented | |

---

## Section 3: Data Management

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 3.1.1 | L1 | Ensure Microsoft 365 audit log search is Enabled | Automated | Automated | `exchange.organization.admin_audit_log_config` | Implemented | Check unified_audit_log_ingestion_enabled = True |
| 3.2.1 | L1 | Ensure DLP policies are enabled | Automated | Blocked | | Pending | IPPSSession requires certificate auth |
| 3.2.2 | L1 | Ensure DLP policies are enabled for Microsoft Teams | Automated | Blocked | | Pending | IPPSSession requires certificate auth |
| 3.3.1 | L1 | Ensure Information Protection sensitivity label policies are published | Automated | Blocked | | Pending | IPPSSession requires certificate auth |

---

## Section 4: Microsoft Intune

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 4.1 | L2 | Ensure devices without a compliance policy are marked 'not compliant' | Automated | Automated | `entra.devices.device_management_settings` | Implemented | Uses Microsoft Graph beta /deviceManagement/settings. The Rego policy applies a heuristic requiring secureByDefault and isScheduledActionEnabled to both be true. This heuristic requires validation against the benchmark requirement |
| 4.2 | L2 | Ensure device enrollment for personally owned devices is blocked by default | Automated | Automated | `entra.devices.enrollment_restrictions` | Implemented | |

---

## Section 5: Microsoft Entra ID

### 5.1 - User Settings

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 5.1.2.1 | L1 | Ensure 'Per-user MFA' is disabled | Automated | Manual | | N/A | Only available in beta API; not stable |
| 5.1.2.2 | L2 | Ensure third party integrated applications are not allowed | Automated | Automated | `entra.policies.authorization_policy` | Implemented | Check allowedToCreateApps |
| 5.1.2.3 | L1 | Ensure 'Restrict non-admin users from creating tenants' is set to 'Yes' | Automated | Automated | `entra.policies.authorization_policy` | Implemented | Check allowedToCreateTenants |
| 5.1.2.4 | L1 | Ensure access to the Entra admin center is restricted | Manual | Manual | | N/A | Only available via internal Azure API |
| 5.1.2.5 | L2 | Ensure the option to remain signed in is hidden | Manual | Manual | | N/A | Setting not exposed via Graph API |
| 5.1.2.6 | L2 | Ensure 'LinkedIn account connections' is disabled | Manual | Manual | | N/A | Only available via internal Azure API |
| 5.1.3.1 | L1 | Ensure a dynamic group for guest users is created | Automated | Automated | `entra.groups.groups` | Implemented | Uses the groups collector's dynamic_groups evidence. The Rego policy reports compliance when at least one dynamic membership rule contains 'guest' (case-insensitive). It does not fully validate the rule's meaning; review matching rules to confirm they select guest users |
| 5.1.3.2 | L1 | Ensure users cannot create security groups | Automated | Automated | `entra.policies.authorization_policy` | Implemented | Check allowedToCreateSecurityGroups |
| 5.1.4.1 | L2 | Ensure the ability to join devices to Entra is restricted | Automated | Automated | `entra.devices.device_registration_policy` | Implemented | |
| 5.1.4.2 | L1 | Ensure the maximum number of devices per user is limited | Automated | Automated | `entra.devices.device_registration_policy` | Implemented | |
| 5.1.4.3 | L1 | Ensure the GA role is not added as a local administrator during Entra join | Automated | Automated | `entra.devices.device_registration_policy` | Implemented | |
| 5.1.4.4 | L1 | Ensure local administrator assignment is limited during Entra join | Automated | Automated | `entra.devices.device_registration_policy` | Implemented | Collector corrected and Rego policy implemented; OPA tests present |
| 5.1.4.5 | L1 | Ensure Local Administrator Password Solution is enabled | Automated | Automated | `entra.devices.device_registration_policy` | Implemented | Uses Microsoft Graph beta /policies/deviceRegistrationPolicy and maps localAdminPassword.isEnabled to laps_enabled. The Rego policy reports compliance only when laps_enabled is true. Missing, null or invalid values report that LAPS status cannot be determined |
| 5.1.4.6 | L2 | Ensure users are restricted from recovering BitLocker keys | Automated | Automated | `entra.policies.authorization_policy` | Implemented | Check allowedToReadBitlockerKeysForOwnedDevice |
| 5.1.5.1 | L2 | Ensure user consent to apps accessing company data on their behalf is not allowed | Automated | Automated | `entra.policies.authorization_policy` | Implemented | |
| 5.1.5.2 | L1 | Ensure the admin consent workflow is enabled | Automated | Automated | `entra.policies.admin_consent_request_policy` | Implemented | |
| 5.1.6.1 | L2 | Ensure that collaboration invitations are sent to allowed domains only | Automated | Automated | `entra.policies.b2b_policy` | Implemented | |
| 5.1.6.2 | L1 | Ensure that guest user access is restricted | Automated | Automated | `entra.policies.authorization_policy` | Implemented | Check guestUserRoleId |
| 5.1.6.3 | L2 | Ensure guest user invitations are limited to the Guest Inviter role | Automated | Automated | `entra.policies.authorization_policy` | Implemented | Check allowInvitesFrom |
| 5.1.8.1 | L1 | Ensure that password hash sync is enabled for hybrid deployments | Manual | Manual | | N/A | Requires on-premises AD Connect verification |

### 5.2 - Authentication

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 5.2.2.1 | L1 | Ensure multifactor authentication is enabled for all users in administrative roles | Automated | Deferred | `entra.conditional_access.policies` | Implemented | Requires verification of all 15 admin roles |
| 5.2.2.2 | L1 | Ensure multifactor authentication is enabled for all users | Automated | Automated | `entra.conditional_access.policies` | Implemented | Automated: passes if an enabled Conditional Access policy requires MFA for all users and apps. Exclusions are listed in details for assessor review and do not fail the control. No OPA test file yet |
| 5.2.2.3 | L1 | Enable Conditional Access policies to block legacy authentication | Automated | Automated | `entra.conditional_access.legacy_auth_block` | Implemented | |
| 5.2.2.4 | L1 | Ensure Sign-in frequency is enabled and browser sessions are not persistent for Administrative users | Automated | Deferred | `entra.conditional_access.policies` | Implemented | Requires admin role verification |
| 5.2.2.5 | L2 | Ensure 'Phishing-resistant MFA strength' is required for Administrators | Automated | Deferred | `entra.conditional_access.policies` | Implemented | Requires admin role verification |
| 5.2.2.6 | L1 | Enable Identity Protection user risk policies | Automated | Deferred | `entra.conditional_access.policies` | Implemented | Requires policy coverage verification |
| 5.2.2.7 | L1 | Enable Identity Protection sign-in risk policies | Automated | Deferred | `entra.conditional_access.policies` | Implemented | Requires policy coverage verification |
| 5.2.2.8 | L2 | Ensure 'sign-in risk' is blocked for medium and high risk | Automated | Deferred | `entra.conditional_access.policies` | Implemented | Requires policy coverage verification |
| 5.2.2.9 | L1 | Ensure a managed device is required for authentication | Automated | Automated | `entra.conditional_access.policies` | Implemented | Automated: passes if an enabled Conditional Access policy requires a compliant device for all users and apps. Exclusions are not checked. No OPA test file yet |
| 5.2.2.10 | L1 | Ensure a managed device is required to register security information | Automated | Deferred | `entra.conditional_access.policies` | Implemented | Requires policy coverage verification |
| 5.2.2.11 | L1 | Ensure sign-in frequency for Intune Enrollment is set to 'Every time' | Automated | Deferred | `entra.conditional_access.policies` | Implemented | Requires policy coverage verification |
| 5.2.2.12 | L1 | Ensure the device code sign-in flow is blocked | Automated | Automated | `entra.conditional_access.policies` | Implemented | Automated: passes if an enabled Conditional Access policy blocks the device code flow. The users the policy covers and any exclusions are not checked. No OPA test file yet |
| 5.2.3.1 | L1 | Ensure Microsoft Authenticator is configured to protect against MFA fatigue | Automated | Automated | `entra.authentication.mfa_fatigue_protection` | Implemented | |
| 5.2.3.2 | L1 | Ensure custom banned passwords lists are used | Automated | Automated | `entra.authentication.password_protection` | Implemented | |
| 5.2.3.3 | L1 | Ensure password protection is enabled for on-prem Active Directory | Automated | Automated | `entra.authentication.password_protection` | Implemented | |
| 5.2.3.4 | L1 | Ensure all member users are 'MFA capable' | Automated | Automated | `entra.authentication.mfa_registration_report` | Implemented | |
| 5.2.3.5 | L1 | Ensure weak authentication methods are disabled | Automated | Automated | `entra.authentication.authentication_methods` | Implemented | Check SMS/Voice disabled |
| 5.2.3.6 | L1 | Ensure system-preferred multifactor authentication is enabled | Automated | Automated | `entra.authentication.authentication_methods` | Implemented | |
| 5.2.3.7 | L2 | Ensure the email OTP authentication method is disabled | Automated | Automated | `entra.authentication.authentication_methods` | Implemented | |
| 5.2.4.1 | L1 | Ensure 'Self service password reset enabled' is set to 'All' | Manual | Manual | | N/A | SSPR settings not exposed via Graph API |

### 5.3 - Privileged Access

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 5.3.1 | L2 | Ensure 'Privileged Identity Management' is used to manage roles | Automated | Automated | `entra.governance.pim_role_policies` | Implemented | |
| 5.3.2 | L1 | Ensure 'Access reviews' for Guest Users are configured | Automated | Automated | `entra.governance.access_reviews` | Implemented | |
| 5.3.3 | L1 | Ensure 'Access reviews' for privileged roles are configured | Automated | Automated | `entra.governance.access_reviews` | Implemented | Combined with pim_role_policies |
| 5.3.4 | L1 | Ensure approval is required for Global Administrator role activation | Automated | Automated | `entra.governance.pim_role_policies` | Implemented | |
| 5.3.5 | L1 | Ensure approval is required for Privileged Role Administrator activation | Automated | Automated | `entra.governance.pim_role_policies` | Implemented | |

---

## Section 6: Exchange Online

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 6.1.1 | L1 | Ensure 'AuditDisabled' organizationally is set to 'False' | Automated | Automated | `exchange.organization.organization_config` | Implemented | |
| 6.1.2 | L1 | Ensure mailbox audit actions are configured | Automated | Automated | `exchange.mailbox.mailbox_audit_actions` | Implemented | |
| 6.1.3 | L1 | Ensure 'AuditBypassEnabled' is not enabled on mailboxes | Automated | Automated | `exchange.mailbox.mailbox_audit` | Implemented | |
| 6.2.1 | L1 | Ensure all forms of mail forwarding are blocked and/or disabled | Automated | Automated | `exchange.transport.transport_rules` | Implemented | |
| 6.2.2 | L1 | Ensure mail transport rules do not whitelist specific domains | Automated | Automated | `exchange.transport.transport_rules` | Implemented | |
| 6.2.3 | L1 | Ensure email from external senders is identified | Automated | Automated | `exchange.transport.external_in_outlook` | Implemented | |
| 6.3.1 | L2 | Ensure users installing Outlook add-ins is not allowed | Automated | Automated | `exchange.mailbox.role_assignment_policy` | Implemented | |
| 6.5.1 | L1 | Ensure modern authentication for Exchange Online is enabled | Automated | Automated | `exchange.organization.organization_config` | Implemented | Check OAuth2ClientProfileEnabled |
| 6.5.2 | L1 | Ensure MailTips are enabled for end users | Automated | Automated | `exchange.organization.organization_config` | Implemented | Collector and Rego policy implemented; no OPA test file yet |
| 6.5.3 | L2 | Ensure additional storage providers are restricted in Outlook on the web | Automated | Automated | `exchange.organization.owa_mailbox_policy` | Implemented | |
| 6.5.4 | L1 | Ensure SMTP AUTH is disabled | Automated | Automated | `exchange.organization.transport_config` | Implemented | |
| 6.5.5 | L2 | Ensure Direct Send submissions are rejected | Automated | Automated | `exchange.organization.organization_config` | Implemented | Collector and Rego policy implemented; no OPA test file yet |

---

## Section 7: SharePoint Online

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 7.2.1 | L1 | Ensure modern authentication for SharePoint applications is required | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Collector and Rego policy implemented (PnP tenant collector); OPA tests present |
| 7.2.2 | L1 | Ensure SharePoint and OneDrive integration with Azure AD B2B is enabled | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Collector and Rego policy implemented (PnP tenant collector); no OPA test file yet |
| 7.2.3 | L1 | Ensure external content sharing is restricted | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Collector and Rego policy implemented (PnP tenant collector); OPA tests present |
| 7.2.4 | L2 | Ensure OneDrive content sharing is restricted | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Collector and policy implemented using PnP integration; OPA tests present |
| 7.2.5 | L2 | Ensure that SharePoint guest users cannot share items they don't own | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Collector and Rego policy implemented (PnP tenant collector); no OPA test file yet |
| 7.2.6 | L2 | Ensure SharePoint external sharing is restricted | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Collector and Rego policy implemented (PnP tenant collector); no OPA test file yet |
| 7.2.7 | L1 | Ensure link sharing is restricted in SharePoint and OneDrive | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Collector extended with default_sharing_link_type and policy implemented; OPA tests present |
| 7.2.8 | L2 | Ensure external sharing is restricted by security group | Manual | Automated | `sharepoint.pnp.tenant` | Implemented | CIS says Manual; automated via GuestSharingGroupAllowListInTenantByPrincipalIdentity. Passes only when sharing is disabled tenant-wide; groups set fails pending membership review |
| 7.2.9 | L1 | Ensure guest access to a site or OneDrive will expire automatically | Automated | Blocked | `sharepoint.pnp.tenant` | Blocked | Uses sharepoint.pnp.tenant evidence for ExternalUserExpirationRequired and ExternalUserExpireInDays. Eight policy tests passed using OPA 1.13.1-debug. Live end-to-end validation remains unconfirmed in this review; access to the approved SharePoint PnP certificate credentials is pending. Restore ready status after successful live collection and verification of the policy result against the tenant settings |
| 7.2.10 | L1 | Ensure reauthentication with verification code is restricted | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Uses the existing sharepoint.pnp.tenant collector with EmailAttestationRequired and EmailAttestationReAuthDays evidence; OPA tests present (inline in the policy file) |
| 7.2.11 | L1 | Ensure the SharePoint default sharing link permission is set | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Collector and Rego policy implemented (PnP tenant collector); OPA tests present |
| 7.3.1 | L2 | Ensure Office 365 SharePoint infected files are disallowed for download | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Collector and Rego policy implemented (PnP tenant collector); no OPA test file yet |
| 7.3.2 | L2 | Ensure OneDrive sync is restricted for unmanaged devices | Automated | Automated | `sharepoint.pnp.tenant` | Implemented | Collector and Rego policy implemented (PnP tenant collector); OPA tests present |

---

## Section 8: Microsoft Teams

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 8.1.1 | L2 | Ensure external file sharing in Teams is enabled for only approved cloud storage services | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.1.2 | L1 | Ensure users can't send emails to a channel email address | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.2.1 | L2 | Ensure external domains are restricted in the Teams admin center | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.2.2 | L1 | Ensure communication with unmanaged Teams users is disabled | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.2.3 | L1 | Ensure external Teams users cannot initiate conversations | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.2.4 | L1 | Ensure the organization cannot communicate with accounts in trial Teams tenants | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.4.1 | L1 | Ensure app permission policies are configured | Manual | Manual | | N/A | CIS marks as Manual; also affected by ACM migration |
| 8.5.1 | L2 | Ensure anonymous users can't join a meeting | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.5.2 | L1 | Ensure anonymous users and dial-in callers can't start a meeting | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.5.3 | L1 | Ensure only people in my org can bypass the lobby | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.5.4 | L1 | Ensure users dialing in can't bypass the lobby | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.5.5 | L2 | Ensure meeting chat does not allow anonymous users | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.5.6 | L2 | Ensure only organizers and co-organizers can present | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.5.7 | L1 | Ensure external participants can't give or request control | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.5.8 | L2 | Ensure external meeting chat is off | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.5.9 | L2 | Ensure meeting recording is off by default | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |
| 8.6.1 | L1 | Ensure users can report security concerns in Teams | Automated | Blocked | | Pending | Teams module AccessTokens auth not working |

---

## Section 9: Microsoft Fabric

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 9.1.1 | L1 | Ensure guest user access is restricted | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.2 | L1 | Ensure external user invitations are restricted | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.3 | L1 | Ensure guest access to content is restricted | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.4 | L1 | Ensure 'Publish to web' is restricted | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.5 | L2 | Ensure 'Interact with and share R and Python' visuals is 'Disabled' | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.6 | L1 | Ensure 'Allow users to apply sensitivity labels for content' is 'Enabled' | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.7 | L1 | Ensure shareable links are restricted | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.8 | L1 | Ensure enabling of external data sharing is restricted | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.9 | L1 | Ensure 'Block ResourceKey Authentication' is 'Enabled' | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.10 | L1 | Ensure access to APIs by service principals is restricted | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.11 | L1 | Ensure service principals cannot create and use profiles | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |
| 9.1.12 | L1 | Ensure service principals ability to create workspaces, connections and deployment pipelines is restricted | Manual | Blocked | | Pending | Fabric API auth untested; CIS says Manual but can be automated |

---

## Implementation Priority

### Priority 1: Fix Authentication Blockers

| Blocker | Controls Affected | Resolution |
|---------|-------------------|------------|
| Teams PowerShell AccessTokens bug | 8.1.1-8.6.1 (16 controls) | Wait for Microsoft fix or implement certificate auth |
| IPPSSession certificate auth | 2.4.1, 3.2.1, 3.2.2, 3.3.1 (4 controls) | Implement certificate-based authentication |
| Fabric API auth | 9.1.1-9.1.12 (12 controls) | Test and validate Fabric API token auth |

### Priority 2: Complete SharePoint Controls

| Component | Controls Affected |
|-----------|-------------------|
| `sharepoint.pnp.tenant` (implemented) | 7.2.1-7.2.8, 7.2.10, 7.2.11, 7.3.1, 7.3.2 |
| `sharepoint.pnp.tenant` (blocked, awaiting certificate credentials and live validation) | 7.2.9 |

### Priority 3: Complete Remaining Collectors

Controls with collectors that exist but need control logic defined or new collectors needed.
