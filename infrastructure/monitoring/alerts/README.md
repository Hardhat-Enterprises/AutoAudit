# AutoAudit Alerting Rules Module

## Notification Channels
- Email
- Microsoft Teams (if applicable)
- Other configured channels as per infrastructure team standards

## Deployment
- Alerting rules are deployed via Helm charts to the AKS cluster.

## Testing
- Alert rule syntax should be validated using `promtool check rules`.
- Functional testing of alerting rules is currently under development.

## Alerting Rules Structure
- Alerting rules are organised by category in YAML files under this directory.
- Each alert rule includes PromQL expressions, severity levels, and annotations.

## Alertmanager Configuration
- Alertmanager routes alerts to configured receivers based on team and severity.
- Currently, no Slack or Azure Sentinel integrations are used. These are to be expanded upon once the MVP has been approved.
- Alertmanager secrets are not set up in this repository.

## CI/CD Pipeline
- The CI/CD pipeline includes a job to validate alert rule syntax using `promtool`.
- Automated alert firing simulation tests are planned but not yet implemented.

## Notes
- Placeholder webhook URLs and APIs have been removed to avoid confusion.
- Please coordinate with the DevSecOps and Infrastructure team lead for any alerting configuration changes.
