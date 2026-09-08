# Policy Metadata in OPA

This directory contains compliance policies written in Rego for evaluation by Open Policy Agent (OPA). We use OPA's native metadata annotations to embed control information directly in the policy files themselves.

## Why embed metadata in the policy files?

We considered a few approaches for managing policy metadata:

1. **Separate JSON/YAML files** - Store metadata in sidecar files alongside policies
2. **Database storage** - Keep metadata in our application database
3. **OPA annotations** - Embed metadata directly in Rego files using the `# METADATA` block

We went with option 3 because it keeps everything in one place. When you're reading a policy, you immediately see what control it implements, what permissions it needs, and how to fix issues it finds. No jumping between files or querying a database.

OPA's annotation system was designed for exactly this use case. The metadata travels with the policy through version control, code review, and deployment. If someone copies a policy file to another system, the context goes with it.

## The annotation format

OPA expects metadata in a YAML block at the top of the file, starting with `# METADATA`. Here's the structure we use:

```rego
# METADATA
# title: Short name of the control
# description: |
#   What this control checks for and why it matters.
#   Can span multiple lines using YAML's pipe syntax.
# related_resources:
# - ref: https://example.com/benchmark
#   description: Link to the source benchmark
# custom:
#   control_id: CIS-1.1.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v3.1.0
#   severity: critical
#   service: EntraID
#   requires_permissions:
#   - User.Read.All

package your.package.name

# ... policy rules ...
```

### Standard OPA fields

These are recognized by OPA tooling:

- **title** - A short, human-readable name
- **description** - What the policy does
- **related_resources** - Links to external documentation (benchmark sources, etc.)

### Custom fields

Everything under `custom:` is ours to define. We use:

- **control_id** - The identifier from the compliance framework (e.g., CIS-1.1.1)
- **framework** - Which framework this comes from (cis, nist, essential8, etc.)
- **benchmark** - The specific benchmark slug
- **version** - Benchmark version
- **severity** - Risk level: critical, high, medium, or low
- **service** - The cloud service being checked (EntraID, Exchange, SharePoint, etc.)
- **requires_permissions** - API permissions needed to collect data for this control


## Accessing metadata at runtime

OPA provides built-in functions to query metadata:

```rego
# Get metadata for the current rule
metadata := rego.metadata.rule()

# Get the full annotation chain (including package-level metadata)
chain := rego.metadata.chain()
```

You can also inspect all metadata from the command line:

```bash
opa inspect -a policies/
```

This is useful for building tooling that generates documentation or validates that all policies have required fields.

## Directory structure

Policies are organized by framework, benchmark, and version:

```
policies/
  cis/
    microsoft-365-foundations/
      v3.1.0/
        1.1.1_admin_cloud_only.rego
        1.1.3_global_admin_count.rego
    gcp/
      v1.0.0/
        ...
  essential-eight/
    asd-essential-eight/
      v2025/
        e8_mac_2_1_win32_api_block.rego
        metadata.json
```

The package name in each policy mirrors this structure, with dots replacing slashes and hyphens becoming underscores:

```
cis/microsoft-365-foundations/v3.1.0/1.1.1_...
→ package cis.microsoft_365_foundations.v3_1_0.control_1_1_1

essential-eight/asd-essential-eight/v2025/e8_mac_2_1_...
→ package essential_eight.asd_essential_eight.v2025.control_e8_mac_2_1
```

## Naming convention: kebab on the metadata side, snake on the Rego side

This split is deliberate, not accidental:

- **Human-readable side** (directories, metadata.json `framework` / `slug`, file names other than .rego) uses **kebab-case**. It matches the existing CIS tree and is easier to read in URLs and shell commands.
- **Rego side** (package paths, .rego file names) uses **snake_case**. The Rego language doesn't allow hyphens in package identifiers, so this isn't a choice.
- **Control IDs** are kept **verbatim from the framework's published format** — no re-stylising. For CIS that means dotted lowercase (`1.1.1`); for ASD Essential Eight that means uppercase with hyphens and dots (`E8-MAC-2.1`, `E8-MFA-2.1`, `E8-PRIV-1.1`). The reason is auditor traceability: someone cross-referencing AutoAudit's output against the source benchmark should get a line-for-line match without mental translation.

The engine bridges the two sides automatically. `engine/worker/tasks.py` normalises framework names and control IDs when building the OPA package path at scan time — lowercasing and replacing hyphens / dots with underscores. The transform is a no-op on CIS inputs (which are already lowercase + dot-separated) and the right thing on Essential Eight inputs.

In practice this means contributors adding a new non-CIS control don't have to think about the conversion: keep the framework / slug / control_id in their published form on the metadata side, name the Rego file and package in snake_case, and the engine wires them together correctly.

## References

- [OPA Policy Language - Annotations](https://www.openpolicyagent.org/docs/latest/policy-language/#annotations)
- [OPA Policy Reference - Metadata Built-ins](https://www.openpolicyagent.org/docs/latest/policy-reference/#rego)
- [Styra Rego Style Guide](https://docs.styra.com/opa/rego-style-guide)
