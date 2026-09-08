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
// The Search API has a much stricter *secondary* rate limit (30
// requests/minute) than every other endpoint this codebase calls — easy
// to exceed calling it once per PR when backfilling many at once, which
// is exactly what happened the first time a real backfill ran at scale.
// Rather than just tolerating that limit (retries, pacing delays), this
// avoids the endpoint entirely: fetch the full PR list once per process
// (a handful of calls against the generous core rate limit, however many
// PRs exist), cache it, and derive "is this author's first PR" from that
// — O(PRs/100) calls total for an entire run, not one Search call per PR.
let prCountsByAuthorPromise = null;

async function getPrCountsByAuthor(github, owner, repo) {
  if (!prCountsByAuthorPromise) {
    prCountsByAuthorPromise = github
      .paginate(github.rest.pulls.list, { owner, repo, state: "all", per_page: 100 })
      .then((allPrs) => {
        const counts = new Map();
        for (const p of allPrs) {
          const login = p.user?.login;
          if (!login) continue;
          counts.set(login, (counts.get(login) || 0) + 1);
        }
        return counts;
      });
  }
  return prCountsByAuthorPromise;
}

async function isFirstContribution(github, owner, repo, author) {
  try {
    const counts = await getPrCountsByAuthor(github, owner, repo);
    return (counts.get(author) || 0) <= 1;
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
