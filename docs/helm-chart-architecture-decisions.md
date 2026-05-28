# Helm Chart Architecture Decisions

This document captures the architectural decisions made during the design of the AutoAudit Helm chart for deployment to Azure Kubernetes Service (AKS). Each section describes the issue or challenge discovered, the options considered, and the decision made with rationale.

## 1. Container Image Licensing

### Issue

The initial design considered using [Bitnami Helm charts](https://github.com/bitnami/charts) as subcharts for PostgreSQL and Redis, which is a common pattern in the Helm ecosystem. However, Bitnami container images are no longer freely available, making them unsuitable for this project.

### Decision

Use only official container images from Docker Hub:

- **PostgreSQL**: `postgres:17` (official PostgreSQL image)
- **Redis**: `redis:alpine` (official Redis image)

### Rationale

Official images are free, well-maintained by their respective upstream projects, and do not impose licensing restrictions. The trade-off is that we must write our own Kubernetes resource templates (StatefulSet, Service, PersistentVolumeClaim) rather than relying on pre-built Bitnami subcharts. This is additional upfront work but avoids licensing concerns and gives us full control over the deployment configuration.

---

## 2. Ingress Approach

### Issue

Kubernetes offers two main mechanisms for routing external HTTP traffic into the cluster:

- **Ingress** (legacy): The traditional `networking.k8s.io/v1/Ingress` resource with an IngressController
- **Gateway API** (modern): The newer `gateway.networking.k8s.io/v1` resources (`Gateway`, `HTTPRoute`) which provide richer routing capabilities

### Decision

Use the **Gateway API** with `HTTPRoute` resources.

### Rationale

The target AKS cluster already has Gateway API support configured. Gateway API is the successor to the Ingress API, offering more expressive routing (header-based, path rewriting, traffic splitting), better separation of concerns between infrastructure operators and application developers, and a standardised specification across implementations. Since the cluster already supports it, there is no reason to use the legacy Ingress API.

---

## 3. Routing Topology

### Issue

The application has two externally-facing services: the **frontend** (React SPA served by nginx) and the **backend API** (FastAPI). Two routing approaches were considered:

**Option A: Separate subdomains**
- `app.autoaudit.example.com` serves the frontend
- `api.autoaudit.example.com` serves the backend API
- Requires CORS configuration on the backend since the browser considers these different origins
- `VITE_API_URL` must be set to the full API domain at frontend image build time

**Option B: Same domain with path-based routing**
- `autoaudit.example.com/*` serves the frontend
- `autoaudit.example.com/api/*` routes to the backend API
- No CORS needed since frontend and API share the same origin
- `VITE_API_URL` can be a relative path (`/api`), eliminating build-time domain coupling

### Decision

**Same domain with path-based routing**, using the `/api` prefix.

The HTTPRoute uses a `URLRewrite` filter with `ReplacePrefixMatch` to strip the `/api` prefix before forwarding requests to the backend service. This means the backend continues to serve routes at `/v1/*` without modification:

```
Browser request:  /api/v1/auth/login
Gateway rewrites: /v1/auth/login
Backend receives: /v1/auth/login
```

### Rationale

1. **No CORS**: Same-origin requests eliminate cross-origin concerns entirely. No `Access-Control-Allow-Origin` headers, no preflight OPTIONS requests, no credentials configuration.

2. **No build-time domain coupling**: The frontend image is built with `VITE_API_URL=/api` (a relative path). Since the JavaScript runs in the browser, relative URLs resolve against the current page's origin. This means the same frontend image works on any domain without rebuilding.

3. **Simpler infrastructure**: One hostname, one TLS certificate, one DNS record.

4. **Backend unchanged**: The `URLRewrite` filter handles prefix stripping at the Gateway level, so the backend's `API_PREFIX=/v1` configuration remains unchanged.

---

## 4. Frontend Build-Time Variable (`VITE_API_URL`)

### Issue

The frontend uses [Vite](https://vitejs.dev/) as its build tool. Environment variables prefixed with `VITE_` are replaced with their values at **build time** and baked into the JavaScript bundle. The variable `VITE_API_URL` (used in `frontend/src/api/client.ts`) cannot be changed at runtime via Kubernetes environment variables because it is already embedded in the compiled JavaScript.

The current `frontend/Dockerfile` runs a Vite development server (`npm start`), which is not suitable for production deployment.

### Decision

1. Create a new **production Dockerfile** (`frontend/Dockerfile.prod`) using a multi-stage build:
   - **Stage 1** (node:20-alpine): Installs dependencies and runs `npm run build` with `VITE_API_URL=/api` as a build argument
   - **Stage 2** (nginx:alpine): Copies the built static files and serves them with nginx

2. Set `VITE_API_URL=/api` as the default build argument. Since we use same-domain path-based routing (see decision #3), this relative path works on any domain.

3. Include an `nginx.conf` that handles SPA routing (`try_files $uri $uri/ /index.html`) so that client-side routes work correctly on page refresh.

### Rationale

A production frontend should serve pre-built static assets via a lightweight web server, not a development server. The multi-stage build keeps the final image small (only nginx + static files). The relative `VITE_API_URL` value, combined with same-domain routing, means the image is environment-agnostic.

---

## 5. OPA Policy Delivery

### Issue

The compliance engine uses [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) to evaluate policy rules written in Rego. The `engine/policies/` directory contains approximately 64 `.rego` files and metadata files organised in a nested directory structure:

```
engine/policies/cis/microsoft-365-foundations/
  v3.1.0/*.rego
  v4.0.0/*.rego
  v6.0.0/*.rego
```

In docker-compose, this directory is mounted as a read-only volume into the OPA container. In Kubernetes, host volume mounts are not available, so an alternative delivery mechanism is needed. Three options were considered:

**Option A: ConfigMap with init container**
- Store policy files in a Kubernetes ConfigMap
- Use an init container to reconstruct the nested directory structure (ConfigMaps are flat key-value stores)
- No custom image needed; uses the official `openpolicyagent/opa` image directly
- Policy updates require a `helm upgrade`

**Option B: Custom OPA image**
- Build a Docker image extending the official OPA image with policies copied in
- Include a build-time `manifest.json` listing all included policy files with SHA-256 checksums
- Requires an additional image build in CI/CD and storage in ACR
- Policies are immutable and version-tracked via image tags

**Option C: Sidecar/init from backend-api image**
- The backend-api image already contains the policies
- Use it as an init container to copy policies into a shared volume
- No extra image build, but pulls a much larger image just for file copying

### Decision

**Custom OPA image** (Option B) with a build-time `manifest.json` for traceability.

### Rationale

1. **Traceability**: The `manifest.json` generated at build time provides a complete inventory of which policy files (with checksums) are included in any given image version. This can be inspected at runtime via `kubectl exec`.

2. **Immutability**: Policies are baked into the image, making deployments reproducible. The image tag serves as a version identifier for the policy set.

3. **Clean runtime**: No init containers, no ConfigMap size limits to worry about, no directory reconstruction scripts.

4. **CI/CD fit**: The project already builds and pushes multiple custom images to ACR. Adding one more (a two-line Dockerfile) is minimal overhead.

---

## 6. Secrets Management

### Issue

The application requires several sensitive values:

| Secret | Purpose | Consumed By |
|--------|---------|-------------|
| PostgreSQL password | Database authentication | backend-api, worker, postgresql, migration job |
| JWT secret key | Signing authentication tokens | backend-api |
| Encryption key (Fernet) | Encrypting M365 credentials at rest | backend-api, worker |
| Redis password | Redis AUTH (optional) | backend-api, worker, redis |
| Google OAuth client ID | SSO integration (optional) | backend-api |
| Google OAuth client secret | SSO integration (optional) | backend-api |

Options considered:

1. **Inline values in `values.yaml`**: Simple but insecure; secrets visible in version control or Helm release history
2. **Platform-specific secret provider in the chart**: e.g., Azure Key Vault CSI `SecretProviderClass` template. Ties the chart to a specific cloud platform.
3. **Pre-created Kubernetes Secret (external to chart)**: The chart references a Kubernetes Secret by name. How that secret is created is the platform's responsibility - Azure Key Vault CSI driver, AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault, External Secrets Operator, Sealed Secrets, Terraform, or manual `kubectl create secret`.

### Decision

**Pre-created Kubernetes Secret, external to the chart.** The chart accepts a `secrets.existingSecret` value pointing to the name of an existing Kubernetes Secret. All pod templates reference this secret via standard `valueFrom.secretKeyRef`.

### Rationale

1. **Platform-agnostic**: The Helm chart contains no cloud-specific resources (no Azure Key Vault `SecretProviderClass`, no AWS IAM annotations, no GCP workload identity labels). It deploys to any Kubernetes cluster regardless of cloud provider.

2. **Separation of concerns**: Secret provisioning is an infrastructure concern, not an application concern. The mechanism for getting secrets into the cluster (CSI driver, External Secrets Operator, Terraform, etc.) is configured outside the chart, typically as part of the platform's infrastructure-as-code.

3. **Standard Kubernetes API**: All pods reference secrets via `valueFrom.secretKeyRef`, which is the standard Kubernetes pattern. This works identically whether the Secret was created by a CSI driver, an operator, or manually.

4. **Composable**: Operators can layer their preferred secrets solution on top without modifying the chart. For example, on Azure they would deploy a `SecretProviderClass` alongside the Helm release; on AWS they might use External Secrets Operator.

### Required Kubernetes Secret

A Kubernetes Secret must exist in the release namespace before installing the chart. The secret name is provided via `secrets.existingSecret` in values.yaml.

**Required keys:**

| Key | Description | Generation |
|-----|-------------|------------|
| `postgresql-password` | PostgreSQL user password | Strong random string |
| `jwt-secret-key` | JWT signing key | Strong random string (64+ characters) |
| `encryption-key` | Fernet symmetric encryption key | Output of `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `redis-password` | Redis AUTH password | Strong random string |

**Optional keys** (if Google OAuth SSO is enabled):

| Key | Description | Generation |
|-----|-------------|------------|
| `google-oauth-client-id` | Google OAuth client ID | From Google Cloud Console |
| `google-oauth-client-secret` | Google OAuth client secret | From Google Cloud Console |

---

## 7. Database Migration Strategy

### Issue

The backend API uses [Alembic](https://alembic.sqlalchemy.org/) for database schema migrations. In the docker-compose setup, migrations run as part of the `entrypoint.sh` script before the application starts:

```bash
uv run alembic upgrade head      # Apply migrations
uv run python -m app.db.init_db  # Seed default admin user
exec uv run uvicorn ...          # Start application
```

In Kubernetes, this approach is problematic when running multiple replicas: every pod would attempt to run migrations simultaneously on startup, creating race conditions and potential deadlocks.

Two options were considered:

**Option A: Init container on the backend-api Deployment**
- Each pod runs migrations before the main container starts
- Simple configuration, but races with multiple replicas
- Works for single-replica development

**Option B: Helm hook Job**
- A Kubernetes Job runs migrations once before any pods start
- Uses Helm's `pre-install` and `pre-upgrade` hook annotations
- Migrations complete before the Deployment is created/updated

### Decision

**Helm hook Job** (Option B).

### Rationale

A Job runs exactly once per Helm install/upgrade, regardless of replica count. It uses the same backend-api image but overrides the command to only run migrations and seeding. The backend-api pods can then start with a simplified command that only launches `uvicorn`, avoiding redundant migration attempts.

The Job spec includes:
- `helm.sh/hook: pre-install,pre-upgrade` to run before deployments
- `helm.sh/hook-weight: "-5"` to ensure it runs before other hooks
- `helm.sh/hook-delete-policy: before-hook-creation` to clean up previous Jobs
- `backoffLimit: 3` for retry on transient failures

---

## 8. Worker DATABASE_URL Driver Difference

### Issue

The backend API and the Celery worker both connect to the same PostgreSQL database, but they use different Python database drivers:

- **Backend API**: Uses `postgresql+asyncpg://` (asynchronous driver via [asyncpg](https://github.com/MagicStack/asyncpg) with SQLAlchemy's async engine)
- **Worker**: Uses `postgresql://` (synchronous driver via [psycopg2](https://www.psycopg.org/) with SQLAlchemy's standard engine)

Both services receive their database connection string via the `DATABASE_URL` environment variable, but the URL prefix must differ.

### Decision

The Helm chart's `_helpers.tpl` includes two template functions that construct the correct `DATABASE_URL` for each service from shared components (host, port, database name, username):

```
# backend-api and migration job:
postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}

# worker:
postgresql://{user}:{password}@{host}:{port}/{database}
```

The password is injected via the `$(POSTGRESQL_PASSWORD)` environment variable reference (Kubernetes variable interpolation), sourced from the synced Key Vault secret.

### Rationale

Constructing the URLs from shared components in templates ensures consistency (same host, port, database, credentials) while allowing the driver prefix to vary per service. This avoids requiring two separate `DATABASE_URL` values in Key Vault or values.yaml.

---

## 9. Infrastructure Scope

### Issue

PostgreSQL and Redis can be deployed either as containers within the Kubernetes cluster or as Azure Platform-as-a-Service (PaaS) resources:

- **Azure Database for PostgreSQL Flexible Server**: Managed backups, HA, automated patching, point-in-time restore
- **Azure Cache for Redis**: Managed Redis with clustering, persistence, and geo-replication
- **In-cluster containers**: Self-managed using official Docker images and PersistentVolumeClaims

### Decision

Deploy PostgreSQL and Redis as **in-cluster containers** for the proof of concept.

### Rationale

This is a PoC environment where operational simplicity and cost minimisation are priorities. In-cluster containers allow the entire application stack to be deployed with a single `helm install` command without requiring additional Azure PaaS resources or Terraform configuration beyond the AKS cluster itself.

**Production note**: For a production deployment, migrating to Azure managed services is strongly recommended. Managed services provide automated backups, high availability, patching, and monitoring that would otherwise require significant operational effort to replicate with in-cluster containers. The Helm chart's `_helpers.tpl` constructs database and Redis URLs from configurable values, making it straightforward to point at external services by changing values.yaml without modifying templates.

---

## 10. PostgreSQL and Redis as Custom Templates

### Issue

Without Bitnami subcharts (see decision #1), we need to write our own Kubernetes resource templates for PostgreSQL and Redis. This includes:

- **PostgreSQL**: StatefulSet (for stable network identity and ordered deployment), headless Service, PersistentVolumeClaim
- **Redis**: Deployment, Service, PersistentVolumeClaim

### Decision

Write custom templates using official images with:

- **Health checks**: `pg_isready` for PostgreSQL, `redis-cli ping` for Redis (matching the existing docker-compose health checks)
- **Persistent storage**: PersistentVolumeClaims with configurable size and storage class (defaulting to AKS's `managed-csi`)
- **Security**: Non-root containers where supported, read-only root filesystems where possible
- **Password injection**: PostgreSQL password set via `POSTGRES_PASSWORD` environment variable from the synced Key Vault secret; Redis password via `--requirepass` command argument

### Rationale

Writing custom templates gives us full control over the deployment configuration without external chart dependencies. The templates are straightforward (each service needs only 2-3 resource files) and closely mirror the existing docker-compose configuration, making them easy to understand and maintain.
