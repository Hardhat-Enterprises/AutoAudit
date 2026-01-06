# Regular Backups (RB) strategy

This strategy checks evidence for Essential Eight Regular Backups controls.

It supports detection for both Maturity Level 1 (ML1) and Maturity Level 2 (ML2) requirements
as defined by the Australian Cyber Security Centre (ACSC) Essential Eight framework.

The strategy analyses plain text evidence such as backup logs, audit records,
policy exports, and restore test reports using keyword-based detection.

---

## 1. Tests implemented

| Test ID     | Level | Sub-strategy                                           | What it checks                

| ML1-RB-01   | ML1   | Backups are configured and recent                      | Whether backups are running successfully or failing              
| ML1-RB-02   | ML1   | Backups stored offsite or immutable                    | Whether backups are offsite or immutable  
| ML1-RB-03   | ML1   | Restore tests completed                                | Whether restore tests are performed and their outcome             |
| ML1-RB-04   | ML1   | Backup retention policy in place                       | Whether a retention policy exists                                 |
| ML1-RB-05   | ML1   | Backups encrypted                                      | Whether backups are encrypted                               
| ML1-RB-06   | ML1   | Backup access restricted                               | Whether backup access is restricted to administrators             
| ML2-RB-01   | ML2   | Backup jobs verified through audit logs                | Verification events recorded in audit logs                        
| ML2-RB-02   | ML2   | Offsite + immutability enforced by policy              | Policy enforcement of offsite and immutable backups               
| ML2-RB-03   | ML2   | Restore to a common point proven                       | Ability to restore data consistently to a common point            
| ML2-RB-04   | ML2   | Retention and immutability meet policy baseline        | Alignment of retention and immutability with policy               
| ML2-RB-05   | ML2   | Encryption enforcement verified                        | Encryption and KMS enforcement                                    
| ML2-RB-06   | ML2   | Access control enforcement for backup administrators   | Enforcement of backup administrator access controls               

---

## 2. How the scanner decides PASS and FAIL

The strategy performs simple keyword checks on the extracted text.

### ML1 tests

#### **ML1-RB-01 Backups are configured and recent**
- PASS if text contains:  
  `status=success` or `last_backup=`
- FAIL if text contains:  
  `status=failure` or `reason=no_recent_backup`

#### **ML1-RB-02 Offsite or immutable backups**
- PASS if text contains:  
  `backup_location=offsite` or `immutability=enabled` or `offsite`

#### **ML1-RB-03 Restore tests completed**
- PASS if text contains:  
  `restore_test=full` and `status=success` and `common_point=true`
- FAIL if text contains:  
  `restore_test=full` and `status=fail`

#### **ML1-RB-04 Backup retention policy**
- PASS if text contains:  
  `retention_policy=defined` or `retention_days=`

#### **ML1-RB-05 Backups encrypted**
- PASS if text contains:  
  `encryption=aes-256`
- FAIL if text contains:  
  `encryption=none` or `unencrypted backup` or `kms=missing`

#### **ML1-RB-06 Backup access restricted**
- PASS if text contains:  
  `access=restricted` and `role=backup-admin`

---

### ML2 tests

#### **ML2-RB-01 Backup jobs verified through audit logs**
- PASS:  
  Contains `backup job verified` and `verification=success`
- FAIL:  
  Contains `verification=fail` or `audit log missing`

#### **ML2-RB-02 Offsite and immutability enforced by policy**
- PASS if text contains:  
  `immutability=enabled` and `policy=enforced`

#### **ML2-RB-03 Restore to a common point proven**
- PASS if text contains:  
  `restore test=item-level` and `status=success` and `common point=`
- FAIL if text contains:  
  `restore test=item-level` and `status=fail`

#### **ML2-RB-04 Retention & immutability meet policy baseline**
- PASS:  
  `retention_days=30` and `immutability=enabled` and `policy_match=true`
- FAIL:  
  `retention<policy` or `immutability=disabled`

#### **ML2-RB-05 Encryption enforcement verified**
- PASS:  
  `encryption=aes-256` and `kms=verified`
- FAIL:  
  `kms=missing` or `encryption=none` or `unencrypted backup`

#### **ML2-RB-06 Access control enforcement**
- PASS:  
  `role=backup-admin` and `access=allowed` and `audit=success`
- FAIL:  
  `is_backup_admin=false` and `access=allowed`

---

## 3. Evidence files used for testing

These are the **exact contents from your test files**.

### ML1 evidence files

| File | Content used by scanner |
|------|--------------------------|
| **backup_success.txt** | `status=success` `last_backup=2025-12-01T23:45Z` |
| **backup_failed.txt** | `status=failure` `reason=no_recent_backup` |
| **offsite_backup.txt** | `backup_location=offsite` `immutability=enabled` |
| **retention_policy.txt** | `retention_policy=defined` `retention_days=30` |
| **restore_test.txt** | `restore_test=full` `status=success` `common_point=true` |
| **restore_failed.txt** | `restore_test=full` `status=fail` |
| **encrypted_backup.txt** | `encryption=aes-256` |
| **access_admin_only.txt** | `access=restricted` `role=backup-admin` |

### ML2 evidence files

| File | Content used by scanner |
|------|--------------------------|
| **backup_verification_ml2_pass.txt** | `backup job verified via audit log verification=success status=success` |
| **backup_verification_ml2_fail.txt** | `backup job verification=fail audit log missing for backup` |
| **offsite_policy_enforced_ml2.txt** | `offsite backup immutability=enabled policy=enforced` |
| **restore_report_ml2_pass.txt** | `restore test=item-level status=success common point=2025-12-01T23:30Z` |
| **restore_report_ml2_fail.txt** | `restore test=item-level status=fail` |
| **policy_ml2_pass.txt** | `retention_days=30` `immutability=enabled` `policy_match=true` |
| **policy_ml2_fail.txt** | `retention<policy immutability=disabled` |
| **encryption_ml2_pass.txt** | `encryption=aes-256 kms=verified` |
| **encryption_ml2_fail.txt** | `unencrypted backup kms=missing encryption=none` |
| **access_admin_only_ml2.txt** | `role=backup-admin access=allowed audit=success` |
| **repo_audit_fail.txt** | `role=sysadmin` `is_backup_admin=false` `access=allowed` `result=success` |

---

## 4. Strategy execution behaviour

- Evidence files **without `_ml2`** in the filename are evaluated as **ML1 only**
- Evidence files **with `_ml2`** in the filename are evaluated as **ML2 evidence**
- ML2 evidence always produces **both ML1 and ML2 results**
- ML2 PASS implies ML1 PASS
- ML2 FAIL implies ML1 FAIL
- No evidence file is ignored or produces empty results

This ensures deterministic and auditable Essential Eight maturity assessment.