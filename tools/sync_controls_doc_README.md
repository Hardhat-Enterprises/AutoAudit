# sync_controls_doc.py

Keeps `controls.md` in sync with `metadata.json`.

`metadata.json` is the source of truth (the engine reads it). `controls.md` is the
human-readable status table that GRC maintains. This script fixes the parts of `controls.md`
that can be worked out from the metadata.

Python 3.10 or newer, standard library only. It writes only to the `controls.md` you point it at.

## How to run

Run from the repository root. In Git Bash on Windows, use `python` if `python3` is not found.

```bash
# Check only. Changes nothing. Exits with 1 if controls.md is out of date.
python3 tools/sync_controls_doc.py --check

# Update controls.md.
python3 tools/sync_controls_doc.py
```

Run it after any change to `metadata.json`.

The script updates what it can without listing every change. It prints one status line, plus one
message for each thing a person has to do by hand (see "New controls").

## What it updates

| In controls.md | Comes from |
|---|---|
| Our Audit Type, Collector ID and Status of each control row | `automation_status` and `data_collector_id` |
| Total Controls | number of controls in `metadata.json` |
| CIS Automated and CIS Manual | `benchmark_audit_type` |
| The five "Our Implementation Status" counts | the table below |
| `*Last Updated: YYYY-MM-DD*` | today, but only when something else changed |

| Metadata status | Our Audit Type | Status |
|---|---|---|
| ready | Automated | Implemented |
| deferred | Deferred | Implemented |
| blocked, with a collector | Blocked | Blocked |
| blocked, no collector | Blocked | Pending |
| manual | Manual | N/A |
| not_started | Not Started | Not Started |

The Collector ID is copied from `data_collector_id` (left empty if the metadata has none).

## What it does not change

Titles, levels, notes, the legend, the intro sentence ("all N controls"), the Description column
of the summary table, and the Implementation Priority section. Check these by hand when the
metadata changes.

## Options

| Option | Meaning |
|---|---|
| `--check` | Change nothing. Exit 1 if rows or summary counts are out of date. |
| `--doc PATH` | The controls.md to update (default: the v6.0.0 file in `docs/engine/policies/cis/`). |
| `--metadata PATH` | The metadata.json to read (default: the v6.0.0 file in `engine/policies/cis/`). |
| `--date YYYY-MM-DD` | The Last Updated value (default: today). Useful for tests. |

Exit codes: `0` ok, `1` `--check` found it out of date, `2` error (nothing is written).

## New controls

- A control in `metadata.json` with no row in `controls.md` is **not** added. The script prints
  `ADD A ROW: <id> is in metadata.json but not in controls.md (<title>).` Add the row by hand
  (copy a nearby row), then run the script again to fill in the cells. The summary counts already
  include it, so the table can show more controls than there are rows until you add the row.
- A row in `controls.md` whose control is not in `metadata.json` is left alone. The script prints
  `CHECK: <id> is in controls.md but not in metadata.json (removed or renumbered?)`.
- A new collector ID is copied as it is.
- A new `automation_status` value is not guessed. The script stops with an error. Add it to
  `labels()` in the script and to the table above.

## Errors

The script stops and writes nothing if the files are missing or not valid, if a control has an
unknown status, or if a control row does not have exactly 8 cells (for example a `|` typed inside
a note). The error gives the line number.

## Try it on the sample files

`sample/` has a small `metadata.json`, a `controls_before.md`, and the `controls_expected.md` that
the script should produce. It covers every status, a row that is already correct, a new control
with no row, and a removed control.

```bash
cp tools/sample/controls_before.md /tmp/sample.md

# 1. Out of date: prints "controls.md is out of date...", then the two manual-work messages. Exit 1.
python3 tools/sync_controls_doc.py --doc /tmp/sample.md --metadata tools/sample/metadata.json --check

# 2. Update it (prints "Updated ..."), then compare with the expected file (no diff output = identical)
python3 tools/sync_controls_doc.py --doc /tmp/sample.md --metadata tools/sample/metadata.json --date 2026-01-15
diff /tmp/sample.md tools/sample/controls_expected.md

# 3. Check again: "controls.md is up to date." (the two manual-work messages stay). Exit 0.
python3 tools/sync_controls_doc.py --doc /tmp/sample.md --metadata tools/sample/metadata.json --check
```

Notes are left as they are on purpose (row 2.1.1 keeps its old note).

## Limits

- It expects the layout of the v6.0.0 `controls.md`: an 8-cell table row for each control, summary
  rows such as `| Automated | 47 | ... |`, and a `*Last Updated: ...*` line. Other benchmarks can use
  it with `--doc` and `--metadata` if their files follow the same layout.
- The Status rule for blocked controls with no collector (Pending) follows the pattern already
  in `controls.md`. Change `labels()` if the rule changes.
