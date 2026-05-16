"""Registry of available data collectors."""

from collectors.base import BaseDataCollector

# Applications
from collectors.entra.applications.apps_and_services_settings import (
    AppsAndServicesSettingsDataCollector,
)
from collectors.entra.applications.forms_settings import FormsSettingsDataCollector

# Authentication
from collectors.entra.authentication.authentication_methods import (
    AuthenticationMethodsDataCollector,
)
from collectors.entra.authentication.mfa_fatigue_protection import (
    MfaFatigueProtectionDataCollector,
)
from collectors.entra.authentication.mfa_registration_report import (
    MFARegistrationReportDataCollector,
)
from collectors.entra.authentication.password_protection import (
    PasswordProtectionDataCollector,
)

# Conditional Access
from collectors.entra.conditional_access.conditional_access_policies import (
    ConditionalAccessPoliciesDataCollector,
)
from collectors.entra.conditional_access.legacy_auth_block import (
    LegacyAuthBlockDataCollector,
)

# Devices
from collectors.entra.devices.device_management_settings import (
    DeviceManagementSettingsDataCollector,
)
from collectors.entra.devices.device_registration_policy import (
    DeviceRegistrationPolicyDataCollector,
)
from collectors.entra.devices.enrollment_restrictions import (
    EnrollmentRestrictionsDataCollector,
)

# Domains
from collectors.entra.domains.password_policy import PasswordPolicyDataCollector

# Governance
from collectors.entra.governance.access_reviews import AccessReviewsDataCollector
from collectors.entra.governance.pim_role_policies import PimRolePoliciesDataCollector

# Groups
from collectors.entra.groups.groups import GroupsDataCollector

# Policies
from collectors.entra.policies.admin_consent_request_policy import (
    AdminConsentRequestPolicyDataCollector,
)
from collectors.entra.policies.authorization_policy import (
    AuthorizationPolicyDataCollector,
)
from collectors.entra.policies.b2b_policy import B2BPolicyDataCollector

# Roles
from collectors.entra.roles.cloud_only_admins import CloudOnlyAdminsDataCollector
from collectors.entra.roles.privileged_roles import PrivilegedRolesDataCollector

# Exchange - DNS
from collectors.exchange.dns.dns_security_records import (
    DnsSecurityRecordsDataCollector,
)

# Exchange - Organization
from collectors.exchange.organization.organization_config import (
    OrganizationConfigDataCollector,
)
from collectors.exchange.organization.owa_mailbox_policy import (
    OwaMailboxPolicyDataCollector,
)
from collectors.exchange.organization.sharing_policy import (
    SharingPolicyDataCollector,
)
from collectors.exchange.organization.transport_config import (
    TransportConfigDataCollector,
)

# Exchange - Authentication
from collectors.exchange.authentication.dkim_signing_config import (
    DkimSigningConfigDataCollector,
)

# Exchange - Mailbox
from collectors.exchange.mailbox.mailbox_audit import MailboxAuditDataCollector
from collectors.exchange.mailbox.mailbox_audit_actions import (
    MailboxAuditActionsDataCollector,
)
from collectors.exchange.mailbox.mailboxes import MailboxesDataCollector
from collectors.exchange.mailbox.role_assignment_policy import (
    RoleAssignmentPolicyDataCollector,
)

# Exchange - Protection
from collectors.exchange.protection.anti_phish_policy import (
    AntiPhishPolicyDataCollector,
)
from collectors.exchange.protection.atp_policy_o365 import AtpPolicyO365DataCollector
from collectors.exchange.protection.hosted_connection_filter import (
    HostedConnectionFilterDataCollector,
)
from collectors.exchange.protection.hosted_content_filter import (
    HostedContentFilterDataCollector,
)
from collectors.exchange.protection.hosted_outbound_spam_filter import (
    HostedOutboundSpamFilterDataCollector,
)
from collectors.exchange.protection.malware_filter_policy import (
    MalwareFilterPolicyDataCollector,
)
from collectors.exchange.protection.safe_attachment_policy import (
    SafeAttachmentPolicyDataCollector,
)
from collectors.exchange.protection.safe_links_policy import (
    SafeLinksPolicyDataCollector,
)
from collectors.exchange.protection.teams_protection_policy import (
    TeamsProtectionPolicyDataCollector,
)

# Exchange - Transport
from collectors.exchange.transport.external_in_outlook import (
    ExternalInOutlookDataCollector,
)
from collectors.exchange.transport.transport_rules import TransportRulesDataCollector


# Registry mapping data_collector_id to collector class
DATA_COLLECTORS: dict[str, type[BaseDataCollector]] = {
    # Applications
    "entra.applications.apps_and_services_settings": AppsAndServicesSettingsDataCollector,
    "entra.applications.forms_settings": FormsSettingsDataCollector,
    # Authentication
    "entra.authentication.authentication_methods": AuthenticationMethodsDataCollector,
    "entra.authentication.mfa_fatigue_protection": MfaFatigueProtectionDataCollector,
    "entra.authentication.mfa_registration_report": MFARegistrationReportDataCollector,
    "entra.authentication.password_protection": PasswordProtectionDataCollector,
    # Conditional Access
    "entra.conditional_access.policies": ConditionalAccessPoliciesDataCollector,
    "entra.conditional_access.legacy_auth_block": LegacyAuthBlockDataCollector,
    # Devices
    "entra.devices.device_management_settings": DeviceManagementSettingsDataCollector,
    "entra.devices.device_registration_policy": DeviceRegistrationPolicyDataCollector,
    "entra.devices.enrollment_restrictions": EnrollmentRestrictionsDataCollector,
    # Domains
    "entra.domains.password_policy": PasswordPolicyDataCollector,
    # Governance
    "entra.governance.access_reviews": AccessReviewsDataCollector,
    "entra.governance.pim_role_policies": PimRolePoliciesDataCollector,
    # Groups
    "entra.groups.groups": GroupsDataCollector,
    # Policies
    "entra.policies.admin_consent_request_policy": AdminConsentRequestPolicyDataCollector,
    "entra.policies.authorization_policy": AuthorizationPolicyDataCollector,
    "entra.policies.b2b_policy": B2BPolicyDataCollector,
    # Roles
    "entra.roles.cloud_only_admins": CloudOnlyAdminsDataCollector,
    "entra.roles.privileged_roles": PrivilegedRolesDataCollector,
    # Users
    # Exchange - DNS
    "exchange.dns.dns_security_records": DnsSecurityRecordsDataCollector,
    # Exchange - Organization
    "exchange.organization.organization_config": OrganizationConfigDataCollector,
    "exchange.organization.owa_mailbox_policy": OwaMailboxPolicyDataCollector,
    "exchange.organization.sharing_policy": SharingPolicyDataCollector,
    "exchange.organization.transport_config": TransportConfigDataCollector,
    # Exchange - Authentication
    "exchange.authentication.dkim_signing_config": DkimSigningConfigDataCollector,
    # Exchange - Mailbox
    "exchange.mailbox.mailbox_audit": MailboxAuditDataCollector,
    "exchange.mailbox.mailbox_audit_actions": MailboxAuditActionsDataCollector,
    "exchange.mailbox.mailboxes": MailboxesDataCollector,
    "exchange.mailbox.role_assignment_policy": RoleAssignmentPolicyDataCollector,
    # Exchange - Protection
    "exchange.protection.anti_phish_policy": AntiPhishPolicyDataCollector,
    "exchange.protection.atp_policy_o365": AtpPolicyO365DataCollector,
    "exchange.protection.hosted_connection_filter": HostedConnectionFilterDataCollector,
    "exchange.protection.hosted_content_filter": HostedContentFilterDataCollector,
    "exchange.protection.hosted_outbound_spam_filter": HostedOutboundSpamFilterDataCollector,
    "exchange.protection.malware_filter_policy": MalwareFilterPolicyDataCollector,
    "exchange.protection.safe_attachment_policy": SafeAttachmentPolicyDataCollector,
    "exchange.protection.safe_links_policy": SafeLinksPolicyDataCollector,
    "exchange.protection.teams_protection_policy": TeamsProtectionPolicyDataCollector,
    # Exchange - Transport
    "exchange.transport.external_in_outlook": ExternalInOutlookDataCollector,
    "exchange.transport.transport_rules": TransportRulesDataCollector,
}


def get_collector(collector_id: str) -> BaseDataCollector:
    """Get a collector instance by ID."""
    collector_class = DATA_COLLECTORS.get(collector_id)
    if not collector_class:
        raise ValueError(f"Unknown collector: {collector_id}")
    return collector_class()
