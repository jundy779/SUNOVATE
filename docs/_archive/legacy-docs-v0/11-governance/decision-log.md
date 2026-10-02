# Decision Log

**Status:** CONFIRMED  
**Last Updated:** 2026-10-01

| ID | Date | Status | Decision | Rationale / consequence |
|---|---|---|---|---|
| ADR-001 | 2026-10-01 | CONFIRMED | Use a modular monolith. | Minimize operational complexity while preserving domain boundaries. |
| ADR-002 | 2026-10-01 | CONFIRMED | Use Next.js App Router, strict TypeScript, and Tailwind. | Current frontend baseline. |
| ADR-003 | 2026-10-01 | CONFIRMED | Use FastAPI, Pydantic v2, SQLAlchemy 2, and Alembic. | Supersedes legacy NestJS/Prisma proposal. |
| ADR-004 | 2026-10-01 | CONFIRMED | Use PostgreSQL with FTS and pgvector. | One data platform for structured records and derived retrieval indexes. |
| ADR-005 | 2026-10-01 | CONFIRMED | Deny Hermes direct database access. | Preserve authorization, validation, and audit at API boundary. |
| ADR-006 | 2026-10-01 | CONFIRMED | Mark every repository seed record `SIMULATED_DATA`. | Prevent demo data being mistaken for official data. |
| ADR-007 | 2026-10-01 | PROPOSED | Start with local development identity and permission fixtures. | Production SSO is unavailable; production identity remains undecided. |
| ADR-008 | 2026-10-01 | PROPOSED | Treat FTS/vector indexes as derived data. | Authoritative metadata stays relational and rebuildable. |
| ADR-009 | 2026-10-01 | CONFIRMED | Do not claim unavailable production integrations. | SSO, SharePoint, Power BI, Telegram, WhatsApp, Kemenkeu Satu, BI, and market data are unavailable. |
| ADR-010 | 2026-10-01 | OPEN QUESTION | Define SUN Tematik scope only after mentor validation. | Avoid inventing organizational responsibilities. |

New decisions must include date, evidence status, owner, alternatives considered, and documents affected.

## Related Documents

- [Architecture](../03-architecture/README.md)
- [Risk register](risk-register.md)
- [Mentor questions](open-questions-mentor.md)
