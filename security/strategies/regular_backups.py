from __future__ import annotations

import re
from typing import List, Dict, DefaultDict
from collections import defaultdict

from .overview import Strategy


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _parse_kv_multi(text: str) -> Dict[str, List[str]]:
    """
    Parses key=value pairs from ANYWHERE in the text.
    Supports multiple key=value pairs on one line and repeated keys.

    Example line:
      unencrypted_backup kms=missing encryption=none

    Returns:
      {
        "kms": ["missing"],
        "encryption": ["none"],
        ...
      }
    """
    kv: DefaultDict[str, List[str]] = defaultdict(list)

    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        pairs = re.findall(r"([A-Za-z0-9_]+)\s*=\s*([A-Za-z0-9_\-]+)", line)
        for k, v in pairs:
            k2 = _norm(k)
            v2 = _norm(v)
            kv[k2].append(v2)

    return dict(kv)


def _has_text(text: str, phrase: str) -> bool:
    return _norm(phrase) in _norm(text)


def _has_all_text(text: str, *phrases: str) -> bool:
    t = _norm(text)
    for p in phrases:
        p2 = _norm(p)
        if p2 and p2 not in t:
            return False
    return True


def _kv_has(kv: Dict[str, List[str]], key: str, value: str) -> bool:
    k = _norm(key)
    v = _norm(value)
    vals = kv.get(k, [])
    return any(_norm(x) == v for x in vals)


def _kv_any(kv: Dict[str, List[str]], key: str) -> bool:
    return _norm(key) in kv and len(kv.get(_norm(key), [])) > 0


def _row(level: str, test_id: str, control_name: str, pf: str, priority: str, rec: str, evidence: str) -> Dict:
    return {
        "test_id": test_id,
        "sub_strategy": control_name,
        "detected_level": level,
        "pass_fail": pf,
        "priority": priority,
        "recommendation": rec,
        "evidence": [evidence[:200]],
    }


class RegularBackups(Strategy):
    id = "RB"
    name = "Regular Backups"

    def description(self) -> str:
        return "Evaluates Essential Eight Regular Backups evidence for ML1 and ML2."

    def emit_hits(self, text: str, source_file: str = "") -> List[Dict]:
        rows: List[Dict] = []
        t = text or ""
        kv = _parse_kv_multi(t)
        src = _norm(source_file)
        run_ml2 = "_ml2" in src

        # -------------------------
        # ML1-RB-01 Backups recent
        # -------------------------
        if _kv_has(kv, "status", "failure") or _kv_has(kv, "status", "fail") or _kv_has(kv, "reason", "no_recent_backup"):
            rows.append(_row("ML1", "ML1-RB-01", "Backups configured and recent", "FAIL", "High",
                             "Investigate backup failures and ensure recent backups exist.", t))
        elif _kv_has(kv, "status", "success"):
            rows.append(_row("ML1", "ML1-RB-01", "Backups configured and recent", "PASS", "High",
                             "Maintain regular backups and monitor success.", t))

        # --------------------------------
        # ML1-RB-02 Offsite / immutable
        # --------------------------------
        if _kv_has(kv, "backup_location", "offsite") and _kv_has(kv, "immutability", "enabled"):
            rows.append(_row("ML1", "ML1-RB-02", "Offsite or immutable backups", "PASS", "Medium",
                             "Maintain offsite backups with immutability enabled.", t))
        elif _kv_has(kv, "backup_location", "local"):
            rows.append(_row("ML1", "ML1-RB-02", "Offsite or immutable backups", "FAIL", "Medium",
                             "Move backups offsite and enable immutability.", t))

        # -------------------------
        # ML1-RB-03 Restore testing
        # -------------------------
        if _kv_has(kv, "restore_test", "full") and (_kv_has(kv, "status", "failure") or _kv_has(kv, "status", "fail")):
            rows.append(_row("ML1", "ML1-RB-03", "Restore testing", "FAIL", "High",
                             "Fix restore failures and retest full restore.", t))
        elif _kv_has(kv, "restore_test", "full") and _kv_has(kv, "status", "success"):
            rows.append(_row("ML1", "ML1-RB-03", "Restore testing", "PASS", "Medium",
                             "Continue periodic restore testing.", t))

        # -------------------------
        # ML1-RB-04 Retention policy
        # -------------------------
        if _kv_has(kv, "retention_policy", "defined") and _kv_any(kv, "retention_days"):
            rows.append(_row("ML1", "ML1-RB-04", "Retention policy", "PASS", "Medium",
                             "Ensure retention meets policy requirements.", t))
        elif _kv_has(kv, "retention_policy", "defined") and not _kv_any(kv, "retention_days"):
            rows.append(_row("ML1", "ML1-RB-04", "Retention policy", "FAIL", "Medium",
                             "Define retention_days to match policy.", t))
        elif _kv_has(kv, "retention_policy", "missing") or _kv_has(kv, "immutability", "disabled"):
            rows.append(_row("ML1", "ML1-RB-04", "Retention policy", "FAIL", "Medium",
                             "Define retention policy and enable immutability.", t))

        # -------------------------
        # ML1-RB-05 Backup encryption
        # -------------------------
        if _kv_has(kv, "encryption", "none") or _kv_has(kv, "kms", "missing") or _has_text(t, "unencrypted_backup"):
            rows.append(_row("ML1", "ML1-RB-05", "Backup encryption", "FAIL", "High",
                             "Enable encryption and ensure KMS is configured.", t))
        elif _kv_has(kv, "encryption", "aes-256"):
            rows.append(_row("ML1", "ML1-RB-05", "Backup encryption", "PASS", "High",
                             "Maintain strong encryption for backups.", t))

        # -------------------------
        # ML1-RB-06 Access control
        # -------------------------
        # ML1 PASS: restricted + backup-admin (or is_backup_admin true)
        if _kv_has(kv, "access", "restricted") and (
            _kv_has(kv, "role", "backup-admin") or _kv_has(kv, "role", "backup_admin") or _kv_has(kv, "is_backup_admin", "true")
        ):
            rows.append(_row("ML1", "ML1-RB-06", "Access control", "PASS", "High",
                             "Restrict backup access to administrators.", t))
        # ML1 FAIL: access allowed (general) or user role
        elif _kv_has(kv, "access", "allowed") and (_kv_has(kv, "role", "user") or not (_kv_has(kv, "role", "backup-admin") or _kv_has(kv, "role", "backup_admin"))):
            rows.append(_row("ML1", "ML1-RB-06", "Access control", "FAIL", "High",
                             "Restrict backup access to administrators only.", t))

        # =========================
        # ML2 checks (only for _ml2)
        # =========================
        if run_ml2:
            # -------------------------
            # ML2-RB-01 Audit verification
            # -------------------------
            if _kv_has(kv, "verification", "fail") or _kv_has(kv, "audit_log", "missing"):
                rows.append(_row("ML2", "ML2-RB-01", "Audit verification", "FAIL", "High",
                                 "Fix verification failures and ensure audit logging is present.", t))
            elif _kv_has(kv, "verification", "success"):
                rows.append(_row("ML2", "ML2-RB-01", "Audit verification", "PASS", "High",
                                 "Maintain verification and audit logging.", t))

            # -------------------------
            # ML2-RB-02 Policy enforcement
            # -------------------------
            if _kv_has(kv, "policy", "enforced") and _kv_has(kv, "backup_location", "offsite") and _kv_has(kv, "immutability", "enabled"):
                rows.append(_row("ML2", "ML2-RB-02", "Policy enforcement", "PASS", "High",
                                 "Keep offsite and immutability policies enforced.", t))
            elif _kv_has(kv, "policy", "enforced"):
                rows.append(_row("ML2", "ML2-RB-02", "Policy enforcement", "FAIL", "High",
                                 "Ensure offsite backups and immutability are enabled when policy is enforced.", t))

            # -------------------------
            # ML2-RB-03 Restore consistency (item-level)
            # -------------------------
            if _kv_has(kv, "restore_test", "item-level") and (_kv_has(kv, "status", "failure") or _kv_has(kv, "status", "fail")):
                rows.append(_row("ML2", "ML2-RB-03", "Restore consistency", "FAIL", "High",
                                 "Resolve item-level restore failures and retest.", t))
            elif _kv_has(kv, "restore_test", "item-level") and _kv_has(kv, "status", "success") and _kv_any(kv, "common_point"):
                rows.append(_row("ML2", "ML2-RB-03", "Restore consistency", "PASS", "High",
                                 "Maintain item-level restore capability.", t))

            # -------------------------
            # ML2-RB-04 Policy alignment
            # -------------------------
            if _kv_has(kv, "retention_policy", "missing") or _kv_has(kv, "immutability", "disabled"):
                rows.append(_row("ML2", "ML2-RB-04", "Policy alignment", "FAIL", "High",
                                 "Fix retention policy and enable immutability.", t))
            elif _kv_has(kv, "policy_match", "true") and _kv_has(kv, "immutability", "enabled") and _kv_any(kv, "retention_days"):
                rows.append(_row("ML2", "ML2-RB-04", "Policy alignment", "PASS", "High",
                                 "Maintain retention policy alignment.", t))

            # -------------------------
            # ML2-RB-05 Encryption enforcement
            # -------------------------
            if _kv_has(kv, "kms", "missing") and _kv_has(kv, "encryption", "none"):
                rows.append(_row("ML2", "ML2-RB-05", "Encryption enforcement", "FAIL", "High",
                                 "Enforce encryption with verified KMS.", t))
            elif _kv_has(kv, "encryption", "aes-256") and _kv_has(kv, "kms", "verified"):
                rows.append(_row("ML2", "ML2-RB-05", "Encryption enforcement", "PASS", "High",
                                 "Maintain encryption enforcement with KMS.", t))

            # -------------------------
            # ML2-RB-06 Access enforcement
            # -------------------------
            # PASS needs: backup-admin + access allowed + audit success + is_backup_admin true
            if (
                (_kv_has(kv, "role", "backup-admin") or _kv_has(kv, "role", "backup_admin"))
                and _kv_has(kv, "access", "allowed")
                and _kv_has(kv, "audit", "success")
                and _kv_has(kv, "is_backup_admin", "true")
            ):
                rows.append(_row("ML2", "ML2-RB-06", "Access enforcement", "PASS", "High",
                                 "Maintain enforced admin access and auditing.", t))
            elif _kv_has(kv, "access", "allowed") and _kv_has(kv, "is_backup_admin", "false"):
                rows.append(_row("ML2", "ML2-RB-06", "Access enforcement", "FAIL", "High",
                                 "Remove unauthorised access and enforce admin-only access.", t))

        # ------------------------------------
        # Hard rule: NOTHING can be blank
        # ------------------------------------
        if not rows:
            # If ML2 file, add both ML1 and ML2 fallback FAIL so it triggers.
            if run_ml2:
                rows.append(_row("ML1", "ML1-RB-00", "Evidence parsing", "FAIL", "High",
                                 "Evidence did not match expected format. Fix the evidence text keys.", t))
                rows.append(_row("ML2", "ML2-RB-00", "Evidence parsing", "FAIL", "High",
                                 "Evidence did not match expected format. Fix the evidence text keys.", t))
            else:
                rows.append(_row("ML1", "ML1-RB-00", "Evidence parsing", "FAIL", "High",
                                 "Evidence did not match expected format. Fix the evidence text keys.", t))

        return rows


def get_strategy() -> Strategy:
    return RegularBackups()