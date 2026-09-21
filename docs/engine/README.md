# Compliance Engine

The Engine turns benchmark requirements (for example CIS Microsoft 365 controls) into automated checks against a Microsoft 365 tenant. **Collectors** retrieve evidence from the tenant, **Rego policies** evaluate that evidence, the **worker** runs each check, and AutoAudit **stores the result** so the dashboard can show it.

If the local stack is not running yet, start with [Getting Started](../GETTING_STARTED.md).

## How a scan works

1. You start a scan in AutoAudit.
2. The backend queues that scan for the Engine.
3. The worker loads controls that are marked ready to run.
4. A collector retrieves evidence from the tenant.
5. A Rego policy evaluates that evidence.
6. The result is stored for AutoAudit to display.

**Failed** means the check ran and the tenant did not meet the requirement. **Error** means the Engine could not finish the check (for example a missing collector or a permission failure).

Full explanation: [Engine architecture](architecture.md).

## Start with your task

| I want to… | Read |
| --- | --- |
| Understand how the Engine works | [Engine architecture](architecture.md) |
| Develop a first control | [Control development walkthrough](control-development-walkthrough.md) |
| Develop a SharePoint control | [SharePoint control development](sharepoint-control-development.md) |
| Configure SharePoint locally | [SharePoint local runtime](sharepoint-local-runtime.md) |
| Work with Security & Compliance PowerShell | [Security & Compliance local runtime](compliance-local-runtime.md) |
| Manually test a collector | [Manual collector testing](manual-collector-testing.md) |
| Verify policy behaviour | [Compliance engine verification](compliance-engine-verification.md) |
| Understand the general contribution process | [Contributing](../CONTRIBUTING.md) |

## Main Engine locations

| Location | What it is |
| --- | --- |
| [`engine/collectors/`](../../engine/collectors/) | Code that fetches tenant evidence |
| [`engine/policies/`](../../engine/policies/) | Rego checks and the metadata that wires them to collectors |
| [`engine/worker/`](../../engine/worker/) | The process that runs a scan and each control |
| [`engine/powershell/`](../../engine/powershell/) | The service that collects evidence through Exchange, SharePoint PnP, and Security & Compliance PowerShell cmdlets |

## Developing a control

requirement → evidence → collector → Rego → tests → metadata → live scan

Worked example (CIS 1.2.2): [Control development walkthrough](control-development-walkthrough.md). SharePoint-specific path: [SharePoint control development](sharepoint-control-development.md).

## Before submitting a PR

- [ ] You know what evidence the collector should return.
- [ ] Rego handles compliant, non-compliant, and missing evidence.
- [ ] Metadata points at the correct collector and policy, and is marked ready only when the control can actually run.
- [ ] Engine tests pass.
- [ ] A live scan executes your control without a runtime error (a tenant *fail* is acceptable; an *error* for your control is not).
- [ ] No secrets, certificates, or tenant-specific files are committed.
