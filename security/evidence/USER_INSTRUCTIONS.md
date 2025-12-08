# Evidence preparation guide – Regular Backups (ML1 + ML2)
This guide explains how to prepare evidence files for the Regular Backups strategy so the Evidence Scanner can read them and map them to the maturity-level tests. Files should be simple text logs or policy extracts that contain clear key–value fields such as `status=success`, `role=backup-admin`, or `immutability=enabled`.

## 1. General guidelines for evidence files
- Files should be plain text (.txt) or CSV exports.
- Each line should describe one event, policy entry, or result.
- Include clear indicators that allow the scanner to match ML1 and ML2 conditions.
- Extra descriptive text is fine. The scanner only checks for key phrases.

## 2. Evidence files for ML1 tests

### 2.1 Successful backups – `backup_success.txt`
Example:
2025-12-01T22:05Z job=nightly-backup status=success "Backup completed successfully"


### 2.2 Failed or missing backups – `backup_failed.txt`
Example:
2025-12-01T22:05Z job=nightly-backup status=fail "Backup failed – network error"


### 2.3 Offsite or immutable backups – `offsite_backup.txt`
Example:
target=cloud-vault location=offsite immutability=enabled copy_type=immutable


### 2.4 Successful restore test – `restore_test.txt`
Example:
restore test=full status=success "Test restore completed successfully"


### 2.5 Failed restore test – `Restore_failed.txt`
Example:
restore test=full status=fail "Restore failed – checksum error"


### 2.6 Encrypted backups – `Encrypted_backup.txt`
Example:
encryption=AES-256 key_type=KMS "backup encryption enabled"


### 2.7 Restricted access – `access_admin_only.txt`
Example:
console_access_roles=backup-admin,security-admin mfa=enabled

## 3. Evidence files for ML2 tests

### 3.1 Repository access controlled – `repo_audit_pass.txt`
Example:
timestamp=2025-12-01T09:15Z role=backup-admin user=jane result=success repo=primary-backups


### 3.2 Unauthorized access allowed – `repo_audit_fail.txt`
Example:
timestamp=2025-12-01T10:05Z role=sysadmin is_backup_admin=false result=success repo=primary-backups


### 3.3 Successful restore to a common point – `restore_report_ml2_pass.txt`
Example:
restore test=item-level status=success common point=2025-12-01T23:30Z scope=key-workloads


### 3.4 Failed restore test – `restore_report_ml2_fail.txt`
Example:
restore test=item-level status=fail "Unable to restore all items to common point"


### 3.5 Policy alignment (retention + immutability) – `policy_ml2_pass.txt`
Example:
retention=30days immutability=enabled policy_name=backup-gold


### 3.6 Policy misalignment – `policy_ml2_fail.txt`
Example:
retention=<policy immutability=disabled policy_name=legacy-backups

## 4. How to use the Evidence Scanner
1. Prepare the evidence files using the examples above.
2. Open the Evidence Assistant web interface.
3. Select the Regular Backups strategy.
4. Upload one of your evidence files.
5. Review the results:
   - Check the test ID and maturity level.
   - Confirm PASS or FAIL behaves as expected.

If the tool does not detect the evidence, check that the key fields are present and spelled correctly.