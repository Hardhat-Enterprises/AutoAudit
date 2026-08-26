# SharePoint Control Development

How to add a CIS SharePoint control using the existing PnP integration. Use CIS 7.3.1 as the reference.

## Before You Start

Set up certificates and Compose using [SharePoint local runtime](./sharepoint-local-runtime.md).

- Reuse the existing SharePoint PnP path (`sharepoint.pnp.*`). Do not add a second SharePoint authentication flow.
- Do not use or register REST-era collectors such as `sharepoint.spo_tenant`.
- Collector IDs for this integration are `sharepoint.pnp.*`.

## 1. Check Existing Evidence First

Before creating a collector, check whether a shared collector already returns the CIS property.

For tenant-wide settings, start with `sharepoint.pnp.tenant`, which runs `Get-PnPTenant` and returns the full tenant object plus normalized fields.

If the raw cmdlet already includes the property:

- reuse `sharepoint.pnp.tenant`
- add a normalized field only if the policy needs it
- do **not** create one collector per CIS control

## 2. Follow CIS 7.3.1

```
CIS 7.3.1
  → sharepoint.pnp.tenant
  → Get-PnPTenant
  → DisallowInfectedFileDownload
  → disallow_infected_file_download
  → metadata + Rego
```

| Piece | Location |
|---|---|
| Collector | `engine/collectors/sharepoint/pnp/tenant.py` |
| Registry | `engine/collectors/registry.py` (`sharepoint.pnp.tenant`) |
| Metadata | `engine/policies/cis/microsoft-365-foundations/v6.0.0/metadata.json` (control `7.3.1`) |
| Policy | `engine/policies/cis/microsoft-365-foundations/v6.0.0/7.3.1_disallow_infected_file_download.rego` |

Normalized field:

```text
disallow_infected_file_download  ←  tenant["DisallowInfectedFileDownload"]
```

Compliant when that field is `true`. Worker passes collector output to OPA as root `input`.

## 3. Implement Your Control

1. Confirm the CIS requirement and the exact evidence property.
2. Check whether `sharepoint.pnp.tenant` / `Get-PnPTenant` already returns it.
3. Reuse the collector; add a normalized field if needed.
4. Wire the control in metadata (`ready`, `sharepoint.pnp.*`, policy file).
5. Add the Rego policy.
6. Add focused tests.

A different SharePoint cmdlet can justify another **shared** PnP collector (for example sync restrictions via `Get-PnPTenantSyncClientRestriction`). Do not create a second tenant collector.

## 4. Rego

Rego sees the collector dict at the root (not nested under a wrapper). For 7.3.1 that is `input.disallow_infected_file_download`.

Handle:

- compliant (`true` → pass)
- non-compliant (`false` → fail)
- null / missing → fail closed (must not silently pass)

## 5. Validate

targeted tests → Engine pytest → local SharePoint runtime → real scan

`PASS` or `FAIL` from real tenant evidence is successful E2E. `ERROR`, authentication failure, collection failure, or missing evidence is a runtime failure.

## Important Rules

- Never commit certificates, passwords, or `docker-compose.sharepoint.override.yml`.
- Do not duplicate SharePoint auth, routing, or client code.
- Do not register `sharepoint.spo_tenant`.
- Reuse shared `sharepoint.pnp.*` collectors.
- Before changing collector output shape, check other controls that consume it.
