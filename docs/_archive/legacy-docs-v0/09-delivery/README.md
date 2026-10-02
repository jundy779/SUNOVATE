# Delivery Plan

**Status:** PROPOSED  
**Last Updated:** 2026-10-01

## Delivery window

- **CONFIRMED:** internship period is 21 September 2026–20 March 2027.
- **PROPOSED:** delivery uses incremental vertical slices, each with authorization, validation, audit evaluation, and documentation.

## Proposed phases

1. Foundation: repository scaffold, local environment, simulated identities, RBAC, and application shell.
2. Core management: teams, outputs, assignments, dashboard summaries, and audit foundation.
3. Collaboration: meetings, follow-ups, and inspection tracking after workflow validation.
4. Knowledge: metadata, ingestion, FTS, pgvector retrieval, citations, and approval.
5. SUN Business read models and reporting only after mentor validates sources and fields.
6. Hermes integration after APIs and permission enforcement are stable.

Dates, sprint commitments, and feature priorities within the window remain **OPEN QUESTION**.

## Quality gates

- strict frontend type-check and backend type/static checks;
- database migration upgrade/downgrade tested;
- unit tests for permission and non-trivial state logic;
- integration tests for API, database, audit, and approval;
- critical user flow tests with `SIMULATED_DATA`;
- documentation updated with each behavior change.

## Related Documents

- [Deployment](deployment.md)
- [Requirements](../02-requirements/README.md)
- [Validation](../12-validation/README.md)
