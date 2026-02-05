"""Base class for data collectors."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collectors.graph_client import GraphClient


class BaseDataCollector(ABC):
    """Abstract base class for data collectors."""

    @abstractmethod
    async def collect(self, client: "GraphClient") -> dict[str, Any]:
        """Collect data from the cloud API.

        Args:
            client: The API client to use for data collection.

        Returns:
            Dictionary of collected data to be passed to OPA for evaluation.
        """
        pass
