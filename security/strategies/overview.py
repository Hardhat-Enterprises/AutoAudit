from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Sequence
import re


class Strategy(ABC):
    """
    Base strategy every mitigation strategy will follow.
    """

    # Class metadata
    id: str = "GEN"          # short form e.g., AC, RAP
    name: str = "Generic"    # visible name in menus

    # Detection configuration (immutable by default; override in subclasses)
    keywords: Sequence[str] = ()
    regex_any: Sequence[str] = ()
    exclude: Sequence[str] = ()

    def normalize(self, text: Optional[str]) -> str:
        if text is None:
            return ""
        return " ".join(text.lower().split())

    # returns the first phrase as a substring in text
    def _any_substr(self, text: str, phrases: Sequence[str]) -> Optional[str]:
        for p in phrases:
            if p and p in text:
                return p
        return None

    # returns the first regex pattern that matches
    def _any_regex(self, text: str, patterns: Sequence[str]) -> Optional[str]:
        for pat in patterns:
            if pat and re.search(pat, text):
                return f"re:{pat}"
        return None

    @abstractmethod
    def description(self) -> str:
        # brief description of mitigation strategy — each child must implement
        return "No description"

    # detection logic
    def match(self, raw_text: str) -> List[str]:
        # normalise the OCR text
        t = self.normalize(raw_text)

        # check for any exclusions
        for ex in self.exclude:
            if ex in t:
                return []

        hits: List[str] = []

        # check for any keyword match
        for kw in self.keywords:
            if kw in t:
                hits.append(kw)

        # check for any regex match
        for pat in self.regex_any:
            if re.search(pat, t):
                hits.append(f"re:{pat}")

        # return the list of matches
        return hits

    # standardized report fields
    def emit_hits(self, raw_text: str) -> List[dict]:
        rows: List[dict] = []
        for s in self.match(raw_text):
            rows.append({
                "test_id": "",
                "sub_strategy": "",
                "detected_level": "",
                "pass_fail": "",
                "priority": "",
                "recommendation": "",
                "evidence": [s],
            })
        return rows
