# strategies/regular_backups.py
from __future__ import annotations
from typing import List, Dict
from .overview import Strategy


class RegularBackups(Strategy):
    """
    Essential Eight - Regular Backups (ML1-RB-01 .. ML1-RB-06, ML2-RB-01 .. ML2-RB-06)
    Accepts:
      - OCR/text from backup logs
      - Reports confirming offsite backups, encryption, retention, and test restores
    """

    id = "RB"
    name = "Regular Backups"

    def description(self) -> str:
        return "Checks if backups are configured, recent, encrypted, and tested."

    # ---- helpers ------------------------------------------------------------
    @staticmethod
    def _row(tid: str, sub: str, pf: str, prio: str, rec: str, ev: List[str]) -> Dict:
        return {
            "test_id": tid,
            "sub_strategy": sub,
            "detected_level": "ML1",
            "pass_fail": pf,
            "priority": prio,
            "recommendation": rec,
            "evidence": ev,
        }

    @staticmethod
    def _row_ml(level: str, tid: str, sub: str, pf: str, prio: str,
                rec: str, ev: List[str]) -> Dict:
        return {
            "test_id": tid,
            "sub_strategy": sub,
            "detected_level": level,   # "ML1" or "ML2"
            "pass_fail": pf,
            "priority": prio,
            "recommendation": rec,
            "evidence": ev,
        }

    @staticmethod
    def _has(text: str, *phrases: str) -> bool:
        t = text.lower()
        return any(p.lower() in t for p in phrases)

    @staticmethod
    def _clip(text: str, n: int = 200) -> str:
        t = " ".join(text.split())
        return (t[:n] + "…") if len(t) > n else t

    # ---- Strategy API -------------------------------------------------------
    def emit_hits(self, text: str, source_file: str = "") -> List[Dict]:
        rows: List[Dict] = []
        t = text or ""
        ev = lambda s="": [self._clip(s)] if s else []

        # ---------------- ML1 tests ----------------

        # ML1-RB-01: Backups configured and recent
        # (avoid generic "success" so ML2 files do not trigger this)
        if self._has(t, "backup completed", "last backup",
                     "backup status=success", "backup job status=success"):
            rows.append(self._row(
                "ML1-RB-01", "Backups are configured and recent", "PASS", "High",
                "Ensure automated regular backups are scheduled.",
                ev(t),
            ))
        elif self._has(t, "backup failed", "no recent backup"):
            rows.append(self._row(
                "ML1-RB-01", "Backups are configured and recent", "FAIL", "High",
                "Review backup jobs and confirm scheduling.",
                ev(t),
            ))

        # ML1-RB-02: Offsite or immutable backups
        if self._has(t, "offsite", "immutable", "cloud backup", "remote storage"):
            rows.append(self._row(
                "ML1-RB-02", "Backups stored offsite/immutable", "PASS", "Medium",
                "Maintain offsite/immutable copies to prevent ransomware impact.",
                ev(t),
            ))

        # ML1-RB-03: Backup restore tested
        if self._has(t, "restore test successful", "test restore completed"):
            rows.append(self._row(
                "ML1-RB-03", "Restore tests completed", "PASS", "Medium",
                "Perform restore tests regularly to validate backup usability.",
                ev(t),
            ))
        elif self._has(t, "restore failed", "restore error"):
            rows.append(self._row(
                "ML1-RB-03", "Restore tests completed", "FAIL", "High",
                "Investigate restore failures to ensure backups are usable.",
                ev(t),
            ))

        # ML1-RB-04: Retention policy
        if self._has(t, "retention policy", "kept for", "retained for"):
            rows.append(self._row(
                "ML1-RB-04", "Backup retention policy in place", "PASS", "Medium",
                "Ensure backups are retained according to business/legislative needs.",
                ev(t),
            ))

        # ML1-RB-05: Backup encryption
        # First recognise clear FAIL (unencrypted), then PASS.
        if self._has(t, "unencrypted backup", "encryption=none", "kms=missing"):
            rows.append(self._row(
                "ML1-RB-05", "Backups encrypted", "FAIL", "High",
                "Encrypt all backups and integrate with a key management service.",
                ev(t),
            ))
        elif self._has(t, "encrypted backup", "encryption=aes-256",
                       "aes-256", "backup secured"):
            rows.append(self._row(
                "ML1-RB-05", "Backups encrypted", "PASS", "High",
                "Encrypt all backups to prevent unauthorized access.",
                ev(t),
            ))

        # ML1-RB-06: Access controls for backups
        if self._has(t, "restricted access", "admin only", "access control"):
            rows.append(self._row(
                "ML1-RB-06", "Backup access restricted", "PASS", "High",
                "Restrict backup system access to administrators only.",
                ev(t),
            ))

        # ---------------- ML2 tests ----------------

        # ML2-RB-01: Backup jobs verified through audit logs
        if self._has(t, "verification=fail") or self._has(t, "audit log missing"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-01", "Backup jobs verified through audit logs",
                "FAIL", "High",
                "Investigate missing or unsuccessful verification events.",
                ev(t),
            ))
        elif self._has(t, "backup job verified") and self._has(t, "verification=success"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-01", "Backup jobs verified through audit logs",
                "PASS", "High",
                "Ensure audit logs continue to validate backup job success.",
                ev(t),
            ))

        # ML2-RB-02: Offsite & immutability enforced by policy
        if self._has(t, "immutability=enabled") and self._has(t, "policy=enforced"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-02", "Offsite and immutability enforced",
                "PASS", "High",
                "Ensure offsite and immutability policy remains enforced.",
                ev(t),
            ))

        # ML2-RB-03: Restore to a common point proven
        if self._has(t, "restore test") and self._has(t, "status=success") and self._has(t, "common point"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-03", "Restore to a common point proven",
                "PASS", "Medium",
                "Continue testing restores to verify backup usability.",
                ev(t),
            ))
        elif self._has(t, "restore test") and self._has(t, "status=fail"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-03", "Restore to a common point proven",
                "FAIL", "High",
                "Investigate restore failures and repeat tests.",
                ev(t),
            ))

        # ML2-RB-04: Retention + immutability verified against policy baseline
        if self._has(t, "retention=") and self._has(t, "immutability=enabled") and self._has(t, "policy=match"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-04", "Retention & immutability meet policy baseline",
                "PASS", "High",
                "Retention and immutability settings match required policy.",
                ev(t),
            ))
        elif self._has(t, "retention<policy") or self._has(t, "immutability=disabled"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-04", "Retention & immutability meet policy baseline",
                "FAIL", "High",
                "Update retention and enable immutability to meet policy.",
                ev(t),
            ))

        # ML2-RB-05: Encryption enforcement + KMS audit
        if self._has(t, "encryption=aes-256") and self._has(t, "kms=verified"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-05", "Encryption enforcement verified",
                "PASS", "High",
                "Ensure encryption and KMS-policy enforcement remain active.",
                ev(t),
            ))
        elif self._has(t, "kms=missing") or self._has(t, "unencrypted backup") or self._has(t, "encryption=none"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-05", "Encryption enforcement verified",
                "FAIL", "High",
                "Backups are not encrypted or KMS verification failed.",
                ev(t),
            ))

        # ML2-RB-06: Only backup-admins allowed, enforced by audit logs
        if self._has(t, "role=backup-admin") and self._has(t, "access=allowed") and self._has(t, "audit=success"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-06", "Access control enforcement (admins only)",
                "PASS", "High",
                "Access is properly restricted to backup-admins.",
                ev(t),
            ))
        elif self._has(t, "is_backup_admin=false") and (
            self._has(t, "access=allowed") or self._has(t, "result=success")
        ):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-06", "Access control enforcement (admins only)",
                "FAIL", "High",
                "Non-admin access detected. Restrict repository immediately.",
                ev(t),
            ))

        return rows


def get_strategy() -> Strategy:
    return RegularBackups()
