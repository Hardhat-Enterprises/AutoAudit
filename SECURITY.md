# Security Policy

## Overview

AutoAudit is a compliance automation platform that handles sensitive cloud configuration data and tenant credentials. We take security seriously and appreciate responsible disclosure from the community.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` branch |  Active |
| Feature branches |  Development only — not production |

---

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

If you discover a security vulnerability in AutoAudit, please report it responsibly by contacting the project maintainers directly through the Hardhat Enterprises team channel on Microsoft Teams.

### What to include in your report

- A clear description of the vulnerability
- Steps to reproduce the issue
- The potential impact (e.g. credential exposure, data leakage, privilege escalation)
- Any suggested mitigations or patches, if you have them

### What to expect

- We will acknowledge your report within **3 business days**
- We will investigate and aim to provide a resolution or mitigation plan within **14 days**
- We will credit you in the fix if you wish


---

## Scope

The following areas are in scope for security reports:

- **Backend API** — authentication, authorization, JWT handling, API endpoints
- **Engine** — data collectors, OPA policy evaluation, M365 credential handling
- **Frontend** — XSS, insecure data exposure, authentication bypass
- **CI/CD Pipelines** — secrets in workflows, insecure build steps
- **Docker images** — exposed credentials, known CVEs in base images
- **Infrastructure** — misconfigured cloud resources, overly permissive IAM roles

---

## Security Best Practices for Contributors

### Secrets & Credentials
- **Never** commit API keys, client secrets, tenant IDs, or credentials to the repository
- Use the `env.example` file as a template — store real values in `.env` files that are `.gitignore`d
- If you accidentally commit a secret, rotate it immediately and notify the team

### Dependencies
- Keep dependencies up to date and check for known CVEs before adding new packages
- Use `pip audit` for Python dependencies and `npm audit` for Node.js packages

### CI/CD
- All secrets used in GitHub Actions must be stored as **GitHub Secrets**, not hardcoded in workflow files
- Do not disable or bypass security scanning steps (CodeQL, Grype) in pull requests

### Pull Requests
- Never merge code that hardcodes credentials, even for testing
- Flag any code that handles M365 tenant credentials for extra review

---

## Known Security Controls

AutoAudit currently runs the following automated security checks on every pull request:

- **CodeQL** — static analysis for code vulnerabilities
- **Grype** — container and dependency vulnerability scanning

---

## Disclosure Policy

We follow a **coordinated disclosure** model. Please give us reasonable time to investigate and patch before any public disclosure. We are committed to working with security researchers transparently and in good faith.

---

*This security policy was established as part of the AutoAudit DevSecOps initiative.*
