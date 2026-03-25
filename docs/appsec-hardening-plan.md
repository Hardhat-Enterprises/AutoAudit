# AutoAudit Application Security Hardening Plan

## Context

The AppSec team has conducted a comprehensive audit of the AutoAudit codebase ahead of planned penetration testing. This document catalogues security deficiencies, proposes remediation strategies, and assigns ownership areas so relevant teams can plan and execute fixes independently. The goal is to be **secure-by-default** before external testing begins.

**This is a plan document only — no code changes are included.** Each section is self-contained and can be disseminated to the relevant team.

**Repository status:** The repository is public. There is no production deployment — all usage is developer workstations only. However, all findings are written assuming a future production deployment and should be fixed before that occurs.

---

## Prioritised Execution Summary

Findings are grouped into four severity tiers. Within each tier, items are ordered by recommended fix sequence.

### Critical — Fix Before Any Deployment

| # | Finding | Owner |
|---|---------|-------|
| 1 | [PowerShell Executor — Command Injection](#1-powershell-executor--command-injection) | Engine Team |
| 2 | [Path Traversal in Evidence Report Download](#2-path-traversal-in-evidence-report-download) | Backend API Team |

### High — Fix Before Pentest

| # | Finding | Owner |
|---|---------|-------|
| 3 | [Authentication Rate Limiting](#3-authentication-rate-limiting) | Backend API Team |
| 4 | [CORS Configuration](#4-cors-configuration) | Backend API Team |
| 5 | [Security Headers](#5-security-headers) | Backend API Team + Frontend Team |
| 6 | [File Upload Hardening](#6-file-upload-hardening) | Backend API Team |
| 7 | [Docker Container Hardening](#7-docker-container-hardening) | DevOps Team |
| 8 | [Sensitive Token Logging](#8-sensitive-token-logging) | Backend API Team |
| 9 | [M365 Token Exposure in Process Arguments](#9-m365-token-exposure-in-process-arguments) | Engine Team |
| 10 | [CI/CD Security Cleanup](#10-cicd-security-cleanup) | DevOps Team |
| 11 | [Source Maps in Production Build](#11-source-maps-in-production-build) | Frontend Team |
| 12 | [Frontend OAuth State Validation](#12-frontend-oauth-state-validation) | Frontend Team |

### Medium — Address in Near-Term Sprints

| # | Finding | Owner |
|---|---------|-------|
| 13 | [JWT Token Revocation](#13-jwt-token-revocation) | Backend API Team |
| 14 | [Frontend Token Storage](#14-frontend-token-storage) | Frontend + Backend API Teams |
| 15 | [Celery Task Security](#15-celery-task-security) | Engine Team |
| 16 | [Change Password Endpoint](#16-change-password-endpoint) | Backend API Team |
| 17 | [Docker Compose Hardening](#17-docker-compose-hardening) | DevOps Team |
| 18 | [OPA Communication Security](#18-opa-communication-security) | Engine Team |
| 19 | [Input Validation Gaps](#19-input-validation-gaps) | Backend API Team |

### Low — Improve When Capacity Allows

| # | Finding | Owner |
|---|---------|-------|
| 20 | [SECURITY.md](#20-securitymd) | AppSec Team |
| 21 | [SBOM Generation](#21-sbom-generation) | DevOps Team |
| 22 | [CODEOWNERS for Security-Sensitive Files](#22-codeowners-for-security-sensitive-files) | AppSec Team |
| 23 | [Frontend Console Logging](#23-frontend-console-logging) | Frontend Team |

### Process and Workflow Recommendations

| # | Recommendation | Owner |
|---|----------------|-------|
| P1 | [Pre-commit Hooks](#p1-pre-commit-hooks) | DevOps Team |
| P2 | [Dependency Scanning in CI](#p2-dependency-scanning-in-ci) | DevOps Team |
| P3 | [Dependabot Configuration](#p3-dependabot-configuration) | DevOps Team |
| P4 | [Secrets Management Strategy](#p4-secrets-management-strategy) | DevOps + Backend API Teams |
| P5 | [DAST Scanning](#p5-dast-scanning) | AppSec Team |

---

## Positive Security Controls Already in Place

Before cataloguing deficiencies, the following security practices are correctly implemented and should be preserved:

- **No code injection surface in backend-api:** No `eval()`, `exec()`, or `os.system()` calls
- **No SQL injection:** All database queries use parameterised SQLAlchemy ORM — no raw SQL
- **Proper password hashing:** FastAPI-Users password helper with bcrypt
- **Encryption at rest:** M365 client secrets encrypted with Fernet before database storage (`backend-api/app/services/encryption.py`)
- **Endpoint authorisation:** Scan endpoints verify resource ownership against `user_id`
- **Pydantic schema validation:** Request/response models enforce type and length constraints
- **Google OAuth state validation (backend):** Backend validates OAuth `state` parameter via cookie (`backend-api/app/api/v1/auth.py:169-171`)
- **Role-based access control:** RBAC with admin/auditor/viewer roles enforced on protected endpoints
- **No `dangerouslySetInnerHTML` in React:** No raw HTML injection in JSX
- **Proper URL encoding:** `encodeURIComponent` used on filename parameters in API client (`frontend/src/api/client.js:317`)

---

## CRITICAL Findings

---

## 1. PowerShell Executor — Command Injection

**Severity:** CRITICAL
**Owner:** Engine Team
**Files:**
- `engine/powershell/service/executor.py` (lines 15-34, 56-102)
- `engine/collectors/powershell_client.py` (lines 269-337)
- `engine/powershell/service/schemas.py` (lines 10-13)

### 1.1 Problem Description

The PowerShell executor builds script strings using Python f-string interpolation. Three categories of input are injected without adequate validation or escaping:

**a) `tenant_id` — Unescaped string interpolation into connection commands**

```python
# executor.py lines 59, 74, 89
Connect-ExchangeOnline -AccessToken $env:EXO_TOKEN -Organization "{tenant_id}" -ShowBanner:$false
Connect-IPPSSession -AccessToken $env:EXO_TOKEN -Organization "{tenant_id}" -ShowBanner:$false
Connect-MicrosoftTeams -AccessTokens @($env:GRAPH_TOKEN, $env:TEAMS_TOKEN) -TenantId "{tenant_id}"
```

An attacker who controls `tenant_id` (stored in the database via the M365 connection setup) can break out of the quoted string and inject arbitrary PowerShell. Example payload: `contoso.com"; Remove-Mailbox -Identity admin -Confirm:$false; #`

**b) `cmdlet` — Unvalidated interpolation into script body**

```python
# executor.py line 61, powershell_client.py line 295
$result = {cmdlet}{param_str}
```

The cmdlet name is directly interpolated with zero validation. If an attacker controls this value, arbitrary PowerShell executes.

**c) Parameter values — Inconsistent escaping between execution paths**

- `executor.py` line 30 escapes double quotes in string values: `value.replace('"', '`"')`
- `powershell_client.py` line 286 does **NOT** escape string values at all
- Parameter **names** (keys) are never validated in either path

### 1.2 Call Chain Context

The full call chain from user input to PowerShell execution is:

1. **API:** `backend-api/app/api/v1/scans.py` — user creates scan with `m365_connection_id`
2. **Celery:** `backend-api/app/services/celery_client.py` — task queued
3. **Worker:** `engine/worker/tasks.py` — loads M365 credentials (tenant_id, tokens) from encrypted DB storage
4. **Collector:** Individual collector classes (e.g., `engine/collectors/exchange/organization/organization_config.py`) call `client.run_cmdlet()`
5. **PowerShell Client:** `engine/collectors/powershell_client.py` — routes to Docker or HTTP service
6. **Executor:** `engine/powershell/service/executor.py` — builds and runs PowerShell script

The `tenant_id` originates from user input at M365 connection creation time and is stored in the database. It flows through the entire chain without validation until it reaches PowerShell string interpolation.

### 1.3 Current Cmdlet Inventory

All 31 cmdlets currently used in the codebase are read-only `Get-*` commands:

| Module | Cmdlets |
|--------|---------|
| ExchangeOnline | `Get-OrganizationConfig`, `Get-AntiPhishPolicy`, `Get-DkimSigningConfig`, `Get-MailboxAuditBypassAssociation`, `Get-EXOMailbox`, `Get-RoleAssignmentPolicy`, `Get-OwaMailboxPolicy`, `Get-TransportConfig`, `Get-SharingPolicy`, `Get-SafeAttachmentPolicy`, `Get-SafeLinksPolicy`, `Get-TeamsProtectionPolicy`, `Get-HostedConnectionFilterPolicy`, `Get-HostedContentFilterPolicy`, `Get-MalwareFilterPolicy`, `Get-HostedOutboundSpamFilterPolicy`, `Get-AtpPolicyForO365`, `Get-TransportRule`, `Get-ExternalInOutlook`, `Get-AdminAuditLogConfig` |
| Compliance (IPPSSession) | `Get-ReportSubmissionPolicy`, `Get-DlpCompliancePolicy`, `Get-LabelPolicy` |
| Teams | `Get-CsTeamsMeetingPolicy`, `Get-CsTenantFederationConfiguration`, `Get-CsTeamsClientConfiguration`, `Get-CsTeamsMessagingPolicy`, `Get-CsExternalAccessPolicy` |

### 1.4 Proposed Remediation

**Step 1: Implement a cmdlet allowlist (executor.py and powershell_client.py)**

Create a set of permitted cmdlets and validate before execution:

```python
ALLOWED_CMDLETS = frozenset({
    "Get-OrganizationConfig",
    "Get-AntiPhishPolicy",
    # ... all 31 cmdlets listed above
})

def validate_cmdlet(cmdlet: str) -> str:
    if cmdlet not in ALLOWED_CMDLETS:
        raise ValueError(f"Cmdlet not permitted: {cmdlet}")
    return cmdlet
```

Call `validate_cmdlet()` at the top of both `execute()` in `executor.py` and `_build_script()` / `_run_via_service()` in `powershell_client.py`. This prevents injection via the cmdlet parameter without breaking any existing collector — every collector uses one of these 31 cmdlets.

The `schemas.py` file already restricts `module` to `Literal["ExchangeOnline", "Compliance", "Teams"]` (line 10-13), which is the right pattern. Extend this approach to cmdlets.

**Step 2: Validate `tenant_id` format**

M365 tenant IDs are either GUIDs or verified domain names. Validate at input time (M365 connection creation in `backend-api/app/api/v1/m365_connections.py`) and again at execution time:

```python
import re

TENANT_ID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'  # GUID
    r'|'
    r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'  # domain
    , re.IGNORECASE
)

def validate_tenant_id(tenant_id: str) -> str:
    if not TENANT_ID_PATTERN.match(tenant_id):
        raise ValueError(f"Invalid tenant_id format: {tenant_id}")
    return tenant_id
```

Apply this validation:
- At the API layer when creating/updating M365 connections (input validation)
- At the executor layer before script generation (defense in depth)

This will not break any existing functionality because legitimate tenant IDs are always GUIDs or domain names.

**Step 3: Fix parameter value escaping in `powershell_client.py`**

The `_build_script()` method at line 286 does not escape string values. Port the escaping logic from `executor.py` line 30:

```python
# powershell_client.py line 286 — CURRENT (no escaping)
param_str += f' -{key} "{value}"'

# PROPOSED (matches executor.py)
escaped = value.replace('"', '`"')
param_str += f' -{key} "{escaped}"'
```

**Step 4: Validate parameter names**

Parameter names should only contain alphanumeric characters. Add validation in both `build_param_string()` functions:

```python
import re
PARAM_NAME_PATTERN = re.compile(r'^[A-Za-z][A-Za-z0-9]*$')

for key, value in params.items():
    if not PARAM_NAME_PATTERN.match(key):
        raise ValueError(f"Invalid parameter name: {key}")
```

### 1.5 Testing Strategy

- **Unit tests:** Create test cases for each validation function with both valid inputs and known injection payloads (e.g., `tenant_id` containing semicolons, pipes, backticks)
- **Integration tests:** Run every existing collector against a test tenant to verify the allowlist doesn't block any legitimate cmdlet
- **Regression:** The 31 cmdlets in the inventory above represent the complete set. If a new collector is added, the allowlist must be updated — add a comment documenting this requirement

### 1.6 Validation Checklist

#### Code Review

- [ ] **Cmdlet allowlist exists:** Confirm an `ALLOWED_CMDLETS` set (or equivalent) is defined containing exactly the 31 permitted cmdlets listed in section 1.3
- [ ] **Allowlist enforced in executor.py:** Verify that `execute()` calls the validation function **before** any string interpolation occurs. Search for the cmdlet variable — it must not appear in an f-string before validation
- [ ] **Allowlist enforced in powershell_client.py:** Verify that both `_build_script()` and `_run_via_service()` validate the cmdlet before use
- [ ] **tenant_id validation at API layer:** Check `backend-api/app/api/v1/m365_connections.py` — the create/update endpoints must validate tenant_id against the GUID/domain regex pattern before saving to the database
- [ ] **tenant_id validation at executor layer:** Check `executor.py` — tenant_id must be validated again before it is interpolated into any PowerShell script string (defense in depth)
- [ ] **Parameter value escaping in powershell_client.py:** Confirm that string parameter values have double quotes escaped (i.e., `value.replace('"', '`"')` or equivalent) in the `_build_script()` method
- [ ] **Parameter name validation:** Confirm both `executor.py` and `powershell_client.py` validate that parameter names match `^[A-Za-z][A-Za-z0-9]*$` before use
- [ ] **No raw f-string interpolation of user input remains:** Search `executor.py` and `powershell_client.py` for f-strings containing `{tenant_id}`, `{cmdlet}`, or `{param` — every instance must be preceded by validation/escaping

#### Manual Testing

- [ ] **Cmdlet injection blocked:** Call the executor (via unit test or direct invocation) with `cmdlet="Get-OrganizationConfig; Remove-Mailbox"` — it must raise an error and not execute
- [ ] **Unknown cmdlet blocked:** Call with `cmdlet="Invoke-Expression"` — must be rejected by the allowlist
- [ ] **Malicious tenant_id blocked:** Call with `tenant_id='contoso.com"; Remove-Mailbox -Identity admin -Confirm:$false; #'` — must be rejected by format validation
- [ ] **Valid GUID tenant_id accepted:** Call with `tenant_id="12345678-1234-1234-1234-123456789abc"` — must pass validation
- [ ] **Valid domain tenant_id accepted:** Call with `tenant_id="contoso.onmicrosoft.com"` — must pass validation
- [ ] **Parameter value with quotes escaped:** Call with a parameter value containing `"test"value"` — verify the generated script escapes the inner quotes correctly
- [ ] **Invalid parameter name blocked:** Call with a parameter name like `"; Invoke-Expression"` — must be rejected

#### Automated Tests

- [ ] **Unit tests exist** for `validate_cmdlet()`, `validate_tenant_id()`, and parameter name/value validation functions
- [ ] **Tests cover injection payloads:** At minimum, test inputs containing: `;`, `|`, `` ` ``, `$(...)`, `"`, `\n`, and `#`
- [ ] **All 31 existing cmdlets pass the allowlist:** A parameterised test iterates over all cmdlets in section 1.3 and confirms each is accepted
- [ ] **Integration test:** At least one collector runs end-to-end against a test tenant without being blocked by the new validation

---

## 2. Path Traversal in Evidence Report Download

**Severity:** CRITICAL
**Owner:** Backend API Team
**Files:**
- `backend-api/app/api/v1/evidence.py` (lines 185-195)
- `security/evidence_ui/app.py` (lines 388-401)

### 2.1 Problem Description

The evidence report download endpoint accepts a user-supplied `filename` path parameter and uses it directly to construct a file path, with no sanitisation or path traversal protection.

**Backend API route** (`backend-api/app/api/v1/evidence.py` lines 185-195):
```python
@router.get("/reports/{filename}")
async def download_report(filename: str):
    # Reuse existing download handler in security/evidence_ui/app.py
    return evidence_ui.download_report(filename)
```

**Underlying implementation** (`security/evidence_ui/app.py` lines 388-401):
```python
@app.get("/reports/{filename}")
def download_report(filename: str):
    path = OUT_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    media = (
        "application/pdf"
        if filename.lower().endswith(".pdf")
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if filename.lower().endswith(".docx")
        else "text/plain"
    )
    return FileResponse(str(path), media_type=media, filename=filename)
```

The `filename` parameter is concatenated with `OUT_DIR` via the `/` operator on `pathlib.Path`. An attacker can request:

```
GET /v1/evidence/reports/..%2F..%2F..%2Fetc%2Fpasswd
```

This resolves to a path outside `OUT_DIR` and returns arbitrary files from the server filesystem. The `text/plain` fallback media type ensures non-PDF/DOCX files are served.

### 2.2 Additional Concerns

- **No authentication required:** The `download_report` endpoint does not use `Depends(get_current_user)`. The scan endpoint at line 82 does require auth, but the download endpoint is unprotected.
- **Filename not sanitised for directory traversal:** No check that the resolved path is still within `OUT_DIR`.

### 2.3 Proposed Remediation

**Step 1: Add path traversal protection**

Resolve the path and verify it remains within the intended directory:

```python
def download_report(filename: str):
    # Strip directory components — only allow bare filenames
    safe_name = Path(filename).name
    if not safe_name or safe_name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    path = (OUT_DIR / safe_name).resolve()

    # Defense in depth: verify the resolved path is inside OUT_DIR
    if not str(path).startswith(str(OUT_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    media = (
        "application/pdf"
        if safe_name.lower().endswith(".pdf")
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if safe_name.lower().endswith(".docx")
        else "text/plain"
    )
    return FileResponse(str(path), media_type=media, filename=safe_name)
```

**Step 2: Add authentication**

Require a valid user session for report downloads:

```python
# In backend-api/app/api/v1/evidence.py
@router.get("/reports/{filename}")
async def download_report(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    return evidence_ui.download_report(filename)
```

**Step 3: Restrict file extensions**

Only serve known report formats:

```python
ALLOWED_REPORT_EXTENSIONS = {".pdf", ".docx"}
if Path(safe_name).suffix.lower() not in ALLOWED_REPORT_EXTENSIONS:
    raise HTTPException(status_code=400, detail="Invalid report format")
```

### 2.4 Validation Checklist

#### Code Review

- [ ] **Path traversal blocked:** Verify `download_report()` in `security/evidence_ui/app.py` strips directory components from `filename` (e.g., `Path(filename).name`) **before** constructing the file path
- [ ] **Resolved path checked:** Verify the code calls `.resolve()` on the constructed path and confirms it starts with `OUT_DIR.resolve()`
- [ ] **Authentication added:** Verify the `GET /v1/evidence/reports/{filename}` endpoint in `backend-api/app/api/v1/evidence.py` requires authentication via `Depends(get_current_user)`
- [ ] **File extension restricted:** Verify only `.pdf` and `.docx` extensions are served

#### Manual Testing

- [ ] **Path traversal rejected:** Request `GET /v1/evidence/reports/..%2F..%2Fetc%2Fpasswd` — expect HTTP 400, not file contents
- [ ] **Nested traversal rejected:** Request `GET /v1/evidence/reports/....//....//etc/passwd` — expect HTTP 400
- [ ] **Null byte rejected:** Request `GET /v1/evidence/reports/report.pdf%00.txt` — expect HTTP 400 or 404
- [ ] **Valid report still works:** Upload evidence, generate a report, then download it via the reports endpoint — should succeed
- [ ] **Unauthenticated request rejected:** Request the endpoint without a valid JWT — expect HTTP 401

---

## HIGH Findings

---

## 3. Authentication Rate Limiting

**Severity:** HIGH
**Owner:** Backend API Team
**Files:**
- `backend-api/app/api/v1/auth.py` (lines 18-28)
- `backend-api/app/main.py`

### 3.1 Problem Description

The login (`/v1/auth/login`), registration (`/v1/auth/register`), password reset (`/v1/auth/forgot-password`), and password change endpoints have no rate limiting. An attacker can make unlimited brute-force attempts against any user account with no throttling or lockout.

### 3.2 Proposed Remediation

Use the `slowapi` package (a Starlette/FastAPI rate limiter backed by Redis or in-memory storage):

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# In main.py
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

Apply per-endpoint limits:

| Endpoint | Recommended Limit |
|----------|-------------------|
| `POST /v1/auth/login` | 5 requests per minute per IP |
| `POST /v1/auth/register` | 3 requests per minute per IP |
| `POST /v1/auth/forgot-password` | 3 requests per minute per IP |
| `POST /v1/auth/me/change-password` | 5 requests per minute per IP |

Since Redis is already in the stack (used by Celery), use Redis as the storage backend for `slowapi` to ensure rate limits persist across backend-api restarts and scale across multiple instances.

### 3.3 Validation Checklist

- [ ] **Rate limiter installed:** Verify `slowapi` (or equivalent) is in `backend-api/pyproject.toml`
- [ ] **Rate limiter registered:** Verify the limiter is registered in `main.py`
- [ ] **Login rate limited:** Make 6 rapid login attempts with wrong credentials from the same IP — the 6th should receive HTTP 429
- [ ] **Registration rate limited:** Make 4 rapid registration attempts — the 4th should receive HTTP 429
- [ ] **Rate limit resets:** Wait the rate limit window, then retry — the request should succeed
- [ ] **Legitimate login still works:** Log in with correct credentials within the rate limit — should succeed

---

## 4. CORS Configuration

**Severity:** HIGH
**Owner:** Backend API Team
**Files:**
- `backend-api/app/main.py` (lines 21-27)
- `backend-api/app/core/config.py` (lines 20-21)
- `docker-compose.yml` (lines 95-96, 170)

### 4.1 Problem Description

The backend API uses a wildcard CORS origin (`allow_origins=["*"]`) with `allow_methods=["*"]` and `allow_headers=["*"]`. There is no mechanism to enforce stricter origins in production.

### 4.2 Development Scenarios to Support

The CORS solution must work for all existing development profiles:

| Profile | Frontend | Backend API | Frontend Origin |
|---------|----------|-------------|-----------------|
| `frontend-dev` | Local (`npm start`) on `http://localhost:3000` | Docker on `http://localhost:8000` | `http://localhost:3000` |
| `backend-dev` | Docker on `http://localhost:3000` | Local (`uvicorn`) on `http://localhost:8000` | `http://localhost:3000` |
| `all` | Docker on `http://localhost:3000` | Docker on `http://localhost:8000` | `http://localhost:3000` |
| Production | Deployed URL (TBD) | Deployed URL (TBD) | Production frontend URL |

In all current development scenarios, the frontend origin is `http://localhost:3000`.

### 4.3 Proposed Remediation

**Step 1: Add a `CORS_ORIGINS` setting to `config.py`**

```python
# config.py
CORS_ORIGINS: str = "http://localhost:3000"  # comma-separated list of allowed origins
```

This defaults to the development frontend URL. In production, set the environment variable `CORS_ORIGINS` to the production frontend URL.

**Step 2: Parse and apply in `main.py`**

```python
# main.py
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # now safe with explicit origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Step 3: Update `docker-compose.yml`**

Add the environment variable to the backend-api service:

```yaml
# docker-compose.yml backend-api environment
- CORS_ORIGINS=http://localhost:3000
```

**Step 4: Document for production**

Document that `CORS_ORIGINS` must be set to the production frontend URL(s) when deploying.

### 4.4 Validation Checklist

#### Code Review

- [ ] **No wildcard origin in codebase:** Search `backend-api/` for `allow_origins=["*"]` or `allow_origins=['*']` — must return zero results
- [ ] **CORS_ORIGINS config exists:** Verify `backend-api/app/core/config.py` defines a `CORS_ORIGINS` setting with a safe default (e.g., `http://localhost:3000`), not `*`
- [ ] **Origins parsed from config:** Verify `backend-api/app/main.py` reads origins from the config setting and passes them as a list to `CORSMiddleware`, not as a hardcoded wildcard
- [ ] **allow_headers is explicit:** Confirm `allow_headers` lists specific headers (e.g., `["Authorization", "Content-Type"]`) rather than `["*"]`
- [ ] **allow_methods is explicit:** Confirm `allow_methods` lists specific methods rather than `["*"]`

#### Manual Testing

- [ ] **Allowed origin receives CORS headers:**
  ```bash
  curl -s -o /dev/null -w "%{http_code}" -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -X OPTIONS http://localhost:8000/v1/auth/login
  ```
  Response must include `Access-Control-Allow-Origin: http://localhost:3000` (not `*`)
- [ ] **Disallowed origin is rejected:**
  ```bash
  curl -s -D - -H "Origin: http://evil.example.com" -X OPTIONS http://localhost:8000/v1/auth/login
  ```
  Response must NOT include an `Access-Control-Allow-Origin` header echoing the attacker's origin
- [ ] **Frontend still works:** Open the frontend, log in, and navigate to a data-loading page. Check the browser console for CORS errors — there should be none

---

## 5. Security Headers

**Severity:** HIGH
**Owner:** Backend API Team + Frontend Team
**Files:**
- `backend-api/app/main.py`
- `backend-api/app/core/middleware.py`

### 5.1 Problem Description

No security headers are set on any HTTP response from either the backend API or the frontend. This leaves the application vulnerable to clickjacking, MIME sniffing, and other client-side attacks.

### 5.2 Required Headers

| Header | Value | Why |
|--------|-------|-----|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-sniffing. Directly relevant given the file upload feature. |
| `X-Frame-Options` | `DENY` | Prevents clickjacking via iframe embedding. |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Forces HTTPS. **Production only** — do not set in local development. |
| `Content-Security-Policy` | See section 5.4 | Controls resource loading. Mitigates XSS. |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Prevents leaking internal URLs to external services. |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Disables unused browser features. |
| `X-XSS-Protection` | `0` | Disables legacy XSS auditor (can introduce vulnerabilities). Rely on CSP instead. |

### 5.3 Backend API Implementation

Create a `SecurityHeadersMiddleware` in `backend-api/app/core/middleware.py`:

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-XSS-Protection"] = "0"
        if settings.APP_ENV != "dev":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
```

Register in `main.py` **before** CORSMiddleware (so it runs after CORS, wrapping all responses).

### 5.4 Frontend Content-Security-Policy

A starting-point CSP for the React frontend:

```
default-src 'self';
script-src 'self';
style-src 'self' 'unsafe-inline';
img-src 'self' data: blob:;
font-src 'self';
connect-src 'self' {BACKEND_API_URL};
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
```

Notes:
- `'unsafe-inline'` for `style-src` is commonly needed with Tailwind CSS. Test if this can be removed with nonce-based styles.
- `connect-src` must include the backend API URL.
- `frame-ancestors 'none'` is the CSP equivalent of `X-Frame-Options: DENY`.

### 5.5 Validation Checklist

- [ ] **SecurityHeadersMiddleware exists:** Verify `backend-api/app/core/middleware.py` contains the middleware
- [ ] **Middleware registered in main.py**
- [ ] **All required headers set** on API responses (test with `curl -s -D - http://localhost:8000/v1/auth/login -o /dev/null`)
- [ ] **Headers present on error responses** (test with `GET /v1/nonexistent` — 404 should still include security headers)
- [ ] **HSTS absent in dev:** When running with `APP_ENV=dev`, confirm `Strict-Transport-Security` is NOT present
- [ ] **CSP defined for frontend** either in Vite config, HTML `<meta>` tag, or documented for reverse proxy
- [ ] **No CSP violations in browser console** when navigating all major pages
- [ ] **Charts still render** (CSP can block inline scripts that some chart libraries use)

---

## 6. File Upload Hardening

**Severity:** HIGH
**Owner:** Backend API Team
**Files:**
- `backend-api/app/api/v1/evidence.py` (lines 81-182)

### 6.1 Problem Description

The evidence scanning endpoint (`POST /v1/evidence/scan`) accepts file uploads with:
- No file size limit — entire file read into memory (`await evidence.read()` at line 107)
- No MIME type validation — file type determined solely by extension
- No file extension whitelist enforcement at the API layer

### 6.2 Proposed Remediation

**Step 1: Enforce file size limit**

```python
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

# Check Content-Length header first (fast rejection)
if evidence.size and evidence.size > MAX_UPLOAD_SIZE:
    raise HTTPException(413, "File too large. Maximum size is 10 MB.")

# Read with limit (defense in depth against spoofed Content-Length)
content_bytes = await evidence.read(MAX_UPLOAD_SIZE + 1)
if len(content_bytes) > MAX_UPLOAD_SIZE:
    raise HTTPException(413, "File too large. Maximum size is 10 MB.")
```

**Step 2: Enforce file extension whitelist**

```python
ALLOWED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp",
    ".pdf", ".docx",
    ".txt", ".log", ".reg", ".csv", ".ini", ".json", ".xml", ".htm", ".html",
}

ext = Path(evidence.filename).suffix.lower()
if ext not in ALLOWED_EXTENSIONS:
    raise HTTPException(400, f"Unsupported file type: {ext}")
```

**Step 3: Validate MIME type via content inspection**

Use `python-magic` or the pure-Python `filetype` package to verify file content matches the claimed extension.

**Step 4: Sanitise filenames**

```python
from pathlib import PurePosixPath
safe_filename = PurePosixPath(evidence.filename).name  # strips directory components
```

### 6.3 Dependency Note

`python-magic` requires `libmagic` (`apt-get install libmagic1`). The `filetype` package is a pure-Python alternative with no system dependencies.

### 6.4 Validation Checklist

- [ ] **File size limit defined:** A `MAX_UPLOAD_SIZE` constant exists
- [ ] **Size check before full read:** The handler does NOT call `await evidence.read()` without a size argument
- [ ] **Extension whitelist enforced** before processing
- [ ] **MIME type validation present** via content inspection
- [ ] **Filename sanitised:** Directory components stripped
- [ ] **Oversized file rejected:** Upload a 15 MB file — expect HTTP 413
- [ ] **Disallowed extension rejected:** Upload a valid image renamed to `.exe` — expect HTTP 400
- [ ] **MIME mismatch rejected:** Upload a text file renamed to `.png` — expect HTTP 400
- [ ] **Valid files still work:** Upload legitimate `.png`, `.pdf`, and `.docx` — all should process successfully
- [ ] **Path traversal filename handled:** Upload with filename `../../../etc/passwd` — should be sanitised to `passwd`

---

## 7. Docker Container Hardening

**Severity:** HIGH
**Owner:** DevOps Team
**Files:**
- `backend-api/Dockerfile`
- `engine/Dockerfile`
- `engine/powershell/Dockerfile`
- `engine/docker/powershell/Dockerfile`
- `frontend/Dockerfile`

### 7.1 Problem Description

All containers run as `root` by default. If a container is compromised, the attacker has full root privileges within the container, increasing the blast radius of any exploit.

### 7.2 Per-Container Remediation

For each long-running container, add a non-root user after all build steps:

**backend-api/Dockerfile and engine/Dockerfile** (Python 3.11-slim):
```dockerfile
RUN adduser --disabled-password --gecos "" --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser
```

**frontend/Dockerfile** (Node 20-alpine — has a built-in `node` user):
```dockerfile
RUN chown -R node:node /app
USER node
```

**engine/powershell/Dockerfile:**
```dockerfile
RUN adduser --disabled-password --gecos "" --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser
```

Note: The uv installer writes to `/root/.local/bin`. Install uv to `/usr/local/bin` before switching users, or install as the target user.

**engine/docker/powershell/Dockerfile** (ephemeral `docker run --rm` container):
Lower priority given the short lifetime and `--rm` flag, but implement for consistency.

### 7.3 Additional Hardening

- **Pin the uv install script:** Change `https://astral.sh/uv/install.sh` to a version-pinned URL (e.g., `https://astral.sh/uv/0.x.x/install.sh`) or download and verify a checksum
- **Pin base images to patch versions:** Change `python:3.11-slim` to `python:3.11.x-slim` (specific patch)
- **Drop capabilities in docker-compose:** Add `cap_drop: [ALL]` to each service
- **Read-only root filesystem:** Add `read_only: true` where possible with explicit `tmpfs` mounts

### 7.4 Validation Checklist

For each Dockerfile:

- [ ] **`USER` directive present** after all root-requiring build steps
- [ ] **`USER` is not `root`** — must be a named user or non-zero UID
- [ ] **`USER` appears before `ENTRYPOINT`/`CMD`**
- [ ] **App directory owned by non-root user**

Runtime verification:
- [ ] **Each container runs as non-root:** `docker compose exec <service> whoami` must NOT return `root`
- [ ] **Application still functions** after switching to non-root (migrations run, workers connect, frontend serves)

---

## 8. Sensitive Token Logging

**Severity:** HIGH
**Owner:** Backend API Team
**Files:**
- `backend-api/app/core/users.py` (lines 46, 52)
- `backend-api/app/db/init_db.py` (line 60)

### 8.1 Problem Description

Three `print()` statements output sensitive tokens and credentials to stdout, which is captured by Docker logs:

```python
# users.py line 46 — password reset token leaked
print(f"User {user.id} has forgot their password. Reset token: {token}")

# users.py line 52 — email verification token leaked
print(f"Verification requested for user {user.id}. Verification token: {token}")

# init_db.py line 60 — plaintext default admin password
print(f"  Password: {admin_password}")
```

### 8.2 Proposed Remediation

Replace `print()` with structured logging that excludes sensitive values:

```python
# users.py — on_after_forgot_password
logger.info("Password reset requested", extra={"user_id": user.id})

# users.py — on_after_request_verify
logger.info("Email verification requested", extra={"user_id": user.id})

# init_db.py — admin user creation
logger.info("Default admin user created", extra={"email": admin_email})
```

**Key principle:** Never log tokens, passwords, or credentials. Log the **event** (who requested what) but not the **secret**.

### 8.3 Validation Checklist

- [ ] **No `print()` with tokens in users.py:** Search for `print(` containing `token`, `password`, or `Reset token` — zero results
- [ ] **No `print()` with passwords in init_db.py:** Search for `print(` containing `Password` — zero results
- [ ] **Logger used instead:** Replaced with `logger.info()` calls that log events without secrets
- [ ] **No secrets at INFO level:** If `logger.debug()` is used for development, verify production log level is INFO or above
- [ ] **Codebase-wide sweep:** Run `grep -rn "print(.*\(token\|password\|secret\|key\|credential\)" backend-api/app/ engine/` — review all results

---

## 9. M365 Token Exposure in Process Arguments

**Severity:** HIGH
**Owner:** Engine Team
**Files:**
- `engine/collectors/powershell_client.py` (lines 244-256)

### 9.1 Problem Description

When executing PowerShell cmdlets via Docker, M365 access tokens are passed as `-e` flags in the `docker run` command:

```python
# powershell_client.py line 244
env_vars = ["-e", f"EXO_TOKEN={result['access_token']}"]

# line 250
docker_cmd = ["docker", "run", "--rm"] + env_vars + [self.DOCKER_IMAGE, script]
proc = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=120)
```

This makes the access token visible in the process table (`ps aux`) to any user on the Docker host for the full 120-second timeout window. Access tokens are typically valid for 60 minutes, so a captured token can be reused.

### 9.2 Proposed Remediation

**Option A: Use `--env-file` with a temporary file (recommended)**

Write tokens to a temporary file with restrictive permissions, pass it to Docker, and delete it immediately:

```python
import tempfile
import os

with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
    f.write(f"EXO_TOKEN={result['access_token']}\n")
    env_file = f.name

os.chmod(env_file, 0o600)

try:
    docker_cmd = ["docker", "run", "--rm", "--env-file", env_file, self.DOCKER_IMAGE, script]
    proc = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=120)
finally:
    os.unlink(env_file)
```

**Option B: Pass tokens via stdin**

Pipe tokens into the container via stdin rather than command-line arguments.

### 9.3 Validation Checklist

- [ ] **No tokens in docker command args:** Search `powershell_client.py` for `-e.*TOKEN` in subprocess arguments — must not appear
- [ ] **Env file has restrictive permissions:** If using `--env-file`, verify the temp file is created with mode `0o600`
- [ ] **Env file deleted after use:** Verify the temp file is removed in a `finally` block
- [ ] **`ps aux` test:** While a cmdlet is executing, run `ps aux | grep docker` on the host — the access token must NOT appear in the output
- [ ] **Cmdlets still execute successfully** after the change

---

## 10. CI/CD Security Cleanup

**Severity:** HIGH
**Owner:** DevOps Team
**Files:**
- `.github/workflows/backend-api.yml`
- `.github/workflows/engine.yml`
- `.github/workflows/frontend.yml`
- `.github/workflows/security.yml`
- `.github/workflows/gryp.yml`
- `.github/workflows/database.yml`
- `.github/workflows/Collecter.yml`

### 10.1 Broken Configurations to Fix

#### Issue 1: Broken Dockerfile references in CI

| Workflow | Referenced Path | Actual Path |
|----------|----------------|-------------|
| `backend-api.yml` | `backend-api/docker/backend.Dockerfile` | `backend-api/Dockerfile` |
| `engine.yml` | `engine/docker/engine.Dockerfile` | `engine/Dockerfile` |
| `gryp.yml` | `docker/engine.Dockerfile` | `engine/Dockerfile` |

**Fix:** Update the `docker build -f` paths.

#### Issue 2: CodeQL language misconfigurations

| Workflow | Configured Language | Actual Language |
|----------|-------------------|-----------------|
| `backend-api.yml` | `javascript-typescript` | **Python** |
| `security.yml` | `javascript-typescript` | **Python** |

**Fix:** Change the CodeQL language matrix to `python`.

#### Issue 3: Stale `gryp.yml` workflow

- Targets the `Compliance-Engine` branch (not in the branch strategy)
- Uses `anchore/scan-action@v3` (other workflows use `@v6`)
- References a non-existent Dockerfile path

**Fix:** Delete `gryp.yml`. Its functionality is superseded by Grype steps in `engine.yml`.

#### Issue 4: `database.yml` output variable mismatch

The workflow filters for `database/` changes but uses the output variable name `engine`.

**Fix:** Rename the output variable to match the filter name.

#### Issue 5: Grype scans don't block builds

`backend-api.yml` line 150 and `engine.yml` line 131 both set `fail-build: false`. Vulnerable images can be pushed to Docker Hub.

**Fix:** Set `fail-build: true` with `severity-cutoff: high`.

### 10.2 Security Vulnerabilities in CI

#### Issue 6: CI secrets exposed to PR authors

`.github/workflows/database.yml` (lines 35-38) passes `XRAPID_API_KEY`, `XRAPID_API_HOST`, and `VIRUSTOTAL_API_KEY` as environment variables in a job that triggers on `pull_request`. Any fork PR can exfiltrate these secrets.

**Fix:** Move secret-dependent jobs to `push` triggers only, or use `pull_request_target` with explicit checkout controls.

#### Issue 7: `Collecter.yml` commits GCP infrastructure data to repo

This workflow runs `engine/engine/GCPAccess.py` with a `GCP_CREDENTIALS` secret, collects live GCP data (IAM policies, firewalls, networks, SQL instances, BigQuery datasets, DNS zones), and **commits the JSON output directly to the repository** under `engine/test-configs/`.

On a public repository, this permanently exposes GCP infrastructure configuration in git history.

**Fix:** Delete `Collecter.yml`. If test fixture data is needed, use synthetic/mocked data instead of live GCP output. Audit `engine/test-configs/` for any real infrastructure data already committed, and consider the `GCP_CREDENTIALS` secret compromised if this workflow has ever run.

#### Issue 8: Actions not pinned to SHA

All workflows use major version tags (e.g., `@v4`) instead of commit SHAs. A compromised action publisher can push malicious code to an existing tag.

**Fix:** Pin critical actions to commit SHA:
- `actions/checkout`
- `actions/setup-python`
- `github/codeql-action/*`
- `anchore/scan-action`
- `docker/login-action`

#### Issue 9: Unnecessary `packages: write` permission

`backend-api.yml` line 113 and `engine.yml` line 94 grant `packages: write` without need.

**Fix:** Remove `packages: write` from jobs that don't push to GitHub Container Registry.

### 10.3 Validation Checklist

#### Phase 1 — Fix existing issues

- [ ] **Dockerfile paths corrected** in backend-api.yml and engine.yml
- [ ] **CodeQL language fixed** to `python` in backend-api.yml and security.yml
- [ ] **gryp.yml deleted**
- [ ] **Collecter.yml deleted** (or moved to a private repo if needed)
- [ ] **database.yml variable name fixed**
- [ ] **Secrets moved off `pull_request` trigger** in database.yml

#### Phase 2 — Enforce and harden

- [ ] **Grype `fail-build: true`** with `severity-cutoff: high` in backend-api.yml and engine.yml
- [ ] **Critical actions pinned to SHA**
- [ ] **Unnecessary `packages: write` removed**
- [ ] **All workflows pass** after fixes

---

## 11. Source Maps in Production Build

**Severity:** HIGH
**Owner:** Frontend Team
**Files:**
- `frontend/build/static/` (`.map` files)
- `frontend/vite.config.js`

### 11.1 Problem Description

The production build directory contains JavaScript and CSS source map files (`.js.map`, `.css.map`). Source maps expose the full original source code — including component structure, API client logic, auth flow implementation, and internal comments — to anyone who inspects the deployed application via browser DevTools.

### 11.2 Proposed Remediation

Disable source maps in production builds. In `vite.config.js`:

```javascript
export default defineConfig({
  build: {
    sourcemap: false,  // default is false, but verify it's not overridden
  },
});
```

If source maps are intentionally generated for error monitoring (e.g., Sentry), upload them to the monitoring service and exclude them from the deployed bundle.

Delete existing `.map` files from the `build/` directory and add `*.map` to `.gitignore` if build artifacts are committed.

### 11.3 Validation Checklist

- [ ] **No `.map` files in build output:** After `npm run build`, verify `find build/ -name "*.map"` returns no results
- [ ] **Vite config explicitly disables source maps** (or relies on the default `false`)
- [ ] **Existing `.map` files removed** from the repository

---

## 12. Frontend OAuth State Validation

**Severity:** HIGH
**Owner:** Frontend Team
**Files:**
- `frontend/src/pages/Auth/GoogleCallbackPage.jsx` (lines 51-135)

### 12.1 Problem Description

The Google OAuth callback page extracts an `access_token` from the URL hash or query string but does **not** validate a `state` parameter:

```javascript
// GoogleCallbackPage.jsx — getOAuthParams()
// Extracts: access_token, token_type, error, error_description
// Does NOT extract or validate: state
```

The backend does validate `state` via a cookie (`backend-api/app/api/v1/auth.py:169-171`), but the frontend SPA flow has a gap: if the frontend directly processes the token from the URL without confirming it originated from a legitimate auth request, it is vulnerable to token injection attacks where an attacker crafts a callback URL with a stolen or forged token.

### 12.2 Proposed Remediation

**Step 1: Generate and store a state parameter before redirect**

Before redirecting to Google, generate a random `state` value and store it in `sessionStorage`:

```javascript
const state = crypto.randomUUID();
sessionStorage.setItem("oauth_state", state);
// Include state in the OAuth redirect URL
```

**Step 2: Validate state in callback**

In `GoogleCallbackPage.jsx`, extract the `state` parameter from the callback URL and compare it to the stored value:

```javascript
const params = getOAuthParams();
const storedState = sessionStorage.getItem("oauth_state");
sessionStorage.removeItem("oauth_state");

if (!params.state || params.state !== storedState) {
    setError("Invalid OAuth state. Please try again.");
    return;
}
```

### 12.3 Validation Checklist

- [ ] **State parameter generated before redirect:** Verify the Google OAuth redirect URL includes a `state` parameter
- [ ] **State stored in sessionStorage:** Verify the state value is saved before redirect
- [ ] **State validated in callback:** Verify `GoogleCallbackPage.jsx` compares the returned `state` to the stored value
- [ ] **Stored state cleared after use:** Verify `sessionStorage.removeItem("oauth_state")` is called in the callback
- [ ] **Invalid state rejected:** Manually craft a callback URL with a wrong `state` — the app should show an error, not log the user in
- [ ] **Normal OAuth flow still works:** Complete a full Google sign-in — should succeed without errors

---

## MEDIUM Findings

---

## 13. JWT Token Revocation

**Severity:** MEDIUM
**Owner:** Backend API Team
**Files:**
- `backend-api/app/core/users.py` (lines 65-81)

### 13.1 Problem Description

JWTs are stateless — once issued, they cannot be invalidated until they expire (default: 30 minutes). The `/v1/auth/logout` endpoint exists but only clears client-side storage. If a token is stolen, it remains valid for the full lifetime.

### 13.2 Proposed Solutions

**Option A: Switch to `RedisStrategy` (recommended)**

FastAPI-Users natively supports `RedisStrategy`, which stores opaque tokens in Redis. Since Redis is already in the stack:

```python
from fastapi_users.authentication import RedisStrategy
import redis.asyncio as redis

redis_client = redis.from_url(settings.REDIS_URL)

def get_strategy() -> RedisStrategy:
    return RedisStrategy(redis_client, lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
```

Pros: Built into FastAPI-Users, tokens revocable by deleting from Redis, logout is immediate and server-enforced.
Cons: Every request hits Redis (~1ms), tokens are opaque (not JWTs), token state lost if Redis restarts without persistence.

**Option B: JWT + Redis blocklist (custom)**

Keep JWT strategy but add a blocklist: on logout, add the JWT's `jti` to a Redis set with TTL matching remaining lifetime. Check on every authenticated request.

Pros: Most requests don't hit Redis (only the check, which is fast).
Cons: Custom code to maintain, still checks Redis on every request.

**Option C: Shorten JWT lifetime + refresh tokens**

Reduce `ACCESS_TOKEN_EXPIRE_MINUTES` to 5 and implement refresh tokens. Limits the window of exposure but doesn't fully solve the problem.

### 13.3 Validation Checklist

Depends on chosen option. For any option:

- [ ] **Logout invalidates token:** Log in, note the token, log out, reuse the token — expect HTTP 401
- [ ] **Existing login flow still works**
- [ ] **Google OAuth flow still works**
- [ ] **Concurrent sessions handled correctly**

---

## 14. Frontend Token Storage

**Severity:** MEDIUM
**Owner:** Frontend Team + Backend API Team
**Files:**
- `frontend/src/context/AuthContext.jsx` (lines 18-50, 61-112)
- `frontend/src/api/client.js` (lines 17-45)
- `frontend/src/pages/Auth/GoogleCallbackPage.jsx`

### 14.1 Problem Description

JWT tokens are stored in `localStorage` (when "remember me" is checked) or `sessionStorage` (otherwise). Both are accessible to JavaScript, making them vulnerable to XSS attacks, browser extensions, and third-party scripts.

Currently:
- `AuthContext.jsx` lines 39-50: `persistAuth()` stores token and user JSON in either storage based on the `remember` flag
- `client.js` line 24: Token retrieved and set as `Authorization: Bearer {token}` header
- `GoogleCallbackPage.jsx`: SSO tokens always use `sessionStorage`

### 14.2 Proposed Solutions

**Option A: HttpOnly cookies (recommended, requires backend coordination)**

Move token transport from `Authorization` header to `HttpOnly` cookies. FastAPI-Users supports `CookieTransport` natively:

```python
from fastapi_users.authentication import CookieTransport

cookie_transport = CookieTransport(
    cookie_name="autoaudit_token",
    cookie_max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    cookie_secure=settings.APP_ENV != "dev",
    cookie_httponly=True,
    cookie_samesite="lax",
)
```

Frontend changes:
- Remove all `localStorage`/`sessionStorage` token management
- Remove `Authorization` header from `fetchWithAuth()`
- Add `credentials: "include"` to all `fetch()` calls
- "Remember me" maps to `cookie_max_age` (session cookie vs persistent cookie)

CORS must be updated: `allow_credentials=True` with explicit origins (Section 4).

Pros: Token completely inaccessible to JavaScript (XSS-proof), browser handles lifecycle, native FastAPI-Users support.
Cons: Requires coordinated backend + frontend change. Mobile/native app clients cannot use cookies.

**Option B: Keep Bearer tokens but harden storage**

If HttpOnly cookies are not feasible short-term:
1. Always use `sessionStorage` — remove `localStorage` option entirely
2. Implement short-lived access tokens (5 min) with refresh mechanism (Section 13)

### 14.3 Validation Checklist

For Option A:
- [ ] **CookieTransport configured** with `cookie_httponly=True`, `cookie_samesite="lax"`, `cookie_secure` based on environment
- [ ] **No token in localStorage/sessionStorage:** `localStorage.getItem("token")` and `sessionStorage.getItem("token")` both return `null`
- [ ] **No Authorization header in API calls**
- [ ] **`credentials: "include"` on fetch calls**
- [ ] **Cookie set on login** with correct `HttpOnly`, `SameSite`, and `Secure` flags
- [ ] **Cookie cleared on logout**

---

## 15. Celery Task Security

**Severity:** MEDIUM
**Owner:** Engine Team
**Files:**
- `engine/worker/celery_app.py` (lines 1-35)
- `engine/worker/tasks.py` (lines 101-106)

### 15.1 Problem Description

**a) No message signing:** Celery is configured with JSON serialisation but no HMAC signature verification:

```python
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # No message signing configured
)
```

If the Redis broker is compromised or accessible without authentication, an attacker can inject arbitrary tasks — including tasks that execute PowerShell commands with attacker-controlled parameters.

**b) Credentials in task payloads:** M365 credentials are passed directly in Celery task arguments:

```python
# worker/tasks.py lines 101-106
credentials = {
    "tenant_id": scan["tenant_id"],
    "client_id": scan["client_id"],
    "client_secret": scan["client_secret"],  # plaintext
}
evaluate_control.delay(..., credentials=credentials, ...)
```

If Redis is compromised or task history is logged, credentials are exposed.

### 15.2 Proposed Remediation

**Step 1: Enable Celery message signing**

Configure HMAC-based message signing with a shared secret:

```python
celery_app.conf.update(
    security_key=settings.CELERY_SECURITY_KEY,  # new env var
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)
```

**Step 2: Pass credential references, not values**

Instead of passing credentials in task arguments, pass the `m365_connection_id` and have the worker fetch credentials from the database at execution time:

```python
# Instead of: evaluate_control.delay(..., credentials=credentials)
# Do: evaluate_control.delay(..., m365_connection_id=connection.id)
```

**Step 3: Secure Redis**

Ensure Redis requires authentication (`requirepass` in Redis config) and is not exposed to untrusted networks.

### 15.3 Validation Checklist

- [ ] **Redis requires authentication:** Verify `REDIS_URL` includes a password (e.g., `redis://:password@redis:6379/0`)
- [ ] **Celery message signing configured** (if implemented)
- [ ] **No plaintext credentials in task arguments:** Search `tasks.py` for `client_secret` in `.delay()` or `.apply_async()` calls — should not appear
- [ ] **Workers still process tasks successfully** after changes

---

## 16. Change Password Endpoint

**Severity:** MEDIUM
**Owner:** Backend API Team
**Files:**
- `backend-api/app/api/v1/auth.py` (lines 48-82)

### 16.1 Problem Description

The change password endpoint uses nested `async for` loops over dependency generators instead of proper dependency injection:

```python
@users_router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    user: User = Depends(get_current_user),
):
    async for session in get_async_session():        # <-- wrong pattern
        async for user_manager in get_user_manager(session):  # <-- wrong pattern
            try:
                verified, _ = user_manager.password_helper.verify_and_update(
                    password_data.current_password, user.hashed_password
                )
                # ...
```

FastAPI dependency generators are designed to be consumed via `Depends()`, not iterated manually. This pattern:
- May not execute the generator's cleanup code (after `yield`), causing database connection leaks
- Creates a second database session separate from the request's session, leading to inconsistent state
- May silently fail to commit the password update in some error paths

### 16.2 Proposed Remediation

Refactor to use proper dependency injection:

```python
@users_router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    user_manager = Depends(get_user_manager),
):
    verified, _ = user_manager.password_helper.verify_and_update(
        password_data.current_password, user.hashed_password
    )
    if not verified:
        raise HTTPException(status_code=400, detail="Invalid current password")

    user.hashed_password = user_manager.password_helper.hash(password_data.new_password)
    await session.commit()
    return {"message": "Password changed successfully"}
```

### 16.3 Validation Checklist

- [ ] **No manual generator iteration:** Search `auth.py` for `async for session in` and `async for user_manager in` — must return zero results
- [ ] **Proper Depends() usage:** Verify `session` and `user_manager` are injected via `Depends()`
- [ ] **Password change works:** Change a password via the endpoint — new password should work for subsequent login
- [ ] **Invalid current password rejected:** Submit a wrong current password — expect HTTP 400
- [ ] **No connection leaks:** After repeated password change requests, verify database connection pool is not exhausted

---

## 17. Docker Compose Hardening

**Severity:** MEDIUM
**Owner:** DevOps Team
**Files:**
- `docker-compose.yml`

### 17.1 Problems

**a) Unpinned OPA debug image** (line 60):

```yaml
image: openpolicyagent/opa:latest-debug
```

The `latest` tag is non-deterministic — builds are not reproducible. The `debug` variant includes a shell, increasing attack surface if the container is compromised.

**Fix:** Pin to a specific version without debug: `openpolicyagent/opa:1.x.x` (use the current stable version).

**b) No resource limits:**

No `mem_limit`, `cpus`, or `deploy` constraints on any service. A single container (or a large file upload processed by Tesseract OCR) can consume all host resources.

**Fix:** Add resource limits to each service:

```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '1.0'
```

Suggested limits:

| Service | Memory | CPUs |
|---------|--------|------|
| db | 512M | 1.0 |
| redis | 256M | 0.5 |
| opa | 256M | 0.5 |
| backend-api | 512M | 1.0 |
| worker | 1G | 2.0 |
| frontend | 256M | 0.5 |

**c) Missing health checks on application services:**

Only `db` and `redis` have health checks. `backend-api`, `worker`, and `frontend` do not, leading to services starting before their dependencies are healthy.

**Fix:** Add health checks:

```yaml
backend-api:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### 17.2 Validation Checklist

- [ ] **OPA image pinned** to a specific version without `debug` or `latest`
- [ ] **Resource limits set** on all services
- [ ] **Health checks present** on `backend-api`, `worker`, and `frontend`
- [ ] **All services start successfully** with the new constraints

---

## 18. OPA Communication Security

**Severity:** MEDIUM
**Owner:** Engine Team
**Files:**
- `engine/opa_client.py` (lines 41-46)
- `docker-compose.yml` (OPA service)

### 18.1 Problem Description

The OPA client communicates over plain HTTP without authentication:

```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(
        f"{self.base_url}/v1/data/{url_path}/result",
        json={"input": input_data},
    )
```

In the Docker Compose setup, OPA is on the internal network and this is acceptable. However, if OPA is ever deployed as a separate service or accessible across a network boundary, policy evaluation requests and responses would be transmitted in cleartext.

Additionally, the `url_path` is constructed from metadata fields (framework, benchmark, version, control package). If metadata files are compromised, arbitrary OPA packages could be evaluated.

### 18.2 Proposed Remediation

- **Short-term:** Add a comment documenting that OPA must only be accessible on an internal network
- **Medium-term:** Add OPA authentication tokens (OPA supports Bearer token auth)
- **Validate url_path:** Ensure the path components only contain alphanumeric characters, hyphens, underscores, and dots

### 18.3 Validation Checklist

- [ ] **OPA not exposed to external networks:** Verify `docker-compose.yml` does not map OPA ports to the host in production, or restrict to `127.0.0.1:8181:8181`
- [ ] **url_path validated** before use in OPA requests

---

## 19. Input Validation Gaps

**Severity:** MEDIUM
**Owner:** Backend API Team
**Files:**
- `backend-api/app/api/v1/scans.py` (lines 121-122, 157-186)

### 19.1 Problems

**a) Unvalidated pagination parameters** (lines 121-122):

```python
limit: int = 50,
offset: int = 0,
```

An attacker could request `limit=-1` or `limit=999999999`, potentially causing unexpected behaviour or performance issues.

**Fix:**

```python
limit: int = Query(50, gt=0, le=1000),
offset: int = Query(0, ge=0),
```

**b) Unvalidated status filter** (line 162):

```python
status_filter: str | None = None,
```

While SQLAlchemy parameterisation prevents SQL injection, accepting arbitrary strings is not ideal.

**Fix:**

```python
from typing import Literal
status_filter: Literal["pending", "passed", "failed", "error", "skipped"] | None = None,
```

### 19.2 Validation Checklist

- [ ] **Pagination parameters constrained:** `limit` has `gt=0, le=1000` and `offset` has `ge=0`
- [ ] **Status filter uses Enum or Literal type**
- [ ] **Negative limit rejected:** Request with `limit=-1` — expect HTTP 422
- [ ] **Excessive limit rejected:** Request with `limit=999999999` — expect HTTP 422

---

## LOW Findings

---

## 20. SECURITY.md

**Severity:** LOW
**Owner:** AppSec Team

### 20.1 Why This Should Exist

A `SECURITY.md` file tells security researchers how to responsibly report vulnerabilities. Without it, researchers may disclose publicly (in GitHub issues).

### 20.2 Recommended Content

Place at repository root or `.github/SECURITY.md`:

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| main    | :white_check_mark: |
| staging | :white_check_mark: |
| dev     | :x: (development)  |

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

### How to Report

- **GitHub Security Advisories:** Use the "Report a vulnerability" button in the Security tab (preferred)
- **Email:** [security contact email]

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 5 business days

### Scope

In scope: AutoAudit backend API, engine/worker, frontend, Docker configurations, CI/CD pipelines.
Out of scope: Third-party services (Microsoft 365, Google Cloud), denial of service attacks.
```

Also enable GitHub's private vulnerability reporting (Settings > Security > "Private vulnerability reporting").

### 20.3 Validation Checklist

- [ ] **File exists** at repo root or `.github/SECURITY.md`
- [ ] **Contains private reporting channel** (email and/or GitHub Security Advisories)
- [ ] **Does NOT direct to public issues**
- [ ] **GitHub Security tab shows policy**
- [ ] **Private vulnerability reporting enabled** in GitHub settings

---

## 21. SBOM Generation

**Severity:** LOW
**Owner:** DevOps Team

### 21.1 What and Why

A **Software Bill of Materials (SBOM)** is a machine-readable inventory of every component in the software. When a CVE is announced, an SBOM lets you instantly check if you're affected.

### 21.2 Implementation Plan

**Step 1:** Add `syft` (by Anchore, same vendor as Grype) to each build workflow:

```yaml
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    image: ${{ env.IMAGE_NAME }}:${{ github.sha }}
    format: cyclonedx-json
    output-file: sbom.cyclonedx.json

- name: Upload SBOM artifact
  uses: actions/upload-artifact@v4
  with:
    name: sbom-${{ matrix.service }}
    path: sbom.cyclonedx.json
```

**Step 2:** Generate per-component SBOMs (backend-api, engine, frontend).

**Step 3:** Feed SBOMs into Grype for vulnerability scanning.

**Step 4:** Attach SBOMs as release artifacts.

### 21.3 Validation Checklist

- [ ] **SBOM generation step exists** in backend-api.yml, engine.yml, and frontend.yml
- [ ] **SBOMs uploaded as artifacts**
- [ ] **Format is CycloneDX JSON** with populated `components` array
- [ ] **Key packages present** (fastapi, sqlalchemy, react, etc.)

---

## 22. CODEOWNERS for Security-Sensitive Files

**Severity:** LOW
**Owner:** AppSec Team
**Files:**
- `.github/CODEOWNERS`

### 22.1 Current State

The current CODEOWNERS file has a single catch-all rule:

```
*    @du-dhartley @6igby @liyunze-coding
```

### 22.2 Proposed Changes

Add path-specific rules for security-sensitive files:

```
# Default reviewer(s) for everything
*    @du-dhartley @6igby @liyunze-coding

# ── Security-sensitive files: require AppSec team review ──

# Authentication and authorization
backend-api/app/core/auth.py           @du-dhartley @<appsec-team>
backend-api/app/core/users.py          @du-dhartley @<appsec-team>
backend-api/app/core/permissions.py    @du-dhartley @<appsec-team>

# Configuration and secrets
backend-api/app/core/config.py         @du-dhartley @<appsec-team>
backend-api/app/services/encryption.py @du-dhartley @<appsec-team>

# CORS and middleware
backend-api/app/main.py                @du-dhartley @<appsec-team>
backend-api/app/core/middleware.py      @du-dhartley @<appsec-team>

# PowerShell execution (command injection surface)
engine/powershell/                      @du-dhartley @<appsec-team>
engine/collectors/powershell_client.py  @du-dhartley @<appsec-team>

# Dockerfiles (container security)
**/Dockerfile                           @du-dhartley @<appsec-team>

# CI/CD pipelines
.github/workflows/                      @du-dhartley @<appsec-team>

# Security policy and CODEOWNERS itself
.github/SECURITY.md                     @du-dhartley @<appsec-team>
.github/CODEOWNERS                      @du-dhartley @<appsec-team>

# Docker compose (infrastructure, secrets, ports)
docker-compose.yml                      @du-dhartley @<appsec-team>
```

Replace `@<appsec-team>` with the actual GitHub team handle (e.g., `@Hardhat-Enterprises/appsec`).

### 22.3 Enforcement

For CODEOWNERS to be enforced, configure branch protection on `main` and `staging`:
1. Enable "Require a pull request before merging"
2. Enable "Require review from Code Owners"
3. Set minimum approving reviews to 1

### 22.4 Validation Checklist

- [ ] **Path-specific rules exist** for auth, config, PowerShell, Dockerfiles, workflows, and CODEOWNERS itself
- [ ] **Placeholder usernames replaced** with actual handles
- [ ] **Branch protection enabled** with code owner review required
- [ ] **Test PR triggers correct reviewers:** Modify a security-sensitive file and verify CODEOWNERS-specified reviewers are requested

---

## 23. Frontend Console Logging

**Severity:** LOW
**Owner:** Frontend Team
**Files:**
- `frontend/src/pages/AccountPage.jsx` (line 25)

### 23.1 Problem Description

Error objects are logged to the browser console:

```javascript
console.warn("Logout request failed; clearing local auth anyway:", error);
```

Error objects may contain response bodies with sensitive data (user details, internal error messages, stack traces). While only visible in the user's own browser, this is unnecessary information leakage.

### 23.2 Proposed Remediation

Log a generic message without the error object:

```javascript
console.warn("Logout request failed; clearing local auth anyway.");
```

Or, if the error detail is needed for debugging, log only the status code:

```javascript
console.warn(`Logout request failed (status: ${error?.status}); clearing local auth anyway.`);
```

### 23.3 Validation Checklist

- [ ] **No error objects in console.warn/console.log:** Search frontend source for `console.warn(` and `console.log(` calls that include `error` objects — review each for sensitive data
- [ ] **console.error used sparingly:** Only for genuinely unexpected failures, not expected error paths

---

## Process and Workflow Recommendations

These are not vulnerabilities but improvements to security posture and code quality at the process level.

---

## P1. Pre-commit Hooks

**Owner:** DevOps Team

### P1.1 Recommendation

Add a `.pre-commit-config.yaml` with:

- **`detect-secrets`** — prevents accidental secret commits. This is the highest-value hook for a public repository.
- **`ruff`** — Python linting and formatting (covers backend-api and engine)
- **`eslint`** — JavaScript/JSX linting (covers frontend)

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v9.0.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
```

### P1.2 Validation

- [ ] `.pre-commit-config.yaml` exists in repo root
- [ ] `detect-secrets` hook is configured
- [ ] Running `pre-commit run --all-files` passes (or generates a baseline for existing secrets)

---

## P2. Dependency Scanning in CI

**Owner:** DevOps Team

### P2.1 Recommendation

Add dependency vulnerability scanning to CI workflows:

**Python (backend-api and engine):**
```yaml
- name: Audit Python dependencies
  run: |
    pip install pip-audit
    pip-audit -r requirements.txt --desc on --fix --dry-run
```

Or with `uv`:
```yaml
- name: Audit Python dependencies
  run: uv run pip-audit
```

**JavaScript (frontend):**
```yaml
- name: Audit npm dependencies
  run: npm audit --audit-level=high
```

### P2.2 Validation

- [ ] `pip-audit` step exists in backend-api.yml and engine.yml
- [ ] `npm audit` step exists in frontend.yml
- [ ] Both steps pass (or known vulnerabilities are triaged)

---

## P3. Dependabot Configuration

**Owner:** DevOps Team

### P3.1 Recommendation

Create `.github/dependabot.yml` to get automated dependency update PRs:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/backend-api"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "pip"
    directory: "/engine"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "docker"
    directory: "/backend-api"
    schedule:
      interval: "monthly"

  - package-ecosystem: "docker"
    directory: "/engine"
    schedule:
      interval: "monthly"

  - package-ecosystem: "docker"
    directory: "/frontend"
    schedule:
      interval: "monthly"
```

The `github-actions` ecosystem entry will also flag when pinned actions have newer versions available.

### P3.2 Validation

- [ ] `.github/dependabot.yml` exists
- [ ] Covers `pip`, `npm`, `github-actions`, and `docker` ecosystems
- [ ] Dependabot PRs start appearing within a week

---

## P4. Secrets Management Strategy

**Owner:** DevOps + Backend API Teams

### P4.1 Recommendation

Currently, secrets are managed via environment variables and `.env` files. For production deployment, adopt a secrets manager:

- **Option A: Cloud-native** — GCP Secret Manager, AWS Secrets Manager, or Azure Key Vault (depending on deployment target)
- **Option B: Self-hosted** — HashiCorp Vault

At minimum, before any production deployment:
1. **Rotate all committed secrets** — the Fernet `ENCRYPTION_KEY` and `SECRET_KEY` in `backend-api/.env` are in public git history
2. **Add `.env` to `.gitignore`** — keep only `.env.example` with placeholder values
3. **Use unique secrets per environment** — dev, staging, and production must not share keys

### P4.2 Validation

- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` contains only placeholder values (no real keys)
- [ ] Production deployment uses a secrets manager or environment-injected secrets
- [ ] No committed secrets remain valid (rotated)

---

## P5. DAST Scanning

**Owner:** AppSec Team

### P5.1 Recommendation

Add Dynamic Application Security Testing (DAST) to the CI pipeline or as a periodic scan. DAST tools test the running application for vulnerabilities that static analysis misses (e.g., CORS misconfigurations, missing headers, auth bypasses).

**Recommended tools:**
- **OWASP ZAP** (free, open-source) — run as a GitHub Action against a staging deployment
- **Nuclei** (free, open-source) — template-based scanner with community-maintained vulnerability checks

```yaml
- name: OWASP ZAP Scan
  uses: zaproxy/action-full-scan@v0.12.0
  with:
    target: 'http://localhost:8000'
    rules_file_name: '.zap/rules.tsv'
    cmd_options: '-a'
```

### P5.2 Validation

- [ ] DAST scan runs against staging environment (manually or in CI)
- [ ] Results are reviewed and triaged
- [ ] No HIGH/CRITICAL findings remain unaddressed
