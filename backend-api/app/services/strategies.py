from __future__ import annotations

import re
from typing import Dict, List, Tuple, Type, Sequence, ClassVar

from app.models.strategy import ScanResponse, Strategy


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def _default_note(notes: List[str]) -> str | None:
    return "; ".join(notes) if notes else None


def _build_report_name(strategy_name: str) -> str:
    return f"{_slugify(strategy_name)}-report.pdf"

# scanning context from the input provided 
def _extract_evidence_snippets(text: str) -> List[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    # return a couple of short snippets for context
    return lines[:2] if len(lines) >= 2 else lines


class BaseStrategyChecker:
    """Lightweight heuristic checker base class."""

    metadata: Strategy

    # Each subclass can override RULES to emit multiple findings.
    # Fields: test_id, sub_strategy, level, priority, recommendation, risk_keywords
    RULES: ClassVar[Sequence[Tuple[str, str, str, str, str, Tuple[str, ...]]]] = ()

    def __init__(self, metadata: Strategy):
        self.metadata = metadata

    def run_checks(
        self,
        extracted_text: str,
        filename: str | None = None,
        user_id: str | None = None,
        notes: List[str] | None = None,
    ) -> ScanResponse:
        note = _default_note(notes or [])

        if not extracted_text:
            return ScanResponse(ok=True, findings=[], reports=[], note=note or "No readable text extracted.")

        text_lower = extracted_text.lower()
        evidence_snippets = _extract_evidence_snippets(extracted_text)
        if not evidence_snippets:
            evidence_snippets = ["Readable text present, but no specific lines were captured."]

        findings: List[dict] = []
        for test_id, sub, level, priority, recommendation, risk_keywords in self.RULES:
            hit = any(k in text_lower for k in risk_keywords) if risk_keywords else False
            pass_fail = "FAIL" if hit else "PASS"
            finding = {
                "test_id": test_id,
                "sub_strategy": sub,
                "detected_level": level,
                "pass_fail": pass_fail,
                "priority": priority,
                "recommendation": recommendation,
                "evidence": evidence_snippets if hit else evidence_snippets[:1],
                "description": self._description(hit, filename, user_id, sub),
                "confidence": "0.82" if hit else "0.65",
            }
            findings.append(finding)

        response = {
            "ok": True,
            "findings": findings,
            "reports": [_build_report_name(self.metadata.name)],
        }
        if note:
            response["note"] = note

        return ScanResponse(**response)

    def _description(self, risk_detected: bool, filename: str | None, user_id: str | None, sub: str) -> str:
        base = f"File: {filename or 'unknown'} | Check: {sub}"
        if user_id:
            base += f" | User: {user_id}"
        base += " | Risk" if risk_detected else " | No high-risk indicators"
        return base


class CISMicrosoft365Checker(BaseStrategyChecker):
    name = "CIS Microsoft 365 Audit"
    RULES = (
        ("CIS-001", "Identity & Access", "High", "Critical", "Enable MFA for all admins; block legacy auth.", ("mfa disabled", "legacy auth", "basic auth", "no mfa")),
        ("CIS-002", "Data Protection", "Medium", "High", "Implement DLP and encryption for sensitive data.", ("no dlp", "dlp not", "unencrypted", "public link")),
        ("CIS-003", "Access Management", "Low", "Medium", "Review RBAC/least privilege and access reviews.", ("excessive permissions", "global admin", "no access review", "everyone")),
        ("CIS-004", "Audit Logging", "Medium", "Medium", "Extend audit log retention and enable mailbox auditing.", ("audit log", "90 days", "logging disabled", "audit disabled")),
        ("CIS-005", "Email Security", "High", "Critical", "Enable ATP/Defender, anti-phishing, and safe links/attachments.", ("atp not", "safe links off", "phishing", "spoof")),
    )


class NISTComplianceChecker(BaseStrategyChecker):
    name = "NIST Compliance Check"
    RULES = (
        ("NIST-IR", "Incident Response", "High", "High", "Document and test incident response playbooks.", ("no incident response", "missing ir", "untested ir")),
        ("NIST-PF", "Protect", "Medium", "Medium", "Improve access control and least privilege.", ("unauthorized access", "shared account", "no mfa")),
        ("NIST-DE", "Detect", "Medium", "Medium", "Enable monitoring and alerting for key assets.", ("no monitoring", "logging disabled", "no siem")),
        ("NIST-RS", "Recover", "Low", "Low", "Test backups and recovery procedures.", ("no backup", "restore failed", "untested backup")),
    )


class ISO27001Checker(BaseStrategyChecker):
    name = "ISO 27001 Assessment"
    RULES = (
        ("ISO-A.5", "Policies & ISMS", "High", "High", "Maintain current ISMS policies and governance.", ("no policy", "outdated policy", "isms missing")),
        ("ISO-A.8", "Asset Management", "Medium", "Medium", "Keep complete asset inventory and classification.", ("no asset inventory", "unknown assets", "shadow it")),
        ("ISO-A.9", "Access Control", "Medium", "High", "Tighten access control and review rights.", ("weak access control", "shared account", "no mfa")),
        ("ISO-A.12", "Operations Security", "Low", "Medium", "Harden ops: patching, malware protection, logging.", ("no patch", "malware", "logging disabled")),
    )


class SOC2ReadinessChecker(BaseStrategyChecker):
    name = "SOC 2 Readiness"
    RULES = (
        ("SOC2-CC", "Common Criteria", "High", "High", "Enforce access control and MFA across services.", ("no mfa", "shared account", "weak password")),
        ("SOC2-LOG", "Logging & Monitoring", "Medium", "Medium", "Enable centralized logging and alerting.", ("no logging", "missing monitoring", "log retention 7")),
        ("SOC2-AV", "Availability", "Medium", "Medium", "Document DR/BCP and test failover.", ("no dr", "no bcp", "no failover")),
        ("SOC2-CHG", "Change Management", "Low", "Low", "Enforce change reviews and approvals.", ("no change management", "no cab", "unauthorized change")),
    )


class GDPRComplianceChecker(BaseStrategyChecker):
    name = "GDPR Compliance Scan"
    RULES = (
        ("GDPR-ROPA", "Records of Processing", "Medium", "Medium", "Maintain ROPA and DPIA for high-risk processing.", ("no ropa", "no dpia", "missing dpia")),
        ("GDPR-DSR", "Data Subject Rights", "High", "High", "Implement SAR/erasure/rectification workflows.", ("subject access", "sar", "erasure", "no dsr")),
        ("GDPR-RET", "Retention", "Medium", "Medium", "Apply retention limits and deletion schedules.", ("retention violation", "keep forever", "no retention")),
        ("GDPR-DPA", "Processors", "High", "High", "Put DPAs in place with processors and sub-processors.", ("no dpa", "missing dpa", "processor")),
        ("GDPR-SEC", "Security", "Medium", "High", "Encrypt personal data and restrict access.", ("unencrypted personal data", "pii exposed", "open s3")),
    )


StrategyFactory = Dict[str, Tuple[Strategy, Type[BaseStrategyChecker]]]


def _define_strategies() -> StrategyFactory:
    return {
        "CIS Microsoft 365 Audit": (
            Strategy(
                name="CIS Microsoft 365 Audit",
                description="Comprehensive Microsoft 365 security assessment based on CIS benchmarks.",
                category="Cloud Security",
                severity="High",
                checker=f"{CISMicrosoft365Checker.__module__}.{CISMicrosoft365Checker.__name__}",
                evidence_types=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "txt", "docx", "log", "csv"],
            ),
            CISMicrosoft365Checker,
        ),
        "NIST Compliance Check": (
            Strategy(
                name="NIST Compliance Check",
                description="NIST Cybersecurity Framework control verification.",
                category="Framework Alignment",
                severity="Medium",
                checker=f"{NISTComplianceChecker.__module__}.{NISTComplianceChecker.__name__}",
                evidence_types=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "txt", "docx", "log", "csv"],
            ),
            NISTComplianceChecker,
        ),
        "ISO 27001 Assessment": (
            Strategy(
                name="ISO 27001 Assessment",
                description="ISO 27001 ISMS and Annex A control assessment.",
                category="Governance",
                severity="High",
                checker=f"{ISO27001Checker.__module__}.{ISO27001Checker.__name__}",
                evidence_types=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "txt", "docx", "log", "csv"],
            ),
            ISO27001Checker,
        ),
        "SOC 2 Readiness": (
            Strategy(
                name="SOC 2 Readiness",
                description="SOC 2 Type II gap analysis against Trust Services Criteria.",
                category="Assurance",
                severity="Medium",
                checker=f"{SOC2ReadinessChecker.__module__}.{SOC2ReadinessChecker.__name__}",
                evidence_types=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "txt", "docx", "log", "csv"],
            ),
            SOC2ReadinessChecker,
        ),
        "GDPR Compliance Scan": (
            Strategy(
                name="GDPR Compliance Scan",
                description="Assessment of privacy and data protection controls for GDPR readiness.",
                category="Privacy",
                severity="High",
                checker=f"{GDPRComplianceChecker.__module__}.{GDPRComplianceChecker.__name__}",
                evidence_types=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "txt", "docx", "log", "csv"],
            ),
            GDPRComplianceChecker,
        ),
    }


_REGISTRY: StrategyFactory = _define_strategies()


def list_strategies() -> List[Strategy]:
    return [meta for meta, _ in _REGISTRY.values()]


def get_checker(strategy_name: str) -> BaseStrategyChecker | None:
    entry = _REGISTRY.get(strategy_name)
    if not entry:
        return None
    meta, checker_cls = entry
    return checker_cls(meta)
