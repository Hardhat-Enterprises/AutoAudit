# Risk-Impact Prioritisation Matrix

## 1. Purpose
This document outlines a risk prioritisation framework for AutoAudit using a likelihood × impact matrix aligned with CIS, NIST, and ISO 27001.

---

## 2. How the Matrix Works

### Likelihood (How often could this happen?)
- **Almost Certain**: very likely, nothing currently stopping it  
- **Likely**: will probably happen at some point  
- **Possible**: could happen if controls are weak  
- **Unlikely**: not expected but not impossible  
- **Rare**: low chance of happening  

### Consequence (What happens if it does?)
- **Insignificant**: barely noticeable, easily recovered  
- **Minor**: small disruption, fixable quickly  
- **Moderate**: some impact on project or tenant security  
- **Major**: significant breach or compliance failure  
- **Severe**: data loss, regulatory breach, or project-stopping incident  

---

## 3. Probability–Impact Matrix

| Likelihood       | Insignificant | Minor  | Moderate | Major   | Severe  |
|----------------|--------------|--------|----------|---------|---------|
| Almost Certain | Medium       | High   | High     | Extreme | Extreme |
| Likely         | Medium       | Medium | High     | Extreme | Extreme |
| Possible       | Medium       | Medium | High     | High    | Extreme |
| Unlikely       | Low          | Medium | Medium   | High    | High    |
| Rare           | Low          | Low    | Medium   | High    | High    |

---

## 4. Heatmap Guide

| Rating  | Meaning | Action |
|--------|--------|--------|
| **Extreme** | High chance of serious breach or compliance failure | Fix immediately and document |
| **High** | Likely to happen and cause significant problems | Fix within 7 days, assign and track |
| **Medium** | Could happen with moderate impact | Fix within 30 days, log and schedule |
| **Low** | Unlikely and easy to recover | Monitor each trimester |

---

## 5. AutoAudit Risk Impact Table

| ID | Risk Description | Likelihood | Consequence | Rating | Mitigation Strategy | Success Metric |
|----|----------------|-----------|------------|--------|---------------------|---------------|
| R-01 | MFA not enforced on M365 admin accounts | Almost Certain | Severe | Extreme | Enable MFA via Conditional Access | Admins without MFA = 0 |
| R-02 | Legacy authentication enabled | Likely | Major | Extreme | Block via Conditional Access | Legacy auth blocked = 100% |
| R-03 | Global admin roles not time-limited | Likely | Major | Extreme | Use PIM for time-limited access | Permanent admins = 0 |
| R-04 | External sharing open on SharePoint | Likely | Severe | Extreme | Restrict to approved guests | Open sharing sites = 0 |
| R-05 | Guest accounts not reviewed | Possible | Major | High | Review every trimester | Review completed = Yes |
| R-06 | FastAPI endpoints unauthenticated | Possible | Major | High | Add authentication + restrict dev exposure | Unauthenticated endpoints = 0 |
| R-07 | No production environment | Likely | Moderate | High | Set up proper cloud production | Production live = Yes |
| R-08 | No CI/CD pipeline | Possible | Moderate | High | Implement GitHub Actions | Pipeline running = Yes |
| R-09 | PostgreSQL not encrypted | Possible | Major | High | Enable encryption at rest | Encryption = Yes |
| R-10 | Redis not secured | Possible | Moderate | High | Add password + TLS | Redis secured = Yes |
| R-11 | Weak password policies undetected | Likely | Major | Extreme | Add password policy checks | Failures = 0 |
| R-12 | Audit log not enabled | Likely | Major | Extreme | Ensure logs always enabled | Audit log = 100% |
| R-13 | Audit logs < 90 days | Possible | Moderate | High | Increase retention ≥ 365 days | Retention OK = Yes |
| R-14 | Incomplete onboarding docs | Unlikely | Moderate | Medium | Complete onboarding guide | Guide done = Yes |
| R-15 | Meeting notes not recorded | Unlikely | Minor | Medium | Log notes in Teams | Notes logged = Yes |
| R-16 | Reports hard for non-technical users | Unlikely | Insignificant | Low | Add summaries + colour coding | Feedback = satisfactory |

---

## 6. Risk Heat Map

| Likelihood       | Insignificant | Minor  | Moderate             | Major                        | Severe |
|----------------|--------------|--------|----------------------|------------------------------|--------|
| Almost Certain | —            | —      | —                    | —                            | R-01   |
| Likely         | —            | —      | R-07                 | R-02, R-03, R-11, R-12       | R-04   |
| Possible       | —            | —      | R-08, R-10, R-13     | R-05, R-06, R-09             | —      |
| Unlikely       | R-16         | R-15   | R-14                 | —                            | —      |
| Rare           | —            | —      | —                    | —                            | —      |

---

## 7. References

1. G. Porat, *CIS Microsoft 365 v6 Guide*, 2026  
2. Nudge Security, *Top M365 Misconfigurations*, 2025  
3. Metis Security, *Common M365 Misconfigurations*, 2024  
4. Microsoft Learn, *Audit Log Retention*, 2024  
5. KnowledgeHut, *Probability & Impact M*
