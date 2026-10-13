# AGENTS.md

Rules for AI coding agents working on SUNOVATE (SUN Integrated Management and Knowledge Platform,
Direktorat SUN, DJPPR). Read this file first.

## Before changing anything
- Read `docs/README.md`, `docs/13-handover/ai-agent-handoff.md`, `docs/13-handover/task-tracker.md`, and the relevant domain documentation before changing anything.
- Do not edit the root source documents (`*.pdf`, `*.pptx`, `SUNOVATE_WEB_IMPLEMENTATION_BLUEPRINT_v0.1.md`, `14_*.txt`, `20_*.txt`) or `docs/_archive/`.

## Facts and data
- Do not invent Direktorat SUN business processes, SUN figures, job titles, approval chains, or staff authority.
- `SUN Tematik` functionality is an `OPEN QUESTION` (OQ-01); do not invent behavior.
- Label information as `CONFIRMED` (with source), `PROPOSED`, `OPEN QUESTION`, or `OUT OF SCOPE`. Keep confirmed and proposed separate.
- Use only fictional records labelled `SIMULATED_DATA`. Never add real internal, personal, or financial data without explicit approval.
- Treat the older NestJS/Prisma blueprint as historical `PROPOSED`; this codebase uses FastAPI/SQLAlchemy (ADR-002).

## Boundaries
- SUNOVATE is not SUN Job Monitor. It does not replace official SUN transaction systems or make financial decisions.
- Files remain external references; never store documents as database BLOBs.
- Hermes never accesses the database directly. All data reaches Hermes through `HermesGateway` and permission-checked application services.
- Hermes write actions always require human approval; never auto-execute them.
- Do not enable production identity, document, notification, AI, messaging, BI, or market-data integrations. Never claim an integration exists.
- Never commit secrets or production credentials. `.env` stays git-ignored; `.env.example` holds placeholders only.

## Engineering rules
- Enforce authorization in the API for every protected endpoint: permission AND team scope AND data classification. Menu hiding is cosmetic.
- Every schema change needs a new Alembic revision; never edit an applied migration.
- Add or update tests for important changes, especially authorization, Hermes, and data rules.
- Do not delete files or features without checking impact (search references, tests, docs).
- Update documentation when architecture, API, schema, or permissions change; record major decisions in `docs/12-governance/decision-log.md` and `docs/03-architecture/architecture-decisions.md`.
- Update `docs/13-handover/task-tracker.md` and `CHANGELOG.md` for every material task/status change. A plan, mockup, or proposal is not `DONE` without implementation evidence and validation.
- Keep TypeScript strict, Python typed (mypy strict), server components by default, and changes minimal.
- Do not add Turborepo, Kubernetes, microservices, Redis, a message broker, or new dependencies without a concrete, documented need.
- Go, Rust, PWA, Android, and iOS are deferred roadmap items, not MVP requirements. The proposed Cloudflare Tunnel/Access demo path must not be activated without mentor and TIK/security approval.
- Use only the locked SUNOVATE design tokens; no gradients, purple, Unicode icons, or generic oversized card grids.
- Never expose developer language in user-facing UI. Translate internal codes and terms such as API, endpoint, permission, scope, runtime, retrieval, raw enum values, `SIMULATED_DATA`, `PROPOSED`, `BLOCKED`, and `Hermes` into clear Indonesian labels. Keep technical names only in code, logs, tests, and developer documentation. Follow `docs/09-ui-ux/content-language.md`.

## Before declaring done
Run and report actual results (never claim a command passed without running it):

```bash
pnpm lint && pnpm typecheck && pnpm test && pnpm build
pnpm db:sql          # migration renders offline
pnpm db:check        # optional: real PostgreSQL check without Docker
```
