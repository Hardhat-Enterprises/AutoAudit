// sustained.js — 10-minute steady-state run for the "after" snapshot of
// resource usage at scale. Mixes API and scan-fanout load. Use this to
// capture the dashboard screenshots that show every pool stable at its
// scaled-out size.
//
// Run:
//   k6 run tests/load/sustained.js \
//     -e AUTOAUDIT_BASE_URL=http://autoaudit.dev/api \
//     -e AUTOAUDIT_TOKEN=$AUTOAUDIT_TOKEN

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.AUTOAUDIT_BASE_URL || 'http://localhost:8000';
const TOKEN = __ENV.AUTOAUDIT_TOKEN || '';

if (!TOKEN) {
  throw new Error('AUTOAUDIT_TOKEN env var is required (Bearer JWT).');
}

export const options = {
  scenarios: {
    api: {
      executor: 'constant-arrival-rate',
      rate: 80,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 30,
      maxVUs: 200,
      exec: 'apiTraffic',
    },
    fanout: {
      executor: 'constant-arrival-rate',
      rate: 4,
      timeUnit: '10s',
      duration: '10m',
      preAllocatedVUs: 5,
      maxVUs: 15,
      exec: 'fanoutPulse',
    },
  },
  thresholds: {
    'http_req_failed{endpoint:protected}': ['rate<0.02'],
    'http_req_failed{endpoint:synthetic-scan}': ['rate<0.05'],
    'http_req_duration{endpoint:protected}': ['p(95)<500'],
  },
};

const headers = {
  Authorization: `Bearer ${TOKEN}`,
  'Content-Type': 'application/json',
};

export function apiTraffic() {
  const res = http.get(`${BASE_URL}/v1/test/protected`, {
    headers,
    tags: { endpoint: 'protected' },
  });
  check(res, { 'protected 200': (r) => r.status === 200 });
}

export function fanoutPulse() {
  const body = JSON.stringify({
    n_graph: 80,
    n_powershell: 30,
    sleep_ms: 2500,
    cpu_burn_ms: 30,
    call_powershell_service: true,
  });
  const res = http.post(`${BASE_URL}/v1/test/synthetic-scan`, body, {
    headers,
    tags: { endpoint: 'synthetic-scan' },
  });
  check(res, { 'synthetic-scan 200': (r) => r.status === 200 });
}

export function handleSummary(data) {
  return {
    'tests/load/results/sustained-summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data),
  };
}

function textSummary(data) {
  const m = data.metrics;
  return `
sustained summary (10m)
=======================
API requests:     ${m['http_reqs'].values.count}
API failure rate: ${(m['http_req_failed'].values.rate * 100).toFixed(2)}%
API p95 latency:  ${m.http_req_duration.values['p(95)'].toFixed(0)}ms
`;
}
