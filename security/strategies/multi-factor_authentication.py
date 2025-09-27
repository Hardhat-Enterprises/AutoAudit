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
                "evidence": f"[DEBUG OCR from {source_file}]\n{lowered}",
                "detected_level": 0
            })

        if any(p in lowered for p in admins_only):
            findings.append({
                "test_id": "MFA-101",
                "sub_strategy": "Scope",
                "severity": "medium",
                "description": "MFA is enforced for admins only.",
                "evidence": f"[DEBUG OCR from {source_file}]\n{lowered}",
                "detected_level": 1
            })

        if any(p in lowered for p in all_users) and any(p in lowered for p in weak_methods):
            findings.append({
                "test_id": "MFA-201",
                "sub_strategy": "All users (weak)",
                "severity": "low",
                "description": "MFA is enforced for all users, but weak methods are allowed (SMS, app passwords).",
                "evidence": f"[DEBUG OCR from {source_file}]\n{lowered}",
                "detected_level": 2
            })

        if any(p in lowered for p in all_users) and not any(p in lowered for p in weak_methods + legacy_auth) and any(p in lowered for p in strong_methods):
            findings.append({
                "test_id": "MFA-301",
                "sub_strategy": "Strong MFA",
                "severity": "info",
                "description": "MFA enforced for all users with strong methods and legacy auth blocked.",
                "evidence": f"[DEBUG OCR from {source_file}]\n{lowered}",
                "detected_level": 3
            })

        return findings
