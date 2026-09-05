# PR Labeler

Automated pull request labeling for this repository: work-area labels from changed file paths, size labels from diff stats, and activity-status labels that track a 7/10/14-day "waiting on reviewer response" policy — all without ever closing, merging, or deleting anything. This module only adds and removes labels.

It started as a small internal tool to replace manual PR triage tracking (a spreadsheet, originally). It's organized as a self-contained module under `tools/` in case it's ever worth extracting into its own reusable action or open-source project later — nothing here assumes it has to stay embedded in this repo.

## How it works, in one paragraph

Every PR gets area labels (`area: backend-api`, `area: docs`, etc.) the moment it's opened or updated, based on which top-level folders it touches, plus a size label based on lines/files changed. Separately, a nightly scan tracks how long a PR has been waiting on its author since a maintainer last engaged with it, applying `needs-triage` → `stale` → `needs-decision` → `final-notice` as that wait grows — but only once a maintainer (someone with write/admin access) has actually looked at it, and never while the PR's own author is the only one who's touched it. Nothing here ever takes action beyond labels; every outcome (closing, adopting, marking abandoned) stays a human decision.

## Repository layout

```
.github/
  labeler.yml                    # path -> area-label rules (edit this to add/change area mappings)
  labels.yml                     # full label catalog: names, colors, descriptions (source of truth — see ops.label-sync.yml)
  scripts/
    label-taxonomy.js            # single source of truth for which labels are automated vs. manual-only
    pr-range-parser.js           # printer-style PR range parsing ("1,5,7-9"), used by the reset tool
    activity-labeler.js          # the 7/10/14-day activity clock
    pr-metadata-labeler.js       # area:multi / size/* / first-contribution (shared by two workflows below)
    pr-labels-reset.js           # bulk-clears managed labels from chosen PRs (the reset tool)
  workflows/
    pr.area-labeler.yml          # runs on every PR open/push: area + size + first-contribution
    ops.pr-activity-labeler.yml  # nightly cron + manual: stale/needs-decision/final-notice/needs-triage
    pr.labels-backfill.yml       # manual, one-shot: applies every label type to all currently-open PRs
    ops.label-sync.yml           # on push to labels.yml, or manual: creates/updates labels from the catalog
    ops.pr-labels-reset.yml      # manual "clean slate" tool: bulk-clears managed labels from chosen PRs

tools/pr-labeler/
  README.md                      # this file
  testing/
    README.md                    # test harness guide
    run-tests.sh                 # gh-CLI-driven test harness
```

`.github/` holds everything GitHub itself requires to be there (workflows must live under `.github/workflows/`) or that's conventional to keep alongside it (the labeler config and its supporting scripts). Everything else — documentation and the test harness — lives under `tools/pr-labeler/`, out of the way of the workflow machinery but easy to find.

## Setup (one-time)

1. **Settings → Actions → General → Workflow permissions** → set to **"Read and write permissions"**. Every workflow here needs this to add/remove labels; without it they fail with a 403.
2. Merge this to your default branch. Merging alone triggers `ops.label-sync.yml` (it watches `.github/labels.yml`) — check the Actions tab and confirm the full label catalog now exists under Issues → Labels. If it doesn't fire automatically, run it manually: **Actions → Sync Labels → Run workflow**.
3. Run **Actions → Backfill All PR Labels → Run workflow** once. This applies every label type — area, size, multi, first-contribution, and activity status — to every PR that was already open before this system existed.

From there it's automatic: new/updated PRs get area and size labels within seconds, and a nightly scan keeps activity status current on everything else.

## Recovering from a bad state: PR Labels Reset

**Actions → PR Labels Reset → Run workflow.** A manual "clean slate" tool for clearing automatically-managed labels from a chosen set of PRs — useful after a bad test run, a config bug, or any other case where the automation left labels somewhere they shouldn't be. It only ever touches labels this system can apply on its own (`area:*`, `size/*`, `first-contribution`, `docker`, `github_actions`, and the four activity tier labels — the exact list lives in `.github/scripts/label-taxonomy.js`). Manually-curated labels like `abandoned`, `needs-adoption`, `has-conflicts`, or `wontfix` are never touched, since those always reflect a human decision this tool has no business undoing.

**Inputs:**

| Input | Purpose |
|---|---|
| `pr_numbers` | Printer-style ranges, e.g. `1,5,7-9` — same syntax as a print dialog's page range |
| `all_open_prs` | Check this to target every currently open PR instead of listing numbers |
| `open_only` | Skip any listed PR that isn't currently open (default on) |
| `only_labels` | Optional — restrict to specific labels/prefixes (e.g. `stale,needs-decision,final-notice` to clear just the tier labels, or `area: ` to clear just area labels). Leave blank to reset everything managed |
| `dry_run` | **Defaults to on.** Logs exactly what would be removed without changing anything — always run this first |
| `confirm` | Must be typed as exactly `RESET` to allow a real (non-dry-run) run to proceed |

The two safety gates — dry-run-by-default, plus the typed confirmation for real runs — exist because this is the one tool in the whole system whose entire purpose is bulk-removing labels across many PRs at once, where a mistake is the most annoying to walk back by hand. Always run with `dry_run` on first, read the job summary it produces, and only then re-run with `dry_run` off and `confirm: RESET`.

## Label reference

| Label | Applied when |
|---|---|
| `area: <name>` | Changed files match a path rule in `labeler.yml` |
| `area: multi` | More than one `area:` label applies |
| `size/XS` … `size/XL` | Lines changed (and file count, for XL — see note below) |
| `first-contribution` | Author's first-ever PR to this repo |
| `docker` | Touches a `Dockerfile*`, `docker-compose*.yml`, or `.dockerignore` |
| `github_actions` | Touches `.github/workflows/**` |
| `needs-triage` | No maintainer has commented or reviewed yet |
| `stale` | 7+ days since a maintainer's last comment, no author response since |
| `needs-decision` | 10+ days, same condition |
| `final-notice` | 14+ days, same condition |

Labels like `abandoned`, `needs-adoption`, `has-conflicts`, and `wontfix` stay fully manual by design — those require a judgment call this system deliberately doesn't make. A PR carrying any of them, or currently in draft, is skipped entirely by the activity scan.

**How the activity clock works**: it only starts once a maintainer (anyone with write/admin permission on the repo) comments, reviews, or pushes to the PR — and critically, the PR's *own author* opening or updating their own PR never counts as that, even if the author happens to hold maintainer permissions themselves. The moment a non-maintainer responds after that, the clock clears and the tier label is removed automatically. A PR nobody has looked at yet stays at `needs-triage` indefinitely rather than aging into `stale` — the policy is about response time after engagement, not time since the PR was opened.

**Size tiers**: if this repo also runs a separate "PR size warning" check based on total lines or file count, it's worth aligning `size/XL`'s trigger condition with that check's threshold, so the two systems agree on what counts as "large" — see the comment above `sizeTier()` in `pr-metadata-labeler.js` for how that's wired up here.

## Safety properties worth knowing

- **Nothing here closes, merges, or deletes a PR, branch, or file.** The entire system is additive/subtractive on labels only.
- **`skip-delete: true`** on the label sync means removing an entry from `labels.yml` never deletes the actual label from the repo — it just stops managing it. Deleting a label is always a separate, explicit action.
- **Threshold overrides are scoped.** `ops.pr-activity-labeler.yml` accepts optional day-threshold overrides (for testing) and an optional `pr_number` input. Always pass `pr_number` alongside a threshold override — without it, the override applies to every open PR the scan touches, not just the one you're testing.

## Extending

- **Add a new automated label**: add it to `MANAGED_EXACT_LABELS` (or use the existing `area:`/`size/` prefixes) in `.github/scripts/label-taxonomy.js` — this is what the reset tool uses to know what it's allowed to touch, so anything added elsewhere that isn't listed here won't be clearable in bulk later.
- **New top-level folder needs its own area label**: add one block to `.github/labeler.yml` mirroring the existing ones. Until you do, files in an unrecognized folder simply won't get an area label (nothing crashes, it's just a labeling gap worth watching for as the repo evolves).
- **Change the day thresholds**: edit the three default values in `.github/scripts/activity-labeler.js`.
- **Change the cron schedule**: edit the `cron:` line in `ops.pr-activity-labeler.yml`.
- **Rename or recolor a label**: edit `.github/labels.yml` and push (or run Sync Labels manually).

## Testing

See [`testing/README.md`](testing/README.md) for the test harness — it drives real branches, commits, and PRs through `gh` and asserts on the resulting labels, so a change here can be verified end-to-end without hand-building test fixtures each time.
