# Evidence Preparation Guide – Regular Backups (Essential Eight)

This guide explains how to prepare evidence files for the Regular Backups strategy so the AutoAudit Evidence Scanner can detect ML1 and ML2 results.

Evidence detection is **key=value driven**, deterministic, and case-insensitive.

---

## 1. General rules

- Files must be plain text (`.txt`)
- Evidence is parsed using `key=value` pairs (anywhere in the text)
- Extra descriptive text is allowed, but required keys must be present
- Each file must represent **one clear outcome**
- Do not mix contradictory values in one file (example: both `access=restricted` and `access=allowed`)
- Do not mix multiple restore types in one file (example: both `restore_test=full` and `restore_test=item-level`)

### Maturity handling

- Files without `_ml2` in the filename are treated as **ML1 evidence**
- Files with `_ml2` in the filename are treated as **ML2 evidence**
- ML2 evidence outputs:
  - one ML1 row, and
  - one ML2 row
- ML2 PASS implies ML1 PASS
- ML2 FAIL implies ML1 FAIL

---

## 2. ML1 evidence files (no `_ml2`)

backup_success.txt
status=success

backup_failed.txt
status=failure
reason=no_recent_backup

offsite_backup.txt 
backup_location=offsite
or
immutability=enabled

restore_test.txt
restore_test=full
status=success
common_point=true

restore_failed.txt
restore_test=full
status=failure

retention_policy.txt
retention_policy=defined
retention_days=30

Encrypted_backup.txt
encryption=aes-256

access_admin_only.txt
access=restricted
role=backup-admin

repo_audit_fail.txt
access=allowed
is_backup_admin=false
role=user
result=success

repo_audit_pass.txt
access=restricted
role=backup-admin
result=success

## 3. ML2 evidence files (must include _ml2)
backup_verification_ml2_pass.txt
verification=success
status=success

backup_verification_ml2_fail.txt
verification=fail
audit_log=missing

offsite_policy_enforced_ml2.txt
backup_location=offsite
immutability=enabled
policy=enforced

restore_report_ml2_pass.txt
restore_test=item-level
status=success
common_point=true

restore_report_ml2_fail.txt
restore_test=item-level
status=failure

policy_ml2_pass.txt
retention_days=30
immutability=enabled
policy_match=true

policy_ml2_fail.txt
retention_policy=missing
immutability=disabled

encryption_ml2_pass.txt
encryption=aes-256
kms=verified

encryption_ml2_fail.txt
encryption=none
kms=missing

access_admin_only_ml2.txt
access=allowed
role=backup-admin
is_backup_admin=true
audit=success

4. Using the Evidence Scanner

Open the AutoAudit Evidence Scanner UI

Select Regular Backups (RB)

Upload one or more evidence files

Review results (Test ID, maturity level, PASS/FAIL)

If results are not produced:

Confirm _ml2 is present for ML2 evidence

Confirm keys match this guide

Confirm the file represents one outcome




