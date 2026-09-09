# Dependency review

`.github/workflows/ci.dependency-review.yml` checks dependency changes introduced
by pull requests using GitHub's dependency graph and Advisory Database. It runs
when a PR is opened, reopened, or updated with new commits, for all target branches
and paths. It does not install dependencies or execute application code.

## Policy and feedback

The check fails when an introduced dependency has a known high or critical
vulnerability. Runtime, development, and unknown scopes are included. License
enforcement is disabled. Low and moderate findings do not fail this policy.

Read the **Dependency review** check logs and Actions job summary for affected
packages and advisory details. Patched versions are shown when available. Failure
summaries are also posted on same-repository PRs when the token permits comments.
Fork and Dependabot PR comments are disabled because their tokens are normally
read-only; dependency checking and job summaries still run. First-time contributor
workflows may need maintainer approval to start.

If the check fails, update or remove the affected dependency, regenerate the
relevant lockfile, run the affected project's tests, and push the fix. For a
transitive dependency, update the parent package or discuss a safe resolution with
maintainers. Review API/configuration errors separately from vulnerability
findings; do not disable the check to hide a failure.

## Relationship to Grype

Dependency review compares the PR's dependency changes. Grype in
`.github/workflows/ci.grype.yml` scans the repository's broader dependency state
and uploads security findings. Neither replaces the other. This change leaves
Grype unchanged.

## Testing

Local validation passed: actionlint checked workflow syntax and expressions,
configured inputs were verified against the v5 action definition, and Git diff
whitespace checks passed. Grype has no diff. Live GitHub pass/fail and PR-comment
behavior have not yet been tested; use the plan below. No vulnerable dependencies
were added to the implementation branch.

1. Open the implementation PR. Confirm the workflow starts and that a change
   without new vulnerable dependencies passes. Save the run URL and job summary.
2. Create a separate temporary branch from the implementation branch and open a
   clearly labelled **DO NOT MERGE: dependency review test** PR targeting the
   implementation branch (or main after the implementation is merged).
3. Only on that temporary branch, add a dependency version covered by a current
   high/critical GitHub advisory and update its manifest/lockfile consistently.
   Record the advisory ID and affected version. Do not run application code with
   the vulnerable dependency; disable install scripts when generating test data.
4. Confirm the check fails with the package/advisory and a patched version where
   available. On a same-repository PR, confirm the failure comment appears.
5. Repeat with the dependency in development scope to verify that scope is gated.
   Upgrade to a patched version and confirm the check passes on the next push.
6. Use a separate temporary fork PR if available to verify that review and job
   summaries work without a comment or comment-permission error. Obtain any
   required workflow approval from a maintainer.
7. Close all temporary test PRs without merging and delete their branches. Keep
   the run URLs as evidence. Never merge vulnerable test changes.

## Limitations and maintainer setup

- Dependency graph access must be enabled. Coverage depends on GitHub-supported
  manifests/lockfiles, resolved versions, and available dependency snapshots.
  A passing check does not prove every Python or JavaScript dependency was seen;
  inspect the dependency diff when validating coverage.
- Only known advisories and dependencies introduced by the PR are reviewed. This
  is not a full-repository scan, runtime test, or guarantee of exploitability.
- Organization token policies can restrict comments even on same-repository PRs.
  No personal token or `pull_request_target` is used to bypass restrictions.
- To block merges, maintainers must make the **Dependency review** check required
  in branch protection/rulesets. Adding a failing workflow alone does not enforce
  that setting. Changes to the workflow itself also need normal code review.
- Actions use the GitHub-hosted `ubuntu-latest` runner. API outages or unavailable
  dependency graph data may fail a run independently of this severity policy.

Reference: [GitHub dependency-review-action documentation](https://github.com/actions/dependency-review-action).
