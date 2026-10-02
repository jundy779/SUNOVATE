# API Conventions

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Menetapkan konvensi penamaan, paginasi, filter, konkurensi, penghapusan, dan format waktu untuk seluruh endpoint SUNOVATE agar kontrak API konsisten antara `apps/api`, `apps/web`, dan `packages/contracts`.

## Confirmed Information

- **CONFIRMED** Prefix `/api/v1` (sumber: fact sheet bagian 9).
- **CONFIRMED** Paginasi memakai `page` (>= 1) dan `pageSize` (1–100, default 20) (sumber: fact sheet bagian 9).
- **CONFIRMED** Optimistic concurrency dengan integer `revision`; pembaruan basi menghasilkan 409 `REVISION_CONFLICT` (sumber: ADR-011).
- **CONFIRMED** Soft delete melalui `deleted_at` untuk rekaman bisnis (sumber: ADR-010).
- **CONFIRMED** Envelope respons `{ "data": ..., "meta": { "dataLabel": "SIMULATED_DATA", "page", "pageSize", "total", "totalPages" } }` (sumber: fact sheet bagian 9).

Butir pada bagian berikut yang tidak diberi label adalah konvensi **PROPOSED** yang mengikat untuk endpoint baru; kesesuaian scaffold terhadap setiap rincian perlu diverifikasi melalui uji.

## Penamaan

| Aspek | Konvensi | Contoh |
|---|---|---|
| Resource | Kata benda jamak | `/documents`, `/tasks`, `/approvals` |
| Path multi-kata | kebab-case | `/work-outputs`, `/pending-matters`, `/audit-logs`, `/data-quality-issues` |
| Sub-resource | Di bawah resource induk | `/documents/{id}/versions` |
| Aksi non-CRUD | Sub-path kata kerja/kata benda pada rekaman, dengan POST | `/knowledge/{id}/submit`, `/approvals/{id}/decision` |
| Field JSON | camelCase | `pageSize`, `dataLabel`, `requestId` |
| Kolom database | snake_case; dipetakan ke camelCase di skema Pydantic | `owner_team_id` menjadi `ownerTeamId` |
| Nilai enum | UPPER_SNAKE_CASE | `IN_REVIEW`, `DUE_SOON`, `KNOWLEDGE_PUBLICATION` |
| Kode permission | `resource:action` | `knowledge:read` |

Pengecualian yang sudah ada: `/knowledge` memakai bentuk tak jamak karena "knowledge" adalah kata benda tak terhitung; `/dashboard/summary` adalah resource baca-saja. Nama resource tunggal seperti `/health` bukan koleksi.

## Method

| Method | Pemakaian |
|---|---|
| GET | Membaca daftar atau rekaman; tanpa efek samping selain audit bila diperlukan |
| POST | Membuat rekaman atau menjalankan aksi |
| PATCH | Perubahan sebagian dengan `revision` |
| PUT, DELETE | Belum dipakai pada scaffold (PROPOSED: DELETE melakukan soft delete) |

## Paginasi

- Parameter query: `page` (>= 1) dan `pageSize` (1–100, default 20). Nilai di luar rentang menghasilkan 422 `VALIDATION_ERROR`.
- `meta` memuat `page`, `pageSize`, `total`, `totalPages`.
- Rekaman yang tidak boleh dibaca pengguna tidak ditampilkan (lihat [authorization-rbac](../06-security/authorization-rbac.md)).

## Filter dan sorting

- **PROPOSED** Filter sebagai parameter query camelCase yang eksplisit per endpoint, mis. `status`, `teamId`, `knowledgeType`, `classificationCode`.
- **PROPOSED** Sorting dengan `sort=<field>` dan prefix `-` untuk menurun, mis. `sort=-updatedAt`; hanya field yang didaftarkan per endpoint yang diterima.
- **CONFIRMED** Pencarian memakai `GET /search?q=` (sumber: fact sheet bagian 9).
- **PROPOSED** Filter tidak pernah memperluas akses; filter diterapkan setelah otorisasi.

## Konkurensi dan PATCH

- Setiap rekaman bisnis yang dapat diubah membawa `revision`.
- Body PATCH wajib menyertakan `revision` yang terakhir dibaca klien.
- Jika `revision` tidak sama dengan nilai tersimpan, API mengembalikan 409 `REVISION_CONFLICT` dan tidak mengubah apa pun.
- Pembaruan yang berhasil menaikkan `revision` satu angka dan dicatat sebagai `UPDATE` di audit log.

## Soft delete

- Rekaman bisnis tidak dihapus fisik; `deleted_at` diisi.
- Rekaman dengan `deleted_at` tidak tampil pada daftar dan menghasilkan 404 pada detail.
- `audit_logs` tidak pernah dihapus (append-only).

## Idempotency (PROPOSED)

- POST yang membuat rekaman atau memicu efek di luar sistem pada fase lanjutan menerima header `Idempotency-Key`.
- Kunci yang sama dengan body yang sama mengembalikan respons pertama; kunci sama dengan body berbeda menghasilkan 409.
- Belum diimplementasikan pada scaffold. Pendaftaran versi dokumen sudah terlindung dari duplikasi melalui checksum (`DUPLICATE_CHECKSUM`).

## Waktu dan identitas

- Timestamp dalam ISO-8601 UTC dengan akhiran `Z`, mis. `2026-10-01T03:00:00Z`.
- Id rekaman berupa UUID.
- Setiap respons membawa header `X-Request-ID`; nilai yang sama muncul sebagai `requestId` pada error.

## Label data

- Selama data simulasi, `meta.dataLabel` selalu `SIMULATED_DATA`.
- Rekaman membawa `data_origin` (`SIMULATED_DATA`, `USER_ENTERED`, `INTEGRATION`) pada skema data.

## Related Documents

- [api-overview](api-overview.md)
- [error-format](error-format.md)
- [openapi-guidelines](openapi-guidelines.md)
- [logical-data-model](../04-data/logical-data-model.md)
