# Regular Backups (RB) strategy

This strategy checks evidence for Essential Eight Regular Backups controls.

It currently supports:

- ML1 tests ML1-RB-01 to ML1-RB-06  
- ML2 tests ML2-RB-01 to ML2-RB-06  

The strategy reads OCR text or log text from backup reports, policy extracts or configuration files.

---

## 1. Tests implemented

| Test ID     | Level | Sub-strategy                                           | What it checks                                                   |
|-------------|-------|--------------------------------------------------------|------------------------------------------------------------------|
| ML1-RB-01   | ML1   | Backups are configured and recent                      | Recent successful or failed backup jobs                          |
| ML1-RB-02   | ML1   | Backups stored offsite or immutable                    | Whether backups use offsite or immutable storage                 |
| ML1-RB-03   | ML1   | Restore tests completed                                | Whether restore tests are executed and if they pass or fail      |
| ML1-RB-04   | ML1   | Backup retention policy in place                       | Whether a retention policy exists                                |
| ML1-RB-05   | ML1   | Backups encrypted                                      | Whether backups are encrypted                                    |
| ML1-RB-06   | ML1   | Backup access restricted                               | Whether access to backup systems is restricted                   |
| ML2-RB-01   | ML2   | Backup jobs verified through audit logs                | Verification events in audit logs                                |
| ML2-RB-02   | ML2   | Offsite + immutability enforced by policy              | Policy enforcing immutability and offsite storage                |
| ML2-RB-03   | ML2   | Restore to a common point proven                       | Restore test proving consistent restore points                   |
| ML2-RB-04   | ML2   | Retention and immutability meet policy baseline        | Whether retention + immutability match policy                    |
| ML2-RB-05   | ML2   | Encryption enforcement verified                        | Whether encryption + KMS verification appear in logs             |
| ML2-RB-06   | ML2   | Access control enforcement for backup administrators   | Whether only backup-admins are allowed                           |

---

## 2. How the scanner decides PASS and FAIL

The strategy performs simple keyword checks on the extracted text.

### ML1 tests

#### **ML1-RB-01 Backups are configured and recent**
- PASS if text contains:  
  `backup completed`, `last backup`, `status success`
- FAIL if text contains:  
  `backup failed`, `no recent backup`

#### **ML1-RB-02 Offsite or immutable backups**
- PASS if text contains:  
  `offsite`, `immutable`, `cloud`, `immutable storage`

#### **ML1-RB-03 Restore tests completed**
- PASS if text contains:  
  `restore test status=success` or `test restore completed`
- FAIL if text contains:  
  `status fail`, `restore failed`

#### **ML1-RB-04 Backup retention policy**
- PASS if text contains:  
  `retention policy`, `kept for`, `retained for`

#### **ML1-RB-05 Backups encrypted**
- PASS if text contains:  
  `encrypted backup`, `AES-256`, `encryption`

#### **ML1-RB-06 Backup access restricted**
- PASS if text contains:  
  `restricted access`, `admin users`, `admin only`

---

### ML2 tests

#### **ML2-RB-01 Backup jobs verified through audit logs**
- PASS:  
  Contains `backup job verified`, `audit log`, `verification=success`
- FAIL:  
  Contains `verification=fail`, `audit log missing`

#### **ML2-RB-02 Offsite and immutability enforced by policy**
- PASS if text contains:  
  `immutability=enabled` + `policy=enforced`

#### **ML2-RB-03 Restore to a common point proven**
- PASS if text contains:  
  `restore test`, `status=success`, `common point`
- FAIL if text contains:  
  `restore test`, `status=fail`

#### **ML2-RB-04 Retention & immutability meet policy baseline**
- PASS:  
  `retention=30 days`, `immutability=enabled`, `policy match`
- FAIL:  
  `retention<policy`, `immutability=disabled`

#### **ML2-RB-05 Encryption enforcement verified**
- PASS:  
  `encryption=aes-256`, `kms verified`
- FAIL:  
  `kms=missing`, `unencrypted backup`, `encryption none`

#### **ML2-RB-06 Access control enforcement**
- PASS:  
  `role=backup-admin`, `access=allowed`, `audit=success`
- FAIL:  
  `role=sysadmin`, `is_backup_admin=false`, `access allowed`

---

## 3. Evidence files used for testing

These are the **exact contents from your test files**.

### ML1 evidence files

| File | Content used by scanner |
|------|--------------------------|
| **backup_success.txt** | `backup completed successfully. last backup 2025-09-10 23:45 status success` |
| **backup_failed.txt** | `no recent backup found in the last seven days. status failure` |
| **offsite_backup.txt** | `daily backup completed to immutable cloud storage (offsite)` |
| **retention_policy.txt** | `backup retention policy kept for 30 days. retained for 30 days` |
| **restore_test.txt** | `restore test status=success common point` |
| **restore_failed.txt** | `restore failed during test restore. status fail` |
| **encrypted_backup.txt** | `encrypted backup file created. encryption algorithm AES-256` |
| **access_admin_only.txt** | `restricted access admin users only` |

### ML2 evidence files

| File | Content used by scanner |
|------|--------------------------|
| **backup_verification_ml2_pass.txt** | `backup job verified via audit log verification=success status=success` |
| **backup_verification_ml2_fail.txt** | `backup job verification=fail audit log missing for backup` |
| **offsite_policy_enforced_ml2.txt** | `immutability=enabled policy=enforced` |
| **restore_report_ml2_pass.txt** | `restore test=item-level status=success common point=2025-12-01T23:30Z` |
| **restore_report_ml2_fail.txt** | `restore test=item-level status=fail` |
| **policy_ml2_pass.txt** | `retention=30days immutability=enabled policy match` |
| **policy_ml2_fail.txt** | `retention<policy immutability=disabled` |
| **encryption_ml2_pass.txt** | `encryption=aes-256 kms verified` |
| **encryption_ml2_fail.txt** | `encrypted backup kms=missing encryption=none` |
| **access_admin_only_ml2.txt** | `role=backup-admin access=allowed audit=success` |
| **repo_audit_fail.txt** | `role=sysadmin is_backup_admin=false access=allowed result=success` |

---