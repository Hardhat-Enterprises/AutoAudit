"""Registry of available data collectors."""

from collectors.base import BaseDataCollector
from collectors.entra.conditional_access.legacy_auth_block import (
    LegacyAuthBlockDataCollector,
)
from collectors.entra.domains.password_policy import PasswordPolicyDataCollector
from collectors.entra.roles.cloud_only_admins import CloudOnlyAdminsDataCollector
from collectors.entra.roles.privileged_roles import PrivilegedRolesDataCollector

# Registry mapping data_collector_id to collector class
DATA_COLLECTORS: dict[str, type[BaseDataCollector]] = {
    "entra.roles.cloud_only_admins": CloudOnlyAdminsDataCollector,
    "entra.roles.privileged_roles": PrivilegedRolesDataCollector,
    "entra.domains.password_policy": PasswordPolicyDataCollector,
    "entra.conditional_access.legacy_auth_block": LegacyAuthBlockDataCollector,
}


def get_collector(collector_id: str) -> BaseDataCollector:
    """Get a collector instance by ID."""
    collector_class = DATA_COLLECTORS.get(collector_id)
    if not collector_class:
        raise ValueError(f"Unknown collector: {collector_id}")
    return collector_class()
