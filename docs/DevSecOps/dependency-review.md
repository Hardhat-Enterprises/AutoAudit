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

Local validation passed: actionlint checked workflow syntax and expressions, configured inputs were verified against the v5 action definition, and Git diff whitespace checks passed. Grype has no diff and was not modified.

Live GitHub testing was completed after opening the implementation PR.

Testing completed:
1. The Dependency Review workflow passed on the clean implementation PR, confirming that the workflow can run successfully without blocking valid dependency/documentation workflow changes.
2. A separate temporary **DO NOT MERGE** test PR was created in my fork to test failure behaviour.
3. The temporary test PR introduced `lodash 4.17.18` only on the test branch.
4. Dependency Review failed as expected and reported high severity vulnerabilities, affected package details, and patched versions.
5. The vulnerable test PR was used only for validation and must not be merged.

No vulnerable dependencies were added to the implementation branch.

PR comment behaviour remains permission-dependent. The workflow is configured to post failure summaries where the GitHub token allows it, but contributors should rely on the Actions job summary and check logs as the consistent source of dependency review results.

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
