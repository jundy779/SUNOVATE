# Requirements Baseline

**Status:** NEEDS MENTOR VALIDATION  
**Last Updated:** 2026-10-01

## Functional requirements

- **PROPOSED — FR-01:** authenticated users see only modules and records permitted by role, team/entity scope, and classification.
- **PROPOSED — FR-02:** the Management Cockpit summarizes authorized work, pending matters, follow-ups, and recent knowledge; exact indicators are an **OPEN QUESTION**.
- **PROPOSED — FR-03:** Kinerja Tim Kerja records outputs, assignments, milestones, progress, pending matters, meetings, inspections, and follow-ups.
- **PROPOSED — FR-04:** Knowledge Hub manages metadata, summaries, relationships, versions, classifications, source references, and search indexes without storing official files as database BLOBs.
- **PROPOSED — FR-05:** SUN Business begins read-only; transaction processing is **OUT OF SCOPE** until business rules and sources are confirmed.
- **PROPOSED — FR-06:** reporting exports only data the requester may read and generates an audit event.
- **PROPOSED — FR-07:** Hermes answers through SUNOVATE APIs, includes citations, inherits caller permissions, and cannot query PostgreSQL directly.
- **PROPOSED — FR-08:** sensitive AI write actions remain proposals until an authorized human approves them.
- **PROPOSED — FR-09:** important mutations create append-only audit records in normal application flows.
- **CONFIRMED — FR-10:** development/demo data is visibly marked `SIMULATED_DATA`.

## Quality requirements

- **PROPOSED — NFR-01 Security:** backend authorization is mandatory; menu hiding is not an access control.
- **PROPOSED — NFR-02 Accessibility:** keyboard operation, visible focus, semantic structure, labels, and readable contrast are acceptance criteria.
- **PROPOSED — NFR-03 Reliability:** records with concurrent edits use version checks and return `409 Conflict` on stale updates.
- **PROPOSED — NFR-04 Observability:** structured logs include request IDs and redact secrets and sensitive content.
- **PROPOSED — NFR-05 Performance:** list APIs use server pagination; measurable targets need baseline testing.
- **PROPOSED — NFR-06 Maintainability:** module boundaries are explicit and schema changes use Alembic migrations.
- **PROPOSED — NFR-07 Search safety:** retrieval enforces permission and classification filters before content reaches Hermes.

## Acceptance notes

Each requirement needs an owner, priority, acceptance scenario, and mentor disposition before being marked **CONFIRMED**. No numerical SLA, record-retention period, approval chain, SUN calculation, or organization hierarchy is currently asserted.

## Related Documents

- [Product](../01-product/README.md)
- [Security](../06-security/README.md)
- [Validation](../12-validation/README.md)
