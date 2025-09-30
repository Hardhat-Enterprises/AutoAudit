-- =========================================================
-- AutoAudit - Joins Demo for Compliance Reporting
-- Author: Sai Tejaswini
-- Purpose: Example queries to demonstrate reporting use cases
-- =========================================================

-- 1) Show all users and their triggered scans (LEFT JOIN)
SELECT u.username, s.scan_id, s.start_time
FROM autoaudit.users u
LEFT JOIN autoaudit.audit_scans s
  ON u.userid = s.triggered_by
ORDER BY u.username, s.start_time DESC;

-- 2) Show failed checks in the most recent scan (INNER JOIN + CTE)
WITH last_scan AS (
  SELECT MAX(scan_id) AS scan_id FROM autoaudit.audit_scans
)
SELECT u.username, s.scan_id, c.check_title, c.severity, l.log_status, l.check_at
FROM autoaudit.audit_logs l
JOIN autoaudit.audit_scans s        ON s.scan_id = l.scan_id
JOIN autoaudit.users u              ON u.userid  = s.triggered_by
JOIN autoaudit.compliance_checks c  ON c.check_id = l.check_id
JOIN last_scan ls                   ON ls.scan_id = s.scan_id
WHERE l.log_status = 'fail'
ORDER BY l.check_at DESC;

-- 3) Show policies and their related failed checks (multi-join)
SELECT p.policy_name, c.check_title, c.severity, u.username, l.log_status, l.check_at
FROM autoaudit.audit_logs l
JOIN autoaudit.compliance_checks c ON c.check_id = l.check_id
JOIN autoaudit.policies p          ON p.policy_id = c.policy_id
JOIN autoaudit.users u             ON l.emp_user_id = u.userid
ORDER BY p.policy_name, l.check_at DESC;

-- 4) Show scans not linked to any user (FULL OUTER JOIN use case)
SELECT u.username, s.scan_id, s.start_time
FROM autoaudit.users u
FULL OUTER JOIN autoaudit.audit_scans s
  ON u.userid = s.triggered_by
WHERE u.username IS NULL OR s.scan_id IS NULL;
