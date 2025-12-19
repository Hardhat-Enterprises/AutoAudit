"""Registry of available data collectors."""

from collectors.base import BaseDataCollector

# Applications
from collectors.entra.applications.apps_and_services_settings import (
    AppsAndServicesSettingsDataCollector,
)
from collectors.entra.applications.forms_settings import FormsSettingsDataCollector
from collectors.entra.applications.service_principals import (
    ServicePrincipalsDataCollector,
)

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
from collectors.entra.domains.domains import DomainsDataCollector
from collectors.entra.domains.password_policy import PasswordPolicyDataCollector

# Governance
from collectors.entra.governance.access_reviews import AccessReviewsDataCollector
from collectors.entra.governance.pim_role_policies import PimRolePoliciesDataCollector

# Groups
from collectors.entra.groups.groups import GroupsDataCollector

# Policies
from collectors.entra.policies.activity_timeout_policy import (
    ActivityTimeoutPolicyDataCollector,
)
from collectors.entra.policies.admin_consent_request_policy import (
    AdminConsentRequestPolicyDataCollector,
)
from collectors.entra.policies.authorization_policy import (
    AuthorizationPolicyDataCollector,
)
from collectors.entra.policies.b2b_policy import B2BPolicyDataCollector

# Roles
from collectors.entra.roles.cloud_only_admins import CloudOnlyAdminsDataCollector
from collectors.entra.roles.directory_roles import DirectoryRolesDataCollector
from collectors.entra.roles.privileged_roles import PrivilegedRolesDataCollector

# Users
from collectors.entra.users.users import UsersDataCollector

# Exchange
from collectors.exchange.dns.dns_security_records import (
    DnsSecurityRecordsDataCollector,
)

# Fabric
from collectors.fabric.tenant_settings import FabricTenantSettingsDataCollector

# Registry mapping data_collector_id to collector class
DATA_COLLECTORS: dict[str, type[BaseDataCollector]] = {
    # Applications
    "entra.applications.apps_and_services_settings": AppsAndServicesSettingsDataCollector,
    "entra.applications.forms_settings": FormsSettingsDataCollector,
    "entra.applications.service_principals": ServicePrincipalsDataCollector,
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
    "entra.domains.domains": DomainsDataCollector,
    "entra.domains.password_policy": PasswordPolicyDataCollector,
    # Governance
    "entra.governance.access_reviews": AccessReviewsDataCollector,
    "entra.governance.pim_role_policies": PimRolePoliciesDataCollector,
    # Groups
    "entra.groups.groups": GroupsDataCollector,
    # Policies
    "entra.policies.activity_timeout_policy": ActivityTimeoutPolicyDataCollector,
    "entra.policies.admin_consent_request_policy": AdminConsentRequestPolicyDataCollector,
    "entra.policies.authorization_policy": AuthorizationPolicyDataCollector,
    "entra.policies.b2b_policy": B2BPolicyDataCollector,
    # Roles
    "entra.roles.cloud_only_admins": CloudOnlyAdminsDataCollector,
    "entra.roles.directory_roles": DirectoryRolesDataCollector,
    "entra.roles.privileged_roles": PrivilegedRolesDataCollector,
    # Users
    "entra.users.users": UsersDataCollector,
    # Exchange
    "exchange.dns.dns_security_records": DnsSecurityRecordsDataCollector,
    # Fabric
    "fabric.tenant_settings": FabricTenantSettingsDataCollector,
}


def get_collector(collector_id: str) -> BaseDataCollector:
    """Get a collector instance by ID."""
    collector_class = DATA_COLLECTORS.get(collector_id)
    if not collector_class:
        raise ValueError(f"Unknown collector: {collector_id}")
    return collector_class()
