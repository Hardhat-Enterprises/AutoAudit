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
        pass
