# Scaling load tests

k6 scripts that drive the synthetic load levers in the AutoAudit chart so
HPAs / KEDA ScaledObjects scale up under recordable, repeatable load.

## Prerequisites

- k6 installed (`brew install k6` / `choco install k6` / [k6.io/docs/get-started/installation/](https://k6.io/docs/get-started/installation/)).
- Chart deployed with `synthetic.enabled=true` and the relevant `autoscaling.enabled=true` / `keda.enabled=true` per workload.
- Authenticated session: most scripts need a JWT. Set the `AUTOAUDIT_TOKEN` env var to a Bearer token from `POST /v1/auth/login`.
- `AUTOAUDIT_BASE_URL` defaults to `http://localhost:8000`. Set to your AKS ingress URL for cluster runs.

## Scripts

| Script | What it drives | Ramp |
|---|---|---|
| [`api-baseline.js`](./api-baseline.js) | backend-api HPA (CPU + RPS) | `0 → 200 RPS` over 2 min, hold 2 min, ramp down 1 min |
| [`scan-fanout.js`](./scan-fanout.js) | worker per-queue KEDA, OPA HPA, powershell-service HPA | Pulses of synthetic-scan POSTs that fan out to controls.graph + controls.powershell + (optional) powershell-service |
| [`sustained.js`](./sustained.js) | All of the above at moderate steady-state (10 min) for the "after" snapshot |

## Usage

```bash
# 1. log in and grab a token
export AUTOAUDIT_TOKEN=$(
  curl -s -X POST "$AUTOAUDIT_BASE_URL/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@example.com&password=admin" \
    | jq -r .access_token
)

# 2. run a script
k6 run tests/load/scan-fanout.js \
  -e AUTOAUDIT_BASE_URL=http://autoaudit.dev/api \
  -e AUTOAUDIT_TOKEN="$AUTOAUDIT_TOKEN"
```

Each script writes a JSON summary to `tests/load/results/<name>-<timestamp>.json`
(creates the directory if missing). Capture these alongside the Grafana
screenshots for the after-doc.
