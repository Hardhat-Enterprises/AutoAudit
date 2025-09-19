// backend-api/backend/test-server.js
const express = require('express');
const app = express();

// require the test routes relative to this file
const sql = require('./tests/sql-injection.js');
const redos = require('./tests/redos-test.js');

app.use('/sql', sql);
app.use('/redos', redos);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Test server listening on http://localhost:${PORT}`);
});
