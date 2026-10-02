# OpenAPI Guidelines

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose
Cara menjaga dokumentasi OpenAPI dan kontrak TypeScript tetap sesuai dengan kode.

## Kondisi saat ini
- **CONFIRMED (implementasi)** FastAPI menghasilkan skema di `/openapi.json` dan Swagger UI di `/docs` (API lokal `:8000`).
- Tag per modul: `system`, `auth (development stub)`, `users, teams, roles`, `knowledge entries`, `document metadata and versions`, `search`, `dashboard`, `work outputs, tasks, milestones`, `pending matters and follow-ups`, `audit logs`, `approvals`, `Hermes gateway`, `providers and data quality`.
- Model request Pydantic memakai alias camelCase dan `extra="forbid"`, sehingga field tidak dikenal ditolak 422.
- Respons saat ini bertipe `dict` envelope; skema respons per endpoint belum dideklarasikan.
- `packages/contracts` (TypeScript + Zod) dipelihara manual.

## Aturan
1. Setiap endpoint baru memiliki `tags` modul, `summary` singkat, dan model request bertipe.
2. Perubahan kontrak diperbarui bersamaan di backend, `packages/contracts`, [endpoint-catalog.md](endpoint-catalog.md), dan [permission-matrix.md](../06-security/permission-matrix.md).
3. Jangan memasukkan contoh data asli di skema; gunakan placeholder `SIMULATED_DATA`.
4. Endpoint produksi yang belum ada tidak boleh muncul di OpenAPI sebagai tersedia.

## Usulan berikut (PROPOSED)
- Tambahkan `response_model` Pydantic per endpoint dan deklarasi respons error (`responses={401:..., 403:...}`).
- Generate tipe TypeScript dari `/openapi.json` di CI dan bandingkan dengan `packages/contracts`, untuk mendeteksi drift.
- Gunakan `operationId` dengan pola `<modul>_<aksi>`.

## Related Documents
- [api-overview.md](api-overview.md)
- [api-conventions.md](api-conventions.md)
