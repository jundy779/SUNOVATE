# SUNOVATE Web Implementation Blueprint v0.1

**Project:** SUNOVATE  
**Expansion:** SUN Innovated Knowledge & Management Platform  
**Organization / Domain:** Direktorat Surat Utang Negara (SUN), DJPPR  
**Document Purpose:** Technical implementation blueprint for the SUNOVATE web platform  
**Status:** Pre-development / Product Foundation  
**Architecture Style:** Modular Monolith

---

# 1. Implementation Goal

This blueprint translates the approved SUNOVATE product direction into a concrete web implementation plan.

SUNOVATE is a broader SUN-wide platform with these major domains:

1. Management Cockpit
2. SUN Business
3. Kinerja Tim Kerja
4. Knowledge Hub
5. Reporting & Analytics
6. Integrations
7. Hermes Agent
8. Security & Governance

SUNOVATE is **not** a rebrand of SUN Job Monitor.

SUN Job Monitor is a separate existing pilot application. Selected patterns may be reused later, but SUNOVATE must have its own architecture, data model, navigation, and implementation boundaries.

---

# 2. Recommended Technology Stack

## Frontend

- Next.js
- TypeScript
- App Router
- Tailwind CSS
- shadcn/ui
- TanStack Query
- TanStack Table
- React Hook Form
- Zod
- Recharts

## Backend

- NestJS
- TypeScript
- REST API for initial implementation
- OpenAPI / Swagger for API documentation

## Database

- PostgreSQL
- Prisma ORM

## Workspace

- pnpm workspace
- monorepo

## Development Infrastructure

- Docker Compose
- PostgreSQL container
- optional local object/document mock service
- local development auth

## AI

- Hermes Agent
- tool-based integration through SUNOVATE APIs
- no unrestricted direct database access

---

# 3. Recommended Repository Structure

```text
sunovate/
│
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── services/
│   │   └── styles/
│   │
│   └── api/
│       ├── src/
│       │   ├── modules/
│       │   ├── common/
│       │   ├── config/
│       │   ├── guards/
│       │   ├── interceptors/
│       │   ├── filters/
│       │   └── main.ts
│       └── test/
│
├── packages/
│   ├── database/
│   │   ├── prisma/
│   │   └── src/
│   │
│   ├── ui/
│   ├── shared/
│   ├── config/
│   └── types/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── database/
│   ├── product/
│   └── runbooks/
│
├── docker-compose.yml
├── pnpm-workspace.yaml
├── package.json
├── .env.example
└── README.md
```

---

# 4. Backend Module Structure

Recommended NestJS modules:

```text
auth
users
roles
permissions
teams

management-cockpit

work-management
meetings
inspections

knowledge
documents

sun-business
reporting

notifications
integrations
audit

ai
health
```

Do not split into microservices in the initial phase.

---

# 5. Frontend Information Architecture

## Primary Navigation

```text
Dashboard

SUN Business
├── Overview
├── Penerbitan
├── Lelang
├── Private Placement
├── Bookbuilding
├── Buyback
├── Debt Switch
├── Settlement
├── Portfolio
├── Yield & Market
└── Close Out Note

Kinerja Tim Kerja
├── Overview
├── Target & Output
├── Penugasan
├── Progress
├── Milestone
├── Pending Matters
├── Tindak Lanjut
├── Rapat
└── Pemeriksaan

Knowledge Hub
├── Overview
├── Regulasi & Kebijakan
├── Kajian & Analisis SUN
├── Pembiayaan & Pengelolaan SUN
├── Market & Yield Knowledge
├── Transaksi & Lelang
├── SOP & Playbook
├── Laporan & Bahan Analisis
├── Organizational Knowledge
└── Arsip & Referensi

Reporting & Analytics

Ask SUNOVATE

Administration
├── Users
├── Roles
├── Teams
├── Master Data
├── Integrations
└── Audit Log
```

Menu visibility must be permission-aware.

---

# 6. Initial Route Map

## Core

```text
/
  → redirect to /dashboard

/dashboard
```

## SUN Business

```text
/sun-business
/sun-business/issuance
/sun-business/auctions
/sun-business/auctions/[id]
/sun-business/private-placement
/sun-business/bookbuilding
/sun-business/buyback
/sun-business/debt-switch
/sun-business/settlements
/sun-business/portfolio
/sun-business/yield
/sun-business/close-out-notes
/sun-business/close-out-notes/[id]
```

Only implement routes validated for the current phase.

## Kinerja Tim Kerja

```text
/performance
/performance/outputs
/performance/outputs/[id]
/performance/assignments
/performance/progress
/performance/milestones
/performance/pending
/performance/follow-ups
/performance/meetings
/performance/meetings/[id]
/performance/inspections
/performance/inspections/[id]
```

## Knowledge Hub

```text
/knowledge
/knowledge/regulations
/knowledge/regulations/[id]
/knowledge/studies
/knowledge/studies/[id]
/knowledge/financing
/knowledge/market
/knowledge/transactions
/knowledge/sop
/knowledge/reports
/knowledge/organizational
/knowledge/archive
```

## AI

```text
/ask-sunovate
```

## Reporting

```text
/reports
/reports/work
/reports/knowledge
/reports/sun-business
```

## Administration

```text
/admin/users
/admin/roles
/admin/teams
/admin/master-data
/admin/integrations
/admin/audit
```

---

# 7. Page Layout Standard

Every operational page should follow a consistent layout:

```text
Breadcrumb
Page title
Short description
Primary action

Filter / Search bar

KPI / status summary if useful

Main content
- table
- cards
- timeline
- charts only when meaningful

Pagination

Drawer / detail panel / modal if needed
```

Do not create decorative dashboards without an operational purpose.

---

# 8. Management Cockpit

The Management Cockpit should answer:

- What is happening?
- What needs attention?
- What is overdue?
- What is pending?
- What requires follow-up?
- What SUN activities are active?
- What knowledge or decision context has changed?

## Initial widgets

```text
Active Outputs
Due Soon
Overdue
Pending Matters
Active Examinations
Open Follow-ups
Recent SUN Business Activity
Recent Knowledge Updates
```

## "Perlu Perhatian"

This section should be visually dominant.

Potential items:

- overdue tasks
- pending decision
- examination deadline
- follow-up without update
- stale work output
- failed integration
- unresolved data quality issue

---

# 9. Kinerja Tim Kerja Implementation

## Work Output

Fields:

```text
id
title
description
team_id
owner_id
start_date
target_date
status
priority
progress
classification
created_at
updated_at
archived_at
version
```

## Assignment / Task

Fields:

```text
id
work_output_id
title
description
category
status
priority
start_date
due_date
progress
classification
created_by
updated_by
created_at
updated_at
archived_at
version
```

## Task Status

```text
NOT_STARTED
IN_PROGRESS
WAITING_INTERNAL
WAITING_EXTERNAL
ON_HOLD
COMPLETED
CANCELLED
```

## Deadline State

Computed by backend service:

```text
SAFE
DUE_SOON
DUE_TODAY
OVERDUE
COMPLETED
```

Do not calculate deadline state separately in multiple frontend components.

---

# 10. Meeting & Follow-Up

## Meeting

```text
id
title
agenda
scheduled_at
ended_at
location
status
organizer_id
summary
decision
classification
created_at
updated_at
version
```

## Meeting Action

```text
id
meeting_id
title
description
owner_id
due_date
status
converted_task_id
created_at
updated_at
version
```

`converted_task_id` should be unique to prevent duplicate conversion.

---

# 11. Inspection / Examination

Types:

```text
BPK
BPKP
ITJEN
OTHER
```

Track:

```text
title
institution
received_date
due_date
status
primary_pic
request
response
supporting_documents
follow_up
history
```

---

# 12. Knowledge Hub Implementation

Knowledge Hub is a substantive SUN knowledge center.

## Knowledge Entry

```text
id
title
type
status
category_id
summary
content
source
effective_date
expired_at
version_label
superseded_by_id
owner_id
classification
created_by
updated_by
created_at
updated_at
archived_at
version
```

## Knowledge Types

```text
REGULATION
POLICY
STUDY
ANALYSIS
SOP
PLAYBOOK
REPORT
WORKING_PAPER
PRESENTATION
MEETING_NOTE
CLOSE_OUT_NOTE
LESSON_LEARNED
FAQ
BEST_PRACTICE
REFERENCE
OTHER
```

## Study Categories

```text
SUN
FINANCING
MARKET
YIELD
PORTFOLIO
RISK
AUCTION
TRANSACTION
POLICY
OTHER
```

## Study Metadata

```text
study_category
period_start
period_end
executive_summary
background
analysis_summary
conclusion
recommendation
methodology
data_source
author
classification
```

The original study file may remain in SharePoint.

SUNOVATE stores:
- metadata
- summary
- relationships
- classification
- search index reference
- source reference

---

# 13. SUN Business Implementation Boundary

Initial database entities may include:

```text
SunInstrument
SunAuction
SunAuctionInstrument
SunTransaction
YieldRecord
Settlement
CloseOutNote
```

But do **not** implement a full transaction engine before the actual business process and data sources are validated.

Recommended order:

1. read-only SUN Business overview
2. instrument metadata
3. auction metadata
4. close-out note
5. market / yield visualization
6. additional transaction workflows only after mentor validation

---

# 14. Document Architecture

Do not store official files as PostgreSQL BLOBs.

Recommended model:

```text
DocumentReference
├── id
├── title
├── source
├── external_id
├── external_url
├── document_type
├── version_label
├── classification
├── owner_id
├── metadata
├── created_at
└── updated_at
```

Potential sources:

```text
LOCAL_REFERENCE
SHAREPOINT
KEMENKEU_SATU
MICROSOFT_365
OTHER
```

Relationship:

```text
DocumentReference
      ↓
EntityDocument
      ↓
Task / Meeting / Inspection / Auction / Knowledge / Other
```

---

# 15. Integration Architecture

External systems should be accessed through provider interfaces.

## Correspondence

```text
CorrespondenceProvider

Development:
MockCorrespondenceProvider

Future:
KemenkeuSatuProvider
```

## Document

```text
DocumentProvider

Development:
LocalDocumentProvider

Future:
SharePointDocumentProvider
```

## Identity

```text
IdentityProvider

Development:
DevelopmentIdentityProvider

Future:
ApprovedSSOProvider
```

## Market Data

```text
MarketDataProvider

Development:
MockMarketDataProvider

Future:
AuthorizedSunDataProvider
```

Do not scatter direct external API calls across business modules.

---

# 16. Hermes Agent Architecture

```text
User
 ↓
Ask SUNOVATE
 ↓
User Authorization Context
 ↓
Hermes Agent
 ↓
Tool Router
 ↓
SUNOVATE API
 ↓
Authorization
 ↓
Application Services
 ↓
Authorized Data Sources
```

## Initial tools

```text
search_regulation
search_knowledge
search_document
get_team_outputs
get_pending_matters
get_meeting_followups
get_inspection_status
get_closeout_note
get_auction_information
query_yield_data
get_report
```

## Write actions

```text
Hermes
→ proposed action
→ human approval
→ SUNOVATE API
→ execute
→ audit log
```

---

# 17. Authentication & Authorization

## Development

Use development auth with seeded users.

## Production

Do not assume implementation until the approved identity mechanism is known.

Potential future:
- Microsoft Entra ID
- organization SSO
- other approved identity provider

## Authorization

Use:
- role
- permission
- team/entity scope
- data classification

Do not rely only on UI menu hiding.

Backend authorization is mandatory.

---

# 18. Initial Permission Model

Possible roles:

```text
SUPER_ADMIN
ADMIN
PIMPINAN
MANAGER
STAFF
VIEWER
AUDITOR
```

Possible permission pattern:

```text
TASK_READ
TASK_CREATE
TASK_UPDATE
TASK_ARCHIVE

OUTPUT_READ
OUTPUT_MANAGE

KNOWLEDGE_READ
KNOWLEDGE_CREATE
KNOWLEDGE_UPDATE
KNOWLEDGE_APPROVE

SUN_BUSINESS_READ
SUN_BUSINESS_MANAGE

REPORT_READ
REPORT_EXPORT

AUDIT_READ

AI_QUERY
AI_ACTION
```

Final role/permission matrix must be validated before production.

---

# 19. API Contract Direction

Use REST for initial implementation.

Base URL:

```text
/api/v1
```

## Common conventions

```text
GET    /resource
GET    /resource/:id
POST   /resource
PATCH  /resource/:id
POST   /resource/:id/archive
POST   /resource/:id/restore
```

Avoid hard delete for normal business records.

## Pagination

```json
{
  "data": [],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 0,
    "totalPages": 0
  }
}
```

## Error format

```json
{
  "code": "TASK_NOT_FOUND",
  "message": "Task tidak ditemukan",
  "details": null,
  "requestId": "..."
}
```

---

# 20. Initial API Groups

```text
/auth
/users
/roles
/teams

/dashboard

/work-outputs
/tasks
/milestones
/pending-matters
/follow-ups

/meetings
/inspections

/knowledge
/knowledge/categories
/knowledge/tags
/documents

/sun-business/instruments
/sun-business/auctions
/sun-business/yield
/sun-business/close-out-notes

/reports

/notifications

/integrations

/audit

/ai
```

---

# 21. Frontend Data Layer

Recommended:

- TanStack Query for server state
- URL query parameters for filter/search state where practical
- React Hook Form + Zod for forms
- avoid unnecessary global client state

Use local/global client state only for:
- UI shell
- temporary drawer/modal state
- current view preference
- non-server transient data

---

# 22. Table Standard

Operational tables should support:

- server-side pagination
- server-side filters
- sort
- search
- visible column control where useful
- row actions
- loading skeleton
- empty state
- error state
- permission-aware actions

Do not fetch all production rows into the browser.

---

# 23. Form Standard

Forms should include:

- Zod schema
- server validation
- field-level errors
- optimistic concurrency version where needed
- save/loading state
- unsaved change warning for long forms
- confirmation for sensitive actions

---

# 24. Concurrency

Frequently edited records should include:

```text
version
```

Update request example:

```json
{
  "version": 7,
  "title": "..."
}
```

Backend updates only if version matches.

On mismatch:

```text
409 CONFLICT
```

UI message:

```text
Data telah diperbarui oleh pengguna lain.
Muat ulang data sebelum menyimpan perubahan.
```

---

# 25. Audit Architecture

Important actions should generate audit events:

```text
LOGIN
CREATE
UPDATE
ARCHIVE
RESTORE
APPROVE
EXPORT
PERMISSION_CHANGE
AI_ACTION
INTEGRATION_SYNC
```

Audit records should include:

```text
actor
action
entity_type
entity_id
before_data
after_data
request_id
timestamp
```

Audit log must be append-only in normal application flows.

---

# 26. Notification Architecture

Initial notifications:

```text
ASSIGNMENT
DUE_SOON
OVERDUE
MENTION
FOLLOW_UP
STATUS_CHANGE
SYSTEM
```

Use a dedupe key to avoid repeated reminders.

Future delivery channels may include:
- in-app
- email
- Microsoft Teams

Do not implement production channels until integration access is available.

---

# 27. Search Architecture

## Phase 1

Use PostgreSQL search for operational entities and metadata.

## Phase 2

Knowledge Hub can use:

```text
PostgreSQL metadata
+
full-text search
+
external / vector retrieval index
```

Relational database remains the source of truth for structured metadata.

Search index is derived data.

---

# 28. Environment Variables

Example structure:

```text
NODE_ENV=

DATABASE_URL=

WEB_URL=
API_URL=

SESSION_SECRET=

DEV_AUTH_ENABLED=

DOCUMENT_PROVIDER=
CORRESPONDENCE_PROVIDER=
MARKET_DATA_PROVIDER=
IDENTITY_PROVIDER=

HERMES_ENABLED=
HERMES_API_URL=
HERMES_API_KEY=
```

Do not commit real secrets.

---

# 29. Docker Compose Direction

Development compose should initially contain:

```text
postgres
```

Optional later:

```text
redis
local document mock
search service
```

Do not add infrastructure until the feature actually needs it.

---

# 30. Development Seed

Seed data:

```text
roles
permissions
sample users
teams
sample output
sample tasks
sample meeting
sample inspection
sample knowledge categories
sample regulations
sample studies
sample SUN instrument
sample auction
```

Never seed real internal/sensitive production data into the repository.

---

# 31. Coding Conventions

## General

- TypeScript strict mode
- no `any` unless justified
- DTO validation in backend
- Zod/form validation in frontend
- explicit domain naming
- avoid generic `utils.ts` dumping grounds
- module ownership must be clear

## Backend

Structure per module:

```text
module/
├── dto/
├── entities/
├── repositories/
├── services/
├── controllers/
├── policies/
└── module.ts
```

Not every module needs every folder.

## Frontend

Prefer feature-oriented organization:

```text
features/
├── work-management/
├── meetings/
├── inspections/
├── knowledge/
├── sun-business/
└── reports/
```

---

# 32. Testing Strategy

## Unit
- business rules
- deadline state
- permission rules
- status transitions
- duplicate protection

## Integration
- repository/database
- API endpoints
- auth and RBAC
- audit events
- meeting action → task

## E2E
Critical workflows:
- login
- dashboard
- create/update work
- meeting follow-up
- inspection
- knowledge search
- permission denial

## AI tests
- authorized retrieval
- unauthorized retrieval blocked
- citation validation
- no-source behavior
- prompt-injection resistance
- sensitive write requires approval

---

# 33. Observability

Initial:

- structured application logs
- request ID
- error logs
- integration failure logs
- health endpoint

Potential future:

- OpenTelemetry
- centralized logging
- performance monitoring
- security monitoring

Do not log secrets or sensitive document content unnecessarily.

---

# 34. Health Endpoints

Recommended:

```text
GET /health
GET /health/database
```

Potential future:

```text
GET /health/integrations
```

Integration health must not expose credentials or sensitive endpoint details.

---

# 35. UX Error States

Every major page should have:

- loading
- empty
- error
- access denied
- archived/inactive state
- stale/conflict state where relevant

Do not show raw backend stack traces.

---

# 36. Initial Build Order

## Sprint / Phase A — Scaffold

1. pnpm monorepo
2. Next.js app
3. NestJS app
4. PostgreSQL + Prisma
5. shared config/types
6. Docker Compose
7. base lint/typecheck/build
8. development auth
9. initial RBAC
10. application shell

## Phase B — Kinerja Tim Foundation

1. team
2. work output
3. task / assignment
4. milestone
5. pending matter
6. follow-up
7. dashboard summaries
8. audit
9. notification foundation

## Phase C — Meeting & Inspection

1. meeting
2. meeting action
3. task conversion
4. inspection
5. follow-up
6. dashboard integration

## Phase D — Knowledge Hub

1. categories
2. knowledge entry
3. regulation metadata
4. study metadata
5. document reference
6. search
7. relation to operational entities

## Phase E — SUN Business Foundation

1. instrument
2. auction
3. close-out note
4. business overview
5. yield read model after data source validation

## Phase F — Integrations

Only after access/requirements are validated.

## Phase G — Hermes

After knowledge, permissions, and APIs are stable enough to serve as reliable tools.

---

# 37. Definition of Ready Before Coding

Before full feature implementation begins, confirm:

- module map accepted
- navigation accepted
- initial role model accepted
- data source boundaries documented
- first MVP scope accepted
- no confusion with SUN Job Monitor
- initial UI direction accepted
- mock vs production integration clearly labeled

---

# 38. Definition of Done

A feature is done when:

1. requirement is implemented
2. API validation exists
3. authorization is enforced
4. loading/error/empty states exist
5. audit requirement is evaluated
6. tests for critical business logic pass
7. no known regression
8. docs are updated
9. integration status is truthfully represented
10. no real sensitive data is added to the repository

---

# 39. MVP Recommendation

A realistic first SUNOVATE MVP should include:

```text
Application Shell
Management Cockpit foundation
Kinerja Tim Kerja
Target / Output
Assignment / Progress / Milestone
Pending Matters
Meeting & Follow-up
BPK/BPKP/Itjen
Basic Reporting
RBAC
Audit
Notification foundation
Knowledge Hub foundation
```

Do not make full Hermes, full yield integration, Kemenkeu Satu production sync, or a complete transaction engine MVP blockers.

---

# 40. Explicit Non-Goals for Early MVP

Do not claim:

- full production Kemenkeu Satu integration
- full SharePoint synchronization
- production SSO
- full SUN transaction processing engine
- production Hermes autonomous actions
- complete market/yield pipeline
- enterprise production readiness

unless those capabilities are actually implemented and validated.

---

# 41. Current Next Action

The next recommended implementation step is:

```text
Phase 0 Finalization
    ↓
Finalize Permission Matrix
    ↓
Finalize API Contract
    ↓
Finalize Prisma Schema
    ↓
Finalize Route / Navigation Map
    ↓
Create SUNOVATE Monorepo Scaffold
```

This blueprint should be treated as the implementation reference until updated by validated mentor feedback or new requirements.
