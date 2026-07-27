# Secure Coding Guide — DevSecOps Stream

This guide documents secure coding practices for contributors to the AutoAudit codebase, grounded in patterns already used across the project and the security tooling that runs in CI.



* ### Authentication \& Authorization

AutoAudit uses FastAPI's dependency injection system to enforce authentication and role-based access control (RBAC) consistently across the backend. Follow these patterns when adding new endpoints.



\### Authenticating a route



Never manually parse tokens or check headers directly in a route. Use the existing `get\_current\_user` dependency:



​```python

from app.core.auth import get\_current\_user



@router.get("/protected")

async def protected\_route(user: User = Depends(get\_current\_user)):

&#x20;   return {"user": user.email}

​```



\### Enforcing role-based access



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



​```python

from app.core.permissions import RoleChecker

from app.models.user import Role



require\_custom = RoleChecker(\[Role.ADMIN, Role.AUDITOR])

​```



\### Why this matters



Bypassing these dependencies (e.g. checking `user.role` manually inside a route body) is easy to get wrong and inconsistent to review. Centralising the checks means CodeQL and reviewers can verify access control at a glance, and any future permission changes only need updating in one place.

