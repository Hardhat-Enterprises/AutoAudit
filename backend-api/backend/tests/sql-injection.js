// backend-api/backend/tests/sql-injection.js
// ❌ Linting error intentionally added: unused variable `noor`
// ❌ Vulnerability: SQL injection via string concatenation (unsafe)

const express = require('express');
const router = express.Router();
const sqlite3 = require('sqlite3').verbose();

// unused var to trigger ESLint no-unused-vars
let noor = "noor";

const db = new sqlite3.Database(':memory:');

// create a tiny table for demonstration
db.serialize(() => {
  db.run("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)");
  db.run("INSERT INTO users (name) VALUES ('Alice')");
  db.run("INSERT INTO users (name) VALUES ('Bob')");
});

// Vulnerable endpoint: user input concatenated directly into SQL
router.get('/user', (req, res) => {
  const userId = req.query.id;
  // UNSAFE: direct string concatenation allows SQL injection
  const query = `SELECT * FROM users WHERE id = ${userId}`;

  db.all(query, [], (err, rows) => {
    if (err) {
      res.status(500).send('Error');
      return;
    }
    res.json(rows);
  });
});

module.exports = router;

// test trigger for CodeQL
