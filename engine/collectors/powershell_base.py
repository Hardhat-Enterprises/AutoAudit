"""Base class for PowerShell-based collectors."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collectors.powershell_client import PowerShellClient


class BasePowerShellCollector(ABC):
    """Abstract base class for PowerShell collectors.

    This base class is used for collectors that require PowerShell cmdlets
    from Exchange Online, Microsoft Teams, or Security & Compliance modules.

    Authentication uses client secret via MSAL to obtain access tokens,
    which are then passed to PowerShell cmdlets via the -AccessToken parameter.
    """

    @abstractmethod
    async def collect(self, client: "PowerShellClient") -> dict[str, Any]:
        """Collect data using PowerShell cmdlets.

        Args:
            client: The PowerShell client to use for data collection.

        Returns:
            Dictionary of collected data to be passed to OPA for evaluation.
        """
        
def as_list(
    result: dict[str, Any] | list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Normalise a cmdlet result to a list.

    PowerShell cmdlets return None when there are no results, a single object
    when there is one, and a list when there are several. Collectors that expect
    a collection should route the result through this helper.
    """
    if result is None:
        return []
    if isinstance(result, dict):
        return [result]
    return result


def as_dict(
    result: dict[str, Any] | list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Normalise a cmdlet result expected to be a single object.

    Returns an empty dict where the cmdlet returned nothing, so callers can read
    keys without guarding against None.
    """
    if result is None:
        return {}
    if isinstance(result, list):
        return result[0] if result else {}
    return result
