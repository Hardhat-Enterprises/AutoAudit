// Implements the 7/10/14-day rule as a "waiting on author" clock, plus a
// symmetric "waiting on maintainer" signal:
//
//   - The clock STARTS at the timestamp of the most recent maintainer
//     (write/admin permission) comment, review, or commit on the PR.
//   - The clock RESETS (clears) the moment the PR author or any other
//     non-maintainer contributor comments or pushes a commit *after*
//     that maintainer activity — they've responded. When this happens
//     after at least one prior maintainer engagement, the PR gets
//     `needs-review` immediately (no day threshold — a reviewer filtering
//     for "needs my attention" should see it the moment it happens).
//   - If a maintainer has never engaged with the PR at all, it gets
//     `needs-triage` instead — nobody has looked at it yet, so neither
//     "waiting on author" nor "waiting on maintainer" applies.
//   - Bots are ignored entirely (dependabot, github-actions[bot], etc.)
//   - Draft PRs and PRs already carrying a manual outcome label
//     (abandoned / needs-adoption / has-conflicts / wontfix) are skipped
//     — a human has already made the call, the bot shouldn't relitigate it.
//
// The four states below are mutually exclusive — a PR carries at most one:
//   needs-triage    -> no maintainer has ever engaged
//   needs-review    -> maintainer engaged, then someone else had the last word
//   (none)          -> maintainer engaged, waiting on author, under 7 days
//   stale / needs-decision / final-notice -> waiting on author, 7/10/14+ days

const { STATUS_LABELS } = require("./label-taxonomy.js");
const EXEMPT_LABELS = ["abandoned", "needs-adoption", "has-conflicts", "wontfix"];
const MS_PER_DAY = 24 * 60 * 60 * 1000;

// Overridable via env for testing (e.g. set to fractional-day values so a
// test run can observe real tier transitions in seconds instead of days).
// Unset -> real production values. See TESTING.md for how the test harness
// uses this.
function envDays(name, fallback) {
  const v = process.env[name];
  if (v === undefined || v === "") return fallback;
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
}
const DAYS_STALE = envDays("STALE_AFTER_DAYS", 7);
const DAYS_NEEDS_DECISION = envDays("NEEDS_DECISION_AFTER_DAYS", 10);
const DAYS_FINAL_NOTICE = envDays("FINAL_NOTICE_AFTER_DAYS", 14);

module.exports = async ({ github, context, core }) => {
  const { owner, repo } = context.repo;
  const permissionCache = new Map();

  async function isMaintainer(login) {
    if (!login) return false;
    if (permissionCache.has(login)) return permissionCache.get(login);
    let result = false;
    try {
      const { data } = await github.rest.repos.getCollaboratorPermissionLevel({
        owner,
        repo,
        username: login,
      });
      result = data.permission === "admin" || data.permission === "write";
    } catch (e) {
      result = false; // not a collaborator -> definitely not a maintainer
    }
    permissionCache.set(login, result);
    return result;
  }

  function isBot(login) {
    return !login || login.endsWith("[bot]");
  }

  const prsAll = await github.paginate(github.rest.pulls.list, {
    owner,
    repo,
    state: "open",
    per_page: 100,
  });

  const only = process.env.ONLY_PR_NUMBER ? Number(process.env.ONLY_PR_NUMBER) : null;
  const prs = only ? prsAll.filter((p) => p.number === only) : prsAll;

  if (only) {
    core.info(`ONLY_PR_NUMBER set — restricting this run to PR #${only} only`);
  }
  core.info(`Scanning ${prs.length} open PRs`);

  for (const pr of prs) {
    const pr_number = pr.number;
    const labelNames = pr.labels.map((l) => l.name);

    if (pr.draft) {
      core.info(`#${pr_number}: draft, skipping`);
      continue;
    }
    if (labelNames.some((n) => EXEMPT_LABELS.includes(n))) {
      core.info(`#${pr_number}: has manual outcome label, skipping`);
      continue;
    }

    // Gather every timestamped human event on the PR.
    const events = [];

    const [issueComments, reviewComments, reviews, commits] = await Promise.all([
      github.paginate(github.rest.issues.listComments, { owner, repo, issue_number: pr_number, per_page: 100 }),
      github.paginate(github.rest.pulls.listReviewComments, { owner, repo, pull_number: pr_number, per_page: 100 }),
      github.paginate(github.rest.pulls.listReviews, { owner, repo, pull_number: pr_number, per_page: 100 }),
      github.paginate(github.rest.pulls.listCommits, { owner, repo, pull_number: pr_number, per_page: 100 }),
    ]);

    for (const c of issueComments) {
      events.push({ login: c.user?.login, time: c.created_at });
    }
    for (const c of reviewComments) {
      events.push({ login: c.user?.login, time: c.created_at });
    }
    for (const r of reviews) {
      if (r.submitted_at) events.push({ login: r.user?.login, time: r.submitted_at });
    }
    for (const c of commits) {
      const login = c.author?.login; // null if commit email isn't linked to a GH account
      const time = c.commit?.author?.date;
      if (login && time) events.push({ login, time });
    }

    events.sort((a, b) => new Date(a.time) - new Date(b.time));

    const authorLogin = pr.user?.login;
    let clockStart = null;
    let anyMaintainerEver = false;

    for (const ev of events) {
      if (isBot(ev.login)) continue;
      // The PR's own author never counts as "a maintainer engaged with
      // this" — even if that author happens to hold write/admin
      // permission on the repo (e.g. the repo owner opening their own
      // test PR, or a collaborator pushing their own commits). Only a
      // *different* person with write/admin permission starts the clock.
      const isSelf = ev.login === authorLogin;
      const maintainer = !isSelf && (await isMaintainer(ev.login));
      if (maintainer) {
        anyMaintainerEver = true;
        clockStart = ev.time; // maintainer activity (re)starts the clock
      } else {
        clockStart = null; // non-maintainer response clears it
      }
    }

    const currentStatusLabel = labelNames.find((n) => STATUS_LABELS.includes(n)) ?? null;

    let targetLabel;
    if (!anyMaintainerEver) {
      // Nobody has reviewed this yet — waiting-on-author tiers don't apply.
      targetLabel = "needs-triage";
    } else if (clockStart) {
      // Most recent engagement was a maintainer's — waiting on the author.
      // Only the passage of time itself makes this actionable, so nothing
      // is applied until a threshold is actually crossed.
      const days = (Date.now() - new Date(clockStart).getTime()) / MS_PER_DAY;
      if (days >= DAYS_FINAL_NOTICE) targetLabel = "final-notice";
      else if (days >= DAYS_NEEDS_DECISION) targetLabel = "needs-decision";
      else if (days >= DAYS_STALE) targetLabel = "stale";
      else targetLabel = null;
    } else {
      // A maintainer engaged at some point, but the most recent event was
      // someone else (the author, or another non-maintainer) responding
      // after that — the ball is back in the maintainer's court. Unlike
      // the waiting-on-author tiers, this is actionable immediately: a
      // reviewer filtering by label should see it the moment it happens,
      // not after some elapsed-time threshold.
      targetLabel = "needs-review";
    }

    core.info(`#${pr_number}: clockStart=${clockStart}, anyMaintainerEver=${anyMaintainerEver} -> ${targetLabel ?? "none"}`);

    if (currentStatusLabel !== targetLabel) {
      if (currentStatusLabel) {
        await github.rest.issues.removeLabel({ owner, repo, issue_number: pr_number, name: currentStatusLabel }).catch(() => {});
      }
      if (targetLabel) {
        await github.rest.issues.addLabels({ owner, repo, issue_number: pr_number, labels: [targetLabel] });
      }
    }
  }
};
