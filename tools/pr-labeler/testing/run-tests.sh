#!/usr/bin/env bash
# Test harness for the PR labeling system. Run from inside a clone of the
# target repo, on a clean working tree, with `gh` authenticated as a
# maintainer (write/admin) account. See ../TESTING.md for the full guide.
#
# Usage:
#   ./testing/run-tests.sh <test-name>   # run one test
#   ./testing/run-tests.sh all           # run every automated test
#   ./testing/run-tests.sh cleanup       # close/delete every branch+PR this script created
#   ./testing/run-tests.sh list          # show test names
#
# Each test creates its own branch (prefixed test-labeler/) and PR, leaves
# them open (labels are easiest to inspect that way), and records the PR
# number in .test-state so `cleanup` can find them later.

set -euo pipefail

# Git for Windows can prompt interactively ("Deletion of directory 'X'
# failed. Should I try again? (y/n)") when removing the last file in a
# directory, which hangs a non-interactive script. This disables that
# prompt; git proceeds without asking (a harmless leftover empty directory
# is possible but never blocks the script).
export GIT_ASK_YESNO=false

# Location-independent: works whether invoked as
# `./tools/pr-labeler/testing/run-tests.sh` from the repo root, or as
# `./run-tests.sh` after cd-ing into this directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

STATE_FILE="$SCRIPT_DIR/.test-state"
BASE_BRANCH="main"
POLL_INTERVAL=5
POLL_TIMEOUT=180 # seconds to wait for a workflow run to finish

# ---------- helpers ----------

log()  { printf '\n\033[1;34m==>\033[0m %s\n' "$1"; }
pass() { printf '  \033[1;32mPASS\033[0m %s\n' "$1"; }
fail() { printf '  \033[1;31mFAIL\033[0m %s\n' "$1"; FAILED=1; }

record_pr() { echo "$1" >> "$STATE_FILE"; }

require_clean_tree() {
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "Working tree is not clean. Commit/stash changes before running tests." >&2
    exit 1
  fi
}

new_branch() {
  local name="test-labeler/$1-$(date +%s)"
  git fetch origin "$BASE_BRANCH" --quiet
  git checkout -b "$name" "origin/$BASE_BRANCH" --quiet
  echo "$name"
}

open_pr() {
  local branch="$1" title="$2"
  git push -u origin "$branch" --quiet
  gh pr create --base "$BASE_BRANCH" --head "$branch" --title "$title" \
    --body "Automated test PR from run-tests.sh. Safe to close/delete." | tail -1
}

pr_labels() {
  # Prints newline-separated label names for a PR number
  gh pr view "$1" --json labels -q '.labels[].name'
}

has_label() {
  pr_labels "$1" | grep -qx "$2"
}

latest_run_id() {
  # $1 = workflow file, $2 = branch filter (optional)
  local wf="$1" branch="${2:-}"
  if [[ -n "$branch" ]]; then
    gh run list --workflow="$wf" --branch "$branch" --limit 1 --json databaseId -q '.[0].databaseId' 2>/dev/null || echo "none"
  else
    gh run list --workflow="$wf" --limit 1 --json databaseId -q '.[0].databaseId' 2>/dev/null || echo "none"
  fi
}

wait_for_new_completed_run() {
  # Polls until a run ID *different* from $before appears for this
  # workflow+branch AND has finished. Polls .status directly rather than
  # using `gh run watch`, which can error out if invoked in the brief
  # window before GitHub's API fully registers a just-created run —
  # silently skipping the wait if that error isn't surfaced.
  # $1 = workflow file, $2 = branch filter (optional, "" for none), $3 = before-id
  local wf="$1" branch="$2" before="$3" elapsed=0
  log "Waiting for a new $wf run${branch:+ on $branch}..."
  while (( elapsed < POLL_TIMEOUT )); do
    local id status
    id=$(latest_run_id "$wf" "$branch")
    if [[ "$id" != "$before" && "$id" != "none" ]]; then
      status=$(gh run view "$id" --json status -q '.status' 2>/dev/null || echo "")
      if [[ "$status" == "completed" ]]; then
        return 0
      fi
    fi
    sleep "$POLL_INTERVAL"
    elapsed=$((elapsed + POLL_INTERVAL))
  done
  echo "  (timed out waiting for a new completed run — checking labels anyway, may be a false negative)"
}

run_dispatch_and_wait() {
  # Triggers a workflow_dispatch and waits for that specific new run to finish.
  # $1 = workflow file, remaining args = -f key=value pairs
  local workflow="$1"; shift
  local before; before=$(latest_run_id "$workflow")
  gh workflow run "$workflow" "$@"
  wait_for_new_completed_run "$workflow" "" "$before"
}

# ---------- tests ----------

test_area() {
  log "TEST: single-area change gets the matching area label"
  local branch; branch=$(new_branch "area")
  mkdir -p backend-api
  echo "// test $(date +%s)" >> backend-api/_test-touch.txt
  git add -A && git commit -m "test: touch backend-api" --quiet
  local before; before=$(latest_run_id "pr.area-labeler.yml" "$branch")
  local pr; pr=$(open_pr "$branch" "test: area label (backend-api)")
  record_pr "$pr"
  wait_for_new_completed_run "pr.area-labeler.yml" "$branch" "$before"
  has_label "$pr" "area: backend-api" && pass "area: backend-api applied" || fail "area: backend-api missing"
  git checkout "$BASE_BRANCH" --quiet
}

test_multi_and_shrink() {
  log "TEST: two areas -> area: multi, then drop to one -> multi removed"
  local branch; branch=$(new_branch "multi")
  mkdir -p backend-api frontend
  echo "// test $(date +%s)" >> backend-api/_test-touch.txt
  echo "// test $(date +%s)" >> frontend/_test-touch.txt
  git add -A && git commit -m "test: touch backend-api + frontend" --quiet
  local before1; before1=$(latest_run_id "pr.area-labeler.yml" "$branch")
  local pr; pr=$(open_pr "$branch" "test: area:multi")
  record_pr "$pr"
  wait_for_new_completed_run "pr.area-labeler.yml" "$branch" "$before1"
  has_label "$pr" "area: multi" && pass "area: multi applied for 2 areas" || fail "area: multi missing"

  rm -f frontend/_test-touch.txt
  rmdir frontend 2>/dev/null || true
  git add -A
  git commit -m "test: drop frontend change" --quiet
  local before2; before2=$(latest_run_id "pr.area-labeler.yml" "$branch")
  git push --quiet
  wait_for_new_completed_run "pr.area-labeler.yml" "$branch" "$before2"
  has_label "$pr" "area: multi" && fail "area: multi still present after shrinking to 1 area" || pass "area: multi correctly removed"
  git checkout "$BASE_BRANCH" --quiet
}

test_root_catchall() {
  log "TEST: loose root file gets area: root"
  local branch; branch=$(new_branch "root")
  echo "test $(date +%s)" >> _test-root-file.txt
  git add -A && git commit -m "test: touch root file" --quiet
  local before; before=$(latest_run_id "pr.area-labeler.yml" "$branch")
  local pr; pr=$(open_pr "$branch" "test: area: root")
  record_pr "$pr"
  wait_for_new_completed_run "pr.area-labeler.yml" "$branch" "$before"
  has_label "$pr" "area: root" && pass "area: root applied" || fail "area: root missing"
  git checkout "$BASE_BRANCH" --quiet
}

test_docker_label() {
  log "TEST: Dockerfile change gets the docker label"
  local branch; branch=$(new_branch "docker")
  mkdir -p backend-api
  cat > backend-api/Dockerfile.test <<'EOF'
FROM scratch
EOF
  git add -A && git commit -m "test: touch Dockerfile" --quiet
  local before; before=$(latest_run_id "pr.area-labeler.yml" "$branch")
  local pr; pr=$(open_pr "$branch" "test: docker label")
  record_pr "$pr"
  wait_for_new_completed_run "pr.area-labeler.yml" "$branch" "$before"
  has_label "$pr" "docker" && pass "docker label applied" || fail "docker label missing"
  git checkout "$BASE_BRANCH" --quiet
}

test_size_shrink() {
  log "TEST: size label moves down when the diff shrinks"
  local branch; branch=$(new_branch "size-shrink")
  mkdir -p tools
  # ~300 lines -> should land in size/L (>=250)
  seq 1 300 | sed 's/^/line /' > tools/_test-big-file.txt
  git add -A && git commit -m "test: large addition" --quiet
  local before1; before1=$(latest_run_id "pr.area-labeler.yml" "$branch")
  local pr; pr=$(open_pr "$branch" "test: size shrink")
  record_pr "$pr"
  wait_for_new_completed_run "pr.area-labeler.yml" "$branch" "$before1"
  local before; before=$(pr_labels "$pr" | grep '^size/' || echo "none")
  echo "  size before shrink: $before"

  # shrink to ~5 lines -> should land in size/XS
  seq 1 5 | sed 's/^/line /' > tools/_test-big-file.txt
  git add -A && git commit -m "test: shrink file" --quiet
  local before2; before2=$(latest_run_id "pr.area-labeler.yml" "$branch")
  git push --quiet
  wait_for_new_completed_run "pr.area-labeler.yml" "$branch" "$before2"
  local after; after=$(pr_labels "$pr" | grep '^size/' || echo "none")
  echo "  size after shrink: $after"
  if [[ "$after" == "size/XS" && "$before" != "size/XS" ]]; then
    pass "size label moved down after shrinking ($before -> $after)"
  else
    fail "size label did not move down as expected ($before -> $after)"
  fi
  git checkout "$BASE_BRANCH" --quiet
}

test_size_xl_by_filecount() {
  log "TEST: many small files (>30) triggers size/XL even with few total lines"
  local branch; branch=$(new_branch "size-xlfiles")
  mkdir -p tools/_test-many
  for i in $(seq 1 35); do
    echo "x" > "tools/_test-many/file-$i.txt"
  done
  git add -A && git commit -m "test: 35 tiny files" --quiet
  local before; before=$(latest_run_id "pr.area-labeler.yml" "$branch")
  local pr; pr=$(open_pr "$branch" "test: size/XL by file count")
  record_pr "$pr"
  wait_for_new_completed_run "pr.area-labeler.yml" "$branch" "$before"
  has_label "$pr" "size/XL" && pass "size/XL applied for >30 files" || fail "size/XL missing for >30-file PR"
  git checkout "$BASE_BRANCH" --quiet
}

test_triage_and_response() {
  log "TEST: needs-triage on open, persists through self-comment"
  local branch; branch=$(new_branch "triage")
  mkdir -p docs
  echo "test $(date +%s)" >> docs/_test-touch.txt
  git add -A && git commit -m "test: triage flow" --quiet
  local pr; pr=$(open_pr "$branch" "test: needs-triage flow")
  record_pr "$pr"

  run_dispatch_and_wait "ops.pr-activity-labeler.yml"
  has_label "$pr" "needs-triage" && pass "needs-triage applied on untouched PR" || fail "needs-triage missing"

  gh pr comment "$pr" --body "self-comment, should NOT clear needs-triage"
  run_dispatch_and_wait "ops.pr-activity-labeler.yml"
  has_label "$pr" "needs-triage" && pass "needs-triage persists after author's own comment" || fail "needs-triage incorrectly cleared by self-comment"

  echo "  NOTE: to test that an outside maintainer comment clears needs-triage,"
  echo "  comment on PR #$pr from a different maintainer account, then re-run:"
  echo "    ./testing/run-tests.sh verify-triage-cleared $pr"
  git checkout "$BASE_BRANCH" --quiet
}

verify_triage_cleared() {
  local pr="$1"
  log "Re-checking PR #$pr after external maintainer comment"
  run_dispatch_and_wait "ops.pr-activity-labeler.yml"
  has_label "$pr" "needs-triage" && fail "needs-triage still present after outside maintainer comment" || pass "needs-triage correctly cleared"
}

test_draft_immunity() {
  log "TEST: draft PRs get no needs-triage / tier labels"
  local branch; branch=$(new_branch "draft")
  mkdir -p docs
  echo "test $(date +%s)" >> docs/_test-draft.txt
  git add -A && git commit -m "test: draft immunity" --quiet
  git push -u origin "$branch" --quiet
  local pr; pr=$(gh pr create --draft --base "$BASE_BRANCH" --head "$branch" \
    --title "test: draft immunity" --body "Automated test PR, safe to close/delete." | tail -1)
  record_pr "$pr"
  run_dispatch_and_wait "ops.pr-activity-labeler.yml"
  if has_label "$pr" "needs-triage"; then
    fail "draft PR incorrectly got needs-triage"
  else
    pass "draft PR correctly skipped by activity scan"
  fi
  git checkout "$BASE_BRANCH" --quiet
}

test_exempt_label_stops_clock() {
  log "TEST: has-conflicts exempts a PR from tier labels even with a near-zero threshold"
  local branch; branch=$(new_branch "exempt")
  mkdir -p docs
  echo "test $(date +%s)" >> docs/_test-exempt.txt
  git add -A && git commit -m "test: exempt label" --quiet
  local pr; pr=$(open_pr "$branch" "test: exempt label stops clock")
  record_pr "$pr"

  echo "  This test needs a REAL maintainer comment from a DIFFERENT account"
  echo "  than the one running this script — a comment from your own account"
  echo "  is a self-comment and never starts the clock (see the 'triage' test),"
  echo "  so this test can't validate the exemption without it."
  echo "  Comment on PR #$pr now from a different collaborator/maintainer account."
  read -r -p "  Press enter once that comment is posted... " _

  gh pr edit "$pr" --add-label "has-conflicts"
  # near-zero thresholds + pr_number scoping so this ONLY affects this PR,
  # never any other open PR in the repo (see ONLY_PR_NUMBER in activity-labeler.js)
  run_dispatch_and_wait "ops.pr-activity-labeler.yml" \
    -f stale_after_days=0 -f needs_decision_after_days=0 -f final_notice_after_days=0 -f pr_number="$pr"
  if has_label "$pr" "stale" || has_label "$pr" "needs-decision" || has_label "$pr" "final-notice"; then
    fail "tier label applied despite has-conflicts exemption"
  else
    pass "has-conflicts correctly exempted the PR from tier labels"
  fi
  git checkout "$BASE_BRANCH" --quiet
}

test_tier_progression_fast() {
  log "TEST: forced tier progression using tiny day thresholds"
  local branch; branch=$(new_branch "tier-fast")
  mkdir -p docs
  echo "test $(date +%s)" >> docs/_test-tier.txt
  git add -A && git commit -m "test: tier progression" --quiet
  local pr; pr=$(open_pr "$branch" "test: tier progression")
  record_pr "$pr"

  # A maintainer comment on someone else's PR requires a second account in
  # practice; here we simulate "clock started" by commenting ourselves and
  # accepting that self-comments don't start the clock (see triage test) —
  # so for this test, comment from your OTHER (collaborator) gh account if
  # you have `gh auth switch` set up, then continue. Otherwise this test
  # will correctly show no tier label (clock never started), which is
  # itself a valid pass condition worth checking.
  echo "  If you have a second maintainer account, comment on PR #$pr now, then press enter."
  read -r -p "  Press enter to continue once ready (or just press enter to test the no-clock-started path)... " _

  run_dispatch_and_wait "ops.pr-activity-labeler.yml" \
    -f stale_after_days=0.0001 -f needs_decision_after_days=0.0002 -f final_notice_after_days=0.0003 -f pr_number="$pr"
  local labels; labels=$(pr_labels "$pr" | tr '\n' ' ')
  echo "  labels after forced-fast run: $labels"
  if echo "$labels" | grep -q "final-notice"; then
    pass "tier progressed to final-notice with near-zero thresholds"
  elif echo "$labels" | grep -q "needs-triage"; then
    pass "no maintainer comment detected -> correctly stayed at needs-triage"
  else
    fail "unexpected label state: $labels"
  fi
  git checkout "$BASE_BRANCH" --quiet
}

test_reset_tool() {
  log "TEST: PR Labels Reset clears managed labels but never manual ones"
  local branch; branch=$(new_branch "reset")
  mkdir -p backend-api
  echo "test $(date +%s)" >> backend-api/_test-reset.txt
  git add -A && git commit -m "test: reset tool" --quiet
  local before; before=$(latest_run_id "pr.area-labeler.yml" "$branch")
  local pr; pr=$(open_pr "$branch" "test: reset tool")
  record_pr "$pr"
  wait_for_new_completed_run "pr.area-labeler.yml" "$branch" "$before"

  # Add a genuinely manual label alongside the automated ones
  gh pr edit "$pr" --add-label "question"

  run_dispatch_and_wait "ops.pr-labels-reset.yml" -f pr_numbers="$pr" -f dry_run=true
  if has_label "$pr" "area: backend-api" && has_label "$pr" "question"; then
    pass "dry run left all labels untouched"
  else
    fail "dry run changed labels — it should never do that"
  fi

  run_dispatch_and_wait "ops.pr-labels-reset.yml" -f pr_numbers="$pr" -f dry_run=false -f confirm=RESET
  local remaining; remaining=$(pr_labels "$pr" | tr '\n' ' ')
  echo "  labels after real reset: $remaining"
  if has_label "$pr" "area: backend-api" || has_label "$pr" "size/XS"; then
    fail "managed labels still present after a confirmed reset"
  elif ! has_label "$pr" "question"; then
    fail "manual label 'question' was incorrectly removed"
  else
    pass "managed labels cleared, manual label preserved"
  fi
  git checkout "$BASE_BRANCH" --quiet
}

test_sync_regression() {
  log "TEST: label sync still works (regression check for the permissions bug)"
  local test_label="test-sync-$(date +%s)"
  cp "$REPO_ROOT/.github/labels.yml" "$REPO_ROOT/.github/labels.yml.bak"
  cat >> "$REPO_ROOT/.github/labels.yml" <<EOF
- name: "$test_label"
  color: "ffffff"
  description: "Temporary label created by run-tests.sh, safe to delete"
EOF
  git add .github/labels.yml
  git commit -m "test: temporary sync-check label" --quiet
  # ops.label-sync.yml already triggers on push to labels.yml — don't also
  # dispatch it manually, that created two near-simultaneous runs racing
  # each other and made the before/after run-ID check unreliable.
  local before; before=$(latest_run_id "ops.label-sync.yml" "$BASE_BRANCH")
  git push origin HEAD:"$BASE_BRANCH" --quiet
  wait_for_new_completed_run "ops.label-sync.yml" "$BASE_BRANCH" "$before"
  if gh label list --json name -q '.[].name' | grep -qx "$test_label"; then
    pass "label sync created the test label successfully"
  else
    fail "label sync did not create the test label — check the workflow run log"
  fi
  echo "  Cleaning up: removing test label from labels.yml and the repo"
  echo "  (the label ITSELF stays until the explicit delete below — skip-delete"
  echo "  intentionally means removing an entry from labels.yml never auto-deletes"
  echo "  the actual label, same protection that keeps other undocumented"
  echo "  labels safe from being wiped by a sync run)"
  mv "$REPO_ROOT/.github/labels.yml.bak" "$REPO_ROOT/.github/labels.yml"
  git add .github/labels.yml
  git commit -m "test: revert temporary sync-check label" --quiet
  git push origin HEAD:"$BASE_BRANCH" --quiet
  gh label delete "$test_label" --yes 2>/dev/null || true
}

# ---------- runner ----------

FAILED=0

list_tests() {
  echo "Available tests:"
  echo "  area                    - single-area change gets matching label"
  echo "  multi                   - two areas -> area:multi, shrink -> removed"
  echo "  root                    - loose root file -> area: root"
  echo "  docker                  - Dockerfile change -> docker label"
  echo "  size-shrink             - size label moves down when diff shrinks"
  echo "  size-xlfiles            - >30 files -> size/XL regardless of line count"
  echo "  triage                  - needs-triage on open; survives self-comment"
  echo "  draft                   - draft PRs get no activity labels"
  echo "  exempt                  - has-conflicts blocks tier labels"
  echo "  tier-fast               - forced tier progression via tiny thresholds"
  echo "  reset                   - reset tool clears managed labels, preserves manual ones"
  echo "  sync                    - label sync regression check"
  echo "  all                     - run everything above"
  echo "  verify-triage-cleared N - re-check PR #N after an outside comment"
  echo "  cleanup                 - close every PR + delete every branch this script made"
}

main() {
  local cmd="${1:-}"
  case "$cmd" in
    area) require_clean_tree; test_area ;;
    multi) require_clean_tree; test_multi_and_shrink ;;
    root) require_clean_tree; test_root_catchall ;;
    docker) require_clean_tree; test_docker_label ;;
    size-shrink) require_clean_tree; test_size_shrink ;;
    size-xlfiles) require_clean_tree; test_size_xl_by_filecount ;;
    triage) require_clean_tree; test_triage_and_response ;;
    draft) require_clean_tree; test_draft_immunity ;;
    exempt) require_clean_tree; test_exempt_label_stops_clock ;;
    tier-fast) require_clean_tree; test_tier_progression_fast ;;
    reset) require_clean_tree; test_reset_tool ;;
    sync) require_clean_tree; test_sync_regression ;;
    verify-triage-cleared) verify_triage_cleared "${2:?PR number required}" ;;
    all)
      require_clean_tree
      test_area; test_multi_and_shrink; test_root_catchall; test_docker_label
      test_size_shrink; test_size_xl_by_filecount; test_triage_and_response
      test_draft_immunity; test_exempt_label_stops_clock; test_reset_tool; test_sync_regression
      echo
      echo "tier-fast and verify-triage-cleared need manual interaction — run them separately."
      ;;
    cleanup)
      [[ -f "$STATE_FILE" ]] || { echo "No $STATE_FILE found — nothing to clean up."; exit 0; }
      while read -r pr; do
        [[ -z "$pr" ]] && continue
        echo "Closing PR #$pr..."
        gh pr close "$pr" --delete-branch 2>/dev/null || echo "  (already closed or branch already gone)"
      done < "$STATE_FILE"
      rm -f "$STATE_FILE"
      ;;
    list|"") list_tests ;;
    *) echo "Unknown test: $cmd"; list_tests; exit 1 ;;
  esac

  if [[ "$FAILED" -eq 1 ]]; then
    echo
    echo "One or more assertions FAILED — see above."
    exit 1
  fi
}

main "$@"
