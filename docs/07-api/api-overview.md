# API Overview

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Memberikan gambaran API SUNOVATE: gaya, prefix, modul, dokumentasi OpenAPI, dan label data. Detail berada pada dokumen terkait di folder ini.

## Confirmed Information

- **CONFIRMED** Backend Python FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic dalam modular monolith (sumber: brief sesi 2026-10-01; ADR-001, ADR-002).
- **CONFIRMED** API bergaya REST dengan prefix `/api/v1` (sumber: fact sheet bagian 9).
- **CONFIRMED** OpenAPI dihasilkan FastAPI; UI interaktif di `/docs` saat `pnpm api:dev` berjalan pada port 8000 (sumber: fact sheet bagian 9).
- **CONFIRMED** Skema JSON OpenAPI tersedia di `/openapi.json` (default FastAPI; sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED** Seluruh endpoint pada [endpoint-catalog](endpoint-catalog.md) berjalan terhadap simulated store (`DATA_BACKEND=simulated`); repository SQLAlchemy belum diimplementasikan (sumber: ADR-007).
- **CONFIRMED** Setiap respons sukses membawa `meta.dataLabel` = `SIMULATED_DATA`, dan setiap respons membawa header `X-Request-ID` (sumber: fact sheet bagian 9).
- **CONFIRMED** Hermes diakses hanya melalui API (`/hermes/...`) dan `HermesGateway`; tidak ada akses langsung Hermes ke database (sumber: ADR-004).

## Konsumen

| Konsumen | Cara akses | Status |
|---|---|---|
| Aplikasi web Next.js | Server component dan route handler (termasuk proxy `/api/hermes`) memanggil API dengan header Bearer | CONFIRMED |
| Klien lain (bot, Power BI, integrasi) | Belum ada | OUT OF SCOPE sampai divalidasi |

## Modul

| Modul | Path utama | Fungsi singkat |
|---|---|---|
| health | `/health`, `/health/database` | Status layanan dan database |
| auth | `/auth/dev/login`, `/auth/me` | Login pengembangan dan principal aktif |
| identity | `/users`, `/teams`, `/roles`, `/permissions`, `/classifications` | Data identitas dan referensi akses |
| knowledge | `/knowledge` | Knowledge entry dan pengajuan review |
| documents | `/documents` | Document reference dan versi |
| search | `/search` | Pencarian teks atas rekaman yang boleh dibaca |
| work | `/dashboard/summary`, `/work-outputs`, `/tasks`, `/milestones` | Monitoring pekerjaan dan ringkasan dashboard |
| pending | `/pending-matters`, `/follow-ups` | Pending matters dan tindak lanjut |
| audit | `/audit-logs` | Audit log |
| approvals | `/approvals` | Approval request dan keputusan |
| hermes | `/hermes/query`, `/hermes/messages/{id}/feedback` | AI Knowledge Assistant |
| providers | `/providers` | Status provider (development, disabled) |
| data quality | `/data-quality-issues` | Data quality issue |

Modul berada di `apps/api/sunovate_api/modules/`: `health`, `auth`, `identity`, `knowledge`, `documents`, `search`, `dashboard` (`/dashboard/summary`), `work`, `pending`, `audit`, `approvals`, `hermes`, dan `system` (`/providers`, `/data-quality-issues`). Daftar lengkap ada di [endpoint-catalog](endpoint-catalog.md).

## Prinsip

- Otorisasi ditegakkan di API pada setiap endpoint terproteksi (lihat [authorization-rbac](../06-security/authorization-rbac.md)).
- Format sukses dan error konsisten (lihat [api-conventions](api-conventions.md) dan [error-format](error-format.md)).
- Tidak ada webhook pada scaffold (lihat [webhook-policy](webhook-policy.md)).
- Versi API berada di path; perubahan yang memutus kompatibilitas memerlukan `/api/v2` (PROPOSED).

## Envelope respons

```text
{ "data": ..., "meta": { "dataLabel": "SIMULATED_DATA", "page", "pageSize", "total", "totalPages" } }
```

Bentuk di atas adalah ringkasan struktur, bukan JSON literal. Field paginasi hanya bermakna pada endpoint daftar.

## Open Questions

- **OPEN QUESTION** OQ-07 Hosting dan URL dasar API di luar pengembangan lokal.
- **OPEN QUESTION** OQ-10 Indikator dashboard yang dibutuhkan; menentukan isi `/dashboard/summary`.

## Related Documents

- [api-conventions](api-conventions.md)
- [error-format](error-format.md)
- [authentication-flow](authentication-flow.md)
- [endpoint-catalog](endpoint-catalog.md)
- [openapi-guidelines](openapi-guidelines.md)
- [component-architecture](../03-architecture/component-architecture.md)
