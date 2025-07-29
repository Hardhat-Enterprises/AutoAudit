# AutoAudit Folder Structure

AutoAudit/
- README.md                            # Project overview + setup instructions
- docs/                                # Architecture diagrams + sprint plans
- src/                                 # Main source code
    - core-api/                        # Core API integration team
    - compliance-engine/               # Compliance framework engine team
    - security-assessment/             # Security assessment team
    - frontend/                        # Frontend & user experience team
    - backend/                         # Backend architecture team
    - shared/                          # common utilities
- infrastructure/                      # DevOps & infrastructure team (IaC, CI/CD configs)
    - terraform/                       # Terraform modules
    - monitoring/                      # Prometheus/grafana configs
- github/                              # GitHub specific configs
    - workflows/                       # GitHub actions YAML files for CI/CD
    - tests/                           # Integration/unit tests (cross-team)
- scripts/                             # Utility scripts 
