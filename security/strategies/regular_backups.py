# strategies/regular_backups.py
from __future__ import annotations
import re
from typing import List, Dict
from .overview import Strategy


class RegularBackups(Strategy):
    """
    Essential Eight – Regular Backups (ML1 focus, evidence-driven).
    Consumes OCR/text from:
      - Backup product logs and job reports (Veeam, M365, Acronis, Windows Backup, etc.)
      - Windows Task Scheduler exports (.xml/.txt), wbadmin outputs, PowerShell transcripts
      - Screenshots of backup consoles / settings
      - Policy docs or config dumps showing retention/encryption/offsite

    Rules (examples):
      RB-01  scheduled backups configured (frequency)
      RB-02  backups stored offline/offsite/immutable
      RB-03  backup data encryption enabled
      RB-04  recent successful backup completed
      RB-05  restore/recovery tested (evidence of test restore)
      RB-06  retention policy defined (e.g., days/weeks/months or #copies)
      RB-07  access control for backups (MFA/admin separation/role-based)
    """

    id = "REGBAK"
    name = "Regular Backups"

    # ---------- helpers ----------
    @staticmethod
    def _row(tid: str, sub: str, pf: str, prio: str, rec: str, ev: str, lvl: str = "ML1") -> Dict:
        return {
            "test_id": tid,
            "sub_strategy": sub,
            "detected_level": lvl,
            "pass_fail": pf,
            "priority": prio,
            "recommendation": rec,
            "evidence": [ev] if ev else [],
        }

    @staticmethod
    def _has(text: str, *phrases: str) -> bool:
        t = text.lower()
        return any(p.lower() in t for p in phrases)

    @staticmethod
    def _re(text: str, pattern: str) -> bool:
        return re.search(pattern, text, flags=re.I | re.S) is not None

    @staticmethod
    def _clip(text: str, n: int = 200) -> str:
        t = " ".join(text.split())
        return (t[:n] + "…") if len(t) > n else t

    # ---------- main rule emitter ----------
    def emit_hits(self, text: str, source_file: str = "") -> List[Dict]:
        rows: List[Dict] = []
        t = text or ""
        ev = self._clip(t)

        # RB-01: Scheduled backups configured (frequency present)
        # Look for common scheduler/backup job indicators
        freq_hit = (
            self._has(t, "daily backup", "weekly backup", "schedule enabled", "trigger: daily", "trigger: weekly")
            or self._re(t, r"\b(every\s+\d+\s+(hours?|days?|weeks?))\b")
            or self._re(t, r"\bwbadmin\s+start\s+backup\b")
            or self._re(t, r"\btask\s+scheduler\b|\bTaskName:\s+\\.*backup")
            or self._re(t, r"\bjob\s+schedule(d)?\b")
        )
        if freq_hit:
            rows.append(self._row(
                "ML1-RB-01",
                "Backups are scheduled",
                "PASS",
                "High",
                "Maintain automated backup schedules (daily for critical data).",
                ev
            ))

        # RB-02: Offsite/offline/immutable copies
        offsite_hit = (
            self._has(t, "offsite", "off-site", "off line", "offline copy", "air-gapped", "immutable")
            or self._has(t, "object lock", "worm", "s3 bucket with retention", "immutability")
            or self._re(t, r"copy\s+to\s+(tape|external drive|cloud|azure|aws|s3|glacier|dr site)")
        )
        if offsite_hit:
            rows.append(self._row(
                "ML1-RB-02",
                "Backups stored offline/offsite/immutable",
                "PASS",
                "High",
                "Keep at least one offline/offsite/immutable copy (3-2-1 strategy).",
                ev
            ))

        # RB-03: Encryption enabled
        enc_hit = (
            self._has(t, "encryption enabled", "encrypted backups", "encrypt data at rest", "protected with aes")
            or self._re(t, r"\baes-(128|192|256)\b")
            or self._has(t, "bitlocker", "server-side encryption", "sse-s3", "kms key")
        )
        if enc_hit:
            rows.append(self._row(
                "ML1-RB-03",
                "Backup data encryption",
                "PASS",
                "Medium",
                "Ensure backups are encrypted in transit and at rest; protect keys separately.",
                ev
            ))

        # RB-04: Recent successful backup (success keywords + recent date pattern)
        # (We don’t evaluate the actual date window here; we just detect success signals.)
        success_hit = (
            self._has(t, "backup completed successfully", "result: success", "status: success", "return code 0x0")
            or self._re(t, r"\bsuccess(?:ful|fully)\b.*\bbackup\b")
            or self._re(t, r"\bjob\s+result:\s*success\b")
        )
        if success_hit:
            rows.append(self._row(
                "ML1-RB-04",
                "Recent successful backups",
                "PASS",
                "High",
                "Monitor daily and investigate failures immediately; alerting should be enabled.",
                ev
            ))

        # RB-05: Restore test executed / verified
        restore_hit = (
            self._has(t, "test restore", "verified restore", "restore tested", "recovery test", "bare-metal restore")
            or self._re(t, r"\brestore\s+(completed|successful)\b")
        )
        if restore_hit:
            rows.append(self._row(
                "ML1-RB-05",
                "Periodic restore testing",
                "PASS",
                "High",
                "Perform and document regular restore tests from backup media.",
                ev
            ))

        # RB-06: Retention policy defined
        retention_hit = (
            self._has(t, "retention", "keep for", "days to keep", "weeks to keep", "months to keep")
            or self._re(t, r"\b(retention|keep)\s+(for\s+)?\d+\s+(days?|weeks?|months?)\b")
            or self._re(t, r"\b(?:gfs|grandfather-father-son)\b")
        )
        if retention_hit:
            rows.append(self._row(
                "ML1-RB-06",
                "Retention policy defined",
                "PASS",
                "Medium",
                "Define and enforce retention (e.g., 30–90 days, plus monthly/annual where needed).",
                ev
            ))

        # RB-07: Access control on backup platform (MFA / separate admin)
        access_hit = (
            self._has(t, "mfa enabled", "multi-factor", "two-factor", "role-based access", "rbac")
            or self._has(t, "separate admin account", "break-glass account", "least privilege")
        )
        if access_hit:
            rows.append(self._row(
                "ML1-RB-07",
                "Backup console access control",
                "PASS",
                "Medium",
                "Enforce MFA and least-privilege on backup administration.",
                ev
            ))

        # If nothing matched, emit a single FAIL row so the file still appears in reports
        if not rows:
            rows.append(self._row(
                "ML1-RB-00",
                "No backup controls detected in evidence",
                "FAIL",
                "High",
                "Provide logs/screenshots showing schedule, success, retention, encryption, and restore tests.",
                self._clip(f"{source_file}: {t}")
            ))

        return rows


def get_strategy() -> Strategy:
    return RegularBackups()
