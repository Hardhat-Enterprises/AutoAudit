# PR Size Warning

The PR size warning helps contributors and reviewers identify pull requests that may be difficult to review safely. It runs when a pull request targeting `main` is opened, updated, or reopened.

## When the warning appears

The warning appears when a pull request changes more than 30 files or has more than 500 changed lines in total (additions plus deletions). Open the **PR Size Warning** workflow run from the pull request's **Checks** tab to see the warning and job summary.

This check is warning-only. It does not fail the workflow, block the pull request, or prevent merging.

## What to do

If the warning appears:

- Split unrelated changes into smaller pull requests where possible.
- Avoid combining frontend, backend, engine, documentation, and workflow changes unless they are directly related.
- If the pull request cannot be split, explain in its description why it must remain large.
- Mention generated files, lock file updates, migrations, or formatting-only changes if they increased the reported size.

## When a large PR is acceptable

A large pull request may be reasonable when its changes are tightly related and separating them would make the implementation incomplete or harder to understand. Examples include coordinated cross-component changes, migrations, generated output that must accompany a source change, and repository-wide formatting or dependency updates.

When this happens, describe the relationship between the changes, identify any mechanical or generated changes, and suggest a useful review order.

## Why smaller PRs help

Smaller, focused pull requests reduce reviewer fatigue, make defects and security issues easier to spot, and allow feedback to arrive sooner. They are also easier to test, revert, and understand later from the project history.
