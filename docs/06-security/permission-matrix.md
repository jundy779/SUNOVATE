# Permission Matrix

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-28

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
| `secure_document:manage_team` | Menentukan pembaca dokumen RAHASIA milik tim sendiri (DEC-20261021-02) |
| `secure_document:manage_all` | Menentukan pembaca dokumen RAHASIA seluruh tim (DEC-20261021-02) |

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
| secure_document:manage_team |  |  | Y |  |  |  |  |  |
| secure_document:manage_all |  | Y |  |  |  |  |  |  |

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
| GET | `/knowledge/drafts/search` | `knowledge:read`, lalu `knowledge:review` atau role `knowledge_owner` (hanya draf miliknya) |
| POST | `/knowledge/chunk-preview`, `/knowledge/extract-preview` | `knowledge:review` |
| POST | `/knowledge/chunk-drafts` | `knowledge:review` + `knowledge:create` + `document:create` + `document:version` |
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
| POST | `/work-outputs` | `work:create` |
| PATCH, DELETE | `/work-outputs/{id}` | `work:update` |
| GET | `/tasks` | `work:read` |
| POST | `/tasks` | `work:create` |
| PATCH | `/tasks/{id}` | `work:update` |
| DELETE | `/tasks/{id}` | `work:update` |
| GET | `/milestones` | `work:read` |
| POST | `/milestones` | `work:create` |
| PATCH, DELETE | `/milestones/{id}` | `work:update` |
| GET | `/pending-matters` | `pending:read` |
| GET | `/follow-ups` | `pending:read` |
| POST | `/pending-matters`, `/follow-ups` | `pending:manage` |
| PATCH, DELETE | `/pending-matters/{id}`, `/follow-ups/{id}` | `pending:manage` |
| GET | `/audit-logs` | `audit:read` |
| GET | `/approvals` | `approval:decide`, atau `approval:request` (hanya request milik sendiri) |
| POST | `/approvals/{id}/decision` | `approval:decide` (+ `knowledge:publish` untuk tipe `KNOWLEDGE_PUBLICATION`) |
| POST | `/hermes/query` | `hermes:query` + `search:query` |
| POST | `/hermes/messages/{id}/feedback` | `hermes:feedback` |
| GET | `/hermes/sme-question-intake`, `/hermes/glossary-intake` | `knowledge:review` + `scope:all_teams` |
| GET | `/providers` | `provider:read` |
| GET | `/data-quality-issues` | `data_quality:read` |
| GET | `/exports/work?kind=` | `work:read` (+ `pending:read` untuk `pending` dan `followUps`) |
| GET | `/exports/attention` | `work:read` |
| GET | `/secure-documents`, `/secure-documents/{id}` | `document:read` + terdaftar sebagai pembaca + clearance cukup |
| POST | `/secure-documents/{id}/acknowledgements` | `document:read` + terdaftar sebagai pembaca |
| GET | `/secure-documents/{id}/pages/{page}` | `document:read` + terdaftar sebagai pembaca + persetujuan pernyataan masih berlaku |
| GET | `/secure-documents/manageable` | `document:read`; daftar hanya berisi dokumen yang dapat dikelola |
| GET, POST | `/secure-documents/{id}/readers` | `secure_document:manage_all`, atau `secure_document:manage_team` untuk dokumen tim sendiri |
| DELETE | `/secure-documents/{id}/readers/{email}` | `secure_document:manage_all`, atau `secure_document:manage_team` untuk dokumen tim sendiri |

Catatan:

- Endpoint yang membaca atau mengubah rekaman tunggal juga menerapkan team scope dan klasifikasi; rekaman yang tidak boleh dibaca menghasilkan 404.
- Konsekuensi matriks saat ini: keputusan approval `KNOWLEDGE_PUBLICATION` hanya dapat dilakukan knowledge_coordinator, karena hanya role ini yang memiliki `approval:decide` dan `knowledge:publish` sekaligus.
- Permission `user:manage`, `team:manage`, `role:manage`, `knowledge:review`, `knowledge:archive`, `document:create`, `document:update`, dan `data_quality:manage` sudah didefinisikan tetapi belum dipakai oleh endpoint scaffold. `work:create` dan `pending:manage` dipakai endpoint monitoring sejak 2026-10-10.

## Usulan Perubahan: Pembatasan Hak Ubah/Unggah (PROPOSED, belum diimplementasikan)

Status: **PROPOSED**. Bagian ini tidak mengubah katalog role, matriks di atas, kode, seed, atau uji. Semua tabel di atas tetap menggambarkan keadaan scaffold saat ini.

### Dasar

- **CONFIRMED (knowledge owner, deck v1_ slide 24)** Yang dapat mengubah data atau mengunggah adalah ketua tim, kasubdit PMP, Kasi MP, dan PIC yang ditunjuk (OQ-05, DEC-20261002-03). Pengakuan mentor masih tertunda (OQ-24).
- **CONFIRMED (fakta matriks saat ini)** Role `staff` memiliki `knowledge:create`, `knowledge:update`, `knowledge:submit`, dan `document:create` (lihat matriks di atas). Ini lebih luas daripada jawaban knowledge owner, yang tidak menyebut staf biasa.
- **OPEN QUESTION (OQ-25)** Jabatan "kasubdit PMP" dan "Kasi MP" belum dipetakan ke role sistem, kepanjangan "PMP" tidak dijelaskan di deck, dan belum diketahui apakah kedua jabatan itu bekerja lintas tim atau hanya pada tim tertentu. Tidak ada `scope:all_teams` yang diasumsikan untuk keduanya.

### Pemetaan yang diusulkan

| Disebut knowledge owner | Role sistem (PROPOSED) | Catatan |
|---|---|---|
| Ketua tim | `team_lead` | Sudah memiliki `knowledge:create/update/submit`, `document:create/update/version` |
| PIC yang ditunjuk | `knowledge_owner` | Sudah memiliki izin yang sama; penunjukan orang dicatat lewat `owner_user_id` |
| Kasubdit PMP, Kasi MP | `knowledge_coordinator` | Sudah memiliki izin yang sama dan `scope:all_teams`; padanan jabatan ke role perlu konfirmasi |

### Efek yang diusulkan pada role `staff`

| Permission | Matriks saat ini | Usulan |
|---|---|---|
| `knowledge:create` | Y | dicabut |
| `knowledge:update` | Y | dicabut |
| `knowledge:submit` | Y | dicabut |
| `document:create` | Y | dicabut |
| `knowledge:read`, `document:read`, `search:query`, `hermes:query`, `hermes:feedback`, `work:read`, `work:create`, `work:update`, `pending:read`, `team:read` | Y | tidak berubah |
| `approval:request` | Y | perlu diputuskan: dipakai `POST /knowledge/{id}/submit` bersama `knowledge:submit`; bila `knowledge:submit` dicabut, `approval:request` untuk `staff` menjadi tidak terpakai (OPEN QUESTION) |

Permission `document:update` dan `document:version` tidak dimiliki `staff` pada matriks saat ini sehingga tidak berubah. Role `reviewer`, `auditor`, `read_only`, dan `system_admin` tidak memiliki `knowledge:create/update/submit` maupun `document:create` dan juga tidak berubah.

### Konsekuensi bila diterapkan (PROPOSED)

- Endpoint `POST /knowledge`, `PATCH /knowledge/{id}`, dan `POST /knowledge/{id}/submit` memberi 403 untuk `staff`.
- Persona P-02 di [user-personas](../01-product/user-personas.md) hanya membaca, mencari, bertanya ke Hermes, dan memperbarui tugas.
- Pencarian `staff` di `apps/api/tests` menunjukkan uji saat ini memakai `sim.staff.pppsun` untuk membaca, mencari, Hermes, dan memperbarui tugas, bukan untuk membuat atau mengubah knowledge; uji 403 untuk `staff` akan perlu ditambahkan bila perubahan diterapkan.
- Pembatasan tetap berlaku bersama team scope dan klasifikasi (permission AND team scope AND klasifikasi).

### Syarat sebelum diterapkan

1. Mentor atau knowledge owner mengonfirmasi role yang tepat untuk ketiga sebutan di atas dan apakah staf boleh menyusun draf (OQ-25).
2. Mentor mengakui jawaban knowledge owner (OQ-24).
3. Perubahan matriks, seed, dan uji otorisasi dilakukan pada cabang kode terpisah; catatan ada di [future-development](../13-handover/future-development.md).

**Belum diimplementasikan.** Kode, seed, dan uji di repositori ini tidak berubah oleh pembaruan dokumentasi ini.

## Usulan Permission Draft Workspace (PROPOSED, belum diimplementasikan)

| Permission | Batas tindakan |
|---|---|
| `work_file:draft_create` | Membuat lampiran kerja berstatus DRAFT |
| `work_file:draft_update_own` | Mengubah atau mengganti DRAFT milik sendiri sesuai team scope |
| `work_file:draft_delete_own` | Melakukan soft delete DRAFT milik sendiri |
| `work_file:submit` | Membekukan DRAFT dan mengajukannya untuk review |
| `work_file:review` | Mengembalikan SUBMITTED untuk perbaikan atau merekomendasikan publikasi |
| `work_file:publish` | Menerbitkan dan mengunci versi setelah approval |
| `work_file:withdraw` | Menarik atau mengarsipkan versi tanpa menghapus rekaman |
| `access_grant:manage` | Memberi atau mencabut delegasi permission yang terbatas scope dan waktu |

`system_admin` tidak otomatis memperoleh hak mengubah isi file terbit. Jika delegasi per akun diperlukan, gunakan grant terpisah dengan `user_id`, permission, team scope, classification ceiling, `valid_from`, `valid_until`, `granted_by`, alasan, dan audit event. Pemetaan role dan pihak yang boleh memberi, menerbitkan, atau menarik izin menunggu OQ-35.
## Kesesuaian dengan kode

Daftar permission, matriks role, dan tabel endpoint di atas dijaga sama dengan `apps/api/sunovate_api/authz/catalog.py` dan route API oleh test `apps/api/tests/test_permission_matrix_doc.py`. Bila permission, pemberian role, atau endpoint berubah, dokumen ini wajib diperbarui dalam perubahan yang sama. Status matriks tetap NEEDS MENTOR VALIDATION (rencana induk Tahap 1 butir 2).

## Open Questions

- **OPEN QUESTION** Apakah team_lead boleh mempublikasikan knowledge.
- **OPEN QUESTION** Apakah system_admin seharusnya dapat membaca konten knowledge dan dokumen.
- **CONFIRMED (knowledge owner, deck v1_ slide 24)** OQ-09 Knowledge owner dan reviewer per tim adalah ketua tim dan PIC yang ditunjuk; penunjukan orang dan pemetaan ke role tetap OPEN QUESTION (OQ-25).
- **OPEN QUESTION** OQ-25 Pemetaan "ketua tim", "kasubdit PMP", "Kasi MP", dan "PIC" ke role sistem serta nasib hak `staff` (lihat usulan di atas).
- **OPEN QUESTION** OQ-12 Siapa berwenang memutuskan publikasi.
- **OPEN QUESTION** OQ-35 Siapa yang boleh mengelola delegasi permission file pekerjaan, menerbitkan versi, dan menarik rekaman yang sudah terbit.

## Acceptance Criteria

- Setiap endpoint pada tabel di atas memiliki uji yang membuktikan 403 untuk role tanpa permission.
- Matriks di kode dan seed identik dengan tabel ini.

## Related Documents

- [authorization-rbac](authorization-rbac.md)
- [endpoint-catalog](../07-api/endpoint-catalog.md)
- [review-and-approval](../12-governance/review-and-approval.md)
