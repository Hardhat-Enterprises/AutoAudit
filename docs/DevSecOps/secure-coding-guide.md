# Secure Coding Guide — DevSecOps Stream

This guide documents secure coding practices for contributors to the AutoAudit codebase, grounded in patterns already used across the project and the security tooling that runs in CI.

## Authentication & Authorization

AutoAudit uses FastAPI's dependency injection system to enforce authentication and role-based access control (RBAC) consistently across the backend. Follow these patterns when adding new endpoints.

### Authenticating a route

Never manually parse tokens or check headers directly in a route. Use the existing `get_current_user` dependency:

```python
from app.core.auth import get_current_user

@router.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    return {"user": user.email}
```

### Enforcing role-based access

Use the convenience functions in `app/core/permissions.py` rather than writing role checks inline:

- `require_admin` — restricts to admin users only
- `require_auditor_or_above` — allows auditor or admin
- `require_viewer_or_above` — allows any authenticated user

```python
from app.core.permissions import require_admin

@router.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str, user: User = Depends(require_admin)):
    ...
```

If you need a custom role combination not covered by the existing functions, use the `RoleChecker` class rather than duplicating the pattern:

```python
from app.core.permissions import RoleChecker
from app.models.user import Role

require_custom = RoleChecker([Role.ADMIN, Role.AUDITOR])
```

### Why this matters

Bypassing these dependencies (e.g. checking `user.role` manually inside a route body) is easy to get wrong and inconsistent to review. Centralising the checks means CodeQL and reviewers can verify access control at a glance, and any future permission changes only need updating in one place.



## Secrets & Credential Handling

Never commit real credentials, API keys, tokens, or connection strings containing passwords — even temporarily, even in a branch you plan to squash later. Git history is permanent once pushed.

### Automated protection

This repo uses `detect-secrets` as a pre-commit hook to catch potential credentials before they're committed. Make sure it's installed after cloning:

```bash
pip install pre-commit
pre-commit install
```

If `detect-secrets` blocks a commit, don't bypass it — check whether it's a real secret first.

### Handling false positives

Sometimes a placeholder or example value gets flagged even though it isn't a real credential (e.g. a dev-only default password in `docker-compose.yml`). If you're certain it's not sensitive, suppress it with an inline comment rather than disabling the hook:

```python
DATABASE_URL = "postgresql://user:devpassword@localhost/db"  # pragma: allowlist secret
```

Existing findings are tracked in `.secrets.baseline` — check there before assuming something is a new issue.

### Local development credentials

For local development, use environment variables loaded from a `.env` file (already gitignored) rather than hardcoding values in source files. See `env.example` for the expected variables.

### Why this matters

A leaked secret in git history can be extracted long after the file is "fixed" in a later commit — removing a value from the current version of a file does not remove it from history. Prevention at commit time is far cheaper than rotating credentials after a leak.


## Dependency Management

Every dependency you add is code you didn't write but are still responsible for. AutoAudit already scans for known vulnerabilities in dependencies — this section covers how to work with that scanning rather than around it.

### Automated scanning

The repo runs Grype (`ci.grype.yml`) on pull requests and pushes to `main` when files change inside `frontend/`, `backend-api/`, or `engine/`, and weekly on a schedule. Grype checks dependency files — `pyproject.toml`, `requirements.txt`, and `package-lock.json` — against public vulnerability databases. Findings are uploaded to the GitHub Security tab as a SARIF report rather than blocking the build, so a flagged dependency will not fail your PR automatically — it is on you to check the Security tab and treat findings seriously rather than ignoring them because the build went green.

### Adding a new dependency

Before adding a new package:

- Check whether an existing dependency already covers what you need — every new package is another thing Grype has to watch and another potential source of vulnerabilities
- Prefer well-maintained, widely-used packages over small or unmaintained ones
- After adding it, check the GitHub Security tab for any new Grype findings tied to your PR

### Updating dependencies

Keep dependency files current rather than letting them drift:

- Python: update `pyproject.toml` / `requirements.txt` deliberately, and re-run the app locally to confirm nothing breaks
- Frontend: update `package-lock.json` via `npm install` rather than hand-editing it

### A note on Dependabot

Dependabot is currently paused on this repo (`open-pull-requests-limit` set to 0) because the volume of automatic update PRs became difficult to review individually. This means dependency updates are currently a manual responsibility rather than something automation handles for you — don't assume dependencies are being kept current in the background.

### Why this matters

An outdated or vulnerable dependency can introduce a security hole with no code change of your own — the risk is inherited the moment you add the package. Treating dependency scanning results as informational rather than actionable is one of the most common ways security tooling ends up ignored in practice.