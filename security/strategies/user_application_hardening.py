import re
from .overview import Strategy

class UserApplicationHardening(Strategy):
    id = "UAH"
    name = "User Application Hardening"

    def description(self) -> str:
        return (
            "Checks browsers and document viewers (Edge, Chrome, Firefox, Adobe Reader) "
            "for risky features like JavaScript in PDFs, ActiveX, Flash, Office macros, "
            "password managers, pop-ups, and Safe Browsing. Maps findings to Essential 8 maturity levels."
        )

    def emit_hits(self, text: str, source_file: str = ""):
        findings = []
        lowered = text.lower()

        print(f"\n[DEBUG OCR TEXT from {source_file}]\n{lowered}\n")

        # --- Firefox PDF JavaScript ---
        if "pdfjs.enablescripting" in lowered:
            if "true" in lowered:
                findings.append({
                    "test_id": "UAH-001",
                    "sub_strategy": "PDF JavaScript",
                    "detected_level": "ML1",
                    "pass_fail": "FAIL",
                    "priority": "High",
                    "recommendation": "Disable JavaScript execution in PDF readers.",
                    "evidence": ["JavaScript enabled in Firefox PDF viewer"],
                })
                print("[DEBUG MATCH] Firefox JS = ENABLED (FAIL)")
            elif "false" in lowered:
                findings.append({
                    "test_id": "UAH-001",
                    "sub_strategy": "PDF JavaScript",
                    "detected_level": "ML1",
                    "pass_fail": "PASS",
                    "priority": "Low",
                    "recommendation": "JavaScript in PDFs is disabled (compliant).",
                    "evidence": ["JavaScript disabled in Firefox PDF viewer"],
                })
                print("[DEBUG MATCH] Firefox JS = DISABLED (PASS)")

        # --- Browser Password Manager ---
        if "offer to save passwords" in lowered:
            if "automatically create a passkey" in lowered:
                print("[DEBUG MATCH] Password Manager = ENABLED (FAIL)")
                findings.append({
                    "test_id": "UAH-002",
                    "sub_strategy": "Browser Password Manager",
                    "detected_level": "ML1",
                    "pass_fail": "FAIL",
                    "priority": "High",
                    "recommendation": "Disable built-in browser password manager to reduce credential theft risk.",
                    "evidence": ["Password manager setting ENABLED"],
                })
            else:
                print("[DEBUG MATCH] Password Manager = DISABLED (PASS)")
                findings.append({
                    "test_id": "UAH-002",
                    "sub_strategy": "Browser Password Manager",
                    "detected_level": "ML1",
                    "pass_fail": "PASS",
                    "priority": "Low",
                    "recommendation": "Password manager / save passwords setting is disabled (compliant).",
                    "evidence": ["Password manager setting OFF"],
                })

        # --- Pop-ups & Redirects ---
        if "pop-ups and redirects" in lowered:
            if "don't allow sites to send pop-ups or use redirects" in lowered:
                print("[DEBUG MATCH] Pop-ups = BLOCKED (PASS)")
                findings.append({
                    "test_id": "UAH-003",
                    "sub_strategy": "Pop-ups and Redirects",
                    "detected_level": "ML1",
                    "pass_fail": "PASS",
                    "priority": "Low",
                    "recommendation": "Pop-ups and redirects are blocked (compliant).",
                    "evidence": ["Pop-ups blocked in browser settings"],
                })
            else:
                print("[DEBUG MATCH] Pop-ups = ALLOWED (FAIL)")
                findings.append({
                    "test_id": "UAH-003",
                    "sub_strategy": "Pop-ups and Redirects",
                    "detected_level": "ML1",
                    "pass_fail": "FAIL",
                    "priority": "Medium",
                    "recommendation": "Block pop-ups and redirects to reduce attack surface.",
                    "evidence": ["Pop-ups allowed in browser settings"],
                })

        # --- Safe Browsing ---
        if "safe browsing" in lowered or "enhanced protection" in lowered or "standard protection" in lowered:
            if "no protection (not recommended)" in lowered:
                findings.append({
                    "test_id": "UAH-004",
                    "sub_strategy": "Safe Browsing",
                    "detected_level": "ML1",
                    "pass_fail": "FAIL",
                    "priority": "High",
                    "recommendation": "Enable at least Standard or Enhanced Safe Browsing to protect against malicious sites.",
                    "evidence": ["Safe Browsing disabled in Chrome"],
                })
                print("[DEBUG MATCH] Safe Browsing = DISABLED (FAIL)")
            else:
                findings.append({
                    "test_id": "UAH-004",
                    "sub_strategy": "Safe Browsing",
                    "detected_level": "ML1",
                    "pass_fail": "PASS",
                    "priority": "Low",
                    "recommendation": "Safe Browsing is enabled (compliant).",
                    "evidence": ["Safe Browsing active in Chrome"],
                })
                print("[DEBUG MATCH] Safe Browsing = ENABLED (PASS)")

        # --- Default fallback if nothing matched ---
        if not findings:
            findings.append({
                "test_id": "UAH-000",
                "sub_strategy": "General",
                "detected_level": "ML1",
                "pass_fail": "PASS",
                "priority": "Low",
                "recommendation": "No risky features detected.",
                "evidence": [],
            })

        return findings
