# AutoAudit Alerting Rules Module

## Overview

This module implements the comprehensive Prometheus alerting rules for the AutoAudit platform, covering:

- Security incidents  
- Compliance violations  
- Infrastructure health  
- Application errors  
- CI/CD pipeline failures  

The alerting rules are designed to provide precise, actionable alerts with minimal false positives. Alerts are integrated with **Alertmanager** for routing notifications to:

- Slack  
- Teams  
- Email  
- Azure Sentinel  

## Repository Location

All alerting rules are stored under:  
`/infrastructure/monitoring/alerts/`

Each alert category has a separate YAML file.

## Alert Categories and Notification Channels

| Category              | Severity Levels     | Notification Channels                          |
|-----------------------|---------------------|------------------------------------------------|
| Security Alerts       | Critical, High      | Teams, Slack `#security`              |
| Compliance Violations | High, Medium        | Slack `#compliance`, Email                     |
| Infrastructure Health | Critical, Warning   | Teams, Slack `#devops`                |
| Application Errors    | High, Medium        | Slack `#backend`, Email                        |
| CI/CD Pipeline Alerts | High, Medium        | Slack `#devops`, Jira tickets                  |
| Resource Utilisation  | Warning             | Slack `#infra`, Email                          |

## Design Principles

- **Precision**: PromQL queries use precise selectors and thresholds to minimise false positives.  
- **Grouping**: Related alerts are grouped to reduce noise.  
- **Silencing**: Supports scheduled silences during maintenance windows.  
- **Escalation**: Alerts escalate based on severity and duration.  
- **Metadata**: Labels include service, team, environment, and severity.  
- **Security**: Alert payloads exclude sensitive data.  

## File Structure

```bash
/infrastructure/monitoring/alerts/
├── security_alerts.yaml
├── compliance_alerts.yaml
├── infra_health.yaml
├── application_errors.yaml
├── cicd_pipeline.yaml
├── resource_utilisation.yaml
├── alertmanager.yaml
├── README.md
├── ADRs/
│   └── 001-alerting-rules-design.md
└── tests/
    ├── alert_simulation_test.py
    └── promtool_validation.sh
```

## Deployment

- Alerting rules are deployed via **Helm charts** to the **AKS cluster**.  
- CI/CD pipeline validates alert syntax using `promtool check rules`.  
- Automated tests simulate alert firing using synthetic metrics.  
- **Alertmanager secrets** (e.g., Slack tokens, Teams webhooks) are securely stored in **GitHub Secrets** and injected at runtime.

## Usage

1. Modify or add alert rules in the appropriate YAML file.
2. Validate syntax locally using:

    ```bash
    promtool check rules /infrastructure/monitoring/alerts/*.yaml
    ```

3. Run alert simulation tests:

    ```bash
    ./tests/promtool_validation.sh
    python3 tests/alert_simulation_test.py
    ```

4. Submit a PR for review by the **DevSecOps team lead**.

## Contact

For questions or contributions, contact the **DevSecOps team lead**.
