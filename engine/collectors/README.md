# Data Collectors

This directory contains data collectors that fetch information from cloud APIs for compliance evaluation. Each collector gathers specific data that gets passed to OPA policies for assessment.

## How collectors work

A collector is a simple class with one job: call an API and return structured data. The data goes to OPA, which runs the actual compliance checks. Collectors don't make pass/fail decisions - they just gather facts.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Collector  │────▶│  Raw Data   │────▶│  OPA Policy │
│  (fetch)    │     │  (dict)     │     │  (evaluate) │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Writing a new collector

### 1. Pick the client

There are two, and they are not interchangeable. Of the 48 collectors registered in `registry.py`, **26 take a `GraphClient` and 22 take a `PowerShellClient`.** Which one you get is decided by your collector's registered ID, not by your class — see [The two clients](#the-two-clients) below — so choose before you write anything.

Use Graph if the setting has a Graph endpoint. Use PowerShell if it does not: every Exchange Online and SharePoint Online setting AutoAudit reads today comes through a cmdlet.

### 2. Create the collector class

For a Graph collector, inherit from `BaseDataCollector`:

```python
from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class MyNewCollector(BaseDataCollector):
    """One-line description of what this collects."""

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        # Fetch data from the API
        data = await client.get("/some/endpoint")

        # Return structured data for OPA
        return {
            "items": data.get("value", []),
            "count": len(data.get("value", [])),
        }
```

For a PowerShell collector, inherit from `BasePowerShellCollector` and annotate the client accordingly. All 22 PowerShell collectors do this, and no Graph collector does:

```python
from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class MyPowerShellCollector(BasePowerShellCollector):
    """One-line description of what this collects."""

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        policies = await client.run_cmdlet("ExchangeOnline", "Get-SomePolicy")

        # The service returns None, a single object, or a list. Normalise it,
        # and leave the interpretation to the policy.
        if policies is None:
            policies = []
        elif isinstance(policies, dict):
            policies = [policies]

        return {"policies": policies, "total_policies": len(policies)}
```

Imports are rooted at `collectors.`, not `engine.collectors.`: `engine/` is the import root for the worker and the tests.

### 3. Place it in the right folder

Collectors are organized by service and domain:

```
collectors/
  entra/              # Microsoft Entra ID (Azure AD) - Graph
    applications/  authentication/  conditional_access/  devices/
    domains/  governance/  groups/  policies/  roles/  users/
  exchange/           # Exchange Online - PowerShell, except dns/
    audit/  authentication/  dns/  mailbox/  organization/
    protection/  transport/
  sharepoint/         # SharePoint Online - PowerShell
    pnp/
  _pending/           # Written but not registered; not run by a scan
    compliance/  fabric/  teams/
  compliance/  m365/  teams/   # package stubs, no collectors in them
```

`_pending/` holds collectors that exist but are not in `registry.py`. Nothing there runs. The five Teams collectors and the two Purview compliance collectors live there, so no registered collector connects to the `Teams` or `Compliance` PowerShell modules. Teams *settings* are not entirely uncovered: `exchange.protection.teams_protection_policy` reads `Get-TeamsProtectionPolicy` through the `ExchangeOnline` module. The bare `compliance/`, `m365/` and `teams/` packages at the top level hold only an `__init__.py`.

### 4. Register it

Why do we need to register these?

You could dynamically import based on the string path, but that's fragile and has security implications. The registry provides:

- Explicit allowlist - Only registered collectors can be instantiated
- Single place to see all collectors - Easy to audit what's available
- Decoupling - The scan engine doesn't need to know the import paths, just the IDs
- Validation - get_collector() raises a clear error for unknown IDs

Add your collector to `registry.py`:

```python
from collectors.entra.roles.my_new import MyNewCollector

DATA_COLLECTORS: dict[str, type[BaseDataCollector]] = {
    # ... existing collectors ...
    "entra.roles.my_new": MyNewCollector,
}
```

The ID follows the folder path by convention: `entra.roles.my_new` maps to `entra/roles/my_new.py`. It is a convention, not an invariant — `entra.conditional_access.policies` is registered against `entra/conditional_access/conditional_access_policies.py` — but follow it unless you have a reason not to.

**The ID is also what selects your client at runtime**, so a PowerShell collector registered under an `entra.` ID will be handed a `GraphClient` and fail.

### 5. Reference it in metadata.json

In the benchmark's `metadata.json`, set the `data_collector_id` for your control:

```json
{
  "control_id": "CIS-1.2.3",
  "data_collector_id": "entra.roles.my_new",
  ...
}
```

## Guidelines

**Keep collectors focused.** One collector per control, or per logical data set. If two controls need the same data, they can share a collector.

**Return raw data.** Don't make compliance decisions in collectors. Return the facts and let OPA policies interpret them. This keeps the logic testable and the collectors reusable.

**Handle pagination.** Use `client.get_all_pages()` for endpoints that return paged results. The Graph API often limits responses to 100 items.

**Use type hints.** The `collect` method should return `dict[str, Any]`. Document what keys the dict contains in the docstring.

**Async all the way.** Collectors are async. Use `await` for all API calls. This lets us run multiple collectors concurrently during scans.

## The two clients

An earlier version of this page said `GraphClient` was "shared across all Microsoft collectors (Entra, M365 services)". It is not, and the difference is nearly half the registry: 26 of the 48 registered collectors take a `GraphClient`, and the other 22 take a `PowerShellClient`.

`engine/worker/tasks.py` picks between them by **collector ID prefix**, not by anything on your class:

```python
if collector_id.startswith(
    ("exchange.", "compliance.", "sharepoint.pnp.")
) and not collector_id.startswith("exchange.dns."):
    client = PowerShellClient(...)
else:
    client = GraphClient(...)
```

The collector is instantiated first, by ID, and the client is then constructed and passed to `collect()`. That rule and the `collect` annotations agree for all 48 registered collectors today, but the rule is what actually runs: change one without the other and the collector gets the wrong client.

`exchange.dns.dns_security_records` is the carve-out: it lives under `exchange/` but reads tenant domains from Graph and then resolves SPF and DMARC over DNS, so it takes a `GraphClient`.

Of the 22 PowerShell collectors, 21 are `exchange.*` and reach the `ExchangeOnline` module; one is `sharepoint.pnp.tenant` and reaches `SharePointOnline`.

### `GraphClient`

Handles Microsoft Graph API authentication and requests. Every `entra.*` collector uses it, including the device-management ones that read Intune endpoints under `/deviceManagement`, as does `exchange.dns.dns_security_records`.

```python
# Basic GET request
data = await client.get("/users")

# GET with query parameters
data = await client.get("/users", params={"$filter": "accountEnabled eq true"})

# Paginated endpoint (fetches all pages)
all_users = await client.get_all_pages("/users")

# Beta endpoint
data = await client.get("/some/beta/endpoint", beta=True)
```

The client handles:
- OAuth token acquisition via MSAL
- Token caching — note that the cached token is returned without an expiry check, so it is caching, not refresh
- Pagination with @odata.nextLink
- Both v1.0 and beta Graph endpoints

`get_all_pages` follows `@odata.nextLink` up to `max_pages`, which defaults to 100, and returns what it has without raising if there are more. If you expect an endpoint to exceed that, pass a higher `max_pages` rather than assuming the list is complete.

### `PowerShellClient`

Runs a cmdlet through the PowerShell service, for settings Graph does not expose.

```python
# module, cmdlet, then cmdlet parameters as keyword arguments
config = await client.run_cmdlet("ExchangeOnline", "Get-OrganizationConfig")
policy = await client.run_cmdlet("ExchangeOnline", "Get-SafeLinksPolicy", Identity=name)
```

The client handles:
- Access-token acquisition via MSAL. The token authenticates the *connection* command the service runs — `Connect-ExchangeOnline`, and `Connect-MicrosoftTeams` with `-AccessTokens` — not the data cmdlet itself
- Dispatch to the PowerShell HTTP service when `POWERSHELL_SERVICE_URL` is set, and to a local Docker container otherwise
- `SharePointOnline`, which takes a different path entirely: it requires the HTTP service, has no Docker fallback, and authenticates with `Connect-PnPOnline` using a certificate, so the client raises unless both `sharepoint_admin_url` and `certificate_alias` are configured

A cmdlet returns `None`, a single object, or a list depending on how many results there are. Normalise that in the collector rather than in the policy.
