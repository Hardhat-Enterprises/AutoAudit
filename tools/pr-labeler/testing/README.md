# Testing the PR Labeler

A `gh`-CLI-driven test harness that exercises the labeling system end-to-end against a real repo: creating branches, committing files, opening PRs, triggering workflows, and asserting on the resulting labels. Useful whenever you change `labeler.yml`, `labels.yml`, or either script under `.github/scripts/` and want to verify nothing regressed, without hand-building test fixtures each time.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`) as an account with **write/admin** access to the repo — several tests need to act as a maintainer.
- A local clone of the repo, on a **clean working tree**, with the labeler already installed on the default branch (see [`../README.md`](../README.md)).
- A second GitHub account with collaborator (write) access, for the two tests that specifically need an outside maintainer's comment (see below). Everything else runs solo.

Run from either location:
```bash
./run-tests.sh <test>                          # from inside tools/pr-labeler/testing/
./tools/pr-labeler/testing/run-tests.sh <test>  # from the repo root
```
Each test creates its own branch (`test-labeler/<test>-<timestamp>`) and an open PR, recording the PR number locally so `cleanup` can find it later. Nothing is deleted automatically until you run `cleanup`, so you can inspect labels in the GitHub UI after any test before tearing it down.

## Running tests

```bash
./run-tests.sh list        # see all available tests
./run-tests.sh area        # run one test
./run-tests.sh all         # run every fully-automated test back to back
./run-tests.sh cleanup     # close every PR + delete every branch this harness created
```

## What each test checks

| Test | What it does | Pass condition |
|---|---|---|
| `area` | Touches a file under a known top-level folder | Matching `area:` label applied |
| `multi` | Touches two folders, then removes one change | `area: multi` applied, then removed once back to a single area |
| `root` | Touches a loose root-level file | Falls back to the catch-all area label |
| `docker` | Adds a Dockerfile variant | `docker` label applied automatically |
| `size-shrink` | Adds a large file, then shrinks it drastically | Size label moves *down*, not just up |
| `size-xlfiles` | Adds 35+ tiny files | Largest size tier applied despite a low total line count |
| `triage` | Opens a PR, runs the activity scan, then comments as the author | `needs-triage` appears, then **persists** through the self-comment |
| `draft` | Opens a **draft** PR | No activity labels applied at all |
| `exempt` | Adds a manual "no automated action" label, forces the clock to near-zero thresholds | Tier labels stay off despite the time condition being met |
| `reset` | Adds a manual label alongside automated ones, runs the reset tool in dry-run then for real | Dry run changes nothing; real run clears managed labels but preserves the manual one |
| `sync` | Temporarily adds a throwaway label to the catalog file, syncs, checks it exists, then reverts | Confirms the sync workflow can still create labels (a useful regression check after any permissions change) |

### Tests that need a second account

Two scenarios genuinely require two distinct GitHub identities and can't be faked by a script — a comment from the same account that opened the PR is always a self-comment, and self-comments never count as maintainer engagement (by design, see the main README).

**`triage` → `verify-triage-cleared <PR#>`**: after running `triage`, comment on the printed PR number from your *second* account, then run:
```bash
./run-tests.sh verify-triage-cleared 42
```
This confirms an outside maintainer's comment clears `needs-triage`.

**`tier-fast`**: tests the full multi-day progression without waiting. It pauses partway through and asks you to comment from your second account before continuing — the harness then forces the clock's thresholds to near-zero (scoped to only this one PR) so the tier label jumps ahead in seconds instead of days:
```bash
./run-tests.sh tier-fast
```
You can also run the same override manually against any PR, for spot-checking outside the harness:
```bash
gh workflow run ops.pr-activity-labeler.yml \
  -f stale_after_days=0 -f needs_decision_after_days=0 -f final_notice_after_days=0 -f pr_number=42
```
**Always include `pr_number` when overriding thresholds this way.** Without it, the override applies to *every* open PR the scan touches in that run, not just the one you're testing — there's no per-PR isolation otherwise, since the underlying scan always evaluates every open PR in a single pass. Leave the threshold inputs blank entirely for real 7/10/14-day behavior.

## Known limitations (not automated, by nature)

- **Real-time day-based expiry** can't be tested by simply waiting; the threshold-override mechanism above is the practical substitute.
- **Fork PR behavior** (this system's per-PR workflow uses `pull_request_target`, which behaves differently for forked-repo PRs) needs an actual external fork to test, not just a branch on the same repo — worth a manual check if the repo accepts outside contributions.
- **Bot-authored comments** are excluded from the activity clock by design, but this is hard to simulate without a real bot (e.g. Dependabot) commenting on a live PR — worth a spot-check the first time that actually happens organically.

## Troubleshooting

If a test reports a false failure, it's most often a timing issue rather than a real regression — GitHub Actions runs aren't instant, and the harness polls for completion with a timeout. A few things that look like failures but usually aren't:

- **A label-related test fails but the label shows up seconds later when you check manually** — likely the poll returned just before the triggering workflow run actually finished. Re-run the test; if it fails consistently, that's worth investigating as a real issue.
- **`⛔️ Skipping delete for '<label>'` in a sync run's log** — expected. The sync workflow is configured not to delete labels absent from the catalog file, so any pre-existing label not listed there gets this message every run. Not an error.
- **A reverted catalog entry doesn't remove the actual label from the repo** — also expected, for the same reason above. Removing an entry from the catalog file stops the sync from managing that label; it doesn't delete it. Deleting a label is always a separate, explicit action.

If you're on Windows / Git Bash and see an interactive "Deletion of directory... Should I try again?" prompt hang the terminal outside of this script, it's a known Git-for-Windows quirk unrelated to this tool — answering `n` is safe. The harness itself sets `GIT_ASK_YESNO=false` to avoid ever hitting this.

## Inspecting results

```bash
gh pr view <PR#> --json labels -q '.labels[].name'
```
is the fastest way to see exactly what's applied to a given PR. Failures print inline as tests run; scroll up for the full pass/fail summary of a given run.
