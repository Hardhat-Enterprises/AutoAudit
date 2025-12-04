from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple
import re

from .overview import Strategy


def _clean_line(text: str) -> str:
    line = text.strip().lstrip("#*")
    line = re.sub(r"\s*\.\s*", ".", line)
    line = re.sub(r"\s*=\s*", "=", line)
    line = re.sub(r"\s+", " ", line)
    return line


def _extract_evidence_snippets(text: str, max_lines: int = 2) -> List[str]:
    lines = [_clean_line(ln) for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    return lines[:max_lines]


@dataclass
class StrategyMeta:
    name: str
    description: str
    category: str = ""
    severity: str = ""
    evidence_types: Sequence[str] | None = None


class BaseStrategyChecker:
    """Lightweight heuristic checker base class using keyword rules."""

    # RULES: (test_id, sub_strategy, level, priority, recommendation, risk_keywords)
    RULES: Sequence[Tuple[str, str, str, str, str, Sequence[str]]] = ()

    def __init__(self, metadata: StrategyMeta):
        self.metadata = metadata

    def run_checks(
        self,
        extracted_text: str,
        filename: str | None = None,
        user_id: str | None = None,
    ) -> List[dict]:
        if not extracted_text:
            return []

        text_lower = extracted_text.lower()
        evidence_snippets = _extract_evidence_snippets(extracted_text)
        if not evidence_snippets:
            evidence_snippets = ["Readable text present, but no specific lines were captured."]

        findings: List[dict] = []
        for test_id, sub, level, priority, recommendation, risk_keywords in self.RULES:
            hit = any(k in text_lower for k in risk_keywords) if risk_keywords else False
            pass_fail = "FAIL" if hit else "PASS"
            findings.append({
                "test_id": test_id,
                "sub_strategy": sub,
                "detected_level": level,
                "pass_fail": pass_fail,
                "priority": priority,
                "recommendation": recommendation,
                "evidence": evidence_snippets,
                "description": self._description(hit, filename, user_id, sub),
                "confidence": "0.82" if hit else "0.65",
            })

        return findings

    def _description(self, risk_detected: bool, filename: str | None, user_id: str | None, sub: str) -> str:
        base = f"File: {filename or 'unknown'} | Check: {sub}"
        if user_id:
            base += f" | User: {user_id}"
        base += " | Risk" if risk_detected else " | No high-risk indicators"
        return base


class CISMicrosoft365Checker(BaseStrategyChecker):
    RULES = (
        ("CIS-001", "Identity & Access", "High", "Critical", "Enable MFA for all admins; block legacy auth.", ("mfa disabled", "legacy auth", "basic auth", "no mfa")),
        ("CIS-002", "Data Protection", "Medium", "High", "Implement DLP and encryption for sensitive data.", ("no dlp", "dlp not", "unencrypted", "public link")),
        ("CIS-003", "Access Management", "Low", "Medium", "Review RBAC/least privilege and access reviews.", ("excessive permissions", "global admin", "no access review", "everyone")),
        ("CIS-004", "Audit Logging", "Medium", "Medium", "Extend audit log retention and enable mailbox auditing.", ("audit log", "90 days", "logging disabled", "audit disabled")),
        ("CIS-005", "Email Security", "High", "Critical", "Enable ATP/Defender, anti-phishing, and safe links/attachments.", ("atp not", "safe links off", "phishing", "spoof")),
    )


class NISTComplianceChecker(BaseStrategyChecker):
    RULES = (
        ("NIST-IR", "Incident Response", "High", "High", "Document and test incident response playbooks.", ("no incident response", "missing ir", "untested ir")),
        ("NIST-PF", "Protect", "Medium", "Medium", "Improve access control and least privilege.", ("unauthorized access", "shared account", "no mfa")),
        ("NIST-DE", "Detect", "Medium", "Medium", "Enable monitoring and alerting for key assets.", ("no monitoring", "logging disabled", "no siem")),
        ("NIST-RS", "Recover", "Low", "Low", "Test backups and recovery procedures.", ("no backup", "restore failed", "untested backup")),
    )


class ISO27001Checker(BaseStrategyChecker):
    RULES = (
        ("ISO-A.5", "Policies & ISMS", "High", "High", "Maintain current ISMS policies and governance.", ("no policy", "outdated policy", "isms missing")),
        ("ISO-A.8", "Asset Management", "Medium", "Medium", "Keep complete asset inventory and classification.", ("no asset inventory", "unknown assets", "shadow it")),
        ("ISO-A.9", "Access Control", "Medium", "High", "Tighten access control and review rights.", ("weak access control", "shared account", "no mfa")),
        ("ISO-A.12", "Operations Security", "Low", "Medium", "Harden ops: patching, malware protection, logging.", ("no patch", "malware", "logging disabled")),
    )


class SOC2ReadinessChecker(BaseStrategyChecker):
    RULES = (
        ("SOC2-CC", "Common Criteria", "High", "High", "Enforce access control and MFA across services.", ("no mfa", "shared account", "weak password")),
        ("SOC2-LOG", "Logging & Monitoring", "Medium", "Medium", "Enable centralized logging and alerting.", ("no logging", "missing monitoring", "log retention 7")),
        ("SOC2-AV", "Availability", "Medium", "Medium", "Document DR/BCP and test failover.", ("no dr", "no bcp", "no failover")),
        ("SOC2-CHG", "Change Management", "Low", "Low", "Enforce change reviews and approvals.", ("no change management", "no cab", "unauthorized change")),
    )


class GDPRComplianceChecker(BaseStrategyChecker):
    RULES = (
        ("GDPR-ROPA", "Records of Processing", "Medium", "Medium", "Maintain ROPA and DPIA for high-risk processing.", ("no ropa", "no dpia", "missing dpia")),
        ("GDPR-DSR", "Data Subject Rights", "High", "High", "Implement SAR/erasure/rectification workflows.", ("subject access", "sar", "erasure", "no dsr")),
        ("GDPR-RET", "Retention", "Medium", "Medium", "Apply retention limits and deletion schedules.", ("retention violation", "keep forever", "no retention")),
        ("GDPR-DPA", "Processors", "High", "High", "Put DPAs in place with processors and sub-processors.", ("no dpa", "missing dpa", "processor")),
        ("GDPR-SEC", "Security", "Medium", "High", "Encrypt personal data and restrict access.", ("unencrypted personal data", "pii exposed", "open s3")),
    )


class CheckerStrategy(Strategy):
    """Adapter to make checkers look like Strategy objects expected by the scanner/UI."""

    def __init__(self, metadata: StrategyMeta, checker_cls: type[BaseStrategyChecker]):
        self.meta = metadata
        self.checker_cls = checker_cls
        self.name = metadata.name
        self.id = "BM"

    def description(self) -> str:
        return self.meta.description

    def emit_hits(self, raw_text: str, source_file: str | None = None, user_id: str | None = None, **kwargs):
        checker = self.checker_cls(self.meta)
        return checker.run_checks(raw_text, filename=source_file, user_id=user_id)


# Registry of strategy definitions
STRATEGY_DEFS = [
    {
        "name": "CIS Microsoft 365 Audit",
        "description": "Comprehensive Microsoft 365 security assessment based on CIS benchmarks",
        "category": "Cloud Security",
        "severity": "High",
        "evidence_types": ["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "txt", "docx", "log", "csv"],
        "checker": CISMicrosoft365Checker,
    },
    {
        "name": "NIST Compliance Check",
        "description": "NIST Cybersecurity Framework control verification.",
        "category": "Framework Alignment",
        "severity": "Medium",
        "evidence_types": ["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "txt", "docx", "log", "csv"],
        "checker": NISTComplianceChecker,
    },
    {
        "name": "ISO 27001 Assessment",
        "description": "ISO 27001 ISMS and Annex A control assessment.",
        "category": "Governance",
        "severity": "High",
        "evidence_types": ["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "txt", "docx", "log", "csv"],
        "checker": ISO27001Checker,
    },
    {
        "name": "SOC 2 Readiness",
        "description": "SOC 2 Type II gap analysis against Trust Services Criteria.",
        "category": "Assurance",
        "severity": "Medium",
        "evidence_types": ["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "txt", "docx", "log", "csv"],
        "checker": SOC2ReadinessChecker,
    },
    {
        "name": "GDPR Compliance Scan",
        "description": "Assessment of privacy and data protection controls for GDPR readiness.",
        "category": "Privacy",
        "severity": "High",
        "evidence_types": ["pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "txt", "docx", "log", "csv"],
        "checker": GDPRComplianceChecker,
    },
]


def get_strategy():
    """Return Strategy objects consumed by the scanner / UI."""
    strategies: list[Strategy] = []
    for entry in STRATEGY_DEFS:
        meta = StrategyMeta(
            name=entry["name"],
            description=entry["description"],
            category=entry.get("category", ""),
            severity=entry.get("severity", ""),
            evidence_types=entry.get("evidence_types", ()),
        )
        strategies.append(CheckerStrategy(meta, entry["checker"]))
    return strategies
