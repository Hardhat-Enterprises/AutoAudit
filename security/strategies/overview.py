from abc import ABC, abstractmethod
import re

# base strategy code that every mitigation strategy will follow 
class Strategy(ABC):
    id = "GEN"           # short form for the strategy e.g. application code = AC, restrict admin privileges = RAP
    name = "Generic"     # visible strategy name in the menu i.e. what is visible to user 
    keywords = []        # detection criteria 
    regex_any = []       # regular expression patterns 
    exclude = []         # potential false positives

    def normalize(self, text: str) -> str:
        if text is None:
            return ""
        return " ".join(text.lower().split())

    # returns the first phrase as a substring in text 
    def _any_substr(self, text: str, phrases: list[str]) -> str | None:
        for p in phrases:
            if p and p in text:
                return p
        return None

    # returns the first regex pattern that matches 
    def _any_regex(self, text: str, patterns: list[str]) -> str | None:
        for pat in patterns:
            if pat and re.search(pat, text):
                return f"re:{pat}"
        return None

    @abstractmethod
    def description(self) -> str:
        return "No description" # brief description of mitigation strategy - every child class msut provide their own description

    # detection logic 
    def match(self, raw_text: str):
        # normalise the OCR text
        t = self.normalize(raw_text)

        # check for any exclusions 
        for ex in self.exclude:
            if ex in t:
                return []

        hits = []

        # check for any keyword match 
        for kw in self.keywords:
            if kw in t:
                hits.append(kw)

        # check for any regex match 
        for pat in self.regex_any:
            if re.search(pat, t):
                hits.append(f"re:{pat}")

        # return the list of matched 
        return hits

    # standardised report fields
    def emit_hits(self, raw_text: str):
        rows = []
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