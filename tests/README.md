# tests/

Cross-cutting Python test suites. They import `sunovate_api` and run with the API
environment: `pnpm api:test` (runs `apps/api/tests` and this folder).

| Folder | Content |
|---|---|
| `security/` | Authentication, team scope, classification, leakage, error hygiene |
| `rag-evaluation/` | Hermes golden set with leakage and citation hard gates |
| `integration/` | PostgreSQL checks; skipped unless `SUNOVATE_TEST_DATABASE_URL` is set |
| `fixtures/` | `SIMULATED_DATA` fixtures, including `rag_golden_set.json` |

All fixtures are fictional and labelled `SIMULATED_DATA`. See `docs/10-testing/`.

## Backends

- `pnpm test` / `pnpm api:test`: `SUNOVATE_TEST_BACKEND` unset, so every suite runs on the in-memory
  `simulated` backend; postgres-only tests and `integration/` are skipped.
- `pnpm db:test`: starts a throwaway PostgreSQL (pgserver), runs `alembic upgrade head` and the seed,
  then runs the same pytest suites with `SUNOVATE_TEST_BACKEND=postgres` (ADR-015). `conftest.py`
  resets the database (TRUNCATE + seed) before every test; the reset refuses to run unless
  `APP_ENV=test` and `SUNOVATE_DB_RESET_ALLOWED=1`.
