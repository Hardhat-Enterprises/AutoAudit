# DevSecOps Contribution - Week 1

## Objective
Improve CI/CD security in the AutoAudit project by adding an automated Python security scan.

## Work Completed
- Reviewed the GitHub Actions workflow folder to understand existing CI/CD pipelines
- Identified current workflows for backend, frontend, engine, and security processes
- Noted that there was no dedicated Bandit workflow for Python security scanning
- Created a new GitHub Actions workflow (bandit.yml) to scan the backend-api directory

## Value Added
This contribution improves the DevSecOps pipeline by introducing static application security testing for Python code. It helps detect insecure coding patterns early in the development cycle before deployment.

## Next Step
Analyse the Bandit scan results and create issues for any identified vulnerabilities.