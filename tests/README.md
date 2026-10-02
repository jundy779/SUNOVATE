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
