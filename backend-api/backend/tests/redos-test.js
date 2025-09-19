// backend-api/backend/tests/redos-test.js
// ❌ Vulnerability: ReDoS (catastrophic backtracking) via a bad regex

const express = require('express');
const router = express.Router();

// dangerously ambiguous nested quantifier
const badRegex = /^(a+)+$/;

router.get('/tstMe', (req, res) => {
  const input = req.query.input || 'aaaaaaaaaa';
  // This test may hang or be very slow for crafted long inputs
  const matched = badRegex.test(input);
  res.json({ inputLength: input.length, matched });
});

module.exports = router;
