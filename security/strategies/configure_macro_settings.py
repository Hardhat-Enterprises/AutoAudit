# strategies/configure_macro_settings.py
from __future__ import annotations
import re
from typing import List, Dict, Optional
from .overview import Strategy

class ConfigureMicrosoftOfficeMacroSettings(Strategy):
    """
    Essential Eight - Macro settings (ML1-OM-01 .. ML1-OM-07)
    Accepts:
      - OCR text from screenshots (Trust Center, MoTW banners, regedit)
      - Text exports: gpresult (/r), .reg/.txt dumps, AV logs
      - Simple lists for approved users and AD group (txt)
    """

    id = "CMOMS"
    name = "Configure Microsoft Office Macro Settings"

    def __init__(self) -> None:
        # for ML1-OM-02 comparison
        self._approved_users: Optional[set[str]] = None
        self._approved_src: Optional[str] = None
        self._adgroup_users: Optional[set[str]] = None
        self._adgroup_src: Optional[str] = None
        self._om02_emitted = False
        super().__init__()

    # ---- helpers ------------------------------------------------------------
    @staticmethod
    def _row(tid: str, sub: str, lvl: str, pf: str, prio: str, rec: str, ev: List[str]) -> Dict:
        return {
            "test_id": tid,
            "sub_strategy": sub,
            "detected_level": lvl,
            "pass_fail": pf,
            "priority": prio,
            "recommendation": rec,
            "evidence": ev,
        }

    @staticmethod
    def _has(text: str, *phrases: str) -> bool:
        tl = text.lower()
        return any(p.lower() in tl for p in phrases)

    @staticmethod
    def _regex(text: str, pattern: str) -> bool:
        return re.search(pattern, text, flags=re.I | re.S) is not None

    @staticmethod
    def _clip(text: str, n: int = 180) -> str:
        t = " ".join(text.split())
        return (t[:n] + "…") if len(t) > n else t

    @staticmethod
    def _extract_identities(text: str) -> set[str]:
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text, flags=re.I)
        sams = re.findall(r"\b[A-Za-z0-9][A-Za-z0-9._-]{1,}\b", text)
        stop = {"the", "and", "user", "users", "group", "approved", "domain", "members"}
        sams = [s for s in sams if s.lower() not in stop and len(s) >= 3]
        return set(map(str.lower, emails + sams))

    # ---- Strategy API -------------------------------------------------------
    def description(self) -> str:
        return "Checks if Office macro settings are configured securely."

    def emit_hits(self, text: str, source_file: str = "") -> List[Dict]:
        rows: List[Dict] = []
        t = text or ""
        ev = lambda s="": [self._clip(s)] if s else []

        # ===== ML1-OM-01: Disable for unapproved users =====
        if self._has(
            t,
            "disable all macros without notification",
            "vbawarnings=3",
            "no notifications and disable all macros",
        ) or self._regex(t, r"trust\s*center.+disable\s+all\s+macros\s+without\s+notification") \
          or self._regex(t, r"macro\s+settings.+disable\s+all\s+macros\s+without\s+notification"):
            rows.append(self._row(
                "ML1-OM-01", "Disable for unapproved users", "ML1", "PASS", "High",
                "Enforce 'Disable all macros without notification' via GPO.",
                ev(t),
            ))
        elif self._has(t, "disable with notification"):
            rows.append(self._row(
                "ML1-OM-01", "Disable for unapproved users", "ML1", "FAIL", "High",
                "Change to 'Disable all macros without notification' (not 'with notification').",
                ev(t),
            ))

        # RSOP/GPO text proving enforcement
        if self._regex(t, r"(gpresult|rsop|group policy).+(trust\s*center|macro).+(disable\s+all\s+macros)"):
            rows.append(self._row(
                "ML1-OM-01", "GPO shows macro disabling", "ML1", "PASS", "High",
                "RSOP/Group Policy confirms macro disabling policy is applied.",
                ev(t),
            ))

        # ===== ML1-OM-02: Approved list matches AD group =====
        fname = (source_file or "").lower()

        def is_approved_side() -> bool:
            return ("approved" in fname) or self._has(t, "approved users", "allow list")

        def is_adgroup_side() -> bool:
            return ("ad_group" in fname or "ad-group" in fname or "adgroup" in fname) or \
                   self._has(t, "group members", "security group", "ad group")

        identities = self._extract_identities(t)
        if identities:
            if is_approved_side():
                self._approved_users, self._approved_src = identities, (source_file or "approved_users.txt")
            elif is_adgroup_side():
                self._adgroup_users, self._adgroup_src = identities, (source_file or "ad_group.txt")

        if (not self._om02_emitted) and (self._approved_users is not None) and (self._adgroup_users is not None):
            missing_in_ad = sorted(self._approved_users - self._adgroup_users)
            extra_in_ad   = sorted(self._adgroup_users - self._approved_users)
            if not missing_in_ad and not extra_in_ad:
                rows.append(self._row(
                    "ML1-OM-02", "Approved users list matches AD group", "ML1", "PASS", "Medium",
                    "Approved repository and AD security group are in sync.",
                    [f"{self._approved_src} + {self._adgroup_src}"],
                ))
            else:
                rows.append(self._row(
                    "ML1-OM-02", "Approved users list matches AD group", "ML1", "FAIL", "Medium",
                    "Align AD group with the documented approved list.",
                    [
                        f"MissingInAD={missing_in_ad or 'None'}",
                        f"ExtraInAD={extra_in_ad or 'None'}",
                        f"SRC={self._approved_src} + {self._adgroup_src}",
                    ],
                ))
            self._om02_emitted = True

        # ===== ML1-OM-03: MoTW/internet macros blocked =====
        if self._has(
            t,
            "blocked macros from running because the source is untrusted",
            "blocked macros from running because the file is from the internet",
            "security risk – microsoft has blocked macros",
            "from the internet",
        ):
            rows.append(self._row(
                "ML1-OM-03", "Internet-sourced (MoTW) macros blocked", "ML1", "PASS", "High",
                "Files with Mark-of-the-Web cannot run macros.",
                ev(t),
            ))

        # ===== ML1-OM-04: Registry/GPO: blockcontentexecutionfromInternet=1 =====
        if self._regex(t, r"blockcontentexecutionfrominternet\s*=\s*1") or \
           self._regex(t, r"HKEY_(CURRENT_USER|LOCAL_MACHINE).+\\office\\\d+\.\d+\\(word|excel|powerpoint)\\security\\blockcontentexecutionfrominternet"):
            rows.append(self._row(
                "ML1-OM-04", "Block macros from Internet via GPO/Registry", "ML1", "PASS", "High",
                "Policy shows blockcontentexecutionfromInternet=1 for Office apps.",
                ev(t),
            ))

        # ===== ML1-OM-05: Macro Runtime Scan Scope enabled =====
        if self._regex(t, r"macroruntimescope\s*=\s*(1|2)") or self._has(t, "macro runtime scan scope"):
            rows.append(self._row(
                "ML1-OM-05", "Macro runtime scanning enabled", "ML1", "PASS", "High",
                "Macro Runtime Scan Scope is enabled across Office apps.",
                ev(t),
            ))

        # ===== ML1-OM-06: AV detects EICAR =====
        if self._has(t, "eicar") and self._has(t, "detect", "quarantine", "blocked", "removed"):
            rows.append(self._row(
                "ML1-OM-06", "AV detects macro threat (EICAR)", "ML1", "PASS", "High",
                "AV/EDR log indicates EICAR from macro execution was blocked/quarantined.",
                ev(t),
            ))

        # ===== ML1-OM-07: Users cannot change macro settings =====
        if self._has(
            t,
            "managed by your organization",
            "some settings are managed by your organization",
            "some settings are managed by your administrator",
            "this setting has been disabled by your administrator",
        ):
            rows.append(self._row(
                "ML1-OM-07", "Prevent user changes", "ML1", "PASS", "Medium",
                "Trust Center shows settings are locked by policy.",
                ev(t),
            ))

        # If nothing matched, emit a concise fail so the UI shows a row instead of "no findings"
        if not rows:
            rows.append(self._row(
                "ML1-OM-00",
                "Macro evidence missing",
                "ML1",
                "FAIL",
                "Medium",
                "Provide a screenshot or text from Office Trust Center / GPO showing macro settings (e.g., 'Disable all macros without notification', blockcontentexecutionfromInternet=1).",
                ev(t[:400] or "No readable text extracted"),
            ))
            rows[-1]["details"] = {
                "observed": self._clip(t or "No macro-related content detected."),
                "expected": "Evidence that macros are disabled/blocked via Trust Center or GPO (e.g., 'Disable all macros without notification', blockcontentexecutionfromInternet=1).",
            }

        # Add observed/expected for existing rows when helpful
        for r in rows:
            if "details" not in r:
                r["details"] = {
                    "observed": self._clip(" ".join(r.get("evidence", []))) if r.get("evidence") else self._clip(t),
                    "expected": r.get("recommendation", ""),
                }

        return rows
