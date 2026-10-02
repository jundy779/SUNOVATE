# Validation and Acceptance

**Status:** PROPOSED  
**Last Updated:** 2026-10-01

## Validation strategy

Validation must connect requirements to evidence without relying on unavailable production integrations or real internal data.

| Area | Minimum evidence |
|---|---|
| Build quality | frontend type-check/build; backend lint/type/test; migration check |
| Authorization | allowed and denied API cases, including team/classification scope |
| Core workflows | create/read/update plus conflict and validation errors |
| Knowledge | ingestion provenance, keyword/vector retrieval, citation behavior |
| Hermes | direct DB access absent; unauthorized retrieval denied; write approval enforced |
| Accessibility | keyboard path, labels, focus, contrast, error association |
| Deployment | clean environment starts, migrates, seeds, and passes health checks |

## Acceptance rules

- **CONFIRMED:** test fixtures and demonstrations must use `SIMULATED_DATA`.
- **PROPOSED:** each implemented requirement links to an automated test or a reproducible manual check.
- **PROPOSED:** critical checks include permission denial, stale-write conflict, audit creation, and citation/no-source behavior.
- **OUT OF SCOPE:** production integration acceptance while access is unavailable.
- **OPEN QUESTION:** mentor-approved MVP acceptance criteria and sign-off authority.

## Traceability seed

| Requirement | Planned evidence | Status |
|---|---|---|
| FR-01 permission-aware access | API integration tests | PROPOSED |
| FR-02 Cockpit summaries | API/UI scenario with simulated records | PROPOSED |
| FR-03 work tracking | workflow tests | PROPOSED |
| FR-04 Knowledge Hub | ingestion/search tests | PROPOSED |
| FR-05 RAG citations | retrieval and no-source tests | PROPOSED |
| FR-06 approval/audit | approval state and append-only audit tests | PROPOSED |

## Related Documents

- [Requirements](../02-requirements/README.md)
- [Security](../06-security/README.md)
- [Delivery](../09-delivery/README.md)
- [Handover](../13-handover/README.md)
