# Permission Matrix

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-01

## Purpose

Menetapkan daftar permission, pemberiannya ke role pengembangan, dan permission yang dibutuhkan setiap endpoint API. Seluruh isi matriks berstatus **PROPOSED** dan dipakai untuk scaffold dengan data `SIMULATED_DATA` (sumber: fact sheet bagian 5).

## Confirmed Information

- **CONFIRMED** Prinsip otorisasi permission AND team scope AND klasifikasi, deny by default (sumber: brief sesi 2026-10-01; ADR-006).
- **PROPOSED** Daftar role pengembangan: system_admin, knowledge_coordinator, team_lead, knowledge_owner, reviewer, staff, auditor, read_only (sumber: brief sesi 2026-10-01).
- **PROPOSED** Daftar permission dan matriks di bawah (sumber: fact sheet bagian 5).

## Daftar permission

| Permission | Deskripsi |
|---|---|
| `user:read` | Melihat daftar pengguna |
| `user:manage` | Mengelola pengguna |
| `team:read` | Melihat daftar tim |
| `team:manage` | Mengelola tim dan keanggotaan |
| `role:read` | Melihat role dan permission |
| `role:manage` | Mengelola role dan pemberian permission |
| `knowledge:read` | Membaca knowledge entry sesuai team scope dan klasifikasi |
| `knowledge:create` | Membuat knowledge entry berstatus DRAFT |
| `knowledge:update` | Mengubah knowledge entry |
| `knowledge:submit` | Mengajukan knowledge entry untuk review |
| `knowledge:review` | Mereview knowledge entry yang diajukan |
| `knowledge:publish` | Mempublikasikan knowledge melalui approval `KNOWLEDGE_PUBLICATION` |
| `knowledge:archive` | Mengarsipkan knowledge entry |
| `document:read` | Membaca document reference dan versinya |
| `document:create` | Mendaftarkan document reference baru |
| `document:update` | Mengubah metadata document reference |
| `document:version` | Mendaftarkan versi dokumen baru |
| `search:query` | Menjalankan pencarian |
| `work:read` | Melihat work output, tugas, milestone, dan ringkasan dashboard |
| `work:create` | Membuat work output atau tugas |
| `work:update` | Mengubah work output atau tugas |
| `pending:read` | Melihat pending matters dan follow-up |
| `pending:manage` | Mengelola pending matters dan follow-up |
| `audit:read` | Membaca audit log |
| `approval:request` | Membuat approval request dan melihat request miliknya |
| `approval:decide` | Memutuskan approval request milik orang lain |
| `hermes:query` | Mengajukan pertanyaan ke Hermes |
| `hermes:feedback` | Memberi feedback atas jawaban Hermes |
| `provider:read` | Melihat status provider |
| `data_quality:read` | Melihat data quality issue |
| `data_quality:manage` | Mengelola data quality issue |
| `scope:all_teams` | Mengakses rekaman semua tim (tetap tunduk pada klasifikasi) |

## Matriks role ke permission

Y = diberikan.

| Permission | system_admin | knowledge_coordinator | team_lead | knowledge_owner | reviewer | staff | auditor | read_only |
|---|---|---|---|---|---|---|---|---|
| user:read | Y | Y | Y |  |  |  | Y |  |
| user:manage | Y |  |  |  |  |  |  |  |
| team:read | Y | Y | Y | Y | Y | Y | Y | Y |
| team:manage | Y |  |  |  |  |  |  |  |
| role:read | Y |  |  |  |  |  | Y |  |
| role:manage | Y |  |  |  |  |  |  |  |
| knowledge:read | Y | Y | Y | Y | Y | Y | Y | Y |
| knowledge:create |  | Y | Y | Y |  | Y |  |  |
| knowledge:update |  | Y | Y | Y |  | Y |  |  |
| knowledge:submit |  | Y | Y | Y |  | Y |  |  |
| knowledge:review |  | Y | Y |  | Y |  |  |  |
| knowledge:publish |  | Y |  |  |  |  |  |  |
| knowledge:archive |  | Y |  |  |  |  |  |  |
| document:read | Y | Y | Y | Y | Y | Y | Y | Y |
| document:create |  | Y | Y | Y |  | Y |  |  |
| document:update |  | Y | Y | Y |  |  |  |  |
| document:version |  | Y | Y | Y |  |  |  |  |
| search:query | Y | Y | Y | Y | Y | Y | Y | Y |
| work:read | Y | Y | Y | Y | Y | Y | Y | Y |
| work:create |  |  | Y |  |  | Y |  |  |
| work:update |  |  | Y |  |  | Y |  |  |
| pending:read | Y | Y | Y | Y | Y | Y | Y | Y |
| pending:manage |  |  | Y |  |  |  |  |  |
| audit:read | Y |  |  |  |  |  | Y |  |
| approval:request |  | Y | Y | Y |  | Y |  |  |
| approval:decide |  | Y | Y |  | Y |  |  |  |
| hermes:query |  | Y | Y | Y | Y | Y |  | Y |
| hermes:feedback |  | Y | Y | Y | Y | Y |  | Y |
| provider:read | Y |  |  |  |  |  | Y |  |
| data_quality:read | Y | Y |  |  |  |  | Y |  |
| data_quality:manage |  | Y |  |  |  |  |  |  |
| scope:all_teams | Y | Y |  |  |  |  | Y |  |

Aturan pelengkap (PROPOSED):

- Approver tidak pernah memutuskan request miliknya sendiri (separation of duties).
- Publikasi knowledge hanya melalui `approval_requests` bertipe `KNOWLEDGE_PUBLICATION` yang disetujui.
- Permission tidak menggantikan pemeriksaan team scope dan klasifikasi (lihat [authorization-rbac](authorization-rbac.md)).

## Endpoint ke permission

Semua path relatif terhadap prefix `/api/v1`.

| Method | Path | Permission yang dibutuhkan |
|---|---|---|
| GET | `/health` | Publik |
| GET | `/health/database` | Publik |
| POST | `/auth/dev/login` | Publik (hanya saat dev auth aktif) |
| GET | `/auth/me` | Autentikasi saja |
| GET | `/users` | `user:read` |
| GET | `/teams` | `team:read` |
| GET | `/roles` | `role:read` |
| GET | `/permissions` | `role:read` |
| GET | `/classifications` | Autentikasi saja |
| GET | `/knowledge` | `knowledge:read` |
| GET | `/knowledge/{id}` | `knowledge:read` |
| POST | `/knowledge` | `knowledge:create` |
| PATCH | `/knowledge/{id}` | `knowledge:update` |
| POST | `/knowledge/{id}/submit` | `knowledge:submit` + `approval:request` |
| GET | `/documents` | `document:read` |
| GET | `/documents/{id}` | `document:read` |
| GET | `/documents/{id}/versions` | `document:read` |
| POST | `/documents/{id}/versions` | `document:version` |
| GET | `/search?q=` | `search:query` |
| GET | `/dashboard/summary` | `work:read` |
| GET | `/work-outputs` | `work:read` |
| GET | `/work-outputs/{id}` | `work:read` |
| GET | `/tasks` | `work:read` |
| PATCH | `/tasks/{id}` | `work:update` |
| GET | `/milestones` | `work:read` |
| GET | `/pending-matters` | `pending:read` |
| GET | `/follow-ups` | `pending:read` |
| GET | `/audit-logs` | `audit:read` |
| GET | `/approvals` | `approval:decide`, atau `approval:request` (hanya request milik sendiri) |
| POST | `/approvals/{id}/decision` | `approval:decide` (+ `knowledge:publish` untuk tipe `KNOWLEDGE_PUBLICATION`) |
| POST | `/hermes/query` | `hermes:query` + `search:query` |
| POST | `/hermes/messages/{id}/feedback` | `hermes:feedback` |
| GET | `/providers` | `provider:read` |
| GET | `/data-quality-issues` | `data_quality:read` |

Catatan:

- Endpoint yang membaca atau mengubah rekaman tunggal juga menerapkan team scope dan klasifikasi; rekaman yang tidak boleh dibaca menghasilkan 404.
- Konsekuensi matriks saat ini: keputusan approval `KNOWLEDGE_PUBLICATION` hanya dapat dilakukan knowledge_coordinator, karena hanya role ini yang memiliki `approval:decide` dan `knowledge:publish` sekaligus.
- Permission `user:manage`, `team:manage`, `role:manage`, `knowledge:review`, `knowledge:archive`, `document:create`, `document:update`, `work:create`, `pending:manage`, dan `data_quality:manage` sudah didefinisikan tetapi belum dipakai oleh endpoint scaffold.

## Open Questions

- **OPEN QUESTION** Apakah team_lead boleh mempublikasikan knowledge.
- **OPEN QUESTION** Apakah system_admin seharusnya dapat membaca konten knowledge dan dokumen.
- **OPEN QUESTION** OQ-09 Penetapan knowledge owner dan reviewer per tim.
- **OPEN QUESTION** OQ-12 Siapa berwenang memutuskan publikasi.

## Acceptance Criteria

- Setiap endpoint pada tabel di atas memiliki uji yang membuktikan 403 untuk role tanpa permission.
- Matriks di kode dan seed identik dengan tabel ini.

## Related Documents

- [authorization-rbac](authorization-rbac.md)
- [endpoint-catalog](../07-api/endpoint-catalog.md)
- [review-and-approval](../12-governance/review-and-approval.md)
