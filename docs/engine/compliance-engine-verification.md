# Compliance Engine Verification Framework

## Overview

The Compliance Engine Verification Framework provides reusable behavioural
testing for AutoAudit's active compliance policies.

AutoAudit already includes structural validation that checks whether policy
metadata, collectors, Rego files, package declarations, and control IDs are
wired together correctly. Structural correctness, however, does not guarantee
that a policy will make the correct compliance decision when given known input
data.

This framework complements the existing structural tests by executing real Rego
policies through Open Policy Agent (OPA) against predefined compliant and
non-compliant fixtures. It then validates the returned result structure,
compares the actual compliance decision with the expected outcome, and reports
behavioural coverage across ready automated controls.

The core purpose of the framework is:

> Verify that AutoAudit compliance policies do not only exist and connect
> correctly, but also behave correctly.

---

## Why This Exists

A policy may pass structural validation while still containing incorrect logic.

For example, a policy could:

- exist at the correct path;
- be referenced correctly in `metadata.json`;
- use the expected Rego package;
- reference a registered collector;
- still return `compliant: true` for a configuration that should fail.

The verification framework addresses this gap by testing policy behaviour
against known scenarios.

A fixture defines:

1. the control being tested;
2. a known input configuration;
3. the expected compliance decision.

The framework then executes the real AutoAudit policy and compares the returned
result against the expected outcome.

---

## Architecture

The framework is implemented primarily under:

```text
engine/
├── validation/
│   ├── __init__.py
│   ├── coverage.py
│   ├── discovery.py
│   ├── fixtures.py
│   ├── opa_runner.py
│   └── validator.py
├── scripts/
│   └── validate_engine.py
└── tests/
    ├── fixtures/
    │   └── compliance/
    ├── test_compliance_coverage.py
    └── test_compliance_validator.py
```

The verification flow is:

```text
Fixture discovery
      ↓
Fixture validation
      ↓
Fully-qualified control identity
      ↓
Metadata discovery
      ↓
Policy file discovery
      ↓
Rego package discovery
      ↓
OPA query construction
      ↓
OPA policy execution
      ↓
Result contract validation
      ↓
Expected vs actual comparison
      ↓
PASS / FAIL
      ↓
Behavioural coverage reporting
```

---

## Control Discovery

Controls are discovered automatically from policy `metadata.json` files under:

```text
engine/policies/
```

The framework searches metadata entries containing both:

```json
{
  "control_id": "...",
  "policy_file": "..."
}
```

The associated Rego file is then located relative to the metadata file.

The framework also reads the Rego package declaration directly from the policy
file and constructs the OPA result query automatically.

For example:

```rego
package essential_eight.asd_essential_eight.v2025.control_e8_mfa_2_1
```

becomes:

```text
data.essential_eight.asd_essential_eight.v2025.control_e8_mfa_2_1.result
```

This means contributors do not need to manually define policy paths or OPA
queries in the verification runner.

### Fully-qualified control identity

Control IDs are not globally unique across AutoAudit.

For example, the control ID `1.1.1` exists in multiple CIS Microsoft 365
benchmark versions. Because of this, controls are identified using the following
fully-qualified key:

```text
framework + benchmark + version + control_id
```

For example:

```text
cis / microsoft-365-foundations / v6.0.0 / 1.1.1
```

is treated as a different control from:

```text
cis / microsoft-365-foundations / v3.1.0 / 1.1.1
```

This prevents fixtures from being matched to a policy from the wrong framework
or benchmark version.

---

## Fixture Format

Behavioural fixtures are stored under:

```text
engine/tests/fixtures/compliance/
```

The framework discovers fixture files recursively, so new controls can be added
without modifying the runner.

A fixture uses the following structure:

```json
{
  "framework": "cis",
  "benchmark": "microsoft-365-foundations",
  "version": "v6.0.0",
  "control_id": "5.2.3.1",
  "scenario": "MFA number matching enabled",
  "input": {
    "number_matching_enabled": true
  },
  "expected": {
    "compliant": true
  }
}
```

### Required fixture fields

Each fixture must contain:

```text
framework
benchmark
version
control_id
scenario
input
expected
```

The `expected` object must include:

```json
{
  "compliant": true
}
```

or:

```json
{
  "compliant": false
}
```

The `input` object should represent the data structure expected by the real Rego
policy.

---

## Adding Behavioural Verification for a New Control

In most cases, contributors should not need to modify the Python verification
framework.

### 1. Locate the control metadata

Find the relevant entry in the benchmark `metadata.json` file and confirm:

- framework;
- benchmark;
- version;
- control ID;
- policy file;
- automation status;
- audit type.

### 2. Inspect the Rego policy

Review the policy to determine:

- required input fields;
- compliant behaviour;
- non-compliant behaviour;
- useful boundary or edge cases.

### 3. Create a fixture directory

For example:

```text
engine/tests/fixtures/compliance/cis_1_1_3/
```

### 4. Add representative fixtures

A typical control should include at least:

```text
compliant.json
noncompliant.json
```

Controls with range or boundary logic may benefit from additional cases.

For CIS control `1.1.3`, for example, the verification suite includes:

```text
3 global administrators → compliant
1 global administrator  → non-compliant
5 global administrators → non-compliant
```

### 5. Run the verification framework

From `engine/`:

```bash
python -m scripts.validate_engine
```

If the fixture metadata matches an existing policy-backed control, the framework
will automatically:

- discover the fixture;
- find the control metadata;
- locate the Rego policy;
- read the Rego package;
- construct the OPA query;
- execute the policy;
- validate the result;
- compare expected and actual compliance;
- include the control in behavioural coverage.

No control-specific Python changes should be required.

---

## OPA Execution

The framework executes the real Rego policy through the OPA CLI.

The fixture `input` object is passed directly to OPA. The runner then extracts
the evaluated `result` object returned by the policy.

Conceptually:

```text
fixture input
    ↓
OPA CLI
    ↓
real AutoAudit Rego policy
    ↓
policy result
```

If OPA cannot be found, policy execution fails, or OPA returns an unexpected
result structure, the framework reports an error and exits unsuccessfully.

OPA must therefore be available on the developer or CI environment `PATH`.

---

## Result Contract Validation

Before comparing the expected compliance decision, the framework validates that
the policy result follows the standard AutoAudit result contract.

The required result structure is:

```json
{
  "compliant": true,
  "message": "Human-readable explanation",
  "details": {}
}
```

The framework currently requires:

```text
result              → JSON object
result.compliant    → boolean
result.message      → string
result.details      → object
```

Additional fields are allowed.

This allows the framework to detect two different classes of regression:

### Behavioural regression

The policy returns the wrong compliance decision.

Example:

```text
Expected: compliant = false
Actual:   compliant = true
```

### Contract regression

The policy returns a malformed result that may not be safely consumed by the
rest of AutoAudit.

Example:

```json
{
  "pass": true,
  "reason": "Control passed"
}
```

Even if the logical decision is correct, this does not satisfy the expected
AutoAudit result contract.

---

## Behavioural Coverage

The framework reports the proportion of ready automated policy-backed controls
that currently have behavioural verification fixtures.

A control is included in the coverage denominator when:

```text
automation_status == "ready"
AND
benchmark_audit_type == "Automated"
```

A control counts as behaviour-tested when at least one valid fixture maps to its
fully-qualified control identity.

A failing fixture still counts as behavioural coverage. Coverage measures
whether verification exists, not whether the policy currently passes its
verification.

At the time of writing, the framework reports:

```text
Ready automated controls:   79
Behaviour-tested controls:   3
Behavioural coverage:        3.8%
```

Current behaviour-tested controls are:

```text
CIS Microsoft 365 Foundations v6.0.0 / 1.1.3
CIS Microsoft 365 Foundations v6.0.0 / 5.2.3.1
Essential Eight v2025 / E8-MFA-2.1
```

The current fixture suite contains seven behavioural scenarios.

---

## Current Verification Scenarios

### CIS 1.1.3 — Global Administrator count

The policy requires between two and four Global Administrators.

Current fixtures verify:

```text
3 administrators → compliant
1 administrator  → non-compliant
5 administrators → non-compliant
```

### CIS 5.2.3.1 — MFA fatigue protection

The policy checks whether Microsoft Authenticator number matching is enabled.

Current fixtures verify:

```text
number matching enabled  → compliant
number matching disabled → non-compliant
```

### Essential Eight E8-MFA-2.1 — MFA enforcement

The policy checks whether qualifying Conditional Access policies enforce MFA for
privileged users or all users across Microsoft 365 services.

Current fixtures verify:

```text
qualifying MFA policy present → compliant
no MFA policies present       → non-compliant
```

---

## Running Locally

From the `engine/` directory, activate the project virtual environment and
install development dependencies:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Ensure OPA is available:

```bash
opa version
```

Run behavioural verification:

```bash
python -m scripts.validate_engine
```

Run framework unit tests:

```bash
pytest --tb=line   tests/test_compliance_validator.py   tests/test_compliance_coverage.py
```

Run the existing structural wiring tests:

```bash
pytest --tb=line tests/test_wiring.py
```

Run static type checking:

```bash
mypy \
  validation \
  scripts/validate_engine.py \
  tests/test_compliance_validator.py \
  tests/test_compliance_coverage.py
```

Run Pylint:

```bash
pylint \
  validation \
  scripts/validate_engine.py \
  tests/test_compliance_validator.py \
  tests/test_compliance_coverage.py
```

---

## Example Output

A successful verification run currently looks similar to:

```text
AutoAudit Compliance Engine Verification
========================================

PASS  1.1.3 - Three global administrators configured
PASS  1.1.3 - Only one global administrator configured
PASS  1.1.3 - Five global administrators configured
PASS  5.2.3.1 - MFA number matching enabled
PASS  5.2.3.1 - MFA number matching disabled
PASS  E8-MFA-2.1 - MFA enforced for all users and all cloud apps
PASS  E8-MFA-2.1 - No MFA policies configured

Fixtures executed: 7
Passed:            7
Failed:            0

Ready automated controls:   79
Behaviour-tested controls:  3
Behavioural coverage:        3.8%
```

If a fixture does not match the real policy result, the runner reports the
difference and exits with a non-zero status.

Example:

```text
FAIL  1.1.3 - Five global administrators configured
      Expected compliant: True
      Actual compliant:   False
```

This allows the same runner to act as a CI gate.

---

## CI Integration

The verification framework is integrated into the Engine GitHub Actions workflow
as a dedicated compliance verification job.

The CI job:

1. checks out the repository;
2. sets up Python;
3. installs engine development dependencies;
4. installs the OPA CLI;
5. runs framework unit tests;
6. runs the behavioural verification framework.

Because `validate_engine.py` returns a non-zero exit status when verification
fails, incorrect policy behaviour causes the CI job to fail.

This allows behavioural regressions to be detected before changes are merged.

The framework therefore complements existing AutoAudit CI checks:

```text
Structural engine validation
        +
Behavioural policy verification
        =
stronger compliance-engine assurance
```

---

## Existing Structural Tests vs Behavioural Verification

The verification framework does not replace `tests/test_wiring.py`.

The existing structural checks validate relationships such as:

- policy files existing;
- collectors being registered;
- package names matching expected paths;
- metadata consistency;
- duplicate control IDs;
- orphaned policies or collectors.

The behavioural framework answers a different question:

> Given known input data, does the policy make the correct compliance decision
> and return that decision in the expected result structure?

Both layers are required for stronger confidence in the compliance engine.

---

## Current Limitations

The framework currently has several intentional limitations:

- Behavioural coverage is still low relative to the full set of ready automated
  controls.
- Fixtures must currently be authored manually.
- Coverage is reported at control level rather than scenario or branch level.
- The result contract validates the common top-level fields but does not enforce
  control-specific `details` schemas.
- The framework executes policies through the local OPA CLI rather than the
  runtime OPA REST service.
- There is currently no dashboard or persistent historical coverage tracking.

These limitations do not prevent the framework from being used. They represent
opportunities for future contributors to extend the verification capability.

---

## Recommended Future Improvements

Future contributors may extend the framework by:

- adding behavioural fixtures for additional ready automated controls;
- adding edge-case fixtures for existing controls;
- defining optional control-specific result schemas;
- producing JSON or Markdown verification reports as CI artifacts;
- tracking behavioural coverage changes between pull requests;
- enforcing a minimum behavioural coverage threshold once sufficient baseline
  coverage exists;
- adding fixture schema validation;
- adding changed-policy-aware execution for faster CI;
- expanding verification to additional benchmarks as AutoAudit grows.

The preferred expansion path is to increase coverage through fixtures without
changing the underlying runner unless a genuine new framework requirement is
identified.

---

## Design Principles

The framework was built around the following principles:

1. **Policy-agnostic execution**  
   The runner should not contain control-specific policy paths or queries.

2. **Metadata-driven discovery**  
   Existing AutoAudit metadata should remain the source of truth for locating
   policies.

3. **Version-aware identity**  
   Controls are identified by framework, benchmark, version, and control ID
   rather than control ID alone.

4. **Fixture-driven extensibility**  
   Adding verification for a new control should normally require only new
   fixture data.

5. **Real policy execution**  
   Tests execute the actual Rego policy through OPA instead of recreating policy
   logic in Python.

6. **Separation of structure and behaviour**  
   Existing wiring tests remain responsible for structural consistency, while
   this framework validates behavioural correctness.

7. **CI-enforceable failures**  
   Verification failures must produce a non-zero exit code so policy regressions
   can be blocked in CI.

---

## Summary

The Compliance Engine Verification Framework provides AutoAudit with a reusable
mechanism for continuously checking the behavioural correctness of its
compliance policies.

Rather than only confirming that policies are present and correctly wired, the
framework verifies that real Rego policies:

- receive known inputs;
- produce the expected compliance decisions;
- return a valid AutoAudit result structure;
- remain verifiable as the policy catalogue evolves.

Future contributors can expand behavioural coverage primarily by adding
fixtures, allowing the verification capability to grow alongside AutoAudit
without requiring repeated changes to the core framework.
