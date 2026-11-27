#!/usr/bin/env python3

#Update controls.md from metadata.json.
#See sync_controls_doc_README.md for more details.

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/engine/policies/cis/microsoft-365-foundations/v6.0.0/controls.md"
META = ROOT / "engine/policies/cis/microsoft-365-foundations/v6.0.0/metadata.json"

AUDIT_TYPES = ["Automated", "Deferred", "Blocked", "Manual", "Not Started"]


def fail(message):
    print("ERROR:", message, file=sys.stderr)
    sys.exit(2)


def labels(control):
    #Return (Our Audit Type, Status) for one control.
    status = control.get("automation_status")
    if status == "ready":
        return "Automated", "Implemented"
    if status == "deferred":
        return "Deferred", "Implemented"
    if status == "blocked":
        has_collector = bool(control.get("data_collector_id"))
        return "Blocked", "Blocked" if has_collector else "Pending"
    if status == "manual":
        return "Manual", "N/A"
    if status == "not_started":
        return "Not Started", "Not Started"
    fail(f"control {control.get('control_id')} has an unknown automation_status "
         f"{status!r}. Add it to labels() in this script.")


def load_controls(path):
    #Read metadata.json and return {control_id: control}.
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {control["control_id"]: control for control in data["controls"]}
    except (OSError, ValueError, KeyError, TypeError) as error:
        fail(f"cannot read controls from {path}: {error!r}")


def update_rows(lines, controls):
    #Fix the audit type, collector and status of every control row. Returns (changed, ids_in_doc).
    changed = False
    ids_in_doc = set()
    for number, line in enumerate(lines):
        match = re.match(r"\|\s*(\d+(?:\.\d+)+)\s*\|", line)
        if not match:
            continue
        control_id = match.group(1)
        ids_in_doc.add(control_id)
        if control_id not in controls:
            continue

        # cells: "", id, level, title, cis type, audit type, collector, status, notes, ""
        cells = line.split("|")
        if len(cells) != 10:
            fail(f"line {number + 1} ({control_id}) does not have 8 cells. "
                 "Is there a '|' inside a cell?")
        audit, status = labels(controls[control_id])
        collector = controls[control_id].get("data_collector_id") or ""
        cells[5] = f" {audit} "
        cells[6] = f" `{collector}` " if collector else " "
        cells[7] = f" {status} "

        new_line = "|".join(cells)
        if new_line != line:
            lines[number] = new_line
            changed = True
    return changed, ids_in_doc


def update_summary(lines, controls):
    #Fix the counts in both summary tables. Returns True if anything changed.
    cis_types = [c.get("benchmark_audit_type") for c in controls.values()]
    counts = {
        "**Total Controls**": len(controls),
        "**CIS Automated**": cis_types.count("Automated"),
        "**CIS Manual**": cis_types.count("Manual"),
    }
    for name in AUDIT_TYPES:
        counts[name] = sum(labels(c)[0] == name for c in controls.values())

    changed = False
    for number, line in enumerate(lines):
        match = re.match(r"\| (.+?) \| (\d+) \|(.*)", line)  # "| Automated | 47 | text |"
        if match and match.group(1) in counts:
            label = match.group(1)
            new_line = f"| {label} | {counts[label]} |{match.group(3)}"
            if new_line != line:
                lines[number] = new_line
                changed = True
    return changed


def update_date(lines, today):
    for number, line in enumerate(lines):
        if line.startswith("*Last Updated:"):
            lines[number] = f"*Last Updated: {today}*"
            return


def print_manual_work(controls, ids_in_doc):
    #Tell the user about things that need to be done manually.
    def version(control_id):
        return [int(part) for part in control_id.split(".")]

    for control_id in sorted(set(controls) - ids_in_doc, key=version):
        title = controls[control_id].get("title", "")
        print(f"ADD A ROW: {control_id} is in metadata.json but not in controls.md ({title}).")
    for control_id in sorted(ids_in_doc - set(controls), key=version):
        print(f"CHECK: {control_id} is in controls.md but not in metadata.json "
              "(removed or renumbered?). Its row was left alone.")


def main():
    parser = argparse.ArgumentParser(description="Update controls.md from metadata.json.")
    parser.add_argument("--doc", type=Path, default=DOC, help="controls.md to update")
    parser.add_argument("--metadata", type=Path, default=META, help="metadata.json to read")
    parser.add_argument("--check", action="store_true",
                        help="change nothing; exit 1 if out of date")
    parser.add_argument("--date", type=datetime.date.fromisoformat,
                        default=datetime.date.today(),
                        help="Last Updated date, YYYY-MM-DD (default: today)")
    args = parser.parse_args()

    controls = load_controls(args.metadata)
    try:
        with open(args.doc, encoding="utf-8", newline="") as file:  # newline="" keeps line endings
            text = file.read()
    except OSError as error:
        fail(f"cannot read {args.doc}: {error!r}")
    line_ending = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(line_ending)

    rows_changed, ids_in_doc = update_rows(lines, controls)
    summary_changed = update_summary(lines, controls)
    out_of_date = rows_changed or summary_changed

    if args.check:
        print("controls.md is out of date. Run this script without --check to update it."
              if out_of_date else "controls.md is up to date.")
    elif out_of_date:
        update_date(lines, args.date.isoformat())
        with open(args.doc, "w", encoding="utf-8", newline="") as file:
            file.write(line_ending.join(lines))
        print(f"Updated {args.doc}")
    else:
        print("controls.md is already up to date.")

    print_manual_work(controls, ids_in_doc)
    return 1 if (args.check and out_of_date) else 0


if __name__ == "__main__":
    sys.exit(main())
