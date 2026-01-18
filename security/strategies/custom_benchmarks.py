from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple
import re

from .overview import Strategy


# ---------------- helpers ----------------

def _clean_line(text: str) -> str:
    line = text.strip().lstrip("#*")
    line = re.sub(r"\s*\.\s*", ".", line)
    line = re.sub(r"\s*=\s*", "=", line)
    line = re.sub(r"\s+", " ", line)
    return line


def _extract_evidence_snippets(text: str, max_lines: int = 2) -> List[str]:
    lines = [_clean_line(ln) for ln in text.splitlines() if ln.strip()]
    return lines[:max_lines] if lines else []


# ---------------- metadata ----------------

@dataclass
class StrategyMeta:
    name: str
    description: str
    category: str = ""
    severity: str = ""
    evidence_types: Sequence[str] | None = None


# ---------------- base checker ----------------

class BaseStrategyChecker:
    """
    Lightweight keyword-based checker.
    RULES:
      (test_id, sub_strategy, level, priority, recommendation, keywords)
    """

    RULES: Sequence[Tuple[str, str, str, str, str, Sequence[str]]] = ()

    def __init__(self, metadata: StrategyMeta):
        self.metadata = metadata

    def run_checks(self, text: str, filename: str | None = None, user_id: str | None = None):
        if not text:
            return []

        text_l = text.lower()
        evidence = _extract_evidence_snippets(text) or ["Readable text present"]

        findings = []
        for test_id, sub, level, priority, rec, keywords in self.RULES:
            hit = any(k in text_l for k in keywords)
            findings.append({
                "test_id": test_id,
                "sub_strategy": sub,
                "detected_level": level,
                "pass_fail": "FAIL" if hit else "PASS",
                "priority": priority,
                "recommendation": rec,
                "evidence": evidence,
            })

        return findings


# ---------------- concrete checkers ----------------

class CISMicrosoft365Checker(BaseStrategyChecker):
    RULES = (
        ("CIS-001", "Identity & Access", "High", "Critical",
         "Enable MFA and disable legacy authentication.",
         ("no mfa", "legacy auth", "basic auth")),
    )


class NISTComplianceChecker(BaseStrategyChecker):
    RULES = (
        ("NIST-IR", "Incident Response", "High", "High",
         "Document and test incident response procedures.",
         ("no incident response", "untested ir")),
    )


class ISO27001Checker(BaseStrategyChecker):
    RULES = (
        ("ISO-A.9", "Access Control", "Medium", "High",
         "Apply least privilege and access reviews.",
         ("shared account", "no mfa")),
    )


class SOC2ReadinessChecker(BaseStrategyChecker):
    RULES = (
        ("SOC2-AV", "Availability", "Medium", "Medium",
         "Test backups and disaster recovery.",
         ("no backup", "restore failed")),
    )


class GDPRComplianceChecker(BaseStrategyChecker):
    RULES = (
        ("GDPR-SEC", "Security", "Medium", "High",
         "Encrypt personal data and restrict access.",
         ("unencrypted", "pii exposed")),
    )


# ---------------- Strategy adapter ----------------

class CheckerStrategy(Strategy):
    def __init__(self, meta: StrategyMeta, checker_cls):
        self.meta = meta
        self.checker_cls = checker_cls
        self.name = meta.name
        self.id = "BM"

    def description(self) -> str:
        return self.meta.description

    def emit_hits(self, raw_text: str, source_file: str | None = None, user_id: str | None = None, **_):
        checker = self.checker_cls(self.meta)
        return checker.run_checks(raw_text, source_file, user_id)


# ---------------- registry ----------------

STRATEGY_DEFS = [
    {
        "name": "CIS Microsoft 365 Audit",
        "description": "CIS benchmark checks for Microsoft 365.",
        "category": "Cloud Security",
        "severity": "High",
        "checker": CISMicrosoft365Checker,
    },
    {
        "name": "NIST Compliance Check",
        "description": "NIST Cybersecurity Framework validation.",
        "category": "Framework",
        "severity": "Medium",
        "checker": NISTComplianceChecker,
    },
    {
        "name": "ISO 27001 Assessment",
        "description": "ISO 27001 ISMS and Annex A review.",
        "category": "Governance",
        "severity": "High",
        "checker": ISO27001Checker,
    },
    {
        "name": "SOC 2 Readiness",
        "description": "SOC 2 Type II readiness scan.",
        "category": "Assurance",
        "severity": "Medium",
        "checker": SOC2ReadinessChecker,
    },
    {
        "name": "GDPR Compliance Scan",
        "description": "GDPR privacy and security checks.",
        "category": "Privacy",
        "severity": "High",
        "checker": GDPRComplianceChecker,
    },
]


# ---------------- public API ----------------

def get_strategy():
    """Return benchmark strategies as Strategy objects."""
    strategies = []
    for entry in STRATEGY_DEFS:
        meta = StrategyMeta(
            name=entry["name"],
            description=entry["description"],
            category=entry.get("category", ""),
            severity=entry.get("severity", ""),
        )
        strategies.append(CheckerStrategy(meta, entry["checker"]))
    return strategies