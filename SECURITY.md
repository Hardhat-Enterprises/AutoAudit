# Security Policy

## Purpose

This document outlines the security reporting process and key security practices for the AutoAudit project. AutoAudit is a Microsoft 365 compliance automation platform, so security is important across authentication, API access, file handling, CI/CD, and dependency management.

## Supported Branches

Security-related changes should be made through pull requests and reviewed before being merged.

| Branch | Status |
| --- | --- |
| main | Production/deployment branch |
| staging | Active testing and integration branch |
| feature branches | Used for individual development work |

## Reporting a Vulnerability

If a security issue is found, it should not be posted publicly in GitHub issues unless the team agrees it is safe to disclose.

Security concerns should include:

- A clear description of the issue
- Steps to reproduce the issue
- Affected files, endpoints, or workflows
- Possible impact
- Suggested fix if known
- Screenshots or logs where appropriate

## Areas of Security Concern

The following areas should be treated as security-sensitive:

- Authentication and login endpoints
- User registration and account handling
- File upload endpoints
- Evidence report download paths
- API access between services
- CI/CD workflow permissions
- Secrets and environment variables
- Dependency vulnerabilities
- Docker image security
- Compliance scan output data

## CI/CD Security Controls

AutoAudit uses GitHub Actions to support automated security checks during development.

Current and recommended CI/CD security controls include:

- CodeQL scanning for code analysis
- Bandit scanning for Python static application security testing
- Dependency scanning for vulnerable packages
- Pull request review before merging
- Branch protection rules for main and staging
- Workflow permission restrictions where possible

Bandit is used to detect common insecure Python coding patterns such as hardcoded secrets, unsafe function usage, weak cryptography, and insecure subprocess handling.

## Dependency Security

Dependencies should be reviewed regularly because vulnerable third-party packages can affect the security of the platform.

Recommended practices:

- Keep package files updated
- Review dependency scanning results
- Avoid unused dependencies
- Check security alerts before merging
- Use pinned or controlled dependency versions where practical

## Authentication and Access Control

Authentication and access control should be reviewed carefully because AutoAudit is designed as a multi-tenant SaaS-style platform.

Recommended future improvements:

- Add rate limiting for login and registration endpoints
- Add account lockout protection after repeated failed login attempts
- Reduce user enumeration risks during registration
- Consider using a trusted identity provider such as Auth0 or Microsoft Entra ID
- Review service-to-service authentication between containers

## File Upload and Report Security

File upload and report access functions should be validated to reduce risk.

Recommended controls:

- Limit file size
- Validate file type
- Sanitize uploaded filenames
- Prevent path traversal
- Restrict access to generated reports
- Log suspicious upload or download activity

## Responsible Disclosure

Security issues should be handled carefully and responsibly. The goal is to protect users, project data, and the AutoAudit platform while giving the team enough detail to reproduce and fix the issue.

Security fixes should be tested before merging and should include evidence such as workflow runs, screenshots, or review notes where appropriate.


## Security Testing and Monitoring

Security testing should be performed continuously throughout development and deployment processes.

Recommended security testing activities include:

- Static application security testing using Bandit
- Code scanning through GitHub CodeQL workflows
- Dependency vulnerability monitoring
- CI/CD workflow validation
- Pull request review before merging
- Testing workflow failures using intentionally insecure code samples
- Monitoring GitHub security alerts and Dependabot notifications

Workflow failures caused by detected vulnerabilities should be reviewed before deployment approval.

Security monitoring should also include:

- Logging suspicious authentication attempts
- Monitoring repeated failed login activity
- Reviewing unusual file upload behaviour
- Tracking dependency security advisories
- Reviewing CI/CD workflow permission usage

## Container and Infrastructure Security

AutoAudit uses container-based deployment and infrastructure components that should follow secure configuration practices.

Recommended infrastructure security practices include:

- Restrict unnecessary container privileges
- Use environment variables for sensitive configuration values
- Avoid hardcoded credentials or API keys
- Scan container images for vulnerabilities
- Keep Docker images and dependencies updated
- Restrict public exposure of internal services
- Apply least privilege principles to workflows and deployments
- Review infrastructure configurations regularly

Infrastructure and deployment security should be reviewed continuously as the platform evolves into a larger multi-tenant SaaS environment.