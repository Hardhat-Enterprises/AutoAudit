"""Priority Account Protection collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.4.1, 2.4.2

Connection Method: Microsoft Graph Security API (beta)
Required Scopes: Security.Read.All
Graph Endpoint: /security/priorityAccounts (beta)

Note: The endpoint name and shape may vary by tenant rollout; this collector
returns raw records plus a small summary. If the endpoint is unavailable, the
call will raise to surface the configuration gap.
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient
from collectors.powershell_client import PowerShellClient, PowerShellExecutionError


class PriorityAccountsDataCollector(BaseDataCollector):
    """Collects priority accounts and their protection presets."""

    async def collect(self, client: Any) -> dict[str, Any]:
        """Collect priority accounts via Graph Security; fallback to EXO PowerShell.

        Returns:
            Dict containing:
            - priority_accounts: list of accounts
            - total: count of accounts
            - source: "graph" or "powershell"
        """
        # Prefer Graph Security API; if unavailable, fall back to EXO cmdlet
        try:
            if isinstance(client, GraphClient):
                records = await client.get_all_pages("/security/priorityAccounts", beta=True)
                accounts: list[dict[str, Any]] = []
                for rec in records:
                    accounts.append(
                        {
                            "id": rec.get("id"),
                            "userPrincipalName": rec.get("userPrincipalName") or rec.get("upn"),
                            "displayName": rec.get("displayName"),
                            "protectionPreset": rec.get("protectionPreset") or rec.get("protectionLevel"),
                        }
                    )
                return {
                    "priority_accounts": accounts,
                    "total": len(accounts),
                    "source": "graph",
                }
        except Exception:
            # Fall through to PowerShell if Graph fails
            pass

        if not isinstance(client, PowerShellClient):
            raise RuntimeError("PowerShell fallback requires PowerShellClient")

        try:
            ps_result = await client.run_cmdlet(
                module="ExchangeOnline",
                cmdlet="Get-PriorityAccountProtectionPolicy",
            )
        except PowerShellExecutionError as e:
            raise RuntimeError(f"Priority account collection failed via PowerShell: {e}")

        records = ps_result or []
        # Normalize EXO output shape
        accounts: list[dict[str, Any]] = []
        for rec in records if isinstance(records, list) else [records]:
            # EXO returns Users list and ProtectionPreset
            users = rec.get("Users") or []
            preset = rec.get("ProtectionPreset")
            for u in users:
                accounts.append(
                    {
                        "id": None,
                        "userPrincipalName": u,
                        "displayName": None,
                        "protectionPreset": preset,
                    }
                )

        return {
            "priority_accounts": accounts,
            "total": len(accounts),
            "source": "powershell",
        }
