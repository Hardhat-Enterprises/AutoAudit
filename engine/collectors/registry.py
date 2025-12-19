"""Registry of available data collectors."""

from collectors.base import BaseDataCollector
from collectors.entra.authentication.mfa_fatigue_protection import (
    MfaFatigueProtectionDataCollector,
)
from collectors.entra.conditional_access.legacy_auth_block import (
    LegacyAuthBlockDataCollector,
)
from collectors.entra.domains.password_policy import PasswordPolicyDataCollector
from collectors.entra.governance.pim_role_policies import PimRolePoliciesDataCollector
from collectors.entra.roles.cloud_only_admins import CloudOnlyAdminsDataCollector
from collectors.entra.roles.privileged_roles import PrivilegedRolesDataCollector
from collectors.exchange.dns.dns_security_records import (
    DnsSecurityRecordsDataCollector,
)
from collectors.fabric.tenant_settings import FabricTenantSettingsDataCollector

# Registry mapping data_collector_id to collector class
DATA_COLLECTORS: dict[str, type[BaseDataCollector]] = {
    "entra.authentication.mfa_fatigue_protection": MfaFatigueProtectionDataCollector,
    "entra.conditional_access.legacy_auth_block": LegacyAuthBlockDataCollector,
    "entra.domains.password_policy": PasswordPolicyDataCollector,
    "entra.governance.pim_role_policies": PimRolePoliciesDataCollector,
    "entra.roles.cloud_only_admins": CloudOnlyAdminsDataCollector,
    "entra.roles.privileged_roles": PrivilegedRolesDataCollector,
    "exchange.dns.dns_security_records": DnsSecurityRecordsDataCollector,
    "fabric.tenant_settings": FabricTenantSettingsDataCollector,
}


def get_collector(collector_id: str) -> BaseDataCollector:
    """Get a collector instance by ID."""
    collector_class = DATA_COLLECTORS.get(collector_id)
    if not collector_class:
        raise ValueError(f"Unknown collector: {collector_id}")
    return collector_class()
