git # Evidence preparation guide – Regular Backups (ML1 + ML2)

This guide explains how to prepare evidence files for the Regular Backups strategy so the Evidence Scanner can read and map them to the correct maturity-level tests.  
Files should contain clear text describing backup events, restore results, audit logs or policy settings.

---

## 1. General guidelines for preparing evidence
- Use plain text files (.txt) or log/CSV exports.
- Each file should describe one backup event, restore test, policy entry or access audit.
- The scanner detects specific keywords.  
  Additional sentences will not cause issues.
- Keep the important values visible, for example:  
  `status=success`, `immutability=enabled`, `role=backup-admin`.

---

## 2. ML1 evidence preparation

### 2.1 Successful backups — `backup_success.txt`
**Exact content used in testing:**
```
backup completed successfully. last backup 2025-09-10 23:45 status success
```

### 2.2 Failed backups — `backup_failed.txt`
```
no recent backup found in the last seven days. status failure
```

### 2.3 Offsite or immutable backups — `offsite_backup.txt`
```
daily backup completed to immutable cloud storage (offsite)
```

### 2.4 Restore test passed — `restore_test.txt`
```
restore test status=success common point
```

### 2.5 Restore test failed — `restore_failed.txt`
```
restore failed during test restore. status fail
```

### 2.6 Retention policy — `retention_policy.txt`
```
backup retention policy kept for 30 days. retained for 30 days
```

### 2.7 Encrypted backups — `encrypted_backup.txt`
```
encrypted backup file created. encryption algorithm AES-256
```

### 2.8 Restricted admin access — `access_admin_only.txt`
```
restricted access admin users only
```

---

## 3. ML2 evidence preparation

### 3.1 Backup verification via audit logs — PASS  
`backup_verification_ml2_pass.txt`
```
backup job verified via audit log verification=success status=success
```

### 3.2 Backup verification via audit logs — FAIL  
`backup_verification_ml2_fail.txt`
```
backup job verification=fail audit log missing for backup
```

### 3.3 Offsite + immutability enforced by policy  
`offsite_policy_enforced_ml2.txt`
```
immutability=enabled policy=enforced
```

### 3.4 Restore to common point — PASS  
`restore_report_ml2_pass.txt`
```
restore test=item-level status=success common point=2025-12-01T23:30Z
```

### 3.5 Restore to common point — FAIL  
`restore_report_ml2_fail.txt`
```
restore test=item-level status=fail
```

### 3.6 Retention & immutability match policy — PASS  
`policy_ml2_pass.txt`
```
retention=30days immutability=enabled policy match
```

### 3.7 Retention or immutability misaligned — FAIL  
`policy_ml2_fail.txt`
```
retention<policy immutability=disabled
```

### 3.8 Encryption enforcement — PASS  
`encryption_ml2_pass.txt`
```
encryption=aes-256 kms verified
```

### 3.9 Encryption enforcement — FAIL  
`encryption_ml2_fail.txt`
```
encrypted backup kms=missing encryption=none
```

### 3.10 Access control enforcement — PASS  
`access_admin_only_ml2.txt`
```
role=backup-admin access=allowed audit=success
```

### 3.11 Unauthorized access allowed — FAIL  
`repo_audit_fail.txt`
```
role=sysadmin is_backup_admin=false access=allowed result=success
```

---

## 4. Using the Evidence Scanner

1. Open the Evidence Assistant web interface.
2. Select **Regular Backups (RB)**.
3. Upload any ML1 or ML2 evidence file.
4. Review the detection results:
   - Confirm the test ID (ML1-RB-01 … ML2-RB-06).
   - Check PASS/FAIL behaviour based on your expected outcome.

If the tool does not detect a file, verify that the file’s content includes the required key phrases listed above.
