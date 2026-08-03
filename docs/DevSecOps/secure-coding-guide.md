# Secure Coding Guide — DevSecOps Stream

This guide documents secure coding practices for contributors to the AutoAudit codebase, grounded in patterns already used across the project and the security tooling that runs in CI.


 ### Authentication \& Authorization

AutoAudit uses FastAPI's dependency injection system to enforce authentication and role-based access control (RBAC) consistently across the backend. Follow these patterns when adding new endpoints.


### Authenticating a route


Never manually parse tokens or check headers directly in a route. Use the existing `get\_current\_user` dependency:


```python

from app.core.auth import get\_current\_user


@router.get("/protected")

async def protected\_route(user: User = Depends(get\_current\_user)):

&#x20;   return {"user": user.email}

​```

### Enforcing role-based access


Use the convenience functions in `app/core/permissions.py` rather than writing role checks inline:


\- `require\_admin` — restricts to admin users only

\- `require\_auditor\_or\_above` — allows auditor or admin

\- `require\_viewer\_or\_above` — allows any authenticated user



​```python

from app.core.permissions import require\_admin


@router.delete("/tenants/{tenant\_id}")

async def delete\_tenant(tenant\_id: str, user: User = Depends(require\_admin)):

&#x20;   ...

​```

If you need a custom role combination not covered by the existing functions, use the `RoleChecker` class rather than duplicating the pattern:



```python

from app.core.permissions import RoleChecker

from app.models.user import Role


require\_custom = RoleChecker(\[Role.ADMIN, Role.AUDITOR])

​```

### Why this matters

Bypassing these dependencies (e.g. checking `user.role` manually inside a route body) is easy to get wrong and inconsistent to review. Centralising the checks means CodeQL and reviewers can verify access control at a glance, and any future permission changes only need updating in one place.



## Secrets & Credential Handling

Never commit real credentials, API keys, tokens, or connection strings containing passwords — even temporarily, even in a branch you plan to squash later. Git history is permanent once pushed.

### Automated protection

This repo uses `detect-secrets` as a pre-commit hook to catch potential credentials before they're committed. Make sure it's installed after cloning:

​```bash
pip install pre-commit
pre-commit install
​```

If `detect-secrets` blocks a commit, don't bypass it — check whether it's a real secret first.

### Handling false positives

Sometimes a placeholder or example value gets flagged even though it isn't a real credential (e.g. a dev-only default password in `docker-compose.yml`). If you're certain it's not sensitive, suppress it with an inline comment rather than disabling the hook:

​```python
DATABASE_URL = "postgresql://user:devpassword@localhost/db"  # pragma: allowlist secret
​```

Existing findings are tracked in `.secrets.baseline` — check there before assuming something is a new issue.

### Local development credentials

For local development, use environment variables loaded from a `.env` file (already gitignored) rather than hardcoding values in source files. See `env.example` for the expected variables.

### Why this matters

A leaked secret in git history can be extracted long after the file is "fixed" in a later commit — removing a value from the current version of a file does not remove it from history. Prevention at commit time is far cheaper than rotating credentials after a leak.

