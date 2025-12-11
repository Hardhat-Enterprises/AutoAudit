"""OPA (Open Policy Agent) client for policy evaluation."""

import httpx

from worker.config import settings


class OPAClient:
    """Client for querying Open Policy Agent for policy evaluation."""

    def __init__(self, base_url: str | None = None):
        """Initialize OPA client.

        Args:
            base_url: OPA server URL. Defaults to OPA_URL from settings.
        """
        self.base_url = (base_url or settings.OPA_URL).rstrip("/")

    async def evaluate_policy(
        self, package_path: str, input_data: dict
    ) -> dict:
        """Evaluate a policy against input data.

        Args:
            package_path: The OPA package path (e.g., "cis/microsoft_365_foundations/v3_1_0/control_1_1_1")
            input_data: The data to evaluate (facts collected from the cloud)

        Returns:
            The evaluation result from OPA, typically containing:
            - compliant: bool
            - message: str
            - affected_resources: list
            - details: dict
        """
        # Convert package path to OPA URL format
        # e.g., "cis.microsoft_365_foundations.v3_1_0.control_1_1_1" -> "cis/microsoft_365_foundations/v3_1_0/control_1_1_1"
        url_path = package_path.replace(".", "/")

        # Query the specific "result" rule within the package
        # This gives us the compliance result directly without extra nesting
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/data/{url_path}/result",
                json={"input": input_data},
            )
            response.raise_for_status()
            result = response.json()

        # OPA returns {"result": {...}} - extract the result
        return result.get("result", {})

    async def health_check(self) -> bool:
        """Check if OPA server is healthy.

        Returns:
            True if OPA is responding, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False


# Default client instance
opa_client = OPAClient()
