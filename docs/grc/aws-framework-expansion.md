# AWS Framework Expansion – AutoAudit Starter Mapping

## Purpose

This artefact explores how AWS cloud security areas could align with AutoAudit’s existing GRC and compliance structure. The aim is not to fully implement AWS support, but to provide a starter mapping that future teams can use when expanding AutoAudit beyond Microsoft 365 and CIS-focused controls.

## Starter Mapping

| AWS Security Area | Description | Related AutoAudit Area | Possible Evidence Source | Future Automation Opportunity |
|---|---|---|---|---|
| AWS IAM | Manages users, roles, permissions, and access policies | Access Control | IAM policy export, user/role permission screenshots | Check whether users and roles follow least privilege |
| MFA for AWS Accounts | Adds extra authentication protection for users and privileged accounts | Authentication Security | MFA configuration screenshot or IAM credential report | Validate whether MFA is enabled for root and privileged users |
| AWS CloudTrail | Records account activity and API calls across AWS services | Logging and Monitoring | CloudTrail event logs, trail configuration export | Check whether CloudTrail is enabled across regions |
| Amazon S3 Encryption | Protects stored data in S3 buckets using encryption | Data Protection | S3 bucket encryption settings | Detect buckets without default encryption |
| Security Groups | Controls inbound and outbound network traffic for AWS resources | Network Security | Security group rule export | Identify overly permissive rules such as 0.0.0.0/0 |
| Amazon CloudWatch | Provides monitoring, metrics, and alerts for AWS resources | Security Monitoring | CloudWatch alarm screenshots or alarm exports | Validate whether critical alerts are configured |
| AWS Backup | Supports backup and recovery of AWS workloads | Resilience and Recovery | Backup plan export, recovery point evidence | Check whether critical resources are covered by backup plans |
| AWS Config | Tracks resource configuration and compliance status | Compliance Validation | AWS Config compliance report | Use AWS Config rules as evidence for compliance checks |

## Potential Alignment with AutoAudit

This starter mapping suggests that AWS could be incorporated into AutoAudit using a similar evidence-based approach to existing compliance work. AWS IAM, CloudTrail, CloudWatch, AWS Config, and S3 configuration data could provide useful evidence for future automated compliance checks.

## Future Opportunities

- Add AWS CIS Benchmark mapping.
- Create AWS evidence collection scripts.
- Map AWS controls to ISO 27001, NIST, and CSA STAR.
- Extend AutoAudit report generation to include AWS findings.
- Use AWS Config outputs as structured compliance evidence.
- Identify common AWS misconfigurations such as public S3 buckets, missing MFA, and overly permissive security groups.

## Conclusion

This artefact provides a starter structure for future AWS framework expansion in AutoAudit. While the current platform is mainly focused on Microsoft 365 and CIS-based controls, AWS support could help broaden AutoAudit’s cloud compliance coverage and improve its usefulness for organisations using multiple cloud environments.
