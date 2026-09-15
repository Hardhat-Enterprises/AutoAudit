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
    const author = pr.user.login;
    const { data: pastPRs } = await github.rest.search.issuesAndPullRequests({
      q: `repo:${owner}/${repo} type:pr author:${author}`,
    });
    if (pastPRs.total_count <= 1) {
      await github.rest.issues.addLabels({ owner, repo, issue_number: pr_number, labels: ["first-contribution"] });
    }
  }
}

module.exports = { labelOne, sizeTier };
