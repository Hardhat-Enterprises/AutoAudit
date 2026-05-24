# AutoAudit — SaaS Scaling: AKS Platform Plan

> **Status:** Planning. Companion to [saas-scaling-architecture.md](./saas-scaling-architecture.md). All decisions here are **revisitable** — the doc states defaults so we can move forward, not because they are final.

## Why this document exists

Companion to the logical-architecture doc. That document covers the application-internal changes needed for multi-tenant SaaS (tenancy schema, scan pipeline, OPA bundles, RLS, MSAL caching). This document covers **how AutoAudit *runs* on Azure Kubernetes Service** — cluster topology, managed-vs-self-hosted choices, networking, identity, image supply chain, GitOps, autoscaling, observability, DR, cost, security baseline.

## Decisions that frame this document

| Decision | Value |
|---|---|
| Target | AKS in Azure |
| Scale | Mid-market, 100s of tenant organisations |
| Compliance scope (IRAP / ISO 27001 / SOC 2) | **Out of scope for MVP**, documented as upgrade path |
| Tenant compute isolation | Pooled with hooks for later per-tier separation |
| Audience | Internal technical collaborators |

## Component-maturity bar

Every recommendation names the off-the-shelf component (Microsoft-managed, CNCF graduated/incubating, or vendor-supported) and states why it is mature. We avoid stitched-together developer-driven assemblies when a well-known managed component does the same job.

## How to read this document

Each section follows the same shape:

1. **Recommendation** — the position and the off-the-shelf component
2. **Alternatives considered** — what we rejected and why
3. **Helm/CI changes required** — concrete deliverables in `helm/autoaudit/` and `.github/workflows/`
4. **Open questions** — unresolved decisions, each with a default

Cross-references to the logical-architecture document are marked `[ARCH §N]`.

## Repository state these recommendations build on

Captured during planning so this doc is self-contained:

- **Helm chart** at `helm/autoaudit/` already provides per-service Deployments, a Postgres StatefulSet, a Redis Deployment (no PVC by default), Gateway API HTTPRoute, an `existingSecret` pattern (chart does not create the secret, expects ESO/Sealed/Terraform), an auto-generated admin Secret on first install, ServiceAccount, ConfigMap. Missing: PodDisruptionBudgets, NetworkPolicies, HPA/KEDA, monitoring CRDs, ExternalSecret CRDs, migrations Job, multi-arch images, non-root securityContext.
- **CI/CD** at `.github/workflows/`: backend-api builds and pushes `autoauditservices/backend-api:${ENV_NAME}` to Docker Hub. CodeQL + Bandit + super-linter + Grype wired. Frontend and engine workflows have build/push commented. No multi-arch, no signing, no ACR.
- **Frontend** is already Vite 7 + React 19 with `Dockerfile.prod` (multi-stage → nginx). The dev `Dockerfile` runs `vite` and is dev-only.
- **Observability**: stdlib logging only; `infrastructure/monitoring/alerts/` has AlertManager rules drafted but no Prometheus deployment to consume them.
- **Migrations** run inside backend-api at startup via `entrypoint.sh` — blocks rolling updates and races across replicas.

---

## 1. AKS cluster topology

### Recommendation

**Single regional AKS cluster per environment** (dev / staging / prod), **Azure CNI Powered by Cilium**, zone-redundant control plane, three availability zones, with the following node pools:

| Pool | Purpose | SKU class | Mode | Zones | Scaling |
|---|---|---|---|---|---|
| `system` | CoreDNS, konnectivity, metrics-server, csi drivers, ingress controller data plane | `Standard_D4ds_v5` ×3 | System (CriticalAddonsOnly taint) | 1,2,3 | Fixed 3 |
| `apps` | backend-api, frontend, opa, KEDA, ESO, cert-manager | `Standard_D8ds_v5` | User | 1,2,3 | NAP |
| `workers` | Celery worker Deployments per queue (`controls.graph`, `controls.powershell`, `scheduled`, `drift`, `housekeeping`) | `Standard_D8ds_v5` and `Standard_D16ds_v5` for heavier consumers | User, **spot with on-demand floor** | 1,2,3 | NAP |
| `pwsh` | powershell-service only (`kubernetes.io/arch=amd64` already in chart, plus a dedicated taint `workload=pwsh:NoSchedule`) | `Standard_D4ds_v5` amd64 | User | 1,2,3 | NAP |

If Postgres is ever moved in-cluster (not the recommended path — see §2a), add a dedicated on-demand `stateful` pool with `workload=stateful:NoSchedule` taint.

**Autoscaler: Node Auto Provisioning (NAP)** — Microsoft's managed Karpenter on AKS (GA). Pool taints/tolerations honoured via NAP NodePool CRDs. NAP gives bin-packing, fast scale-up (~30s), and clean spot diversification — all features the legacy Cluster Autoscaler lacks.

**Sizing order-of-magnitude for 100s of tenants**:

- backend-api: 6–12 pods steady, headroom to 30 during morning-login spike → ~6–10 vCPU steady.
- workers: dominant cost. 300 tenants × continuous drift (one light scan / 4h) + on-demand peaks → ~30–60 worker pods steady, burst 150+. Spot is decisive here.
- powershell-service: amd64 only, sized to concurrent EXO sessions; ~8–20 pods steady, burst 40.
- Steady prod: ~15–25 nodes across pools, burst-capable to ~60–80 via NAP. Roughly 200–400 vCPU peak.

PodDisruptionBudgets on backend-api (`minAvailable: 50%`), opa, powershell-service. Anti-affinity (`topologyKey: topology.kubernetes.io/zone`) on backend-api, worker, opa for AZ spread.

### Alternatives considered

- **Legacy Cluster Autoscaler** — rejected. Slower scale-up (1–3 min), no bin-packing, struggles with mixed SKUs and spot diversification. NAP is the strict superset and Microsoft-supported.
- **Self-installed upstream Karpenter** — rejected. NAP gives the same engine with Microsoft support and AKS-native integration; running upstream Karpenter on AKS is developer-driven stitching.
- **Multiple smaller clusters per tenant tier** — rejected at this scale. AKS control-plane cost multiplies and ops overhead with it. Keep as a *future hook* (per-tier pool labels today; cluster split later if a regulated tenant requires it).
- **Single large pool with no role separation** — rejected. Noisy-neighbour risk between Celery bursts and synchronous backend-api latency; hampers spot adoption (you can't run backend-api on spot but you absolutely can run workers on spot).
- **Virtual nodes / ACI** — rejected. Poor fit for long-lived Celery workers, image pull penalties, no DaemonSet support for observability agents.

### Helm/CI changes required

- Add `tolerations` and `nodeSelector` blocks to backend-api, worker, frontend, opa Deployments (currently absent except powershell-service).
- New `values.yaml` keys: `nodePools.apps.tolerations`, `nodePools.workers.tolerations`, etc., wired through templates.
- Anti-affinity stanzas (`topologyKey: topology.kubernetes.io/zone`) on backend-api, worker, opa.
- New PodDisruptionBudget templates for backend-api, opa, powershell-service.
- NAP NodePool CRD manifests in `infra/aks-nap/` (not chart; cluster-level Terraform).

### Open questions

- **Region(s)** — *Default: Australia East primary, Australia Southeast DR pair.* Confirms zonal availability and Flex Server SKU availability.
- **Spot-eviction tolerance for the longest-running scan job** — *Default: yes — Celery retry semantics ([ARCH §3] chord-based finaliser + idempotent `evaluate_control`) make eviction safe.* Justifies 80% spot on workers pool.

---

## 2. Stateful services: managed vs self-hosted

### 2a. PostgreSQL — Azure Database for PostgreSQL Flexible Server

**Recommendation**: Azure Database for PostgreSQL Flexible Server, **General Purpose D4ds_v5** to start (Memory-Optimised E4ds_v5 once hot), **zone-redundant HA**, **PITR enabled (14 days)**, **private VNET integration** (delegated subnet), `azure.extensions=pg_stat_statements,pgaudit`. Use the **built-in PgBouncer (Flex Server feature)** in transaction-pooling mode.

One **in-region async read replica** from day 1 — serves reporting reads (heavy compliance dashboards) and is promoteable for DR.

Drop the in-cluster Postgres StatefulSet entirely for prod/staging. Keep it for dev (or use Flex Server Burstable B1ms in dev for parity).

**Compliance upgrade path**: customer-managed key (CMK) encryption with Key Vault, IRAP-aligned region, geo-restore window extension to 35 days.

### Alternatives considered

- **In-cluster Postgres StatefulSet (current chart)** — rejected for prod. No managed PITR, manual minor-version upgrades, real operator burden. The current chart has a single replica, 10Gi PVC, no backup CronJob — far below mid-market SaaS expectations.
- **CloudNativePG operator** — genuinely mature (CNCF Sandbox, EDB-backed; the reference cloud-native Postgres operator). Rejected as default because (a) Microsoft does not support it on AKS, (b) you carry the upgrade/patch burden, (c) Flex Server already gives PITR, HA, replicas as a service. **Documented as escape hatch** if Flex Server pricing or feature gaps bite (logical replication restrictions, super-user requirements).
- **Azure Cosmos DB for PostgreSQL (Citus)** — rejected. Sharding model is overkill at 100s of tenants and forces a distribution-column choice prematurely.
- **External in-cluster PgBouncer Deployment** — rejected as default since Flex Server provides built-in PgBouncer. Add an in-cluster pooler (PgCat or Supavisor) only if PgBouncer connection limits become the bottleneck.

### Helm/CI changes required

- Make the in-cluster Postgres StatefulSet **conditional**: `postgresql.enabled: false` for prod; chart consumes `postgresql.externalHost`, `postgresql.externalPort`, `postgresql.sslMode=require`. Migrations Job (§6) reads the same env.
- Connection-string secret synced from Key Vault via External Secrets Operator (§4), populated by Terraform that provisions Flex Server.
- New helper template `postgresql-connection.tpl` to compute the DSN consistently across backend-api, worker, migrations Job.

### Open questions

- **PITR retention** — *Default: 14 days.* 35 days available; cost lever.
- **Cross-region geo-restore from day 1?** — *Default: yes — Flex Server geo-redundant backup is cheap and the restore drill is a quarterly task.*
- **CMK now or later?** — *Default: later, deferred per compliance decision.* Microsoft-managed keys at MVP.

### 2b. Redis — Azure Cache for Redis Premium P1

**Recommendation**: Azure Cache for Redis **Premium P1** with persistence (AOF), zone redundancy, VNET injection, AUTH from Key Vault, TLS-only.

Logical separation of roles via separate **databases** (DB 0 = Celery broker, DB 1 = Celery result backend, DB 2 = app cache / rate-limit / MSAL token cache). For mid-market scale a single Premium P1 instance handles all three; only split into separate Redis instances when broker latency starts impacting cache.

**Compliance upgrade path**: Enterprise tier for active-active geo, Redis 7 RDI for streaming use cases.

### Alternatives considered

- **In-cluster Redis Deployment (current chart)** — rejected for prod. Deployment (not StatefulSet), persistence disabled by default, no HA, no AUTH rotation story, single point of failure. Acceptable in dev only.
- **Bitnami Redis Helm chart in-cluster** — mature but Broadcom acquisition has clouded the Bitnami support story (image relocations, license changes). Rejected as primary.
- **Redis Inc. operator (Redis Enterprise K8s operator)** — mature but commercial. If you're paying Enterprise pricing anyway, the managed Azure Cache Enterprise tier wins (Microsoft takes the operational burden).
- **Dragonfly / KeyDB** — rejected. Not mature enough as a Celery broker in production at this scale; Celery community testing is thin.

### Helm/CI changes required

- Make Redis Deployment conditional on `redis.enabled` (currently always-on).
- External-host pattern: `redis.externalHost`, AUTH from ESO-managed secret.
- The chart's Redis PVC template becomes dev-only.

### Open questions

- **TLS-only from day 1** — *Default: yes — Premium tier supports it natively.*
- **Single Redis or split broker / cache from day 1?** — *Default: single Premium P1 with separate DB indexes; split when contention is measured.*

### 2c. OPA — in-cluster Deployment with Blob bundle source

**Recommendation**: keep OPA in-cluster as a **Deployment** (3 replicas, anti-affinity across zones, HPA on CPU). OPA is stateless; latency-sensitive (every scan finding goes through it).

Bundle source: **Azure Blob Storage** with OPA's built-in `bundle` plugin polling on 60s ETag. Signed bundles ([ARCH §5]). Bundle build runs in CI ([§5] below).

**Compliance upgrade path**: bundle-signing key in Key Vault under HSM-backed key (HSM SKU); admission verification at OPA pull time.

### Alternatives considered

- **Open Policy Agent Gatekeeper** — different tool (admission control). Use Gatekeeper *additionally* for cluster admission policies (or Kyverno — see §11). Not a substitute for the policy-evaluation OPA.
- **OPA sidecar per pod** — rejected. 3× pod count, harder bundle rollouts, less efficient cache.
- **Cedar / Styra DAS** — DAS (Styra) is mature commercial OPA management; flagged as **future option** if policy authoring at fleet scale becomes a problem. Not at MVP.

### Helm/CI changes required

- Bump default `opa.replicaCount` to 3, add anti-affinity, add HPA (`templates/opa/hpa.yaml`).
- New chart values: `opa.bundle.url`, `opa.bundle.serviceCredentials` (federated workload identity for Blob).
- A CI job that builds the OPA bundle (`.tar.gz`) and uploads to Blob with versioning ([§5]).

### Open questions

- **Bundle signing scheme** — *Default: OPA native bundle signing (RS256 with key in Key Vault).* cosign-signed bundles are an alternative but OPA native is simpler and what OPA verifies natively.

---

## 3. Networking & ingress

### Recommendation

- **Gateway API controller: Application Gateway for Containers (AGC)** — Microsoft-managed L7 load balancer that natively implements Gateway API on AKS (GA). The chart already produces `HTTPRoute` resources, so AGC slots in directly.
- **TLS edge: Azure Front Door (Standard tier) + Azure Key Vault certs** in front of AGC. Gives global anycast, WAF, DDoS, and managed certs. cert-manager is *not* required if Front Door + Key Vault handles certs.
- **Service mesh: not at MVP.** Cilium (the Azure CNI dataplane) gives WireGuard-based mTLS at the *node* level, NetworkPolicy, and L7-aware policies without the Istio operator burden. Revisit Istio Ambient (sidecarless) only when per-workload mTLS identity becomes a cross-tenant policy proof requirement.
- **Egress: Azure NAT Gateway per zone**, no Azure Firewall at MVP. NAT Gateway provides stable egress IPs available for tenant allowlisting on request.
- **NetworkPolicy: Cilium default-deny baseline** at namespace level, with explicit allow rules per Deployment. Cilium NetworkPolicy (CRD) is preferred over upstream NetworkPolicy because of L7 awareness on the worker ↔ powershell-service path.

**Compliance upgrade path**: Azure Firewall on egress for SOC-driven egress filtering; private endpoints on every PaaS service; WAF rule set tuning; Front Door Premium with private-link origin.

### Alternatives considered

- **Istio Gateway as the Gateway API impl** — mature (CNCF graduated) but operationally heavier than AGC and you self-manage upgrades. Rejected unless you're already running Istio for east-west.
- **Envoy Gateway (CNCF)** — promising but younger; Microsoft does not run it for you. Rejected vs AGC for the maturity / vendor-support lens.
- **NGINX Ingress Controller** — extremely mature but Ingress, not Gateway API; the chart is already on Gateway API. Reverting is regression.
- **cert-manager + Let's Encrypt at the edge** — the canonical CNCF combo, but Front Door + Key Vault is the Azure-native answer at this layer. cert-manager remains a fallback if you ever need cluster-issued certs for in-cluster mTLS material.
- **Azure Firewall for egress** — rejected at MVP cost (~$1k/mo base before traffic). Adopt when egress filtering becomes a compliance requirement.
- **Linkerd / Cilium service mesh as full mesh from day 1** — rejected as premature optimisation at 100s of tenants. The data plane (Cilium CNI) already covers ~80% of the mesh value.

### Helm/CI changes required

- Document the AGC Gateway resource as a **prerequisite** (not chart-managed) — installed once per cluster by platform Terraform.
- The chart's `parentRef` already supports cross-namespace Gateway, good.
- New chart templates: `templates/networkpolicy/*.yaml` for default-deny + allow rules per workload (gated on `networkPolicies.enabled`).
- Front Door origin pointing at AGC FQDN — Terraform/IaC, not Helm.

### Open questions

- **Static egress IP allowlist for any tenant?** — *Default: NAT Gateway gives stable IPs; expose to tenants on request.* Drives NAT Gateway IP count.
- **WAF managed rule set tuning** — *Default: Microsoft default rule set; OWASP CRS 3.2 as a layer when first false-positives surface.*

---

## 4. Identity & secrets

### Recommendation

- **AKS Workload Identity (OIDC federation)** — the only supported path. AAD Pod Identity is deprecated. Each Deployment that touches Azure (Key Vault, Blob, Storage, Service Bus if added) gets its own ServiceAccount annotated with a federated identity, mapped to a User-Assigned Managed Identity in Azure with **least-privilege Azure RBAC**.
- **Secrets: External Secrets Operator (ESO)** syncing from Azure Key Vault into native `Secret` objects. ESO is the right answer because (a) widely adopted in K8s ecosystem, (b) the chart already expects an `existingSecret`, so ESO drops in cleanly, (c) reload-on-rotate via **Reloader (Stakater)** is well-trodden.
- **Per-workspace M365 client secrets** ([ARCH §7]): stored in Postgres encrypted with AES-GCM via per-workspace DEK; the wrapping KEK lives in Key Vault and is non-exportable; pulled via Workload Identity at unwrap time. KEK never leaves Key Vault; DEK lives in pod memory only for the duration of the task.

**Compliance upgrade path**: Key Vault Premium with HSM-backed keys; Key Vault firewall + private endpoint; key-rotation automation; Defender for Key Vault enabled.

### Alternatives considered

- **Secrets Store CSI Driver with Azure Key Vault provider** — Microsoft-supported and mature. Rejected as primary because (a) it mounts secrets as files, requiring app changes, (b) the existing chart works with `Secret` objects, (c) ESO is more flexible (multiple backends, transformation). **Keep CSI Driver as a fallback** for the small set of cases (TLS material that must hit disk).
- **Sealed Secrets (Bitnami)** — rejected. GitOps-encrypted secrets in repo are nice but you still need a key custodian; Key Vault solves the same problem with rotation, audit, RBAC built in.
- **HashiCorp Vault on AKS** — mature but introduces a stateful service to operate. Overkill when Key Vault exists.
- **AAD Pod Identity** — deprecated. Hard reject.

### Helm/CI changes required

- New chart subdirectory `templates/external-secrets/` (gated on `externalSecrets.enabled`) producing `ExternalSecret` resources targeting the chart's `secrets.existingSecret` name.
- ServiceAccount template (`templates/serviceaccount.yaml`) needs `azure.workload.identity/client-id` annotation wired from values.
- New per-workload ServiceAccounts (currently the chart has one shared SA) so each Deployment can have least-privilege federation.
- Reloader annotations on Deployments so rotated secrets trigger rolling restart.

### Open questions

- **Dual-key reads during KEK rotation** — *Default: yes — read with both old and new KEK during rotation window; app-side migration covers re-wrap.* Detail in [ARCH §7].

---

## 5. Image / build supply chain

### Recommendation

- **Registry: Azure Container Registry (ACR), Premium tier**, geo-replicated to a secondary region. Microsoft Defender for Containers scans images on push and at runtime.
- **Multi-arch builds for backend-api, worker, frontend, opa** (`linux/amd64`, `linux/arm64`) via `docker buildx` in GitHub Actions. **powershell-service stays amd64-only** — `mcr.microsoft.com/powershell` ships arm64 tags for some flavours but Mariner-based pwsh + Exchange Online module compatibility is shakiest on arm64. Document as a known constraint; the dedicated `pwsh` node pool stays amd64.
- **Image signing: cosign keyless signing** (Sigstore Fulcio + Rekor) using the GitHub Actions OIDC token. Verify at admission with **Kyverno** (§11). Cosign is the de facto standard; AKS admission supports it via Kyverno or Ratify.
- **ACR Trusted Signing (notation v2)** is also Microsoft-supported. Cosign primary for ecosystem reach; Trusted Signing is the Microsoft-aligned alternative documented for IRAP track.
- **SBOM: syft** generates SPDX in CI, attached to image as referrers in ACR. **Grype gate blocking** in CI on `--fail-on high` (already advisory; flip to blocking).
- **Frontend Dockerfile.prod** already exists and is multi-stage → nginx-unprivileged. Make it the production target; the dev `Dockerfile` (vite server) stays dev-only.

**Compliance upgrade path**: ACR Trusted Signing alongside or replacing cosign; Microsoft Defender for Containers plan tier upgrade for runtime threat detection; SBOM publishing to a customer-facing portal.

### Alternatives considered

- **Stay on Docker Hub** — rejected. Pull rate limits, no geo-replication, no Defender integration, no private VNET integration with AKS.
- **GitHub Container Registry (GHCR)** — mature but loses Defender-for-Containers integration and ACR Tasks (image lifecycle).
- **Quay.io** — mature but adds another vendor relationship; ACR is the Azure-native answer.
- **Notation/Notary v2 only** — rejected as primary. Smaller ecosystem; many CI tools and policy engines speak cosign first.
- **CRA dev server retained for frontend** — moot; frontend is already on Vite + Dockerfile.prod.

### Helm/CI changes required

- All workflows in `.github/workflows/` move from Docker Hub to ACR (`autoaudit.azurecr.io`); login via Azure OIDC federation, not username/password.
- Frontend and engine workflows have build/push commented out — uncomment and enable.
- New workflow steps: `docker buildx build --platform linux/amd64,linux/arm64`, `cosign sign`, `syft` SBOM attach, blocking Grype gate.
- Dockerfiles add non-root `USER` and drop to non-root; drives much of the Pod Security work in §11.

### Open questions

- **Cosign keyless (OIDC) vs key-based** — *Default: keyless for CI provenance; key-based as a backup for break-glass signing.*
- **ACR tag retention** — *Default: 30 latest tags per channel + last 90 days; cost lever.*

---

## 6. Deployment & GitOps

### Recommendation

- **GitOps: Flux v2 via the AKS GitOps extension** (Microsoft-managed). Microsoft installs and updates Flux for you; CRDs are upstream Flux. This is the Microsoft-supported path on AKS.
- **Helm chart distribution: ACR as an OCI Helm registry** (`oci://autoaudit.azurecr.io/helm/autoaudit`). Native, signed (cosign), geo-replicated.
- **Progressive delivery: not at MVP.** Argo Rollouts and Flagger are both mature, but with backend-api at 6–12 replicas and a clear health check, vanilla Kubernetes rolling updates are sufficient. Add Flagger (Flux's natural partner) when you have a meaningful traffic-shaping use case (canary by header, by tenant cohort).
- **Migrations: dedicated Helm pre-upgrade Job** (not `entrypoint.sh`):
  - Template `templates/migrations/job.yaml`, Helm hooks `pre-install,pre-upgrade`, `helm.sh/hook-weight: "-5"`, `helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded`.
  - Image: same as backend-api but command runs `alembic upgrade head`.
  - On failure: hook fails, release fails, no app pods restart with broken schema.
  - For Flux, set `--wait` on HelmRelease so Job completion gates rollout.
- **Per-environment isolation: separate AKS clusters for prod and non-prod** (dev + staging share one cluster with namespace isolation; prod is its own cluster). Don't mix prod data with anything else. NAP scales non-prod down aggressively (down to system pool only) overnight.

### Alternatives considered

- **Argo CD** — equally mature (CNCF graduated) and arguably better UX. Rejected as primary because the AKS-managed Flux extension means Microsoft handles the controller upgrade; Argo CD on AKS is self-managed. If the team prefers Argo's UX, it's defensible — the trade-off is operational ownership.
- **Argo Rollouts vs Flagger** — feature-equivalent for canaries; Flagger pairs with Flux, Rollouts pairs with Argo CD. Choice falls out of GitOps choice.
- **Migrations in entrypoint (status quo)** — rejected. Blocks rolling update, rollback awkward, multiple replicas race the migration.
- **Single cluster for all envs with namespaces** — rejected. Noisy-neighbour and blast radius for prod is unacceptable; the cost of an extra AKS control plane (~$70/mo for SLA tier) is trivial vs the risk.

### Helm/CI changes required

- Remove migration logic from `entrypoint.sh`; add `templates/migrations/job.yaml`.
- New CI workflow step: package chart, push to ACR OCI, sign with cosign.
- HelmRelease manifests in a separate `infra/flux/` directory per environment.

### Open questions

- **Bootstrap admin secret ownership** — *Default: keep auto-generated `admin-secret.yaml` for first install; deferred decision on moving bootstrap to a separate Job.*

---

## 7. Autoscaling

### Recommendation

| Workload | Scaler | Signal |
|---|---|---|
| backend-api | HPA v2 | CPU 70% **and** RPS via custom metric (managed Prometheus → Prometheus Adapter or KEDA `prometheus` scaler). RPS is the right signal because backend-api waits on Postgres / Graph and CPU lies. |
| worker (per queue) | **KEDA** with `redis-streams` or `redis-lists` ScaledObject, **one per queue** (`controls.graph`, `controls.powershell`, `scheduled`, `drift`, `housekeeping`). Each queue gets its own Deployment with queue-specific concurrency and resources. |
| powershell-service | KEDA `redis-lists` if fronted by a queue (recommended for back-pressure); HPA on CPU + custom `pwsh_active_sessions` gauge as fallback if it stays request/response. |
| OPA | HPA on CPU 60%, min 3 / max 10 |
| frontend | HPA on CPU, min 2 / max 6 (mostly static through nginx; cheap insurance) |

**KEDA is CNCF graduated** and the Microsoft-recommended scaler on AKS. The five-ScaledObject pattern is the strongest reason to choose KEDA — HPA can't scale on Redis queue depth out of the box.

NAP triggers from pending pods produced by the above; NAP's bin-packing chooses the right SKU/spot mix.

### Alternatives considered

- **HPA-only with Prometheus Adapter** — works, but you'd write a custom controller for queue scaling. KEDA exists, is mature, and is the right answer.
- **Knative / scale-to-zero for workers** — appealing for `scheduled` queue but Knative adds an autoscaler-on-autoscaler complexity. KEDA does scale-to-zero natively for idle queues.
- **VPA in `Auto` mode** — rejected. VPA `Auto` evicts pods to resize, hostile to long Celery tasks. Use VPA `Off` (recommendation-only) for sizing guidance.

### Helm/CI changes required

- New `templates/keda/scaledobject-*.yaml` per queue, gated on `keda.enabled`.
- Worker Deployment becomes a *template loop* over `worker.queues[]` so each queue has its own Deployment + ScaledObject.
- HPA templates for backend-api, opa, frontend, powershell-service.
- Prometheus Adapter or KEDA Prometheus scaler config (for RPS-based HPA).

### Open questions

- **Min replicas for `worker.drift` queue** — *Default: scale-to-zero for idle workspaces; floor of 1 for active hours.* Cost vs cold-start latency.
- **backend-api scale-down stabilisation window** — *Default: 5 min (kube default).* Affects user-visible 502s during scale-down.

---

## 8. Observability stack on AKS

### Recommendation

- **Metrics: Azure Monitor managed Prometheus + Azure Managed Grafana.** Microsoft runs the storage; you keep Prom-compatible PromQL, recording rules, and AlertManager-style alert rules. Bridges the existing `infrastructure/monitoring/alerts/` content directly.
- **Logs: Azure Monitor Log Analytics (Container Insights)** for cluster + pod logs; KQL for queries. Pair with structured JSON logging in the apps ([ARCH §9]).
- **Traces: Azure Application Insights** receiving OTLP from the **OpenTelemetry Collector** deployed as a DaemonSet (auto-deployed by the AKS Container Insights add-on or self-installed). App-side OTel SDK instrumentation is in [ARCH §9].
- **Existing alert rules** in `infrastructure/monitoring/alerts/` (PromQL) port directly. Migrate to Azure Monitor managed Prometheus rule groups (same syntax). Convert AlertManager routes to **Azure Monitor Action Groups**. This is mostly mechanical YAML translation, not a rewrite.

**Compliance upgrade path**: Sentinel ingestion of cluster activity, AAD sign-ins, Front Door WAF logs, and the application audit log; long-retention archive in Log Analytics archive tier; tail-sampling for App Insights traces.

### Alternatives considered

- **Self-hosted kube-prometheus-stack** — extremely mature (CNCF). Rejected as default because (a) you operate Prometheus storage and HA yourself, (b) Azure managed Prom is cheaper at this scale once you account for ops time, (c) upgrade burden. **Keep as fallback** if managed Prom limits bite.
- **Datadog / New Relic / Dynatrace** — extremely mature commercial. Per-host pricing makes them expensive at burst-heavy worker scale, and they introduce a vendor outside Azure. Documented as the path if the team wants single-pane-of-glass with APM included.
- **Loki for logs** — mature (Grafana Labs) but Log Analytics is already there as part of AKS and KQL is well-supported. Loki is fine if you self-host the rest of the Grafana stack.
- **Tempo / Jaeger for traces** — same reasoning; App Insights wins on AKS unless you're already running Tempo.
- **OpenTelemetry Collector self-managed** — actually **recommended** as the *collector layer* even with Azure Monitor backends, because it decouples app instrumentation from backend choice. (CNCF incubating, very mature.)

### Helm/CI changes required

- New chart subdirectory `templates/monitoring/` producing `PodMonitor` resources for backend-api, worker, opa, powershell-service (consumed by managed Prometheus via `azmonitoring.coreos.com` CRDs).
- Existing `infrastructure/monitoring/alerts/` files → wrapped as `PrometheusRule` CRDs (`azmonitoring.coreos.com/v1`).
- Action Groups + alert routes in Terraform.

### Open questions

- **SIEM consumption** — *Default: deferred per compliance scope decision.* Documented as upgrade path.
- **Log retention period** — *Default: 30 days hot Log Analytics, 90 days warm, archive to Blob for longer.* Drives Log Analytics cost most of all.
- **Trace sampling** — *Default: head-based sampling at 10%.* Tail-based requires OTel Collector tail-sampling processor; deferred.

---

## 9. Backup, DR, multi-region

### Recommendation

- **Postgres**: Flex Server **PITR 14 days** + cross-region geo-restore enabled. One in-region read replica day 1 (also DR-promote candidate).
- **PVCs in cluster** (only OPA bundles cache, dev Postgres, dev Redis): **Velero on AKS via the AKS Backup add-on** (Microsoft-managed Velero), Azure Blob target, daily, 14-day retention.
- **Redis**: persistence on (AOF + RDB) on Premium tier; broker data is reconstructable, so RPO can be lax; result-backend RPO matters more.
- **Blob (OPA bundles, scan reports if persisted)**: GRS (geo-redundant) storage account.
- **DR posture**: single-region active, **warm restore in secondary region**. Don't go active-active at mid-market. Quarterly Velero restore drill + Flex Server geo-restore drill.
- **Recommended targets** (negotiable): RPO 15 min (Flex Server PITR-bounded), RTO 4 hours (warm-restore in secondary region with pre-built AKS via Terraform).

### Alternatives considered

- **Active-active multi-region** — rejected at mid-market. The cost is 2× plus the data-consistency work (Postgres logical replication, Citus, or app-level sharding) is non-trivial. Revisit when a single tenant requires <1h RTO.
- **Cool storage / archive tier for backups** — fine for compliance archives; not for operational backups (restore time hours).
- **Self-managed Velero** vs **AKS Backup add-on** — add-on uses Velero under the hood, Microsoft does the upgrades. Use the add-on.

### Helm/CI changes required

- None directly; this is platform / Terraform territory. The chart should ensure all stateful PVCs have labels Velero can include/exclude.
- Document Velero `Backup` and `Schedule` resources in `infra/` (not chart).

### Open questions

- **RTO/RPO commitments to customers** — *Default: RPO 15 min, RTO 4 hours.* Drives whether you need warm secondary or cold geo-restore.
- **Regulatory data residency** — *Default: in-region backups only (Australia East).* Drives storage account replication choice.

---

## 10. Cost model & sizing

Order-of-magnitude USD/month, illustrative — **not quotes**:

| Component | Monthly $ | Notes |
|---|---|---|
| AKS control plane (Standard tier with Uptime SLA) | ~$75 | Fixed |
| `system` pool (3× D4ds_v5) | ~$420 | Fixed |
| `apps` pool (avg 5× D8ds_v5 on-demand) | ~$1,400 | Reserved 1y → ~$900 |
| `workers` pool (avg 10× D8ds_v5, 80% spot) | ~$1,100 | Spot dominates here; on-demand floor ~2 nodes |
| `pwsh` pool (avg 3× D4ds_v5) | ~$420 | |
| Flex Server Postgres GP_D4ds_v5 + HA + 1 RR + 500GB + PITR 14d | ~$1,200 | Reserved 1y → ~$800 |
| Azure Cache for Redis Premium P1 | ~$420 | |
| Application Gateway for Containers | ~$200 | + capacity units |
| Azure Front Door Standard + WAF | ~$200 | + traffic |
| ACR Premium + geo-replication | ~$150 | |
| NAT Gateway (2 zones) | ~$100 | + data |
| Azure Monitor (managed Prom + Log Analytics) | ~$400–800 | Strongly retention/volume-driven |
| Managed Grafana | ~$25 | |
| Backups (Velero + storage) | ~$50 | |
| **Total prod** | **~$6.5k–8k/mo** | Reserved instances + steady spot pulls to ~$5k |

**Cost levers**:

- **Spot on workers pool**: 60–70% saving on the largest single line.
- **Reserved instances (1y or 3y)** on `system`, `apps`, `pwsh` floors and Flex Server.
- **Dev cluster scale-to-zero overnight** via NAP min=0 on user pools; Flex Server stop/start (Flex Server supports stop for up to 7 days at a time).
- **Per-workspace cost attribution**: **OpenCost on AKS** (CNCF Sandbox, mature in practice; FinOps Foundation aligned). Label every workload with `tenant=<workspace>` or use namespaces; OpenCost slices by label/namespace and feeds Azure-native cost data.

### Alternatives considered

- **Azure Cost Management alone** — gives subscription-level cost but can't attribute pod-level. Pair with OpenCost.
- **Kubecost** — commercial fork of OpenCost; both share the same engine. OpenCost suffices unless you want the Kubecost UI.

### Open questions

- **Reservation level** — *Default: 1y reserved on steady-state floors.* Revisit 3y when shape stabilises.
- **Per-tenant cost attribution timing** — *Default: OpenCost from day 1* (label discipline is cheap).
- **Tenant billing model** — *Default: deferred to product/finance.* Drives whether per-tenant cost attribution is a billing input or an internal margin tool.

---

## 11. Security baseline

### Recommendation

- **Pod Security Standards `restricted` enforced** at namespace level for all app namespaces. Requires `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, drop `ALL` capabilities, no privilege escalation. Backend, worker, frontend, opa Dockerfiles need rework (currently root). powershell-service can run non-root with a writable `/tmp` for pwsh module cache.
- **Admission policy: Kyverno** (CNCF incubating, very mature). Enforces:
  - cosign signature verification on all images
  - no `:latest` tags
  - required labels (`app.kubernetes.io/*`, `tenant=`)
  - PSS-equivalent policies
  - blocks `hostPath`, `hostNetwork`
- **Image scanning gate**: Microsoft Defender for Containers (registry + runtime) + Grype in CI blocking.
- **Private cluster (API server VNET integration)**, AAD-integrated kubectl, **Azure RBAC for K8s Authorization** day one.
- **Network**: NetworkPolicy default-deny, explicit allows per workload (Cilium L7-aware).
- **CMK (customer-managed encryption keys)** — *deferred per compliance scope decision*; documented in the upgrade path. Microsoft-managed keys day one.
- **Microsoft Defender for Cloud / Defender for Containers**: enabled at base plan day one; **plan tier upgrade deferred** per compliance decision.
- **Microsoft Sentinel**: **deferred per compliance scope decision**, documented as upgrade path. Application audit log stays in app DB ([ARCH §9]).

### Alternatives considered

- **OPA Gatekeeper** instead of Kyverno — both CNCF, both mature. Kyverno has the better DX (no Rego required for policies) and is more relevant since OPA is already used for app policy (don't conflate the two roles). Either is defensible.
- **Falco** for runtime threat detection — CNCF graduated, very mature. Defender for Containers covers most of the same ground with Microsoft management; add Falco only if Defender's coverage gaps bite.
- **AAD groups directly bound to ClusterRoles** vs **Azure RBAC for K8s Authorization** — recommend Azure RBAC for K8s; centralises in Azure RBAC.
- **Self-hosted SIEM (Elastic / Splunk)** — mature but adds vendor relationship. Sentinel is the Azure-native answer.

### Helm/CI changes required

- All Dockerfiles: non-root user, read-only root filesystem, explicit `WORKDIR` and writable `emptyDir` volumes for `/tmp` and any cache paths.
- All Deployments: `securityContext` with `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`, `seccompProfile: RuntimeDefault`.
- Kyverno policies live in a separate `infra/kyverno/` directory, not in the app chart.
- CI: `cosign verify` smoke test before deploy.

### Open questions

- **IRAP / ISO 27001 / SOC 2 in scope** — *Default: out of scope at MVP.* See Compliance Upgrade Path appendix.
- **Pen test cadence** — *Default: pre-launch + annually.*

---

## 12. Open questions / decisions to surface

These are the explicit revisitable defaults:

| Question | Default |
|---|---|
| Region(s) | Australia East primary, Australia Southeast DR pair |
| GitOps tool | Flux v2 via AKS extension |
| Postgres | Flex Server (CNPG documented as fallback) |
| Redis tier | Premium P1 (Enterprise E10 if Redis 7 streams / RDI become needed) |
| TLS edge | Front Door + Key Vault certs in front of AGC |
| Egress static-IP allowlist | NAT Gateway gives stable IPs; expose to tenants on request |
| Spot tolerance for workers | 80% spot on workers pool |
| DR targets | RPO 15 min, RTO 4 hours |
| Reservation level | 1y reserved on steady-state floors |
| Per-tenant cost attribution timing | OpenCost from day 1 |
| Compliance scope (IRAP / ISO 27001 / SOC 2) | **Out of scope at MVP**; documented as upgrade path |
| CMK day 1? | No, Microsoft-managed keys |
| Image signing model | Cosign keyless |
| Workload Identity vs CSI Driver split | ESO for non-TLS, CSI for TLS material that must hit disk |
| Migration runner ownership | Helm pre-upgrade Job; rip out app-startup migration once Job pattern lands |

---

## Compliance upgrade path appendix

When IRAP / ISO 27001 / SOC 2 becomes in scope, the following changes apply (organised by section):

- **§2a Postgres**: Flex Server → CMK-encrypted with Key Vault key; PITR 35 days; Microsoft Purview integration; pgaudit-driven access logs to Sentinel.
- **§2b Redis**: Enterprise tier (FedRAMP/IRAP-aligned regions); CMK encryption.
- **§2c OPA**: signed bundles with HSM-backed Key Vault key; admission verification at OPA pull time; bundle-rollout audit trail.
- **§3 Networking**: Azure Firewall on egress (SOC-driven egress filtering); private endpoints on every PaaS service; Front Door Premium with private-link origin; WAF rule-set tuning to OWASP CRS.
- **§4 Identity & secrets**: Key Vault Premium with HSM keys; Key Vault firewall + private endpoint; key-rotation automation; Defender for Key Vault enabled.
- **§5 Image supply chain**: ACR Trusted Signing alongside / replacing cosign; Microsoft Defender for Containers plan tier upgrade for runtime threat detection; SBOM publishing to a customer-facing portal; mandatory Grype `--fail-on critical`.
- **§6 GitOps**: signed HelmReleases; Argo CD / Flux deployment provenance into Sentinel.
- **§8 Observability**: Sentinel ingestion of cluster activity, AAD sign-ins, Front Door WAF logs, and application audit log; long-retention archive in Log Analytics archive tier; tail-sampling for App Insights traces.
- **§9 Backup/DR**: cross-region backup retention extension; immutable backups (legal hold); annual DR exercise certification.
- **§11 Security baseline**: Defender for Cloud Standard plan; Defender for Containers P2; Defender for Servers / Storage / Key Vault / DBs; Sentinel analytics rules + automation; CMK across every encrypted store; full audit retention to 7 years; pen test → external attestation.

---

## Cross-reference index to logical-architecture document

| AKS-layer concern (this doc) | App-layer counterpart ([saas-scaling-architecture.md](./saas-scaling-architecture.md)) |
|---|---|
| §2a Flex Server's built-in PgBouncer | PgBouncer transaction-pool semantics, `statement_cache_size=0` (ARCH §6) |
| §2c OPA Blob bundle source | OPA bundle protocol, signing, channels (ARCH §5) |
| §3 Cilium / mTLS | HMAC at app layer; mTLS at platform layer (ARCH §4) |
| §4 ESO + Workload Identity | Per-workspace DEK envelope encryption (ARCH §7) |
| §6 Helm pre-upgrade Job | Migrations as pre-deploy job; expand/contract pattern (ARCH §6) |
| §7 KEDA ScaledObject per queue | Per-queue worker Deployments (ARCH §3) |
| §8 Managed Prom + Log Analytics + App Insights | structlog + Prometheus + OTel SDKs (ARCH §9) |
| §10 OpenCost | Per-workspace fairness hooks; tenant labels (ARCH §3) |
| §11 PSS restricted + Kyverno | Workspace isolation testing; defence in depth (ARCH §10) |
