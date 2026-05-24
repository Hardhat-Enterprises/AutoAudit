# In-cluster k6 load runner

Runs k6 inside the AKS cluster against the in-namespace `autoaudit-backend-api`
Service. Traffic load-balances across all backend-api pods via kube-proxy —
unlike `kubectl port-forward` which only forwards to a single pod.

## Files

| File | Purpose |
|---|---|
| `run.sh` | Refresh the script ConfigMap, render the Job, follow logs. |
| `k6-job.yaml` | Job template — init container logs in and writes the JWT to a shared volume, k6 container reads the token and runs the script. |
| `demo.sh` | Orchestrates `api-baseline.js` → 60s cooldown → `scan-fanout.js` for the full scaling story. |

## Prerequisites

The chart auto-generates the admin password into the `autoaudit-admin` Secret
on first install — the in-cluster Job picks it up automatically. To verify or
log in from elsewhere:

```bash
kubectl get secret -n autoaudit autoaudit-admin -o jsonpath='{.data.admin-password}' | base64 -d
```

Default username is always `admin@example.com`.

For live observation during runs, put each port-forward in its own
terminal (they block):

```bash
kubectl -n autoaudit port-forward svc/grafana 3001:80          # http://localhost:3001  admin / admin
kubectl -n autoaudit port-forward svc/prometheus-server 9090:80 # http://localhost:9090
```

## Fire it

```bash
# 1. Light HTTP load against backend-api (HPA, p95/p99 in Grafana)
bash tests/load/in-cluster/run.sh api-baseline.js

# 2. Worker / KEDA / powershell-service / OPA load — pass smaller per-pulse
#    sizes than the script defaults to fit comfortably on 2 nodes
bash tests/load/in-cluster/run.sh scan-fanout.js -e N_GRAPH=20 -e N_POWERSHELL=10

# 3. Steady-state 10-min snapshot — only when ready for the panel run
bash tests/load/in-cluster/run.sh sustained.js

# 4. Full demo sequence — fires (1) then (2) back-to-back with a 60s pause
#    so backend-api HPA scales back to min before the worker phase starts.
#    Best single command to show the whole scaling story on Grafana.
bash tests/load/in-cluster/demo.sh
```

Each invocation creates a new Job (`generateName: k6-<script>-<rand>`), so
re-running does not collide. `ttlSecondsAfterFinished: 3600` cleans up an
hour after completion.

## Follow / inspect

The launcher already follows logs. To re-attach after disconnect:

```bash
kubectl -n autoaudit get jobs -l app.kubernetes.io/name=k6
kubectl -n autoaudit logs -f job/<name> --all-containers=true
```

## What happens under the hood

1. **Init container (`curlimages/curl`)** — `POST /v1/auth/login` with the
   admin password from the `autoaudit-admin` Secret, writes the access
   token to `/work/token` (shared `emptyDir`).
2. **Main container (`grafana/k6:0.55.0`)** — sources the token, exports
   `AUTOAUDIT_TOKEN` + `AUTOAUDIT_BASE_URL=http://autoaudit-backend-api.autoaudit:8000`,
   runs `k6 run /scripts/<script>` with any extra args.
