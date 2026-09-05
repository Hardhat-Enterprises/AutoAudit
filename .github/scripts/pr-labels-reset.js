// Clears automatically-managed labels from a chosen set of PRs — a
// "clean slate" tool for recovering from a bad test run, a config bug, or
// any other case where automated labels on real PRs need a manual reset.
//
// Only ever touches labels defined in label-taxonomy.js as "managed" —
// manually-curated labels (abandoned, needs-adoption, has-conflicts,
// wontfix, bug, enhancement, etc.) are never removed, since those always
// reflect a human decision this tool has no authority to undo.
//
// Safety defaults: dry_run is true unless explicitly set to "false", and
// even then a real run requires confirm to be exactly "RESET". Both
// guards exist because this script's whole purpose is bulk label removal
// — the one operation in this whole system where a mistake is annoying
// to fix by hand across many PRs at once.

const { parsePrRanges } = require("./pr-range-parser.js");
const { isManagedLabel } = require("./label-taxonomy.js");

function parseOnlyFilter(onlyInput) {
  if (!onlyInput || !onlyInput.trim()) return null; // null = no restriction, reset every managed label
  return onlyInput
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);
}

function matchesOnlyFilter(labelName, onlyTokens) {
  if (!onlyTokens) return true;
  return onlyTokens.some((t) => labelName === t || labelName.startsWith(t));
}

module.exports = async ({ github, context, core }) => {
  const { owner, repo } = context.repo;

  const allOpenPrs = (process.env.ALL_OPEN_PRS || "false") === "true";
  const openOnly = (process.env.OPEN_ONLY || "true") === "true";
  const dryRun = (process.env.DRY_RUN ?? "true") !== "false";
  const confirm = process.env.CONFIRM || "";
  const onlyTokens = parseOnlyFilter(process.env.ONLY_LABELS);

  if (!dryRun && confirm !== "RESET") {
    core.setFailed(
      'Refusing to make changes: dry_run is false but confirm is not exactly "RESET". ' +
        'Re-run with dry_run left as true to preview first, or set confirm to "RESET" to proceed.'
    );
    return;
  }

  let targetPrNumbers;
  if (allOpenPrs) {
    const openPrs = await github.paginate(github.rest.pulls.list, { owner, repo, state: "open", per_page: 100 });
    targetPrNumbers = openPrs.map((p) => p.number).sort((a, b) => a - b);
  } else {
    try {
      targetPrNumbers = parsePrRanges(process.env.PR_NUMBERS || "");
    } catch (e) {
      core.setFailed(`Could not parse pr_numbers: ${e.message}`);
      return;
    }
  }

  core.info(
    `${dryRun ? "[DRY RUN] " : ""}Processing ${targetPrNumbers.length} PR number(s): ${targetPrNumbers.join(", ")}`
  );
  if (onlyTokens) core.info(`Restricting to labels matching: ${onlyTokens.join(", ")}`);

  const summaryRows = [];

  for (const pr_number of targetPrNumbers) {
    let pr;
    try {
      const res = await github.rest.pulls.get({ owner, repo, pull_number: pr_number });
      pr = res.data;
    } catch (e) {
      core.warning(`#${pr_number}: not found or not accessible, skipping (${e.message})`);
      summaryRows.push([String(pr_number), "-", "skipped (not found)"]);
      continue;
    }

    if (openOnly && pr.state !== "open") {
      core.info(`#${pr_number}: state is "${pr.state}", open_only is set, skipping`);
      summaryRows.push([String(pr_number), pr.state, "skipped (not open)"]);
      continue;
    }

    const currentLabels = pr.labels.map((l) => l.name);
    const toRemove = currentLabels.filter((n) => isManagedLabel(n) && matchesOnlyFilter(n, onlyTokens));

    if (toRemove.length === 0) {
      core.info(`#${pr_number}: no matching managed labels present`);
      summaryRows.push([String(pr_number), pr.state, "no matching labels"]);
      continue;
    }

    core.info(`#${pr_number}: ${dryRun ? "would remove" : "removing"} ${toRemove.join(", ")}`);
    summaryRows.push([String(pr_number), pr.state, `${dryRun ? "would remove" : "removed"}: ${toRemove.join(", ")}`]);

    if (!dryRun) {
      for (const name of toRemove) {
        try {
          await github.rest.issues.removeLabel({ owner, repo, issue_number: pr_number, name });
        } catch (e) {
          core.warning(`#${pr_number}: failed to remove "${name}": ${e.message}`);
        }
      }
    }
  }

  await core.summary
    .addHeading(dryRun ? "PR Labels Reset — dry run (no changes made)" : "PR Labels Reset — changes applied")
    .addTable([[{ data: "PR", header: true }, { data: "State", header: true }, { data: "Result", header: true }], ...summaryRows])
    .write();
};
