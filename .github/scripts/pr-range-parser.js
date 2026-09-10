// Parses printer-style number ranges (the same syntax used by print
// dialogs' "page range" field): "1,5,7-9" -> [1, 5, 7, 8, 9].
// Dedupes and returns ascending order. Throws a descriptive error on any
// malformed token rather than silently skipping it — for a tool that
// removes labels in bulk, a silently-dropped PR number is worse than a
// loud failure.

function parsePrRanges(input) {
  if (!input || !input.trim()) {
    throw new Error('No PR numbers provided (expected e.g. "5" or "1,5,7-9").');
  }

  const numbers = new Set();
  const tokens = input
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

  for (const token of tokens) {
    const rangeMatch = token.match(/^(\d+)\s*-\s*(\d+)$/);
    if (rangeMatch) {
      const start = Number(rangeMatch[1]);
      const end = Number(rangeMatch[2]);
      if (start > end) {
        throw new Error(`Invalid range "${token}": start (${start}) is greater than end (${end}).`);
      }
      for (let n = start; n <= end; n++) numbers.add(n);
    } else if (/^\d+$/.test(token)) {
      numbers.add(Number(token));
    } else {
      throw new Error(`Could not parse "${token}" as a PR number or range (expected e.g. "5" or "7-9").`);
    }
  }

  return [...numbers].sort((a, b) => a - b);
}

module.exports = { parsePrRanges };
