# Security and Governance

**Status:** NEEDS MENTOR VALIDATION  
**Last Updated:** 2026-10-01

## Principles

- **CONFIRMED:** backend authorization is mandatory; hidden UI controls are not security.
- **CONFIRMED:** Hermes inherits the requesting user's authorization context.
- **CONFIRMED:** Hermes has no direct database access.
- **PROPOSED:** access decisions combine permission, team scope, and data classification.
- **PROPOSED:** sensitive AI writes require explicit human approval and immutable audit evidence.
- **OPEN QUESTION:** classification levels, permission catalogue, retention periods, and approver eligibility.

## Controls

| Area | Initial control |
|---|---|
| Identity | Development-only seeded identities |
| API access | Server-side permission checks |
| Data | Classification and scope filters |
| Changes | Validation, concurrency control, audit |
| AI | Permission-preserving retrieval, citations, approval |
| Secrets | Environment injection; never commit |
| Logs | Exclude secrets and document contents by default |

**OUT OF SCOPE:** asserting compliance certification, penetration-test completion, or production identity readiness.

## Related Documents

- [Authentication](authentication.md)
- [Approval flow](approval-flow.md)
- [Architecture](../03-architecture/README.md)
