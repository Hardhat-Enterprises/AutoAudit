# AutoAudit Runbooks

---

## ResourceUtilisation/ClusterStorageCapacityWarning

### Summary
Alert triggers when cluster storage capacity falls below 15% for more than 10 minutes.

### Impact
Low storage capacity can cause pod evictions, application failures, and data loss.

### Investigation Steps
1. Access Kubernetes nodes and check volume usage:
   ```bash
   kubectl describe pvc
   df -h
   ```
2. Identify pods consuming excessive storage.
3. Check for logs indicating storage pressure or eviction events.
4. Review recent deployments or jobs that may have increased storage usage.

### Remediation
- Clean up unused volumes, logs, or artifacts.
- Scale storage capacity or add new persistent volumes.
- Adjust retention policies for logs and backups.
- Notify storage team if hardware limits are reached.

### Verification
- Confirm storage usage rises above 15% threshold.
- Monitor for alert resolution in Prometheus.

---

## ResourceUtilisation/NetworkBandwidthThreshold

### Summary
Alert triggers when network bandwidth usage exceeds 1Gbps for more than 5 minutes.

### Impact
High bandwidth usage may cause network congestion, latency, or packet loss.

### Investigation Steps
1. Identify pods or services with high network traffic:
   ```bash
   kubectl top pods --namespace=<namespace>
   ```
2. Use network monitoring tools (e.g., Cilium, Calico) to trace traffic sources.
3. Check for abnormal traffic patterns or DDoS attacks.
4. Review recent deployments or batch jobs causing spikes.

### Remediation
- Throttle or limit bandwidth for noisy services.
- Scale network infrastructure or increase bandwidth.
- Block malicious traffic if detected.
- Optimise application network usage.

### Verification
- Confirm bandwidth usage returns below threshold.
- Validate alert clears in monitoring dashboards.

---

## ResourceUtilisation/CPUUsageHigh

### Summary
Alert triggers when CPU usage exceeds 85% for more than 10 minutes on any node.

### Impact
High CPU usage can degrade application performance and cause timeouts.

### Investigation Steps
1. Identify high CPU usage nodes:
   ```bash
   kubectl top nodes
   ```
2. Check pods consuming CPU on affected nodes:
   ```bash
   kubectl top pods --all-namespaces --sort-by=cpu
   ```
3. Review application logs for performance issues.
4. Check for runaway processes or infinite loops.

### Remediation
- Scale out workloads or add nodes.
- Optimise application code or resource requests.
- Restart problematic pods or nodes if necessary.

### Verification
- Confirm CPU usage drops below threshold.
- Monitor alert resolution.

---

## ResourceUtilisation/MemoryUsageHigh

### Summary
Alert triggers when available memory falls below 15% for more than 10 minutes on any node.

### Impact
Low memory can cause pod evictions, OOM kills, and degraded performance.

### Investigation Steps
1. Identify nodes with low memory:
   ```bash
   kubectl top nodes
   ```
2. Check pods with high memory usage:
   ```bash
   kubectl top pods --all-namespaces --sort-by=memory
   ```
3. Review logs for OOM kill events.
4. Check for memory leaks or misconfigured resource limits.

### Remediation
- Increase node memory or add nodes.
- Optimise application memory usage.
- Adjust resource requests and limits.
- Restart affected pods.

### Verification
- Confirm memory availability improves.
- Alert clears in monitoring.

---

## CICD/BuildFailures

### Summary
Alert triggers when one or more CI build failures occur within 15 minutes.

### Impact
Build failures block deployment pipelines and delay releases.

### Investigation Steps
1. Access CI system logs for failed builds.
2. Identify failure causes: compilation errors, test failures, environment issues.
3. Check recent code changes or dependency updates.

### Remediation
- Fix build errors or flaky tests.
- Roll back problematic commits if needed.
- Verify build environment stability.

### Verification
- Confirm successful builds in subsequent runs.
- Alert resolves after no failures detected.

---

## CICD/DeploymentRollback

### Summary
Alert triggers when deployment rollbacks occur within 10 minutes.

### Impact
Rollbacks indicate failed deployments impacting production stability.

### Investigation Steps
1. Review deployment logs and events.
2. Identify rollback reasons: failed health checks, crashes, config errors.
3. Check recent changes in deployment manifests or images.

### Remediation
- Fix deployment issues.
- Test changes in staging before production.
- Coordinate with development teams.

### Verification
- Confirm successful deployments without rollbacks.
- Alert clears after stable deployment.

---

## CICD/SecurityScanFailures

### Summary
Alert triggers when security scans in CI pipeline fail within 15 minutes.

### Impact
Failed scans may allow vulnerabilities to reach production.

### Investigation Steps
1. Review security scan logs and reports.
2. Identify scan tool errors or misconfigurations.
3. Check for network or credential issues.

### Remediation
- Fix scan tool configuration.
- Resolve network or permission problems.
- Re-run scans after fixes.

### Verification
- Confirm successful scan completions.
- Alert resolves when no failures detected.

---

## Application/APIErrorRateHigh

### Summary
Alert triggers when API error rate exceeds 20 errors in 5 minutes.

### Impact
High error rates degrade user experience and indicate service issues.

### Investigation Steps
1. Check API gateway logs for error details.
2. Identify error types (4xx, 5xx) and affected endpoints.
3. Review recent deployments or configuration changes.

### Remediation
- Fix application bugs or misconfigurations.
- Roll back recent changes if needed.
- Scale backend services if overloaded.

### Verification
- Confirm error rate drops below threshold.
- Alert clears after stabilisation.

---

## Application/ScanEngineFailure

### Summary
Alert triggers when scan engine errors occur within 1 minute.

### Impact
Scan engine failures reduce security and compliance coverage.

### Investigation Steps
1. Review scan engine logs for error messages.
2. Check resource usage and connectivity.
3. Verify scan engine service health.

### Remediation
- Restart scan engine service.
- Fix configuration or dependency issues.
- Allocate additional resources if needed.

### Verification
- Confirm scan engine operates without errors.
- Alert clears after recovery.

---

## Application/JobFailureRateHigh

### Summary
Alert triggers when batch job failures exceed 5 in 10 minutes.

### Impact
High job failure rates affect data processing and system reliability.

### Investigation Steps
1. Review batch job logs and error messages.
2. Identify common failure causes.
3. Check resource availability and dependencies.

### Remediation
- Fix job scripts or code.
- Increase resource allocation.
- Retry failed jobs if appropriate.

### Verification
- Confirm job success rates improve.
- Alert clears after sustained success.

---

## Infrastructure/NodeCPUSaturation

### Summary
Alert triggers when node CPU idle time falls below 10% for 5 minutes.

### Impact
CPU saturation can cause slowdowns and service degradation.

### Investigation Steps
1. Identify affected nodes.
2. Check running pods and CPU usage.
3. Review recent workload changes.

### Remediation
- Scale cluster or redistribute workloads.
- Optimise CPU-intensive applications.
- Restart problematic pods or nodes.

### Verification
- Confirm CPU idle time recovers.
- Alert clears after normalisation.

---

## Infrastructure/PodRestartsHigh

### Summary
Alert triggers when pod container restarts exceed 3 in 10 minutes.

### Impact
Frequent restarts indicate instability or crashes.

### Investigation Steps
1. Identify pods with high restart counts.
2. Review pod logs and events.
3. Check resource limits and health probes.

### Remediation
- Fix application crashes or bugs.
- Adjust resource requests and limits.
- Update liveness/readiness probes.

### Verification
- Confirm restart rates decrease.
- Alert clears after stability.

---

## Infrastructure/DiskSpaceLow

### Summary
Alert triggers when disk space on root filesystem falls below 15% for 15 minutes.

### Impact
Low disk space can cause system failures and data loss.

### Investigation Steps
1. Check disk usage on affected nodes.
2. Identify large files or logs consuming space.
3. Review recent deployments or backups.

### Remediation
- Clean up unnecessary files and logs.
- Increase disk capacity.
- Implement log rotation policies.

### Verification
- Confirm disk space usage improves.
- Alert clears after remediation.

---

## Compliance/MissingComplianceScans

### Summary
Alert triggers when no successful compliance scans occur in 1 hour.

### Impact
Lack of scans risks undetected compliance violations.

### Investigation Steps
1. Verify compliance scanner service status.
2. Check scan schedules and logs.
3. Investigate connectivity or permission issues.

### Remediation
- Restart or fix scanner service.
- Adjust scan schedules if needed.
- Resolve network or credential problems.

### Verification
- Confirm successful scans resume.
- Alert clears after scans complete.

---

## Compliance/FailedAuditChecks

### Summary
Alert triggers when compliance audit failures exceed 5 in 30 minutes.

### Impact
Audit failures indicate non-compliance risks.

### Investigation Steps
1. Review audit failure logs.
2. Identify failed controls or policies.
3. Check recent configuration changes.

### Remediation
- Remediate non-compliant configurations.
- Update policies or controls.
- Communicate with compliance team.

### Verification
- Confirm audit failures reduce.
- Alert clears after compliance restored.

---

## Compliance/MissingControlsDetected

### Summary
Alert triggers when required compliance controls are missing or disabled.

### Impact
Missing controls increase security and compliance risks.

### Investigation Steps
1. Identify missing or disabled controls.
2. Review control configuration and enforcement.
3. Check recent changes or overrides.

### Remediation
- Enable or implement missing controls.
- Audit control configurations.
- Train teams on compliance requirements.

### Verification
- Confirm controls are active.
- Alert clears after remediation.

---

## Security/UnauthorisedAccessAttempt

### Summary
Alert triggers when failed login attempts exceed 10 in 5 minutes.

### Impact
May indicate brute force or credential stuffing attacks.

### Investigation Steps
1. Review authentication logs.
2. Identify source IPs and accounts.
3. Check for suspicious patterns.

### Remediation
- Block malicious IPs.
- Enforce multi-factor authentication.
- Notify security team.

### Verification
- Confirm failed attempts decrease.
- Alert clears after mitigation.

---

## Security/ScanEngineFailure

### Summary
Alert triggers on scan engine errors within 1 minute.

### Impact
Reduces security scanning effectiveness.

### Investigation Steps
1. Check scan engine logs.
2. Verify service health and connectivity.
3. Review resource usage.

### Remediation
- Restart scan engine.
- Fix configuration or dependencies.
- Allocate resources as needed.

### Verification
- Confirm error-free operation.
- Alert clears after recovery.

---

## Security/PrivilegeEscalation

### Summary
Alert triggers are sent for detected privilege escalation events within 10 minutes.

### Impact
Indicates potential insider threat or attack.

### Investigation Steps
1. Review escalation event logs.
2. Identify affected accounts and actions.
3. Correlate with other security events.

### Remediation
- Contain affected accounts.
- Conduct forensic analysis.
- Update access controls.

### Verification
- Confirm no further escalations.
- Alert clears after containment.

---

## Security/VulnerabilityScanFailure

### Summary
Alert triggers when no successful vulnerability scans occur in 30 minutes.

### Impact
Vulnerabilities may remain undetected.

### Investigation Steps
1. Check vulnerability scanner status.
2. Review scan schedules and logs.
3. Investigate connectivity or permission issues.

### Remediation
- Restart or fix the scanner.
- Adjust schedules.
- Resolve network or credential problems.

### Verification
- Confirm scans resume successfully.
- Alert clears after scans complete.
