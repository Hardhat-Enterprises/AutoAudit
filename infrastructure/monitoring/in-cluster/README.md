# In-cluster monitoring for the scaling demo

Plain Prometheus + Grafana running in the `autoaudit` namespace, scraping
the AutoAudit chart's pods + KEDA + celery-exporter directly. Deliberately
avoids `kube-prometheus-stack` so no cluster-wide CRDs (PodMonitor,
ServiceMonitor, PrometheusRule) are added on the shared AKS cluster.

## What gets installed

| Chart / manifest | Namespace | Provides |
|---|---|---|
| `kedacore/keda` (helm) | `keda` | KEDA operator (namespace-scoped to `autoaudit`). The `prometheus.operator.enabled=true` flag is what exposes `keda_scaler_metrics_value` on the operator pod's `/metrics:8080`. |
| `prometheus-community/prometheus` (helm) | `autoaudit` | Prometheus server + kube-state-metrics |
| `grafana/grafana` (helm) | `autoaudit` | Grafana (sidecar auto-loads dashboards) |
| `celery-exporter.yaml` (plain manifest) | `autoaudit` | `danihodovic/celery-exporter` Deployment + Service. Requires worker `worker_send_task_events=True` (already configured in `engine/worker/celery_app.py`). |
| Dashboard ConfigMap | `autoaudit` | Wraps [`../dashboards/autoaudit-scaling.json`](../dashboards/autoaudit-scaling.json) so the Grafana sidecar picks it up. |

## Install (order matters)

```bash
helm repo add kedacore https://kedacore.github.io/charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# 1. KEDA — namespace-scoped, with operator + metricServer prometheus metrics enabled.
#    Without these flags, keda_scaler_metrics_value (queue depth panel) returns no data.
helm upgrade --install keda kedacore/keda \
  -n keda --create-namespace \
  --set watchNamespace=autoaudit \
  --set prometheus.operator.enabled=true \
  --set prometheus.metricServer.enabled=true \
  --wait --timeout 5m

# 2. Prometheus + kube-state-metrics. 15s scrape (NOT default 30s) so the
#    dashboard's rate(...[1m]) queries get enough samples to render cleanly.
helm upgrade --install prometheus prometheus-community/prometheus \
  -n autoaudit \
  -f infrastructure/monitoring/in-cluster/prometheus-values.yaml \
  --wait --timeout 5m

# 3. celery-exporter Deployment + Service (scrapes worker events from Redis,
#    exposes celery_task_succeeded_total / celery_task_failed_total / runtime).
kubectl apply -f infrastructure/monitoring/in-cluster/celery-exporter.yaml

# 4. Dashboard ConfigMap — sidecar picks up any CM with grafana_dashboard=1 label.
kubectl -n autoaudit create configmap autoaudit-scaling-dashboard \
  --from-file=autoaudit-scaling.json=infrastructure/monitoring/dashboards/autoaudit-scaling.json
kubectl -n autoaudit label configmap autoaudit-scaling-dashboard grafana_dashboard=1

# 5. Grafana
helm upgrade --install grafana grafana/grafana \
  -n autoaudit \
  -f infrastructure/monitoring/in-cluster/grafana-values.yaml \
  --wait --timeout 5m
```

## Access

```bash
# Prometheus UI
kubectl -n autoaudit port-forward svc/prometheus-server 9090:80
# → http://localhost:9090/targets to confirm all scrape jobs are UP

# Grafana
kubectl -n autoaudit port-forward svc/grafana 3001:80
# → http://localhost:3001 (admin / admin)
# → Dashboards → "AutoAudit — Scaling Demo"
```

## What works on day one and what doesn't

The autoaudit-scaling dashboard has 14 panels. After this install:

| Panel group | Source | Works? |
|---|---|---|
| Pod counts per workload | kube-state-metrics | ✓ |
| HPA current / desired | kube-state-metrics | ✓ |
| Backend-api RPS / p95 / p99 | backend-api `/metrics` | ✓ |
| Container CPU | cAdvisor (kubelet) | ✓ |
| KEDA queue depth (`keda_scaler_metrics_value`) | KEDA metrics-apiserver | ✓ |
| pwsh active subprocesses / executions | powershell-service `/metrics` | ✓ |
| OPA decisions/sec, p95 latency | opa `/metrics` | ✓ |
| Redis queue depth (`redis_db_keys`) | redis-exporter (not installed) | empty — deferred |
| Celery task success/fail rate | celery-exporter via `celery-exporter.yaml` | ✓ |

The Redis queue depth panel is deferred per
[`docs/scaling/scaling-after.md`](../../../docs/scaling/scaling-after.md#what-this-still-doesnt-address);
`keda_scaler_metrics_value` (KEDA's own queue-depth reading) covers the
same signal for the demo.

## Teardown

```bash
helm -n autoaudit uninstall grafana prometheus
kubectl -n autoaudit delete -f infrastructure/monitoring/in-cluster/celery-exporter.yaml
kubectl -n autoaudit delete configmap autoaudit-scaling-dashboard
helm -n keda uninstall keda
kubectl delete namespace keda
```
