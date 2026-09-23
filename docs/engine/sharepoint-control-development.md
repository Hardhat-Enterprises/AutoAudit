# SharePoint Control Development

Use this guide to add a CIS SharePoint control using the existing PnP integration.

Local setup: [SharePoint local runtime](./sharepoint-local-runtime.md).

## 1. Identify the Evidence

Identify the CIS requirement, the SharePoint setting/property, the PnP/PowerShell cmdlet that returns it, and the expected compliant value.

For tenant-wide settings, check `Get-PnPTenant` first.

## 2. Reuse an Existing Collector

Inspect `engine/collectors/sharepoint/pnp/`. For tenant settings, prefer `sharepoint.pnp.tenant`.

- Reuse an existing collector when possible.
- Add a normalized field only if the policy needs it.
- Do not create one collector per control.
- Do not use or register `sharepoint.spo_*`.

## 3. Update Metadata

In `engine/policies/cis/microsoft-365-foundations/v6.0.0/metadata.json`, set `automation_status` to `ready`, `data_collector_id` to the correct `sharepoint.pnp.*` collector, and `policy_file` to the new Rego file.

## 4. Add the Rego Policy

Add the policy under `engine/policies/cis/microsoft-365-foundations/v6.0.0/`.

OPA receives the collector dict as root input (`input.<field_name>`). Handle compliant, non-compliant, and null/missing. Missing evidence must not silently pass.

## 5. Add Tests

Add focused tests for compliant, non-compliant, and null/missing. Then run the Engine tests.

## 6. Validate Locally

Use the shared SharePoint runtime: tests → runtime → real scan.

`PASS` or `FAIL` from real tenant evidence is successful E2E. `ERROR`, authentication failure, collection failure, or missing evidence is a runtime or implementation problem.

## Rules

- Reuse `sharepoint.pnp.*`.
- Do not use `sharepoint.spo_*`.
- Do not create another SharePoint authentication flow.
- Do not commit certificates, passwords, or `docker-compose.sharepoint.override.yml`.
- Check other controls before changing a shared collector.
