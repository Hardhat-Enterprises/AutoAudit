from __future__ import annotations

import re
from collections import defaultdict
from typing import DefaultDict, Dict, List, Tuple

from .overview import Strategy


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _parse_kv_multi(text: str) -> Dict[str, List[str]]:
    """
    Parse key=value pairs from anywhere in the text.
    - Supports multiple pairs per line
    - Supports repeated keys
    - Case-insensitive
    """
    kv: DefaultDict[str, List[str]] = defaultdict(list)

    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        pairs = re.findall(r"([A-Za-z0-9_]+)\s*=\s*([A-Za-z0-9_\-]+)", line)
        for k, v in pairs:
            kv[_norm(k)].append(_norm(v))

    return dict(kv)


def _has_text(text: str, phrase: str) -> bool:
    return _norm(phrase) in _norm(text)


def _kv_has(kv: Dict[str, List[str]], key: str, value: str) -> bool:
    k = _norm(key)
    v = _norm(value)
    return any(_norm(x) == v for x in kv.get(k, []))


def _kv_any(kv: Dict[str, List[str]], key: str) -> bool:
    k = _norm(key)
    return k in kv and len(kv.get(k, [])) > 0


def _row(
    level: str,
    test_id: str,
    control_name: str,
    pf: str,
    priority: str,
    rec: str,
    evidence: str,
) -> Dict:
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

    # Map each ML2 control to the corresponding ML1 control for implied ML1 rows
    _ML2_TO_ML1: Dict[str, Tuple[str, str]] = {
        "ML2-RB-01": ("ML1-RB-01", "Backups configured and recent"),
        "ML2-RB-02": ("ML1-RB-02", "Offsite or immutable backups"),
        "ML2-RB-03": ("ML1-RB-03", "Restore testing"),
        "ML2-RB-04": ("ML1-RB-04", "Retention policy"),
        "ML2-RB-05": ("ML1-RB-05", "Backup encryption"),
        "ML2-RB-06": ("ML1-RB-06", "Access control"),
    }

    def description(self) -> str:
        return "Evaluates Essential Eight Regular Backups evidence for ML1 and ML2."

    def emit_hits(self, text: str, source_file: str = "") -> List[Dict]:
        t = text or ""
        kv = _parse_kv_multi(t)
        run_ml2 = "_ml2" in _norm(source_file)

        
        if not run_ml2:
            rows: List[Dict] = []

            # ML1-RB-01 Backups configured and recent
            if (
                _kv_has(kv, "status", "failure")
                or _kv_has(kv, "status", "fail")
                or _kv_has(kv, "reason", "no_recent_backup")
            ):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-01",
                        "Backups configured and recent",
                        "FAIL",
                        "High",
                        "Investigate backup failures and ensure recent backups exist.",
                        t,
                    )
                )
            elif _kv_has(kv, "status", "success"):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-01",
                        "Backups configured and recent",
                        "PASS",
                        "High",
                        "Maintain regular backups and monitor success.",
                        t,
                    )
                )

            # ML1-RB-02 Offsite OR immutable (PASS if either signal exists)
            if _kv_has(kv, "backup_location", "offsite") or _kv_has(kv, "immutability", "enabled"):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-02",
                        "Offsite or immutable backups",
                        "PASS",
                        "Medium",
                        "Maintain offsite backups and/or immutability for backup storage.",
                        t,
                    )
                )
            elif _kv_has(kv, "backup_location", "local"):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-02",
                        "Offsite or immutable backups",
                        "FAIL",
                        "Medium",
                        "Move backups offsite or enable immutability.",
                        t,
                    )
                )

            # ML1-RB-03 Restore testing (PASS requires common_point=true)
            if _kv_has(kv, "restore_test", "full") and (
                _kv_has(kv, "status", "failure") or _kv_has(kv, "status", "fail")
            ):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-03",
                        "Restore testing",
                        "FAIL",
                        "High",
                        "Fix restore failures and retest full restore.",
                        t,
                    )
                )
            elif (
                _kv_has(kv, "restore_test", "full")
                and _kv_has(kv, "status", "success")
                and _kv_has(kv, "common_point", "true")
            ):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-03",
                        "Restore testing",
                        "PASS",
                        "Medium",
                        "Continue periodic restore testing and record common restore points.",
                        t,
                    )
                )

            # ML1-RB-04 Retention policy
            if _kv_has(kv, "retention_policy", "defined") and _kv_any(kv, "retention_days"):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-04",
                        "Retention policy",
                        "PASS",
                        "Medium",
                        "Ensure retention meets policy requirements.",
                        t,
                    )
                )
            elif _kv_has(kv, "retention_policy", "defined") and not _kv_any(kv, "retention_days"):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-04",
                        "Retention policy",
                        "FAIL",
                        "Medium",
                        "Define retention_days to match policy.",
                        t,
                    )
                )
            elif _kv_has(kv, "retention_policy", "missing") or _kv_has(kv, "immutability", "disabled"):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-04",
                        "Retention policy",
                        "FAIL",
                        "Medium",
                        "Define retention policy and enable immutability.",
                        t,
                    )
                )

            # ML1-RB-05 Backup encryption
            if _kv_has(kv, "encryption", "none") or _kv_has(kv, "kms", "missing") or _has_text(t, "unencrypted_backup"):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-05",
                        "Backup encryption",
                        "FAIL",
                        "High",
                        "Enable encryption and ensure KMS is configured.",
                        t,
                    )
                )
            elif _kv_has(kv, "encryption", "aes-256"):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-05",
                        "Backup encryption",
                        "PASS",
                        "High",
                        "Maintain strong encryption for backups.",
                        t,
                    )
                )

            # ML1-RB-06 Access control
            if _kv_has(kv, "access", "restricted") and (
                _kv_has(kv, "role", "backup-admin")
                or _kv_has(kv, "role", "backup_admin")
                or _kv_has(kv, "is_backup_admin", "true")
            ):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-06",
                        "Access control",
                        "PASS",
                        "High",
                        "Restrict backup access to administrators.",
                        t,
                    )
                )
            elif _kv_has(kv, "access", "allowed") and (
                _kv_has(kv, "is_backup_admin", "false")
                or _kv_has(kv, "role", "user")
                or not (_kv_has(kv, "role", "backup-admin") or _kv_has(kv, "role", "backup_admin"))
            ):
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-06",
                        "Access control",
                        "FAIL",
                        "High",
                        "Restrict backup access to administrators only.",
                        t,
                    )
                )

            if not rows:
                rows.append(
                    _row(
                        "ML1",
                        "ML1-RB-00",
                        "Evidence parsing",
                        "FAIL",
                        "High",
                        "Evidence did not match expected key=value format.",
                        t,
                    )
                )

            return rows

        # =========================
        # ML2 checks (ML2 evidence only)
        # =========================
        ml2_rows: List[Dict] = []

        # ML2-RB-01 Audit verification
        if _kv_has(kv, "verification", "fail") or _kv_has(kv, "audit_log", "missing"):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-01",
                    "Audit verification",
                    "FAIL",
                    "High",
                    "Fix verification failures and ensure audit logging is present.",
                    t,
                )
            )
        elif _kv_has(kv, "verification", "success"):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-01",
                    "Audit verification",
                    "PASS",
                    "High",
                    "Maintain verification and audit logging.",
                    t,
                )
            )

        # ML2-RB-02 Policy enforcement (offsite + immutability + policy=enforced)
        if (
            _kv_has(kv, "policy", "enforced")
            and _kv_has(kv, "backup_location", "offsite")
            and _kv_has(kv, "immutability", "enabled")
        ):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-02",
                    "Policy enforcement",
                    "PASS",
                    "High",
                    "Keep offsite and immutability policies enforced.",
                    t,
                )
            )
        elif _kv_has(kv, "policy", "enforced"):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-02",
                    "Policy enforcement",
                    "FAIL",
                    "High",
                    "When policy is enforced, evidence must also show offsite + immutability.",
                    t,
                )
            )

        # ML2-RB-03 Restore consistency (item-level + common_point=true)
        if _kv_has(kv, "restore_test", "item-level") and (
            _kv_has(kv, "status", "failure") or _kv_has(kv, "status", "fail")
        ):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-03",
                    "Restore consistency",
                    "FAIL",
                    "High",
                    "Resolve item-level restore failures and retest.",
                    t,
                )
            )
        elif (
            _kv_has(kv, "restore_test", "item-level")
            and _kv_has(kv, "status", "success")
            and _kv_has(kv, "common_point", "true")
        ):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-03",
                    "Restore consistency",
                    "PASS",
                    "High",
                    "Maintain item-level restore capability and record common restore points.",
                    t,
                )
            )

        # ML2-RB-04 Policy alignment
        if _kv_has(kv, "retention_policy", "missing") or _kv_has(kv, "immutability", "disabled"):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-04",
                    "Policy alignment",
                    "FAIL",
                    "High",
                    "Fix retention policy and enable immutability.",
                    t,
                )
            )
        elif (
            _kv_has(kv, "policy_match", "true")
            and _kv_has(kv, "immutability", "enabled")
            and _kv_any(kv, "retention_days")
        ):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-04",
                    "Policy alignment",
                    "PASS",
                    "High",
                    "Maintain retention policy alignment.",
                    t,
                )
            )

        # ML2-RB-05 Encryption enforcement
        if _kv_has(kv, "kms", "missing") and _kv_has(kv, "encryption", "none"):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-05",
                    "Encryption enforcement",
                    "FAIL",
                    "High",
                    "Enforce encryption with verified KMS.",
                    t,
                )
            )
        elif _kv_has(kv, "encryption", "aes-256") and _kv_has(kv, "kms", "verified"):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-05",
                    "Encryption enforcement",
                    "PASS",
                    "High",
                    "Maintain encryption enforcement with KMS.",
                    t,
                )
            )

        # ML2-RB-06 Access enforcement
        if (
            (_kv_has(kv, "role", "backup-admin") or _kv_has(kv, "role", "backup_admin"))
            and _kv_has(kv, "access", "allowed")
            and _kv_has(kv, "audit", "success")
            and _kv_has(kv, "is_backup_admin", "true")
        ):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-06",
                    "Access enforcement",
                    "PASS",
                    "High",
                    "Maintain enforced admin access and auditing.",
                    t,
                )
            )
        elif _kv_has(kv, "access", "allowed") and _kv_has(kv, "is_backup_admin", "false"):
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-06",
                    "Access enforcement",
                    "FAIL",
                    "High",
                    "Remove unauthorised access and enforce admin-only access.",
                    t,
                )
            )

        if not ml2_rows:
            ml2_rows.append(
                _row(
                    "ML2",
                    "ML2-RB-00",
                    "Evidence parsing",
                    "FAIL",
                    "High",
                    "Evidence did not match expected key=value format.",
                    t,
                )
            )

        any_ml2_fail = any(r.get("pass_fail") == "FAIL" for r in ml2_rows)
        implied_pf = "FAIL" if any_ml2_fail else "PASS"

        # Pick the first real ML2 control detected (exclude ML2-RB-00 parsing fallback).
        primary_ml2 = next((r["test_id"] for r in ml2_rows if r.get("test_id") != "ML2-RB-00"), "ML2-RB-00")
        ml1_test_id, ml1_name = self._ML2_TO_ML1.get(primary_ml2, ("ML1-RB-00", "Evidence parsing"))

        rows: List[Dict] = []
        rows.append(
            _row(
                "ML1",
                ml1_test_id,
                ml1_name,
                implied_pf,
                "High",
                "ML1 result is implied by ML2 outcome for this evidence file.",
                t,
            )
        )
        rows.extend(ml2_rows)
        return rows


def get_strategy() -> Strategy:
    return RegularBackups()