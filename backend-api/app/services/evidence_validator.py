"""Evidence validator

This module provides a lightweight validator pass that checks whether an uploaded
evidence artifact contains expected evidence signals for a given strategy.

"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List


# These terms are intentionally conservative and designed to evolve.
STRATEGY_REQUIRED_TERMS: dict[str, list[str]] = {
    "CIS Microsoft 365 Audit": [
        "mfa",
        "conditional access",
        "legacy authentication",
        "audit log",
        "admin",
        "defender",
    ],
    "NIST Compliance Check": [
        "incident response",
        "access control",
        "least privilege",
        "logging",
        "monitoring",
        "backup",
    ],
    "ISO 27001 Assessment": [
        "isms",
        "policy",
        "risk assessment",
        "asset inventory",
        "access control",
        "logging",
    ],
    "SOC 2 Readiness": [
        "access",
        "mfa",
        "logging",
        "monitoring",
        "change management",
        "incident",
    ],
    "GDPR Compliance Scan": [
        "personal data",
        "pii",
        "data retention",
        "encryption",
        "data subject",
        "consent",
    ],
}


def _normalize_text(text: str) -> str:
    """Normalize text for matching.

    - lowercases
    - normalizes whitespace
    - normalizes common dash characters
    """
    if not text:
        return ""
    out = text.lower()
    out = out.replace("\u2010", "-").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    out = re.sub(r"\s+", " ", out)
    return out.strip()


def _count_term(text: str, term: str) -> int:
    """Count occurrences of a term in normalized text (case-insensitive)."""
    if not text or not term:
        return 0

    # For simple word-ish terms, prefer word boundaries to reduce false positives.
    # For multi-word phrases or terms with spaces/symbols, fall back to escaped substring regex.
    term_norm = _normalize_text(term)
    if not term_norm:
        return 0

    is_simple_word = bool(re.fullmatch(r"[a-z0-9]+", term_norm))
    if is_simple_word:
        pattern = rf"\b{re.escape(term_norm)}\b"
    else:
        pattern = re.escape(term_norm)

    return len(re.findall(pattern, text, flags=re.IGNORECASE))


@dataclass(frozen=True)
class ValidatorSummary:
    matchedCount: int
    totalTerms: int


def validate_text(strategy_name: str, extracted_text: str) -> dict:
    """Validate extracted text for expected evidence signals.

    Returns validator_simple schema:
      {
        "matched": [{"term": str, "count": int}, ...],
        "missing": [str, ...],
        "summary": {"matchedCount": int, "totalTerms": int}
      }
    """
    terms = STRATEGY_REQUIRED_TERMS.get(strategy_name, [])
    normalized = _normalize_text(extracted_text)

    matched: List[Dict[str, int | str]] = []
    missing: List[str] = []

    for term in terms:
        count = _count_term(normalized, term)
        if count > 0:
            matched.append({"term": term, "count": count})
        else:
            missing.append(term)

    summary = ValidatorSummary(matchedCount=len(matched), totalTerms=len(terms))

    return {
        "matched": matched,
        "missing": missing,
        "summary": {"matchedCount": summary.matchedCount, "totalTerms": summary.totalTerms},
    }

