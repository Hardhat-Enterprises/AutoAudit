# AutoAudit scaling test runbook (AKS)

End-to-end "deploy this on a fresh AKS cluster" sequence used for the
scaling demo. Companion to [`scaling-after.md`](./scaling-after.md) (the
"what changed and why" doc) and the two component READMEs:

- [`infrastructure/monitoring/in-cluster/README.md`](../../infrastructure/monitoring/in-cluster/README.md) — Prometheus / Grafana / KEDA / celery-exporter
- [`tests/load/in-cluster/README.md`](../../tests/load/in-cluster/README.md) — in-cluster k6 load runner

If you're re-running this after a teardown, skip whatever you've already
done — every step is idempotent.

## Prerequisites

| What | Why |
|---|---|
| `kubectl` configured for the target AKS cluster | Everything that follows |
| `helm` v3+ | KEDA, Prometheus, Grafana, AutoAudit |
| `az` logged in to the subscription holding the ACR | Image push (or `az acr login -n autoaudit`) |
| `docker` | Local builds of the 5 service images |
| Git Bash (Windows) or any POSIX shell | The launcher scripts in `tests/load/in-cluster/` are bash |
| AKS metrics-server present | HPA needs it. Default on AKS, no action. |
| AKS↔ACR pull permission | Either ACR attached to AKS via `az aks update --attach-acr`, or imagePullSecret. |

## 1. Namespace + Secret

```bash
kubectl create namespace autoaudit

# Generate and create the autoaudit-secrets Secret (4 keys the chart requires).
# Keep /tmp/autoaudit-creds.env somewhere safe — Secrets cannot be retrieved
# in cleartext after creation.
python -c "
import secrets
from cryptography.fernet import Fernet
print(f'PG_PASS={secrets.token_urlsafe(24)}')
print(f'JWT_SECRET={secrets.token_urlsafe(48)}')
print(f'FERNET={Fernet.generate_key().decode()}')
print(f'REDIS_PASS={secrets.token_urlsafe(24)}')
" > /tmp/autoaudit-creds.env
source /tmp/autoaudit-creds.env

kubectl create secret generic autoaudit-secrets -n autoaudit \
  --from-literal=postgresql-password="$PG_PASS" \
  --from-literal=jwt-secret-key="$JWT_SECRET" \
  --from-literal=encryption-key="$FERNET" \
  --from-literal=redis-password="$REDIS_PASS"
```

## 2. KEDA + monitoring stack

Follow the install block in
[`infrastructure/monitoring/in-cluster/README.md`](../../infrastructure/monitoring/in-cluster/README.md#install-order-matters).
It installs (in order):

1. KEDA (namespace-scoped to `autoaudit`, with `prometheus.operator.enabled=true` so the queue-depth metric is exposed)
2. Prometheus + kube-state-metrics
3. celery-exporter
4. Dashboard ConfigMap
5. Grafana

## 3. Images in ACR

> **Heads-up for future students / maintainers.** `autoaudit.azurecr.io`
> was set up as a **temporary registry for testing purposes only**. It
> does **not** live in a long-lived or university-owned Azure
> subscription and will be torn down once the scaling proof-of-concept
> is complete. Do **not** assume it will still resolve, and do **not**
> depend on the tags that are pushed there. The "move CI/CD to a
> project-owned ACR" story is captured in
> [saas-scaling-aks-platform.md §5](./saas-scaling-aks-platform.md#5-image--build-supply-chain);
> when you re-run this runbook, substitute your own registry (any OCI
> registry works — ACR, GHCR, Docker Hub) and update
> `helm/autoaudit/values-scaling.yaml` accordingly.

The five custom images live in `autoaudit.azurecr.io/autoaudit/{backend-api,
worker, frontend, opa, powershell-service}`. Existing tags (e.g.
`20260523-1de7943`) were pushed during the original test and are still
valid *while the registry exists*; only rebuild when chart-affecting code changes.

Rebuild + push (run from repo root):

```bash
az acr login -n autoaudit

# Compose-built images. backend-api / worker / powershell-service / frontend
docker compose --profile all build
TAG="$(date +%Y%m%d)-$(git rev-parse --short=7 HEAD)"
for svc in backend-api worker frontend powershell-service; do
  docker tag "autoaudit-${svc}:latest" "autoaudit.azurecr.io/autoaudit/${svc}:latest"
  docker tag "autoaudit-${svc}:latest" "autoaudit.azurecr.io/autoaudit/${svc}:${TAG}"
  docker push "autoaudit.azurecr.io/autoaudit/${svc}:latest"
  docker push "autoaudit.azurecr.io/autoaudit/${svc}:${TAG}"
done

# Custom OPA image (policies baked in) — build context MUST be repo root.
docker build -f engine/opa/Dockerfile \
  -t autoaudit.azurecr.io/autoaudit/opa:latest \
  -t autoaudit.azurecr.io/autoaudit/opa:${TAG} .
docker push autoaudit.azurecr.io/autoaudit/opa:latest
docker push autoaudit.azurecr.io/autoaudit/opa:${TAG}
```

Important: the frontend MUST be built from `frontend/Dockerfile.prod` (nginx
serving the built bundle). Compose uses `frontend/Dockerfile` (vite dev
server on :3000) which mismatches the chart's Service port 80 — pods crash-loop.
The compose `--profile all build` uses the dev Dockerfile, so for the chart
you need:

```bash
docker build -f frontend/Dockerfile.prod \
  -t autoaudit.azurecr.io/autoaudit/frontend:latest \
  -t autoaudit.azurecr.io/autoaudit/frontend:${TAG} ./frontend
docker push autoaudit.azurecr.io/autoaudit/frontend:latest
docker push autoaudit.azurecr.io/autoaudit/frontend:${TAG}
```

## 4. Install the chart

```bash
helm upgrade --install autoaudit ./helm/autoaudit \
  -n autoaudit \
  -f ./helm/autoaudit/values-scaling.yaml \
  --wait --timeout 10m
```

`values-scaling.yaml` is the demo overlay — HPA + KEDA + PDBs + synthetic
load levers all enabled, with maxReplicas tuned for a 2–3 node AKS cluster.
Don't use `values-poc.yaml` for the scaling demo (it disables autoscaling).

## 5. Smoke check

```bash
kubectl get deploy,hpa,pdb,scaledobject -n autoaudit
```

Expected: **9 Deployments** (5 services + 3 worker queues + redis), **1 StatefulSet** (postgresql),
**4 HPAs** + **3 KEDA-managed HPAs** = 7 HPA objects total, **7 PDBs**, **3 ScaledObjects**
all `READY=True`, **1 TriggerAuthentication**.

## 6. Fire load tests

Per [`tests/load/in-cluster/README.md`](../../tests/load/in-cluster/README.md#fire-it):

```bash
# Full demo (api-baseline → 60s cooldown → scan-fanout)
bash tests/load/in-cluster/demo.sh

# Or one phase at a time
bash tests/load/in-cluster/run.sh api-baseline.js
bash tests/load/in-cluster/run.sh scan-fanout.js -e N_GRAPH=150 -e N_POWERSHELL=50
```

## Teardown

```bash
# 1. The chart (delete PVC so a fresh install gets a fresh database).
helm -n autoaudit uninstall autoaudit
kubectl delete pvc -n autoaudit -l app.kubernetes.io/instance=autoaudit

# 2. Monitoring stack (per the in-cluster monitoring README teardown).
helm -n autoaudit uninstall grafana prometheus
kubectl -n autoaudit delete -f infrastructure/monitoring/in-cluster/celery-exporter.yaml
kubectl -n autoaudit delete configmap autoaudit-scaling-dashboard

# 3. KEDA (cluster-wide CRDs).
helm -n keda uninstall keda
kubectl delete namespace keda

# 4. autoaudit namespace (drops the Secrets too — re-create per step 1 next time).
kubectl delete namespace autoaudit
```

Then scale the AKS node pool back down via the Azure portal / CLI to stop
the bill.

## Gotchas hit during the first run

The `Chart bugs found and fixed during AKS testing` section of
[`scaling-after.md`](./scaling-after.md#chart-bugs-found-and-fixed-during-aks-testing)
lists each one with the file/line. Skim it before re-running on a new
cluster — most of the fixes are already merged into the chart, but the
list explains the why.
