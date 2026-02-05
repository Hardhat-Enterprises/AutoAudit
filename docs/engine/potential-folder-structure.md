Plan: Engine Folder Restructure

 Requirements

 - Scan GCP, Azure, and M365 environments
 - Evaluate against CIS benchmarks (other benchmarks in future)
 - Support multiple versions of each benchmark
 - Platform-first organization with rules per-platform
 - Keep /security separate (potential future consolidation)

 Proposed Structure

 /engine
 ├── pyproject.toml              # Package definition
 ├── __init__.py
 │
 ├── /core                       # Shared engine infrastructure
 │   ├── __init__.py
 │   ├── evaluator.py            # Base evaluation logic (OPA integration)
 │   ├── reporter.py             # Report generation (JSON, PDF)
 │   ├── risk_rating.py          # Severity/risk calculations
 │   └── models.py               # Shared data models (ScanResult, Finding, etc.)
 │
 ├── /gcp                        # Google Cloud Platform
 │   ├── __init__.py
 │   ├── collector.py            # GCP API client (current GCPAccess.py)
 │   ├── /benchmarks
 │   │   └── /cis
 │   │       ├── __init__.py
 │   │       ├── /v3.0
 │   │       │   ├── rules.rego  # Rego policy rules
 │   │       │   ├── metadata.json  # Benchmark metadata
 │   │       │   └── mappings.py # Control mappings
 │   │       └── /v2.0
 │   │           └── ...
 │   └── /test-configs           # Mock GCP data for testing
 │
 ├── /azure                      # Microsoft Azure
 │   ├── __init__.py
 │   ├── collector.py            # Azure API client
 │   ├── /benchmarks
 │   │   └── /cis
 │   │       ├── __init__.py
 │   │       ├── /v3.0
 │   │       │   ├── rules.json  # JSON rule definitions
 │   │       │   └── metadata.json
 │   │       └── /v2.1
 │   │           └── ...
 │   └── /test-configs
 │
 ├── /m365                       # Microsoft 365
 │   ├── __init__.py
 │   ├── collector.py            # M365/Graph API client
 │   ├── /benchmarks
 │   │   └── /cis
 │   │       └── /v3.1
 │   │           ├── rules.json
 │   │           └── metadata.json
 │   └── /test-configs
 │
 └── /shared                     # Cross-platform utilities
     ├── __init__.py
     ├── opa.py                  # OPA CLI wrapper
     └── helpers.rego            # Shared Rego helper functions

 Key Design Decisions

 1. Platform-First Hierarchy

 /engine/{platform}/benchmarks/{benchmark}/{version}/
 - Easy to find all GCP-related code in one place
 - Teams can work on platforms independently
 - Adding a new platform = add a new folder

 2. Versioned Benchmarks

 /engine/gcp/benchmarks/cis/v3.0/
 /engine/gcp/benchmarks/cis/v2.0/
 /engine/gcp/benchmarks/nist/v1.0/  # Future
 - Each version is immutable (important for compliance audits)
 - Can run scans against specific versions
 - Easy to add new benchmarks (just add folder)

 3. Consistent Platform Structure

 Each platform follows the same pattern:
 - collector.py - API client for that platform
 - /benchmarks/{name}/{version}/ - Rules organized by benchmark
 - /test-configs/ - Mock data for testing

 4. Shared Core

 /engine/core/ contains:
 - Evaluator logic (OPA integration)
 - Report generation
 - Common models and utilities

 Usage Examples

 # Import pattern
 from engine.gcp.collector import GCPCollector
 from engine.gcp.benchmarks.cis.v3_0 import rules
 from engine.core.evaluator import evaluate

 # Evaluate GCP against CIS v3.0
 collector = GCPCollector(credentials)
 config = collector.collect()
 results = evaluate(config, "gcp", "cis", "v3.0")

 Migration from Current Structure

 | Current Location             | New Location                      |
 |------------------------------|-----------------------------------|
 | engine/legacy/engine/GCPAccess.py   | engine/gcp/collector.py           |
 | engine/legacy/engine/aggregator.py  | engine/core/evaluator.py          |
 | engine/legacy/engine/risk_rating.py | engine/core/risk_rating.py        |
 | engine/legacy/engine/json_to_pdf.py | engine/core/reporter.py           |
 | engine/legacy/engine/Helpers.rego   | engine/shared/helpers.rego        |
 | engine/legacy/rules-gcp/*.rego      | engine/gcp/benchmarks/cis/v3.0/   |
 | engine/legacy/rules-azure/*.json    | engine/azure/benchmarks/cis/v3.0/ |
 | engine/legacy/test-configs/         | engine/gcp/test-configs/          |

 Future Extensibility

 Adding a new platform (e.g., AWS)

 /engine/aws/
 ├── __init__.py
 ├── collector.py
 └── /benchmarks/cis/v3.0/

 Adding a new benchmark (e.g., NIST)

 /engine/gcp/benchmarks/nist/v1.0/
 ├── rules.rego
 └── metadata.json

 Adding a new version

 /engine/gcp/benchmarks/cis/v4.0/
 ├── rules.rego
 └── metadata.json

 No refactoring required for any of these additions.