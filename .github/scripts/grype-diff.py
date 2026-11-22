#!/usr/bin/env python3
"""Grype whitelist gate: evaluate one Grype JSON report against the explicit
whitelist (grype-whitelist.yaml) and gate CI on the result.

Single-scan model (proof of concept): the gate looks at every HIGH/CRITICAL
finding on the scanned tree. Findings covered by the effective whitelist are
suppressed; the rest are classified WARN or FAIL. There is no merge-base scan
and no diffing of two reports — the whitelist IS the baseline.

Usage (gate mode, used by .github/workflows/ci.grype-whitelist.yml):

    grype-diff.py --current grype-report.json \\
                  [--whitelist-pr grype-whitelist.yaml] [--whitelist-main PATH] \\
                  [--report-out PATH] [--json-out PATH] \\
                  [--sarif-full PATH] [--sarif-gate PATH] [--max-rows N]

    Environment:
        FAIL_ON             CRITICAL | HIGH_FIXED | HIGH   (default: HIGH_FIXED)
        IGNORE_WHITELISTED  true | false                    (default: true)
            true  -> whitelisted findings are skipped entirely
            false -> whitelisted findings are gated like any other (audit mode;
                     rows are tagged "whitelisted" so the output stays readable)

    Gate policy — the single place to change it is gate_decision():
        CRITICAL severity          -> FAIL in every mode
        HIGH, FAIL_ON=HIGH         -> FAIL (fixed or not)
        HIGH, FAIL_ON=HIGH_FIXED   -> FAIL when a fix is available, WARN otherwise
        HIGH, FAIL_ON=CRITICAL     -> WARN
        below HIGH                 -> out of gate scope entirely

    Effective whitelist = main(merge-base) entries UNION PR entries, keyed on
    (vulnerability, package). See the header of grype-whitelist.yaml for the
    resolution rules (inherit / add / modify / delete-ignored ratchet).

    Outputs:
        stdout verdict line; a markdown report containing ONLY the WARN/FAIL
        table rows (also appended to $GITHUB_STEP_SUMMARY when set); a JSON
        version of the same; full and gate-filtered SARIF files.

        DECISION (recorded in the workflow too): the GitHub Security tab
        receives the FULL SARIF so it mirrors the complete scan, while the
        artifacts carry the full report plus the gate-only report for
        reviewers. To flip the Security tab to gate-filtered results, point
        the workflow's upload-sarif step at the --sarif-gate output instead
        of the --sarif-full output.

    Exit codes:
        0   pass (warnings allowed)
        1   blocking findings per FAIL_ON
        2   data/config error — fail closed: an unreadable report or malformed
            whitelist must never be interpretable as "clean"

Usage (bootstrap mode — run once, locally, on a clean checkout of main):

    grype-diff.py --current grype-report.json --bootstrap \\
                  --bootstrap-out grype-whitelist.yaml

    Drafts one entry per current HIGH/CRITICAL finding with reason left as
    TODO. Each acceptance must then be justified (or removed) by a human
    before the whitelist is merged. Bootstrap does not gate and always exits
    0 on a readable report.

KNOWN LIMITATIONS (parked by decision — do not "fix" silently):
    - severity escalation: a whitelisted id that later scores a HIGHER
      severity than the one recorded in its entry stays suppressed
    - UNKNOWN-ID findings (no CVE/GHSA alias) cannot be whitelisted by id and
      will always gate
    - no `expires` leases and no stale-entry hygiene job yet
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any

try:
    import yaml
except ImportError:  # explicit, loud failure — no silent fallback
    sys.stderr.write(
        "grype-diff: error: PyYAML is required (python3 -m pip install pyyaml)\n"
    )
    sys.exit(2)

SEVERITIES = ("UNKNOWN", "NEGLIGIBLE", "LOW", "MEDIUM", "HIGH", "CRITICAL")
SEVERITY_RANK = {name: rank for rank, name in enumerate(SEVERITIES)}
GATE_SEVERITIES = {"HIGH", "CRITICAL"}
FAIL_ON_MODES = ("CRITICAL", "HIGH_FIXED", "HIGH")
ENTRY_FIELDS = ("vulnerability", "package", "severity", "reason")
WHITELIST_SCHEMA_VERSION = 1

EXIT_PASS, EXIT_BLOCKED, EXIT_ERROR = 0, 1, 2


# --------------------------------------------------------------------------
# small utilities
# --------------------------------------------------------------------------


def die(messages: list[str] | str) -> None:
    """Exit 2 (fail closed) with one or more error messages."""
    if isinstance(messages, str):
        messages = [messages]
    for message in messages:
        print(f"grype-diff: error: {message}", file=sys.stderr)
    sys.exit(EXIT_ERROR)


def normalise_severity(raw: Any) -> str:
    """Map a Grype severity string onto the canonical enum; unknown -> UNKNOWN."""
    text = str(raw or "").strip().upper()
    return text if text in SEVERITIES else "UNKNOWN"


def parse_bool_env(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().lower()
    if value in ("true", "1", "yes"):
        return True
    if value in ("false", "0", "no"):
        return False
    die(f"{name}={raw!r} is not a boolean (true/false/1/0/yes/no)")
    raise AssertionError("unreachable")


def parse_fail_on() -> str:
    raw = os.environ.get("FAIL_ON", "").strip().upper()
    if not raw:
        return "HIGH_FIXED"
    if raw not in FAIL_ON_MODES:
        die(f"FAIL_ON={raw!r} is not one of {', '.join(FAIL_ON_MODES)}")
    return raw


# --------------------------------------------------------------------------
# whitelist
# --------------------------------------------------------------------------


@dataclass
class Entry:
    vulnerability: str
    package: str | None
    severity: str
    reason: str | None
    origin: str = "pr"  # "main" | "pr"
    status: str = "added"  # "inherited" | "added" | "modified"

    def key(self) -> tuple[str, str | None]:
        return (self.vulnerability, self.package)


@dataclass
class WhitelistResolution:
    entries: list[Entry] = field(default_factory=list)
    inherited: int = 0
    added: int = 0
    modified: int = 0
    deletions_ignored: list[tuple[str, str | None]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def empty_whitelist_text() -> str:
    return f"schema_version: {WHITELIST_SCHEMA_VERSION}\nentries: []\n"


def load_whitelist(path: str | None, origin: str, notes: list[str]) -> list[Entry]:
    """Load and strictly validate one whitelist file; exit 2 on malformed input."""
    if not path or not os.path.exists(path):
        if origin == "main":
            notes.append(
                "no main whitelist found (empty baseline; expected on first run)"
            )
        else:
            notes.append(
                "grype-whitelist.yaml missing from the PR branch — main entries still "
                "apply, but merging this deletes the register (gate on main will fail hard)"
            )
        return []

    with open(path, "r", encoding="utf-8") as handle:
        try:
            doc = yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            die(f"whitelist ({origin}, {path}) is not valid YAML: {exc}")

    if not isinstance(doc, dict):
        die(f"whitelist ({origin}, {path}) must be a YAML mapping")
    unknown_top = sorted(set(doc) - {"schema_version", "entries"})
    if unknown_top:
        die(
            f"whitelist ({origin}, {path}) has unknown top-level keys: {', '.join(unknown_top)}"
        )
    if doc.get("schema_version") != WHITELIST_SCHEMA_VERSION:
        die(
            f"whitelist ({origin}, {path}) schema_version must be "
            f"{WHITELIST_SCHEMA_VERSION}, got {doc.get('schema_version')!r}"
        )
    entries = doc.get("entries")
    if not isinstance(entries, list):
        die(f"whitelist ({origin}, {path}) 'entries' must be a list")

    parsed: list[Entry] = []
    seen_keys: dict[tuple[str, str | None], int] = {}
    problems: list[str] = []
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            problems.append(f"entry #{index} ({origin}) must be a mapping")
            continue
        unknown = sorted(set(raw) - set(ENTRY_FIELDS))
        if unknown:
            problems.append(
                f"entry #{index} ({origin}) has unknown keys: {', '.join(unknown)}"
            )
            continue

        vulnerability = raw.get("vulnerability")
        if not isinstance(vulnerability, str) or not vulnerability.strip():
            problems.append(
                f"entry #{index} ({origin}): 'vulnerability' must be a non-empty string"
            )
            continue

        package = raw.get("package")
        if package is not None and (
            not isinstance(package, str) or not package.strip()
        ):
            problems.append(
                f"entry #{index} ({origin}): 'package' must be a non-empty string or omitted"
            )
            continue

        raw_severity = str(raw.get("severity") or "").strip().upper()
        if raw_severity not in SEVERITIES:
            problems.append(
                f"entry #{index} ({origin}): 'severity' must be one of {', '.join(SEVERITIES)}"
            )
            continue
        severity = raw_severity

        reason = raw.get("reason")
        if reason is not None and not isinstance(reason, str):
            problems.append(f"entry #{index} ({origin}): 'reason' must be a string")
            continue
        if not (reason or "").strip():
            # Business rule, not CI enforcement (see grype-whitelist.yaml header).
            notes.append(
                f"whitelist entry {vulnerability}"
                + (f" (package {package})" if package else "")
                + f" ({origin}) has no reason — required by review policy"
            )

        key = (vulnerability.strip(), package.strip() if package else None)
        if key in seen_keys:
            problems.append(
                f"duplicate whitelist key {key[0]}"
                + (f" (package {key[1]})" if key[1] else "")
                + f" in {origin} file (entries #{seen_keys[key]} and #{index})"
            )
            continue
        seen_keys[key] = index
        parsed.append(
            Entry(
                vulnerability=key[0],
                package=key[1],
                severity=severity,
                reason=(reason or "").strip() or None,
                origin=origin,
            )
        )

    if problems:
        die(problems)
    return parsed


def resolve_whitelist(
    main_entries: list[Entry], pr_entries: list[Entry]
) -> WhitelistResolution:
    """Union with main as base: PR adds/modifies, but can never drop main's keys."""
    result = WhitelistResolution()
    main_by_key = {entry.key(): entry for entry in main_entries}
    pr_by_key = {entry.key(): entry for entry in pr_entries}

    for key, entry in main_by_key.items():
        if key in pr_by_key:
            winner = pr_by_key[key]
            winner.status = "modified"
            result.entries.append(winner)
            result.modified += 1
        else:
            entry.status = "inherited"
            result.entries.append(entry)
            result.inherited += 1
            result.deletions_ignored.append(key)

    for key, entry in pr_by_key.items():
        if key not in main_by_key:
            entry.status = "added"
            result.entries.append(entry)
            result.added += 1

    if result.deletions_ignored:
        rendered = ", ".join(
            vuln + (f" (package {pkg})" if pkg else "")
            for vuln, pkg in result.deletions_ignored
        )
        result.warnings.append(
            f"{len(result.deletions_ignored)} main whitelist entr{'y is' if len(result.deletions_ignored) == 1 else 'ies are'} "
            f"absent from this branch and were still applied for gating (deletions take effect on main): {rendered}"
        )
    return result


def matches(entry: Entry, finding: "Finding") -> bool:
    if entry.vulnerability != finding.vulnerability:
        return False
    return entry.package is None or entry.package == finding.package


def find_whitelist_match(finding: "Finding", entries: list[Entry]) -> Entry | None:
    return next((entry for entry in entries if matches(entry, finding)), None)


# --------------------------------------------------------------------------
# grype report
# --------------------------------------------------------------------------


@dataclass
class Finding:
    vulnerability: str
    severity: str
    package: str
    version: str
    fix_state: str
    fix_versions: list[str]
    locations: list[str]
    description: str
    whitelisted_by: Entry | None = None

    @property
    def fix_available(self) -> bool:
        return self.fix_state == "fixed" or bool(self.fix_versions)

    @property
    def location_text(self) -> str:
        return ", ".join(self.locations) if self.locations else "<no location>"

    @property
    def sort_key(self) -> tuple[int, str, str]:
        return (-SEVERITY_RANK.get(self.severity, 0), self.vulnerability, self.package)


def load_grype_report(path: str) -> list[Finding]:
    with open(path, "r", encoding="utf-8") as handle:
        try:
            doc = json.load(handle)
        except json.JSONDecodeError as exc:
            die(f"{path} is not valid JSON: {exc}")
    matches = doc.get("matches") if isinstance(doc, dict) else None
    if not isinstance(matches, list):
        die(f"{path} is not a recognised Grype JSON report (no 'matches' list)")
    problems: list[str] = []
    findings: list[Finding] = []
    for index, match in enumerate(matches):
        if not isinstance(match, dict):
            problems.append(f"{path}: 'matches[{index}]' is not an object")
            continue
        vulnerability = match.get("vulnerability") or {}
        artifact = match.get("artifact") or {}
        fix = vulnerability.get("fix") or {}
        locations = [
            location.get("path", "")
            for location in (artifact.get("locations") or [])
            if isinstance(location, dict) and location.get("path")
        ]
        findings.append(
            Finding(
                vulnerability=str(vulnerability.get("id") or "UNKNOWN-ID"),
                severity=normalise_severity(vulnerability.get("severity")),
                package=str(artifact.get("name") or "<unknown>"),
                version=str(artifact.get("version") or "<unknown>"),
                fix_state=str(fix.get("state") or "unknown"),
                fix_versions=[str(v) for v in (fix.get("versions") or [])],
                locations=locations,
                description=str(vulnerability.get("description") or "").strip(),
            )
        )
    if problems:
        die(problems)
    return findings


# --------------------------------------------------------------------------
# gate policy
# --------------------------------------------------------------------------


def gate_decision(severity: str, fix_available: bool, fail_on: str) -> str | None:
    """The gate policy. Edit here (and only here) to tighten or loosen.

    Returns "FAIL", "WARN", or None for out-of-scope findings (below HIGH).
    """
    if severity not in GATE_SEVERITIES:
        return None
    if severity == "CRITICAL":
        return "FAIL"
    # HIGH:
    if fail_on == "HIGH":
        return "FAIL"
    if fail_on == "HIGH_FIXED":
        return "FAIL" if fix_available else "WARN"
    return "WARN"  # fail_on == "CRITICAL": highs never block


@dataclass
class Row:
    finding: Finding
    verdict: str  # "FAIL" | "WARN"
    whitelisted_enforced: bool = False  # row kept because IGNORE_WHITELISTED=false

    def sort_key(self) -> tuple[int, str, str]:
        return self.finding.sort_key


# --------------------------------------------------------------------------
# output rendering
# --------------------------------------------------------------------------


def md_cell(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_markdown(
    *,
    passed: bool,
    fail_on: str,
    ignore_whitelisted: bool,
    resolution: WhitelistResolution,
    rows: list[Row],
    suppressed: int,
    total_findings: int,
    notes: list[str],
    max_rows: int,
) -> str:
    fail_count = sum(1 for row in rows if row.verdict == "FAIL")
    warn_count = len(rows) - fail_count
    lines: list[str] = []
    lines.append("## Grype whitelist gate")
    lines.append("")
    lines.append(
        f"**{'PASS ✅' if passed else 'FAIL ❌'}** — "
        f"config: `FAIL_ON={fail_on}`, `IGNORE_WHITELISTED={str(ignore_whitelisted).lower()}`"
    )
    lines.append("")

    lines.append(
        f"Whitelist: **{resolution.inherited}** inherited from main · "
        f"**{resolution.added}** added by this PR · "
        f"**{resolution.modified}** modified · "
        f"**{len(resolution.deletions_ignored)}** deletions ignored"
    )
    if resolution.added:
        lines.append("")
        lines.append("<sub>Added by this PR (scrutinise in review):</sub>")
        for entry in (e for e in resolution.entries if e.status == "added"):
            scope = f" (package `{md_cell(entry.package)}`)" if entry.package else ""
            reason = md_cell(entry.reason) if entry.reason else "_no reason given_"
            lines.append(
                f"- <sub>`{md_cell(entry.vulnerability)}`{scope} — {reason}</sub>"
            )
    if resolution.modified:
        lines.append("")
        lines.append("<sub>Modified by this PR (PR version applied):</sub>")
        for entry in (e for e in resolution.entries if e.status == "modified"):
            scope = f" (package `{md_cell(entry.package)}`)" if entry.package else ""
            lines.append(f"- <sub>`{md_cell(entry.vulnerability)}`{scope}</sub>")
    lines.append("")

    lines.append(
        f"Findings (all severities): **{total_findings}** · suppressed by whitelist: "
        f"**{suppressed}** · blocking: **{fail_count}** · warnings: **{warn_count}**"
    )
    lines.append("")

    lines.append("### WARN / FAIL findings (non-whitelisted, HIGH & CRITICAL only)")
    lines.append("")
    if not rows:
        lines.append("_No non-whitelisted HIGH/CRITICAL findings — table is empty._")
    else:
        lines.append(
            "| Verdict | ID | Severity | Fix | Package | Version | Location(s) |"
        )
        lines.append("|---|---|---|---|---|---|---|")
        for row in sorted(rows, key=Row.sort_key)[:max_rows]:
            finding = row.finding
            fix = "yes" if finding.fix_available else "no"
            verdict = row.verdict
            if row.whitelisted_enforced:
                verdict += " (whitelisted)"
            lines.append(
                f"| {verdict} | `{md_cell(finding.vulnerability)}` | {finding.severity} | {fix} "
                f"| `{md_cell(finding.package)}` | {md_cell(finding.version)} "
                f"| `{md_cell(finding.location_text)}` |"
            )
        if len(rows) > max_rows:
            lines.append(
                f"| … | … | _{len(rows) - max_rows} more (see artifact)_ | | | | |"
            )
    lines.append("")

    for message in resolution.warnings + notes:
        lines.append("> [!WARNING]")
        lines.append(f"> {md_cell(message)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_gate_json(
    *,
    passed: bool,
    fail_on: str,
    ignore_whitelisted: bool,
    resolution: WhitelistResolution,
    rows: list[Row],
    suppressed: int,
    total_findings: int,
) -> dict[str, Any]:
    return {
        "gate": "pass" if passed else "fail",
        "config": {"fail_on": fail_on, "ignore_whitelisted": ignore_whitelisted},
        "totals": {
            "findings_all_severities": total_findings,
            "suppressed_by_whitelist": suppressed,
            "warn": sum(1 for row in rows if row.verdict == "WARN"),
            "fail": sum(1 for row in rows if row.verdict == "FAIL"),
        },
        "whitelist": {
            "inherited": resolution.inherited,
            "added": resolution.added,
            "modified": resolution.modified,
            "deletions_ignored": [
                {"vulnerability": vuln, "package": pkg}
                for vuln, pkg in resolution.deletions_ignored
            ],
            "effective_entries": [
                {
                    "vulnerability": entry.vulnerability,
                    "package": entry.package,
                    "severity": entry.severity,
                    "reason": entry.reason,
                    "status": entry.status,
                }
                for entry in resolution.entries
            ],
        },
        "rows": [
            {
                "verdict": row.verdict,
                "whitelisted_enforced": row.whitelisted_enforced,
                "vulnerability": row.finding.vulnerability,
                "severity": row.finding.severity,
                "package": row.finding.package,
                "version": row.finding.version,
                "fix_state": row.finding.fix_state,
                "fix_available": row.finding.fix_available,
                "locations": row.finding.locations,
            }
            for row in rows
        ],
    }


def build_sarif(tool_name: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    """Minimal valid SARIF 2.1.0 for the GitHub Security tab."""
    rules: list[dict[str, Any]] = []
    rule_index: dict[str, int] = {}
    for result in results:
        rule_id = result["ruleId"]
        if rule_id not in rule_index:
            rule_index[rule_id] = len(rules)
            rules.append(
                {
                    "id": rule_id,
                    "shortDescription": {"text": result["properties"]["short"]},
                }
            )
        result["ruleIndex"] = rule_index[rule_id]
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "informationUri": "https://github.com/anchore/grype",
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }


def full_sarif(findings: list[Finding]) -> dict[str, Any]:
    """SARIF for EVERY match in the report, whitelisted included (tagged)."""
    results = []
    for finding in findings:
        level = (
            "error"
            if finding.severity in GATE_SEVERITIES
            else ("warning" if finding.severity == "MEDIUM" else "note")
        )
        suppressed = finding.whitelisted_by is not None
        message = (
            f"{finding.vulnerability} — {finding.severity} in {finding.package}@{finding.version} "
            f"(fix: {finding.fix_state}"
            + (
                f", versions {'/'.join(finding.fix_versions)}"
                if finding.fix_versions
                else ""
            )
            + ")"
            + (" [suppressed by whitelist]" if suppressed else "")
        )
        results.append(
            {
                "ruleId": finding.vulnerability,
                "level": level,
                "message": {"text": message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": finding.locations[0]
                                if finding.locations
                                else f"package:{finding.package}"
                            }
                        }
                    }
                ],
                "properties": {
                    "short": f"{finding.vulnerability} ({finding.severity})",
                    "severity": finding.severity,
                    "package": finding.package,
                    "version": finding.version,
                    "fix_state": finding.fix_state,
                    "whitelisted": suppressed,
                },
            }
        )
    return build_sarif("Grype (full scan)", results)


def gate_sarif(rows: list[Row]) -> dict[str, Any]:
    """SARIF for the WARN/FAIL gate rows only (the switch target, see header)."""
    results = []
    for row in rows:
        finding = row.finding
        message = (
            f"{finding.vulnerability} — {finding.severity} in {finding.package}@{finding.version} "
            f"(fix: {finding.fix_state}) — {row.verdict}"
            + (
                " (whitelisted, enforced via IGNORE_WHITELISTED=false)"
                if row.whitelisted_enforced
                else ""
            )
        )
        results.append(
            {
                "ruleId": finding.vulnerability,
                "level": "error" if row.verdict == "FAIL" else "warning",
                "message": {"text": message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": finding.locations[0]
                                if finding.locations
                                else f"package:{finding.package}"
                            }
                        }
                    }
                ],
                "properties": {
                    "short": f"{finding.vulnerability} ({finding.severity})",
                    "severity": finding.severity,
                    "package": finding.package,
                    "version": finding.version,
                    "fix_state": finding.fix_state,
                    "verdict": row.verdict,
                },
            }
        )
    return build_sarif("Grype (whitelist gate)", results)


# --------------------------------------------------------------------------
# bootstrap mode
# --------------------------------------------------------------------------


def yaml_double_quoted(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def cmd_bootstrap(args: argparse.Namespace) -> None:
    findings = load_grype_report(args.current)
    in_scope = {}
    for finding in findings:
        if finding.severity in GATE_SEVERITIES:
            in_scope[(finding.vulnerability, finding.package)] = finding

    lines = [
        "# =====================================================================",
        "# Grype vulnerability whitelist — BOOTSTRAP DRAFT",
        "# =====================================================================",
        "# Generated once (locally) by:",
        "#   python3 .github/scripts/grype-diff.py --bootstrap \\",
        f"#     --current {args.current} --bootstrap-out grype-whitelist.yaml",
        "#",
        "# Every current HIGH/CRITICAL finding is drafted below with reason left as",
        "# TODO. A human must justify (or delete) each entry before merging this",
        "# file: an unjustified entry must not survive review (business rule).",
        "",
        f"schema_version: {WHITELIST_SCHEMA_VERSION}",
    ]
    if not in_scope:
        lines.append("entries: []")
    else:
        lines.append("entries:")
        for key in sorted(in_scope, key=lambda k: in_scope[k].sort_key):
            finding = in_scope[key]
            lines.append(
                f"  - vulnerability: {yaml_double_quoted(finding.vulnerability)}"
            )
            lines.append(f"    package: {yaml_double_quoted(finding.package)}")
            lines.append(f"    severity: {finding.severity}")
            lines.append('    reason: "TODO: justify this acceptance (review policy)"')
            lines.append("")

    output = "\n".join(lines).rstrip() + "\n"
    if args.bootstrap_out == "-":
        sys.stdout.write(output)
    else:
        with open(args.bootstrap_out, "w", encoding="utf-8") as handle:
            handle.write(output)
        print(
            f"grype-diff: bootstrap draft written to {args.bootstrap_out} "
            f"({len(in_scope)} HIGH/CRITICAL entries; justify or delete each before merging)"
        )
    sys.exit(EXIT_PASS)


# --------------------------------------------------------------------------
# gate mode
# --------------------------------------------------------------------------


def cmd_gate(args: argparse.Namespace) -> None:
    fail_on = parse_fail_on()
    ignore_whitelisted = parse_bool_env("IGNORE_WHITELISTED", True)

    notes: list[str] = []
    main_entries = load_whitelist(args.whitelist_main, "main", notes)
    pr_entries = load_whitelist(args.whitelist_pr, "pr", notes)
    resolution = resolve_whitelist(main_entries, pr_entries)
    findings = load_grype_report(args.current)

    rows: list[Row] = []
    suppressed = 0
    for finding in findings:
        entry = find_whitelist_match(finding, resolution.entries)
        finding.whitelisted_by = entry
        verdict = gate_decision(finding.severity, finding.fix_available, fail_on)
        if verdict is None:
            continue  # below HIGH: out of gate scope entirely
        if entry and ignore_whitelisted:
            suppressed += 1
            continue
        rows.append(
            Row(
                finding=finding, verdict=verdict, whitelisted_enforced=entry is not None
            )
        )

    fail_count = sum(1 for row in rows if row.verdict == "FAIL")
    passed = fail_count == 0

    markdown = render_markdown(
        passed=passed,
        fail_on=fail_on,
        ignore_whitelisted=ignore_whitelisted,
        resolution=resolution,
        rows=rows,
        suppressed=suppressed,
        total_findings=len(findings),
        notes=notes,
        max_rows=args.max_rows,
    )

    if args.report_out:
        with open(args.report_out, "w", encoding="utf-8") as handle:
            handle.write(markdown)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            json.dump(
                render_gate_json(
                    passed=passed,
                    fail_on=fail_on,
                    ignore_whitelisted=ignore_whitelisted,
                    resolution=resolution,
                    rows=rows,
                    suppressed=suppressed,
                    total_findings=len(findings),
                ),
                handle,
                indent=2,
            )
            handle.write("\n")
    if args.sarif_full:
        with open(args.sarif_full, "w", encoding="utf-8") as handle:
            json.dump(full_sarif(findings), handle, indent=2)
            handle.write("\n")
    if args.sarif_gate:
        with open(args.sarif_gate, "w", encoding="utf-8") as handle:
            json.dump(gate_sarif(rows), handle, indent=2)
            handle.write("\n")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(markdown)

    print(markdown)
    print(
        f"grype-diff: {'PASS' if passed else 'FAIL'} — {fail_count} blocking, "
        f"{len(rows) - fail_count} warning(s), {suppressed} whitelisted/suppressed "
        f"(HIGH/CRITICAL scope; {len(findings)} finding(s) in full report)",
        file=sys.stderr,
    )
    sys.exit(EXIT_PASS if passed else EXIT_BLOCKED)


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="grype-diff.py",
        description="Single-scan Grype whitelist gate (see module docstring for the full contract).",
    )
    parser.add_argument(
        "--current", required=True, help="Grype JSON report of the scanned tree"
    )
    parser.add_argument(
        "--whitelist-pr",
        default="grype-whitelist.yaml",
        help="whitelist file as it exists on this branch (default: ./grype-whitelist.yaml)",
    )
    parser.add_argument(
        "--whitelist-main",
        default=None,
        help="whitelist file extracted from the merge-base/main side (optional)",
    )
    parser.add_argument(
        "--report-out", default=None, help="write the WARN/FAIL markdown report here"
    )
    parser.add_argument(
        "--json-out", default=None, help="write the gate report as JSON here"
    )
    parser.add_argument(
        "--sarif-full", default=None, help="write a SARIF covering ALL matches here"
    )
    parser.add_argument(
        "--sarif-gate", default=None, help="write a SARIF covering WARN/FAIL rows here"
    )
    parser.add_argument(
        "--max-rows", type=int, default=50, help="max table rows in the markdown report"
    )
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="draft a whitelist from --current (run once, locally); never gates",
    )
    parser.add_argument(
        "--bootstrap-out",
        default=None,
        help="output path for --bootstrap ('-' for stdout)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.bootstrap:
        if not args.bootstrap_out:
            die("--bootstrap requires --bootstrap-out (use '-' for stdout)")
        cmd_bootstrap(args)
    cmd_gate(args)


if __name__ == "__main__":
    main()
