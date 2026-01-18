# Regular Backups (RB) strategy

This strategy checks evidence for the ACSC Essential Eight **Regular Backups** control.

Evidence detection is **key=value driven**, deterministic, and case-insensitive. The parser extracts `key=value` pairs from anywhere in the text.

> Note: Evidence screenshots must not be committed to the repo. Store them externally (PR attachments, OneDrive, SharePoint) and link them instead.

---

## 1. Tests implemented

| Test ID   | Level | Sub-strategy | What it checks |
|----------|------|--------------|----------------|
| ML1-RB-01 | ML1 | Backups configured and recent | Backup success or failure, including “no recent backup” reasons |
| ML1-RB-02 | ML1 | Offsite OR immutable backups | Backups stored offsite, or immutability enabled |
| ML1-RB-03 | ML1 | Restore test with proven restore point | Successful full restore plus evidence of a common restore point |
| ML1-RB-04 | ML1 | Retention policy | Retention policy defined and retention days present |
| ML1-RB-05 | ML1 | Backup encryption | Encryption enabled, KMS configured where relevant |
| ML1-RB-06 | ML1 | Access control | Backup access restricted to backup administrators |
| ML2-RB-01 | ML2 | Audit verification | Verification recorded and audit log presence |
| ML2-RB-02 | ML2 | Policy enforcement | Policy enforced for offsite and immutability together |
| ML2-RB-03 | ML2 | Restore consistency | Item-level restore success with a common point |
| ML2-RB-04 | ML2 | Policy alignment | Retention and immutability aligned to baseline |
| ML2-RB-05 | ML2 | Encryption enforcement | Encryption enforced with verified KMS |
| ML2-RB-06 | ML2 | Access enforcement | Admin-only access enforced with auditing |

---

## 2. How PASS and FAIL are decided

The strategy evaluates extracted `key=value` pairs. Extra descriptive text is allowed.

### ML1 rules

**ML1-RB-01 Backups configured and recent**
- PASS when: `status=success`
- FAIL when: `status=failure` or `status=fail` or `reason=no_recent_backup`

**ML1-RB-02 Offsite OR immutable backups**
- PASS when either: `backup_location=offsite` or `immutability=enabled`
- FAIL when: `backup_location=local`

**ML1-RB-03 Restore test with proven restore point**
- PASS when all are present: `restore_test=full`, `status=success`, and `common_point` (any value)
- FAIL when: `restore_test=full` and (`status=failure` or `status=fail`)

**ML1-RB-04 Retention policy**
- PASS when: `retention_policy=defined` and `retention_days` is present
- FAIL when: `retention_policy=missing` or `immutability=disabled`, or when retention is defined but `retention_days` is missing

**ML1-RB-05 Backup encryption**
- PASS when: `encryption=aes-256`
- FAIL when: `encryption=none` or `kms=missing` (or text contains `unencrypted_backup`)

**ML1-RB-06 Access control**
- PASS when: `access=restricted` and (`role=backup-admin` or `role=backup_admin` or `is_backup_admin=true`)
- FAIL when: `access=allowed` and the evidence does not indicate a backup admin role

### ML2 rules

ML2 checks run only when `_ml2` appears in the filename.

**ML2-RB-01 Audit verification**
- PASS when: `verification=success`
- FAIL when: `verification=fail` or `audit_log=missing`

**ML2-RB-02 Policy enforcement**
- PASS when all are present: `policy=enforced`, `backup_location=offsite`, `immutability=enabled`
- FAIL when `policy=enforced` is present but offsite and immutability are not both present

**ML2-RB-03 Restore consistency**
- PASS when: `restore_test=item-level`, `status=success`, and `common_point` is present
- FAIL when: `restore_test=item-level` and (`status=failure` or `status=fail`)

**ML2-RB-04 Policy alignment**
- PASS when: `policy_match=true`, `immutability=enabled`, and `retention_days` is present
- FAIL when: `retention_policy=missing` or `immutability=disabled`

**ML2-RB-05 Encryption enforcement**
- PASS when: `encryption=aes-256` and `kms=verified`
- FAIL when: `encryption=none` and `kms=missing`

**ML2-RB-06 Access enforcement**
- PASS when all are present: backup admin role, `access=allowed`, `audit=success`, `is_backup_admin=true`
- FAIL when: `access=allowed` and `is_backup_admin=false`

---

## 3. Evidence files used for testing

Files are structured as **one outcome per file**, with no contradictory keys and no mixed restore types.

### ML1 evidence (no `_ml2`)

- `backup_success.txt`
- `backup_failed.txt`
- `offsite_backup.txt`
- `retention_policy.txt`
- `restore_test.txt`
- `restore_failed.txt`
- `Encrypted_backup.txt`
- `access_admin_only.txt`
- `repo_audit_pass.txt`
- `repo_audit_fail.txt`

### ML2 evidence (`_ml2` required)

- `backup_verification_ml2_pass.txt`
- `backup_verification_ml2_fail.txt`
- `offsite_policy_enforced_ml2.txt`
- `restore_report_ml2_pass.txt`
- `restore_report_ml2_fail.txt`
- `policy_ml2_pass.txt`
- `policy_ml2_fail.txt`
- `encryption_ml2_pass.txt`
- `encryption_ml2_fail.txt`
- `access_admin_only_ml2.txt`

---

## 4. Strategy execution behaviour

- Files without `_ml2` → ML1-only evaluation
- Files with `_ml2` → ML2 evaluation and output includes **both ML1 and ML2 rows**
- No evidence file should produce empty output
