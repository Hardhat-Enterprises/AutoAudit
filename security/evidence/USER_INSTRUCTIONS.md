# Evidence preparation guide – Regular Backups (Essential Eight)

This guide explains how to prepare evidence files for the Essential Eight – Regular Backups
strategy so the AutoAudit Evidence Scanner can correctly detect
Maturity Level 1 (ML1) and Maturity Level 2 (ML2) results.

This strategy assesses compliance with the Australian Cyber Security Centre (ACSC)
Essential Eight – Regular Backups control.

Evidence files must contain clear, consistent key–value style fields such as
status=success, immutability=enabled, or role=backup-admin.

---

## 1. General guidelines for evidence files

- Files must be plain text (.txt)
- Each file must produce at least one detected result
- Files without `_ml2` are treated as ML1 evidence
- Files with `_ml2` are treated as ML2 evidence
- ML2 evidence always produces both ML1 and ML2 results
- Each file should represent one control outcome
- Evidence may come from:
  - backup logs
  - audit logs
  - policy exports
  - restore test reports
- The scanner uses keyword-based detection
- Extra descriptive text is allowed, but required key phrases must be present

---

## 2. Evidence files for ML1 tests

### 2.1 Successful backups – `backup_success.txt`

status=success


---

### 2.2 Failed or missing backups – `backup_failed.txt`

status=failure  
reason=no_recent_backup


---

### 2.3 Offsite or immutable backups – `offsite_backup.txt`

backup_location=offsite  
immutability=enabled


---

### 2.4 Successful restore test – `restore_test.txt`

restore_test=full  
status=success


---

### 2.5 Failed restore test – `restore_failed.txt`

restore_test=full  
status=fail


---

### 2.6 Backup retention policy – `retention_policy.txt`

retention_policy=defined  
retention_days=30


---

### 2.7 Encrypted backups – `Encrypted_backup.txt`

encryption=aes-256


---

### 2.8 Restricted backup access – `access_admin_only.txt`

access=restricted  
role=backup-admin


---

## 3. Evidence files for ML2 tests

All ML2 files must include `_ml2` in the filename.

ML2 evidence always produces:
- ML1 PASS + ML2 PASS, or
- ML1 FAIL + ML2 FAIL

---

### 3.1 Backup verification via audit logs – PASS  
`backup_verification_ml2_pass.txt`

verification=success  
status=success


---

### 3.2 Backup verification via audit logs – FAIL  
`backup_verification_ml2_fail.txt`

verification=fail  
audit_log=missing


---

### 3.3 Offsite & immutability enforced by policy – PASS  
`offsite_policy_enforced_ml2.txt`

backup_location=offsite  
immutability=enabled  
policy=enforced


---

### 3.4 Restore to a common point – PASS  
`restore_report_ml2_pass.txt`

restore_test=item-level  
status=success  
common_point=true


---

### 3.5 Restore to a common point – FAIL  
`restore_report_ml2_fail.txt`

restore_test=item-level  
status=fail


---

### 3.6 Policy alignment – PASS  
`policy_ml2_pass.txt`

retention_days=30  
immutability=enabled  
policy_match=true


---

### 3.7 Policy misalignment – FAIL  
`policy_ml2_fail.txt`

retention_policy=missing  
immutability=disabled


---

### 3.8 Encryption enforcement – PASS  
`encryption_ml2_pass.txt`

encryption=aes-256  
kms=verified


---

### 3.9 Encryption enforcement – FAIL  
`encryption_ml2_fail.txt`

encryption=none  
kms=missing


---

### 3.10 Access control enforcement – PASS  
`access_admin_only_ml2.txt`

access=restricted  
role=backup-admin  
is_backup_admin=true  
audit=success


---

### 3.11 Unauthorized access allowed – FAIL  
`repo_audit_fail.txt`

access=allowed  
is_backup_admin=false


---

## 4. Using the Evidence Scanner

1. Open the AutoAudit Evidence Scanner
2. Select **Regular Backups (RB)**
3. Upload one or more evidence files
4. Review results:
   - Test ID
   - Detected maturity level
   - PASS or FAIL outcome

If results are not produced:
- Check filename maturity level
- Verify required key–value fields exist
- Ensure ML2 files include `_ml2`

---