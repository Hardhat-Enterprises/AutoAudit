// Single source of truth for which labels this system manages
// automatically, as opposed to labels that are always manually curated
// (abandoned, needs-adoption, has-conflicts, wontfix, bug, enhancement,
// etc.). Used by activity-labeler.js, pr-metadata-labeler.js, and
// pr-labels-reset.js so all three always agree on what "managed" means —
// a label added to automation elsewhere only needs to be added here once.

const AREA_PREFIX = "area: ";
const SIZE_PREFIX = "size/";

// Managed via the activity clock (activity-labeler.js)
const TIER_LABELS = ["stale", "needs-decision", "final-notice"];

// Every exact (non-prefixed) label name this system can apply on its own
const MANAGED_EXACT_LABELS = ["needs-triage", "first-contribution", "docker", "github_actions", ...TIER_LABELS];

function isManagedLabel(name) {
  return name.startsWith(AREA_PREFIX) || name.startsWith(SIZE_PREFIX) || MANAGED_EXACT_LABELS.includes(name);
}

module.exports = { AREA_PREFIX, SIZE_PREFIX, TIER_LABELS, MANAGED_EXACT_LABELS, isManagedLabel };
