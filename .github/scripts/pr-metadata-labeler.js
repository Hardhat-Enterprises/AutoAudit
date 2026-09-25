// Shared by pr.area-labeler.yml (fires per-PR) and pr.labels-backfill.yml
// (manual, loops all open PRs) — one source of truth for area:multi,
// size/*, and first-contribution so the two workflows can't drift apart.
//
const { AREA_PREFIX, SIZE_PREFIX } = require("./label-taxonomy.js");

// Size tiers are deliberately aligned with ops/pr.size-warning.yml's
// warning condition (total lines > 500 OR files changed > 30): size/XL
// fires on exactly that condition, so a PR the size-warning workflow
// flags as large is never sitting in a smaller size/* bucket here.
// Mid-tier boundaries (S/M/L) are ours alone to tune and don't need to
// match anything external.
const SIZE_WARNING_LINES = 500;
const SIZE_WARNING_FILES = 30;

function sizeTier(totalLines, filesChanged) {
  if (totalLines > SIZE_WARNING_LINES || filesChanged > SIZE_WARNING_FILES) return `${SIZE_PREFIX}XL`;
  if (totalLines >= 250) return `${SIZE_PREFIX}L`;
  if (totalLines >= 100) return `${SIZE_PREFIX}M`;
  if (totalLines >= 10) return `${SIZE_PREFIX}S`;
  return `${SIZE_PREFIX}XS`;
}

// --- first-contribution ---
// Deliberately NOT using GitHub's Search API here — it has a much
// stricter *secondary* rate limit (30/min) than everything else this
// codebase calls, and hitting it once per PR is what caused a real
// backfill to fail partway the first time this ran at scale.
//
// Also deliberately NOT fetching the repo's full PR history and caching
// it in memory (an earlier version of this file did exactly that): that
// works fine for a single backfill process looping over many PRs, but
// pr.area-labeler.yml runs this in a FRESH process for every single
// real-time PR event — so that cache was empty every time it mattered,
// and "fixing" the backfill case reintroduced the same scaling problem
// on the far more frequent real-time path (every open/push/reopen event,
// on every PR, forever, would refetch the entire repo's PR history just
// to check one author).
//
// Instead: `creator` filters server-side to just this one author's items
// — cheap in both contexts regardless of total repo size — and this
// stops paginating the instant it's seen enough to know the answer.
async function isFirstContribution(github, owner, repo, author) {
  try {
    let prCount = 0;
    let page = 1;
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { data } = await github.rest.issues.listForRepo({
        owner,
        repo,
        creator: author,
        state: "all",
        per_page: 100,
        page,
      });
      for (const item of data) {
        // listForRepo returns issues AND PRs by this author — `pull_request`
        // is only present on the PR ones, which is all we're counting.
        if (item.pull_request) prCount++;
        if (prCount > 1) return false; // already confirmed not their first — stop here, no need to see the rest
      }
      if (data.length < 100) break; // last page
      page++;
    }
    return prCount <= 1;
  } catch (e) {
    // A missing "nice to have" label is a much smaller problem than
    // letting this crash the caller's loop — log and move on.
    console.warn(`first-contribution check failed for ${author}: ${e.message}`);
    return false;
  }
}

async function labelOne({ github, owner, repo, pr }) {
  const pr_number = pr.number;
  const { data: current } = await github.rest.issues.get({ owner, repo, issue_number: pr_number });
  const labelNames = current.labels.map((l) => l.name);

  // --- area: multi rollup ---
  const areaLabels = labelNames.filter((n) => n.startsWith(AREA_PREFIX) && n !== "area: multi");
  const hasMulti = labelNames.includes("area: multi");
  if (areaLabels.length > 1 && !hasMulti) {
    await github.rest.issues.addLabels({ owner, repo, issue_number: pr_number, labels: ["area: multi"] });
  } else if (areaLabels.length <= 1 && hasMulti) {
    await github.rest.issues.removeLabel({ owner, repo, issue_number: pr_number, name: "area: multi" }).catch(() => {});
  }

  // --- size/* — recalculated every call, so it moves down as well as up ---
  const total = pr.additions + pr.deletions;
  const size = sizeTier(total, pr.changed_files || 0);
  const existingSize = labelNames.find((n) => n.startsWith(SIZE_PREFIX));
  if (existingSize !== size) {
    if (existingSize) {
      await github.rest.issues.removeLabel({ owner, repo, issue_number: pr_number, name: existingSize }).catch(() => {});
    }
    await github.rest.issues.addLabels({ owner, repo, issue_number: pr_number, labels: [size] });
  }

  // --- first-contribution (sticky once set, cheap to skip re-checking) ---
  if (!labelNames.includes("first-contribution")) {
    if (await isFirstContribution(github, owner, repo, pr.user.login)) {
      await github.rest.issues.addLabels({ owner, repo, issue_number: pr_number, labels: ["first-contribution"] });
    }
  }
}

module.exports = { labelOne, sizeTier };
