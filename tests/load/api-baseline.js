// api-baseline.js — drives backend-api HPA scaling.
//
// Hits /v1/test/protected (auth-required, no DB) at a ramping RPS so the
// backend-api HPA reacts on CPU and per-pod RPS. Pairs with the Grafana
// "Pod counts" + "Backend-api RPS + p95 latency" panels.
//
// Run:
//   k6 run tests/load/api-baseline.js \
//     -e AUTOAUDIT_BASE_URL=http://autoaudit.dev/api \
//     -e AUTOAUDIT_TOKEN=$AUTOAUDIT_TOKEN

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

const BASE_URL = __ENV.AUTOAUDIT_BASE_URL || 'http://localhost:8000';
const TOKEN = __ENV.AUTOAUDIT_TOKEN || '';

if (!TOKEN) {
  throw new Error('AUTOAUDIT_TOKEN env var is required (Bearer JWT).');
}

export const options = {
  scenarios: {
    rps_ramp: {
      executor: 'ramping-arrival-rate',
      startRate: 5,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 400,
      stages: [
        { duration: '2m', target: 200 }, // ramp to 200 RPS
        { duration: '2m', target: 200 }, // hold
        { duration: '1m', target: 0 },   // ramp down
      ],
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.02'],          // <2% errors
    http_req_duration: ['p(95)<500'],        // p95 under 500ms
  },
};

const headers = {
  Authorization: `Bearer ${TOKEN}`,
  'Content-Type': 'application/json',
};

const protectedLatency = new Trend('autoaudit_protected_latency_ms');

export default function () {
  const res = http.get(`${BASE_URL}/v1/test/protected`, { headers });
  protectedLatency.add(res.timings.duration);
  check(res, {
    'status 200': (r) => r.status === 200,
  });
  sleep(0.05);
}

export function handleSummary(data) {
  return {
    'tests/load/results/api-baseline-summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data),
  };
}

// Minimal textSummary for stdout — k6 has its own but it's terse on long runs.
function textSummary(data) {
  const m = data.metrics;
  return `
api-baseline summary
====================
HTTP requests:    ${m.http_reqs.values.count}
Avg RPS:          ${m.http_reqs.values.rate.toFixed(1)}
Failure rate:     ${(m.http_req_failed.values.rate * 100).toFixed(2)}%
p95 latency:      ${m.http_req_duration.values['p(95)'].toFixed(0)}ms
p99 latency:      ${m.http_req_duration.values['p(99)'].toFixed(0)}ms
Max latency:      ${m.http_req_duration.values.max.toFixed(0)}ms
`;
}
