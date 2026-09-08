"""The product surface must not claim capabilities the product does not have.

Every claim below was live in the shipped marketing copy and was checked against
the tree rather than against intent:

* **NIST and ISO 27001** were listed beside CIS as supported standards. No
  benchmark, policy corpus or collector exists for either. The only thing in the
  repository that names them is a pair of keyword checkers over an uploaded
  document in the unmaintained TPRM module, one rule each.
* **"real-time" and "continuous" monitoring**, and a **99.9% uptime**
  commitment. There is no scheduler anywhere in the product -- every scan is
  started by a person or an API call -- and no SLA behind the number.
* **a 14-day free trial** and **Premium/Enterprise support plans**. There is no
  billing system, no plan tier and no trial: nothing distinguishes one account's
  entitlements from another's.
* **export "in PDF, Excel, or CSV formats"**. The only report the product
  generates is a plain-text file per evidence scan, served as `text/plain` with
  a `.txt` name.
* **"cut audit preparation time by 80%"**, measured against nothing.

The class that was already clean and must stay clean: no SOC 2 certification or
attestation claim appears anywhere outside the phase documents. The SOC 2 report
endpoint's own `not_a_certification` line is the opposite of a claim and is
allowed by name.

This is a text gate, not a taste gate. It fails on a specific phrase in a
specific place, and the way to satisfy it is to build the thing or to stop
saying it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SURFACE = ROOT / "frontend" / "src"

# Only user-visible surface. Type definitions and tests describe the contract
# and are allowed to name what they forbid.
SKIP_SUFFIXES = (".test.tsx", ".test.ts", ".spec.tsx", ".spec.ts")
SKIP_FILES = {"types/soc2.ts"}


def _surface_files() -> list[Path]:
    found = [
        path
        for path in sorted(SURFACE.rglob("*"))
        if path.suffix in {".ts", ".tsx"}
        and not path.name.endswith(SKIP_SUFFIXES)
        and str(path.relative_to(SURFACE)) not in SKIP_FILES
    ]
    assert found, "no frontend source found; the glob above is wrong"
    return found


FORBIDDEN = {
    "unimplemented-standard": re.compile(r"\b(?:NIST Framework|ISO\s?27001)\b", re.I),
    "no-scheduler": re.compile(r"\breal[- ]time\b|\bcontinuous(?:ly)? monitor", re.I),
    "uptime-commitment": re.compile(r"\b99(?:\.\d+)?%\s*uptime\b", re.I),
    "no-trial-or-plan": re.compile(
        r"\bfree trial\b|\b\d+-day trial\b|\b(?:Premium|Enterprise) plans?\b", re.I
    ),
    "no-such-export": re.compile(
        r"\bin PDF, Excel,? (?:or|and) CSV\b|\bExcel,? (?:or|and) CSV formats\b", re.I
    ),
    "unmeasured-figure": re.compile(r"\bcut audit preparation time by \d+%", re.I),
    "certification-claim": re.compile(
        r"\bSOC\s?2\s+(?:certified|certification|attestation|audited)\b", re.I
    ),
}

# Two kinds of line may name a forbidden phrase: a sentence that denies the
# claim, and a comment, which no reader of the page ever sees. Commenting a
# claim out is a legitimate way to satisfy this gate; it stops being a claim.
ALLOWED_CONTEXT = re.compile(
    r"^\s*(?://|\*|/\*)"
    r"|does not claim SOC 2"
    r"|not_a_certification"
    r"|not a SOC 2"
    r"|do(?:es)? not establish",
    re.I,
)


@pytest.mark.parametrize(
    "path", _surface_files(), ids=lambda p: str(p.relative_to(ROOT))
)
def test_no_untrue_product_claim(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    problems: list[str] = []
    for label, pattern in FORBIDDEN.items():
        for match in pattern.finditer(content):
            line_number = content.count("\n", 0, match.start()) + 1
            line = content.splitlines()[line_number - 1]
            if ALLOWED_CONTEXT.search(line):
                continue
            problems.append(
                f"{path.relative_to(ROOT)}:{line_number} [{label}] {match.group(0)!r}"
            )
    assert not problems, (
        "The product surface claims something the product does not do. Build it "
        "or stop saying it; qualifying it in a comment does not help a reader of "
        "the page:\n  " + "\n  ".join(problems)
    )


def test_the_gate_would_catch_the_claims_it_was_written_for() -> None:
    """A text gate that matches nothing is worse than no gate."""
    samples = {
        "unimplemented-standard": "ISO 27001 compliance built in",
        "no-scheduler": "Continuous monitoring of your tenant",
        "uptime-commitment": "99.9% uptime, guaranteed",
        "no-trial-or-plan": "Start your 14-day free trial today",
        "no-such-export": "Export in PDF, Excel, or CSV formats",
        "unmeasured-figure": "cut audit preparation time by 80%",
        "certification-claim": "AutoAudit is SOC 2 certified",
    }
    for label, sample in samples.items():
        assert FORBIDDEN[label].search(sample), label


def test_the_denial_of_certification_is_not_treated_as_a_claim() -> None:
    line = (
        "AutoAudit does not claim SOC 2 certification or an independent "
        "security audit."
    )
    assert FORBIDDEN["certification-claim"].search(line)
    assert ALLOWED_CONTEXT.search(line)
