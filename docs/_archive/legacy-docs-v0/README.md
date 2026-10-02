# SUNOVATE Documentation

**Status:** DRAFT  
**Last Updated:** 2026-10-01

SUNOVATE (**SUN Integrated Management and Knowledge Platform**) is a proposed integrated management and knowledge platform for Direktorat SUN, DJPPR. The internship delivery period is **21 September 2026–20 March 2027**.

## Evidence labels

- **CONFIRMED** — explicitly established for this documentation baseline.
- **PROPOSED** — a design recommendation requiring acceptance or implementation evidence.
- **OPEN QUESTION** — requires mentor or authorized stakeholder validation.
- **OUT OF SCOPE** — intentionally excluded from the current delivery boundary.

Document statuses are **DRAFT**, **PROPOSED**, **CONFIRMED**, or **NEEDS MENTOR VALIDATION**. Status applies to the document; evidence labels apply to individual statements.

## Documentation map

1. [00 Project](00-project/README.md) — identity, charter, scope, terminology.
2. [01 Product](01-product/README.md) — users, modules, and information architecture.
3. [02 Requirements](02-requirements/README.md) — functional and quality requirements.
4. [03 Architecture](03-architecture/README.md) — context, containers, and boundaries.
5. [04 Data](04-data/README.md) — data model, ownership, and simulated seeds.
6. [05 Knowledge](05-knowledge/README.md) — lifecycle, ingestion, search, and RAG.
7. [06 Security](06-security/README.md) — authentication, authorization, approval, and audit.
8. [07 API](07-api/README.md) — REST conventions and initial API surface.
9. [08 UX](08-ux/README.md) — navigation, design tokens, and accessibility.
10. [09 Delivery](09-delivery/README.md) — roadmap, deployment, and testing.
11. [10 Operations](10-operations/README.md) — observability and operational runbooks.
12. [11 Governance](11-governance/README.md) — decisions, risks, and mentor questions.
13. [12 Validation](12-validation/README.md) — acceptance and traceability.
14. [13 Handover](13-handover/README.md) — handover package and next actions.

## Baseline boundaries

- **CONFIRMED:** architecture is a modular monolith.
- **CONFIRMED:** frontend is Next.js App Router, strict TypeScript, and Tailwind CSS.
- **CONFIRMED:** backend is FastAPI, Pydantic v2, SQLAlchemy 2, and Alembic.
- **CONFIRMED:** PostgreSQL provides relational storage, full-text search, and pgvector.
- **CONFIRMED:** Hermes may call permission-aware SUNOVATE APIs but must not access the database directly.
- **CONFIRMED:** repository seed records must be marked `SIMULATED_DATA`.
- **CONFIRMED:** production SSO, SharePoint, Power BI, Telegram, WhatsApp, Kemenkeu Satu, BI, and market-data integrations are unavailable.
- **OUT OF SCOPE:** claiming unavailable integrations, production readiness, or real internal data.
- **OPEN QUESTION:** the business function of SUN Tematik.

The legacy `SUNOVATE_WEB_IMPLEMENTATION_BLUEPRINT_v0.1.md` remains historical **PROPOSED** context. Its NestJS/Prisma direction is superseded by this session baseline.

## Related Documents

- [Project baseline](00-project/README.md)
- [Architecture](03-architecture/README.md)
- [Decision log](11-governance/decision-log.md)
