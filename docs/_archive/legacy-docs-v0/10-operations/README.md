# Operations

**Status:** PROPOSED  
**Last Updated:** 2026-10-01

## Operational baseline

- **PROPOSED:** expose application and database readiness checks without sensitive details.
- **PROPOSED:** emit structured logs with request ID, actor ID where lawful, route, outcome, and duration.
- **PROPOSED:** record integration failures separately from domain validation failures.
- **CONFIRMED:** never log secrets or unrestricted document content.
- **OUT OF SCOPE:** asserting production monitoring, service-level objectives, or support coverage before infrastructure is provided.

## Minimum runbooks

1. Application fails to start: validate configuration presence, migration state, and database reachability.
2. Migration fails: stop rollout; preserve the database; review Alembic revision order; do not force schema state.
3. Search degradation: verify FTS/vector derived indexes while preserving relational source records.
4. Hermes failure: disable AI entry points without disabling core platform functions.
5. Suspected authorization incident: preserve audit evidence, suspend affected capability, and escalate through the approved channel.

## Backup and recovery

- **OPEN QUESTION:** approved backup frequency, retention, recovery objectives, and responsible operator.
- **PROPOSED:** every restore procedure must be tested in a non-production environment before acceptance.
- **PROPOSED:** derived vector/search data may be rebuilt from authorized source records.

## Related Documents

- [Deployment](../09-delivery/deployment.md)
- [Security](../06-security/README.md)
- [Risk register](../11-governance/risk-register.md)
