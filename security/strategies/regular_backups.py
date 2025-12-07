# strategies/regular_backups.py
from __future__ import annotations
import re
from typing import List, Dict
from .overview import Strategy


class RegularBackups(Strategy):
    """
    Essential Eight - Regular Backups (ML1-RB-01 .. ML1-RB-06)
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
    def _row_ml(level, tid, sub, pf, prio, rec, ev):
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

        # ML1-RB-01: Backups configured and recent
        if self._has(t, "backup completed", "last backup", "success"):
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
        if self._has(t, "encrypted backup", "aes", "rsa", "backup secured"):
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
        # ---- ML2 tests ----

        # ML2-RB-01: only backup-admins may access repositories
        if self._has(t, "role=backup-admin") and self._has(t, "result=success"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-01", "Access limited to backup-admins",
                "PASS", "High",
                "Keep repository access limited to backup-admins and alert on non-member access.",
                ev(t)
            ))
        elif (
            self._has(t, "role=sysadmin")
            and self._has(t, "is_backup_admin=false")
            and self._has(t, "result=success")
        ):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-01", "Access limited to backup-admins",
                "FAIL", "High",
                "Remove non-backup-admin privileges from backup repositories.",
                ev(t)
            ))

        # ML2-RB-02: restore to a common point in time is proven
        if self._has(t, "restore test") and self._has(t, "status=success") and self._has(t, "common point"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-02", "Restore to common point proven",
                "PASS", "Medium",
                "Record periodic restore tests and keep reports.",
                ev(t)
            ))
        elif self._has(t, "restore test") and self._has(t, "status=fail"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-02", "Restore to common point proven",
                "FAIL", "High",
                "Investigate the failure and repeat the test until successful.",
                ev(t)
            ))

        # ML2-RB-03: retention and immutability are enforced
        if self._has(t, "retention=") and self._has(t, "immutability=enabled"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-03", "Retention and immutability enforced",
                "PASS", "High",
                "Keep retention at or above policy and keep immutability enabled.",
                ev(t)
            ))
        elif self._has(t, "immutability=disabled") or self._has(t, "retention=<policy"):
            rows.append(self._row_ml(
                "ML2", "ML2-RB-03", "Retention and immutability enforced",
                "FAIL", "High",
                "Enable object lock or vault immutability and raise retention to policy.",
                ev(t)
            ))
        return rows


def get_strategy() -> Strategy:
    return RegularBackups()
