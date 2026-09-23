"""Base class for collectors that need more than one API client.

AutoAudit's existing collector base classes (BaseDataCollector,
BasePowerShellCollector) each pass exactly one client into collect().
Some controls genuinely need two different APIs at once (for example
E8-PA-1.1, which needs Microsoft Graph for windowsProtectionState and
DVM for software inventory), and there was no supported way to express
that.

This is an ADDITIVE base class. It does not change BaseDataCollector,
BasePowerShellCollector, or any existing collector. Only new collectors
that genuinely need multiple clients should use this.
"""

from abc import ABC, abstractmethod
from typing import Any

# Known client types tasks.py knows how to build. Extend this as new
# client types are added (e.g. FabricClient, once it's promoted out of
# _pending).
KNOWN_CLIENT_TYPES = {"graph", "powershell", "dvm"}


class BaseMultiClientCollector(ABC):
    """Abstract base class for collectors needing multiple API clients.

    Subclasses set `required_clients` to the client keys they need.
    tasks.py builds each required client and passes them all into
    collect() as a dict keyed by name.

    Example:
        class MyCollector(BaseMultiClientCollector):
            required_clients = ("graph", "dvm")

            async def collect(self, clients: dict[str, Any]) -> dict[str, Any]:
                graph_data = await clients["graph"].get_all_pages(...)
                dvm_data = await clients["dvm"].get_software_inventory()
                ...
    """

    #: Client keys this collector needs, e.g. ("graph", "dvm").
    #: Must be a subset of KNOWN_CLIENT_TYPES.
    required_clients: tuple[str, ...] = ()

    @abstractmethod
    async def collect(self, clients: dict[str, Any]) -> dict[str, Any]:
        """Collect data using multiple API clients.

        Args:
            clients: Dict of client name -> client instance, one entry
                per name in required_clients.

        Returns:
            Dictionary of collected data to be passed to OPA for evaluation.
        """
        pass
