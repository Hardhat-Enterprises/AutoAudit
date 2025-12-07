import re
from .overview import Strategy

class MultiFactorAuthentication(Strategy):
    id = "MFA"
    name = "Multi-Factor Authentication"

    def description(self) -> str:
        return (
            "Checks if MFA is enabled and enforced for users and admins. "
            "Maps findings against Essential Eight maturity levels (ML0–ML3)."
        )

    def emit_hits(self, text: str, source_file: str = "") -> list[dict]:
        findings = []
        lowered = text.lower()

        # Keep evidence excerpts short for UI readability
        def _excerpt(t: str, max_chars: int = 400, max_lines: int = 6, keywords=None) -> str:
            lines = t.splitlines()
            if keywords:
                kw_lines = [ln for ln in lines if any(k in ln for k in keywords)]
                if kw_lines:
                    lines = kw_lines
            if len(lines) > max_lines:
                lines = lines[:max_lines]
            clip = "\n".join(lines)
            if len(clip) > max_chars:
                clip = clip[: max_chars - 3] + "..."
            return clip

        # --- Indicators ---
        disabled = ["mfa disabled", "not configured", "disabled for all users"]
        admins_only = ["mfa required for admins", "privileged roles only"]
        all_users = ["mfa required for all users", "enforced for all accounts"]
        weak_methods = ["sms only", "phone call only", "app passwords allowed"]
        legacy_auth = [
            "basic auth enabled", "legacy authentication enabled",
            "imap: enabled", "pop: enabled", "smtp auth: enabled"
        ]
        strong_methods = [
            "fido2", "passkey", "windows hello",
            "number matching: enabled", "authenticator app"
        ]

        # --- Rules by maturity ---
        if any(p in lowered for p in disabled + legacy_auth):
            findings.append({
                "test_id": "MFA-001",
                "sub_strategy": "MFA status",
                "severity": "high",
                "description": "MFA appears disabled or legacy authentication is allowed.",
                "evidence": _excerpt(f"[OCR from {source_file}]\n{lowered}", keywords=disabled + legacy_auth),
                "detected_level": 0
            })

        if any(p in lowered for p in admins_only):
            findings.append({
                "test_id": "MFA-101",
                "sub_strategy": "Scope",
                "severity": "medium",
                "description": "MFA is enforced for admins only.",
                "evidence": _excerpt(f"[OCR from {source_file}]\n{lowered}", keywords=admins_only),
                "detected_level": 1
            })

        if any(p in lowered for p in all_users) and any(p in lowered for p in weak_methods):
            findings.append({
                "test_id": "MFA-201",
                "sub_strategy": "All users (weak)",
                "severity": "low",
                "description": "MFA is enforced for all users, but weak methods are allowed (SMS, app passwords).",
                "evidence": _excerpt(f"[OCR from {source_file}]\n{lowered}", keywords=all_users + weak_methods),
                "detected_level": 2
            })

        if any(p in lowered for p in all_users) and not any(p in lowered for p in weak_methods + legacy_auth) and any(p in lowered for p in strong_methods):
            findings.append({
                "test_id": "MFA-301",
                "sub_strategy": "Strong MFA",
                "severity": "info",
                "description": "MFA enforced for all users with strong methods and legacy auth blocked.",
                "evidence": _excerpt(f"[OCR from {source_file}]\n{lowered}", keywords=all_users + strong_methods),
                "detected_level": 3
            })

        return findings
