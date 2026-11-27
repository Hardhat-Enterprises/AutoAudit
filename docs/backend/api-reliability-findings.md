# API Reliability and Error Handling: Findings (Sprint 1)

Findings from reviewing how the backend API handles invalid requests, missing resources, access control and unexpected failures. Two endpoint groups were examined in depth (AWS connections and scans), plus the global error handling and the project's test coverage.

## Contents

1. [What I investigated](#1-what-i-investigated)
2. [Current implementation](#2-current-implementation)
3. [How I tested](#3-how-i-tested)
4. [Results](#4-results)
5. [Gaps identified](#5-gaps-identified)
6. [Coverage findings](#6-coverage-findings)
7. [Recommendations / next steps](#7-recommendations--next-steps)
8. [Related pull requests and issues](#8-related-pull-requests-and-issues)

## 1. What I investigated

- The AWS connection endpoints (`backend-api/app/api/v1/aws_connections.py`): create, list, get, update, delete and test.
- The scans endpoints (`backend-api/app/api/v1/scans.py`): create, list, readiness, get, summary, results and delete.
- How the API behaves with missing or invalid input, non-existent resources, unauthenticated requests and users without the right role.
- Whether one user can read or delete another user's scan.
- How the API behaves when something inside the system fails (a corrupt stored secret, the job queue being unavailable).
- The existing automated tests and how coverage is measured.

I also checked from the code (not by running it) that the Azure connection endpoints follow the same pattern as the AWS ones.

## 2. Current implementation

**AWS connections.** Every route depends only on `get_current_user`, so any logged-in user (including a viewer) can call create, update, delete and test. The M365 connection endpoints use `require_auditor_or_above` for those four actions. Lookups go through `_get_user_connection`, which filters by `user_id`, so another user's connection returns 404. Secrets are encrypted with Fernet (`services/encryption.py`). The `/test` endpoint decrypts the stored secret but is a stub: it always returns `success=False` with a "not yet implemented" message. Input is validated by Pydantic (`schemas/aws_connection.py`); `account_id` is described as a 12-digit number but only has `min_length=12, max_length=20`.

**Scans.** Create and delete require `require_auditor_or_above`; the read endpoints require a logged-in user. Every lookup filters by `Scan.user_id == current_user.id`. The list endpoint validates its `status` filter with a `Literal` and bounds `limit` and `offset`. The results endpoint takes `status_filter` as a plain string. The summary endpoint counts results per control category (the prefix of the control ID) across seven statuses. `create_scan` commits the scan and its result rows and then calls `queue_scan(scan.id)`.

**Error handling.** `app/main.py` registers a single exception handler, for `NotFound`. `app/core/errors.py` defines a JSON "problem" format, but only `NotFound` uses it. Any other uncaught exception falls through to the framework default.

**Routing.** Both the AWS and Azure routers are included in the real application (`app/api/v1/router.py`), so the findings below apply to the running API.

## 3. How I tested

- Added endpoint tests in `tests/test_aws_connections.py`, `tests/test_rbac_aws_connections.py`, `tests/test_schemas.py` and `tests/test_scans.py`, following the existing patterns (the mocked `client_factory` for request handling and role checks, and the real test database for ownership and success paths).
- Gaps that need a code change are recorded as expected-failure tests, `@pytest.mark.xfail(strict=True, raises=AssertionError, ...)`, with a reason that links to the tracking issue. If the behaviour is fixed, the test unexpectedly passes and fails the run, which forces the marker to be removed.
- For the unexpected-failure cases I used throwaway probes that return the real 500 response instead of re-raising it into the test:

```python
AsyncClient(
    transport=ASGITransport(app=app, raise_app_exceptions=False),
    base_url="http://testserver",
    cookies=auth_client.cookies,
)
```

  - Decrypt failure: store an `AWSConnection` whose `encrypted_secret_access_key` is not a valid Fernet token, then `POST /v1/aws-connections/{id}/test`.
  - Queue failure: patch `app.api.v1.scans.queue_scan` to raise `ConnectionError`, then `POST /v1/scans/` and count the scans left in the database.

  The probe file was not committed.
- Coverage was measured with `uv run pytest tests/ --cov=app --cov-report=term-missing`, and again with a temporary configuration that adds `concurrency = greenlet,thread` (see [Coverage findings](#6-coverage-findings)).

## 4. Results

### AWS connections

| Test case | Request | Expected | Verdict |
|---|---|---|---|
| Non-existent ID | GET, PUT, DELETE and POST `/test` on `/v1/aws-connections/99999` | 404 | Correct |
| Non-integer ID | GET `/v1/aws-connections/abc` | 422 | Correct |
| Missing required field | POST without `name`, `account_id`, `access_key_id` or `secret_access_key` | 422 | Correct |
| Invalid values | POST with an empty name, `account_id` of 3 or 21 characters, an empty access key, secret or region | 422 | Correct |
| Not logged in | All six routes | 401 | Correct |
| Viewer lists connections | GET `/v1/aws-connections/` | 200 | Correct |
| Viewer modifies connections | POST, PUT, DELETE and POST `/test` as a viewer | 403, as for M365 | **Gap:** not blocked (create returns 201; update, delete and test reach the handler and return 404) |
| Non-numeric `account_id` | POST with `account_id="abcdefghijkl"` | Rejected | **Gap:** accepted by the schema |

### Scans

| Test case | Request | Expected | Verdict |
|---|---|---|---|
| Another user's scan | GET `/{id}`, `/{id}/summary`, `/{id}/results` and DELETE `/{id}` | 404, and a delete must not delete it | Correct |
| Own scan | GET `/{id}` | 200 with its results | Correct |
| Delete own scan | DELETE `/{id}` | 204, results removed | Correct |
| Summary counts | GET `/{id}/summary` with results in every status | Per-category counts, including `indeterminate` and `not_assessable`; a `pending` result counts toward the total only | Correct |
| Results filter and order | GET `/{id}/results`, with and without `status_filter=failed` | Filtered, ordered by control ID | Correct |
| Unknown results filter | GET `/{id}/results?status_filter=banana` | 422, as for the list endpoint | **Gap:** returns 200 with `[]` |
| Invalid list filters | GET `/` with an unknown `status`, `limit=0`, `limit=101`, `offset=-1` | 422 | Correct (existing tests) |

### Unexpected failures

| Case | What happens | Verdict |
|---|---|---|
| Stored secret cannot be decrypted | `POST /v1/aws-connections/{id}/test` returns `500`, `Content-Type: text/plain`, body `Internal Server Error` | **Gap** |
| Job queue unavailable on create | `POST /v1/scans/` returns `500`, and one scan is left in the database with status `pending` that nothing will run | **Gap** |
| Content of the 500 response | Generic: no stack trace and no secret; details only go to the server log | Good |
| Database unavailable | The readiness endpoint returns 503 (covered by existing tests) | Correct |

## 5. Gaps identified

| # | Gap | Where | Tracked in |
|---|---|---|---|
| 1 | Create, update, delete and test do not enforce auditor-or-above, so a viewer can modify cloud connections and their stored credentials. Azure has the same pattern (confirmed from the code). | `aws_connections.py`, `azure_connections.py` | Issue #443 |
| 2 | `account_id` accepts non-numeric values although it is described as a 12-digit number | `schemas/aws_connection.py` | Issue #443 |
| 3 | `status_filter` on the results endpoint is not validated, so a typo returns `200 []`, which reads as "no matching results" | `scans.py` | Issue #454 |
| 4 | A failed queue call leaves an orphaned `pending` scan, and a retry creates a duplicate | `scans.py` (`create_scan`) | This document |
| 5 | An undecryptable stored secret gives a bare plain-text 500 | `aws_connections.py` (`test_connection`) | This document |
| 6 | Unexpected exceptions are not returned in the project's JSON problem format | `main.py`, `core/errors.py` | This document |
| 7 | The results endpoint docstring lists five statuses and omits `indeterminate` and `not_assessable` | `scans.py` | This document |

### Observations from the review of the status migration (#437), from reading the code

- `engine/worker/db.py` increments the scan counts with one raw SQL function per status (passed, failed, error, skipped) and none for the two new statuses, so `indeterminate_count` and `not_assessable_count` stay at 0. The summary endpoint's category breakdown is counted live from `scan_result`, so the two can disagree once the engine writes the new statuses.
- The worker computes the compliance score as `passed / (passed + failed)`, so the new statuses are correctly excluded, but a scan whose controls are all `indeterminate` or `not_assessable` gets a score of `0.00`.

## 6. Coverage findings

- The repository's coverage configuration (`[tool.coverage.run]` in `backend-api/pyproject.toml`) has no `concurrency` setting. SQLAlchemy's async engine runs database calls on greenlets, and coverage.py does not trace code that runs after a database `await` without `concurrency = greenlet`. Coverage of database-backed endpoints is therefore understated.
- Measured on the same code and tests, only the configuration differs:

| File | Repo configuration | With `concurrency = greenlet,thread` |
|---|---|---|
| `scans.py` before the new tests | 46% | 75% |
| `scans.py` after the new tests | 49% | 89% |

- With the repository's configuration, `aws_connections.py` went from 32% to 54% after the new tests, and `azure_connections.py` stayed at 32% (no tests added there). These figures are understated for the same reason.
- The temporary configuration did not include the repository's `omit` list, so its overall total is not comparable with the repository's; only the per-file comparison is valid.
- The evidence endpoints are excluded from the coverage report (see `omit` in `pyproject.toml`); see [evidence-handling-findings.md](evidence-handling-findings.md).
- Setting up the test environment also needs `uv sync --extra evidence` and a local Postgres with a database named `autoaudit_test`; the README does not say so.

## 7. Recommendations / next steps

1. **Enforce auditor-or-above** on create, update, delete and test for the AWS and Azure connection endpoints, add the equivalent RBAC tests for Azure, and remove the `xfail` markers. First confirm that the M365 rules are the intended policy.
2. **Handle a queue failure in `create_scan`:** mark the scan `failed` with a note (or delete it) and return a 503 with a problem-style body, so no orphaned `pending` scan is left.
3. **Handle a decrypt failure** in the AWS test endpoint (catch `InvalidToken`) and return a clear error, and check whether the Azure test endpoint has the same pattern.
4. **Consider a catch-all exception handler** that returns the problem format without internal details. It changes error responses across the whole API, so it needs team agreement first.
5. **Validate `status_filter`** with a `Literal`, ideally from one shared list of result statuses (the list now lives in the migration, the model and the schema), and update the docstring.
6. **Tighten `account_id`** to exactly 12 digits.
7. **Fix the coverage configuration** (add `concurrency`), re-measure with the repository's `omit` list, update the baseline and revisit the `fail_under` gate.
8. **Make the engine and the API consistent** for the new statuses: increment the new counts when results are written, and decide how a scan with no `passed` or `failed` results should be scored.
9. **Update the README** test setup (the evidence extra and the `autoaudit_test` database).

The `xfail` tests to flip when the fixes land:

- `tests/test_rbac_aws_connections.py::test_viewer_cannot_modify_aws_connections` (four cases)
- `tests/test_schemas.py::test_aws_account_id_must_be_numeric`
- `tests/test_scans.py::test_results_rejects_unknown_status_filter`

### Not verified

- Behaviour against a real Redis outage (the queue failure was simulated by patching `queue_scan`).
- Whether the Azure endpoints behave exactly like the AWS ones beyond the role dependency (only the `Depends(...)` lines were read).
- Behaviour with production-sized or real data.

## 8. Related pull requests and issues

- [#434](https://github.com/Hardhat-Enterprises/AutoAudit/pull/434): fixes the backend README test setup command.
- [#438](https://github.com/Hardhat-Enterprises/AutoAudit/pull/438): AWS connection endpoint tests, RBAC and `account_id` expected-failure tests.
- [#458](https://github.com/Hardhat-Enterprises/AutoAudit/pull/458): scans endpoint tests, including the `status_filter` expected-failure test.
- [#437](https://github.com/Hardhat-Enterprises/AutoAudit/pull/437): the status migration reviewed from the backend side.
- [Issue #443](https://github.com/Hardhat-Enterprises/AutoAudit/issues/443): AWS and Azure connection endpoints do not enforce auditor-or-above.
- [Issue #454](https://github.com/Hardhat-Enterprises/AutoAudit/issues/454): results endpoint accepts unknown `status_filter` values.
- Coverage configuration issue: [ADD ISSUE NUMBER].
