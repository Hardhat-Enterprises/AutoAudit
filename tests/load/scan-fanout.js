// scan-fanout.js — drives the headline worker scaling story.
//
// POSTs synthetic-scan requests that fan out into many synthetic_evaluate
// tasks across both `controls.graph` and `controls.powershell` queues, with
// the powershell tasks optionally calling /execute/synthetic on the
// powershell-service. Pairs with the Grafana "Pod counts", "KEDA queue
// depths", "Worker tasks/sec/queue", and "PowerShell active subprocesses"
// panels — this script is the one that lights up the whole dashboard.
//
// Run:
//   k6 run tests/load/scan-fanout.js \
//     -e AUTOAUDIT_BASE_URL=http://autoaudit.dev/api \
//     -e AUTOAUDIT_TOKEN=$AUTOAUDIT_TOKEN

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.AUTOAUDIT_BASE_URL || 'http://localhost:8000';
const TOKEN = __ENV.AUTOAUDIT_TOKEN || '';
// Per-pulse scan size — tune up if the queues drain faster than scaling can react.
// Defaults are sized so the queues drain within ~2 min of load stopping; bigger
// values leave too many tasks in the queue past the end of the test window.
const N_GRAPH = parseInt(__ENV.N_GRAPH || '80', 10);
const N_POWERSHELL = parseInt(__ENV.N_POWERSHELL || '25', 10);
const SLEEP_MS = parseInt(__ENV.SLEEP_MS || '2000', 10);
const CPU_BURN_MS = parseInt(__ENV.CPU_BURN_MS || '200', 10);
const CALL_PWSH = (__ENV.CALL_POWERSHELL_SERVICE || 'true').toLowerCase() === 'true';

if (!TOKEN) {
  throw new Error('AUTOAUDIT_TOKEN env var is required (Bearer JWT).');
}

export const options = {
  scenarios: {
    pulses: {
      executor: 'ramping-arrival-rate',
      startRate: 1,
      timeUnit: '10s',
      preAllocatedVUs: 5,
      maxVUs: 20,
      stages: [
        { duration: '2m', target: 6 },    // ramp into demand — KEDA scales up
        { duration: '2m', target: 6 },    // hold — pods reach steady state
        { duration: '1m', target: 0 },    // ramp down — KEDA scales back down
        { duration: '4m', target: 0 },    // observe scale-down + queue drain inside the test window so the demo recording captures the full cycle
      ],
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.05'],
    'http_req_duration{endpoint:synthetic-scan}': ['p(95)<2000'],
  },
};

const headers = {
  Authorization: `Bearer ${TOKEN}`,
  'Content-Type': 'application/json',
};

export default function () {
  const body = JSON.stringify({
    n_graph: N_GRAPH,
    n_powershell: N_POWERSHELL,
    sleep_ms: SLEEP_MS,
    cpu_burn_ms: CPU_BURN_MS,
    call_powershell_service: CALL_PWSH,
  });
  const res = http.post(`${BASE_URL}/v1/test/synthetic-scan`, body, {
    headers,
    tags: { endpoint: 'synthetic-scan' },
  });
  check(res, {
    'status 200': (r) => r.status === 200,
    'body has queued count': (r) => r.json('queued.graph') !== undefined,
  });
  sleep(0.2);
}

export function handleSummary(data) {
  return {
    'tests/load/results/scan-fanout-summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data),
  };
}

function textSummary(data) {
  const m = data.metrics;
  return `
scan-fanout summary
===================
Pulses fired:     ${m.http_reqs.values.count}
Tasks queued:     ~${m.http_reqs.values.count * (N_GRAPH + N_POWERSHELL)} (${N_GRAPH} graph + ${N_POWERSHELL} powershell per pulse)
Per-task sleep:   ${SLEEP_MS}ms (cpu_burn ${CPU_BURN_MS}ms)
Powershell call:  ${CALL_PWSH}
Failure rate:     ${(m.http_req_failed.values.rate * 100).toFixed(2)}%
p95 latency:      ${m.http_req_duration.values['p(95)'].toFixed(0)}ms
Max latency:      ${m.http_req_duration.values.max.toFixed(0)}ms
`;
}
