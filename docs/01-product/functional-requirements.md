# Kebutuhan Fungsional

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Dokumen ini mendefinisikan kebutuhan fungsional SUNOVATE dengan ID `FR-xx`. Setiap kebutuhan memiliki prioritas (P0/P1/P2 menurut Proposal v2.4, slide 11), label bukti, dan user story terkait dari [user-stories.md](user-stories.md). Kolom "Scaffold" menyatakan apakah kebutuhan sudah memiliki implementasi awal per 2026-10-01 (Ya, Sebagian, Belum).

Kata "harus" berarti wajib untuk prioritas tersebut. Semua endpoint berprefiks `/api/v1`.

## 1. Autentikasi Pengembangan

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-01 | Sistem harus menerbitkan token pengembangan bertanda tangan HMAC melalui `POST /auth/dev/login` hanya untuk pengguna simulasi yang di-seed. | P0 | PROPOSED (ADR-005) | US-01 | Ya |
| FR-02 | Endpoint dev login harus mengembalikan 404 `DEV_AUTH_DISABLED` bila dev auth nonaktif, dan aplikasi harus menolak start bila `APP_ENV=production` dengan dev auth aktif. | P0 | PROPOSED (ADR-005) | US-01 | Ya |
| FR-03 | `GET /auth/me` harus mengembalikan principal: pengguna, tim, peran, izin, dan clearance. | P0 | PROPOSED | US-02 | Ya |
| FR-04 | Mekanisme login produksi menggantikan dev auth melalui `IdentityProvider`. | P2 | OPEN QUESTION (OQ-07) | US-01 | Belum |

## 2. Otorisasi (RBAC, Team Scope, Klasifikasi)

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-05 | Setiap endpoint terproteksi harus memeriksa permission, team scope, dan klasifikasi data; deny by default. | P0 | CONFIRMED prinsip (sumber: brief sesi 2026-10-01, ADR-006) | US-03 | Ya |
| FR-06 | Akses record mensyaratkan rank(clearance) >= rank(klasifikasi record). | P0 | PROPOSED | US-04 | Ya |
| FR-07 | Record yang tidak boleh dibaca harus menghasilkan 404, bukan 403. | P0 | PROPOSED | US-04 | Ya |
| FR-08 | Penolakan akses harus dicatat sebagai audit `ACCESS_DENIED`. | P0 | PROPOSED | US-26 | Ya |
| FR-09 | Matriks izin delapan peran pengembangan mengikuti [permission-matrix.md](../06-security/permission-matrix.md). | P0 | PROPOSED | US-27 | Ya |

## 3. Knowledge dan Lifecycle

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-10 | Pengguna dengan `knowledge:create` harus dapat membuat knowledge entry berstatus DRAFT dengan tipe dari daftar 14 tipe knowledge. | P0 | PROPOSED | US-05 | Ya |
| FR-11 | Pembaruan knowledge harus menyertakan `revision`; revision basi menghasilkan 409 `REVISION_CONFLICT`. | P0 | PROPOSED (ADR-011) | US-06 | Ya |
| FR-12 | Lifecycle: DRAFT ke IN_REVIEW ke PUBLISHED ke SUPERSEDED/ARCHIVED; IN_REVIEW kembali ke DRAFT bila perubahan diminta. | P0 | PROPOSED | US-07 | Sebagian |
| FR-13 | Publikasi hanya melalui approval request `KNOWLEDGE_PUBLICATION` yang disetujui; pengaju tidak boleh memutuskan permintaannya sendiri. | P0 | PROPOSED | US-08 | Ya |
| FR-14 | Hanya knowledge PUBLISHED yang masuk pencarian default dan retrieval Hermes. | P0 | PROPOSED | US-12, US-15 | Ya |
| FR-15 | `sharing_scope` TEAM membatasi ke tim pemilik; DIRECTORATE membuka ke semua tim hanya bila PUBLISHED. | P0 | PROPOSED; kebijakan OQ-14 | US-04 | Ya |
| FR-16 | Relasi antarperaturan AMENDS, REVOKES, IMPLEMENTS, REFERENCES, SUPERSEDES dapat dicatat dan ditampilkan. | P1 | PROPOSED | US-10 | Sebagian (tabel ada, endpoint belum) |
| FR-17 | Template knowledge capture SME, Close Out Note, dan playbook. | P1 | NEEDS MENTOR VALIDATION | US-11 | Belum |

## 4. Referensi Dokumen dan Versi

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-18 | Sistem harus menyimpan referensi dokumen beserta metadata, klasifikasi, lokasi provider, dan versi; file tidak disimpan sebagai BLOB. | P0 | CONFIRMED (sumber: brief sesi 2026-10-01, ADR-003) | US-09 | Ya |
| FR-19 | Registrasi versi harus menyimpan checksum SHA-256; pasangan (document_reference_id, checksum_sha256) ganda ditolak dengan 409 `DUPLICATE_CHECKSUM`. | P0 | PROPOSED | US-09 | Ya |
| FR-20 | Status ekstraksi: PENDING, EXTRACTED, FAILED, QUARANTINED, NOT_APPLICABLE. | P0 | PROPOSED | US-09 | Sebagian |
| FR-21 | Registrasi versi dicatat sebagai audit `VERSION_REGISTER`. | P0 | PROPOSED | US-26 | Ya |

## 5. Pencarian

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-22 | `GET /search?q=` harus mengembalikan hanya konten yang boleh dibaca pengguna, dengan filter otorisasi diterapkan sebelum penilaian relevansi. | P0 | PROPOSED | US-12 | Ya (simulated store) |
| FR-23 | Pencarian teks berbasis PostgreSQL FTS setelah repository SQLAlchemy tersedia. | P0 | PROPOSED (ADR-003, ADR-007) | US-12 | Belum |
| FR-24 | Pencarian semantik berbasis pgvector setelah model embedding disetujui. | P0 | OPEN QUESTION (OQ-11) | US-14 | Belum |

## 6. Hermes

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-25 | Hermes hanya diakses melalui HermesGateway; runtime Hermes tidak memiliki kredensial database. | P0 | CONFIRMED (sumber: brief sesi 2026-10-01, ADR-004) | US-15 | Ya |
| FR-26 | ScopeGuard harus mengklasifikasi pertanyaan: domain SUN, coding umum, jailbreak/policy override, dan niat tulis. | P0 | PROPOSED | US-17 | Ya |
| FR-27 | Query mensyaratkan `hermes:query` dan `search:query`. | P0 | PROPOSED | US-15 | Ya |
| FR-28 | Retrieval hanya chunk dari konten PUBLISHED yang boleh dibaca, tidak melebihi `HERMES_MAX_CLASSIFICATION`. | P0 | PROPOSED | US-15 | Ya |
| FR-29 | Chunk berisi teks menyerupai instruksi harus dikeluarkan oleh filter prompt injection. | P0 | PROPOSED | US-17 | Ya |
| FR-30 | CitationValidator: setiap penanda [n] harus menunjuk chunk terotorisasi yang diambil, minimal satu sitasi untuk `ANSWERED`. | P0 | PROPOSED | US-15 | Ya |
| FR-31 | OutputGuard harus memblokir pola rahasia/sensitif dan pelanggaran plafon klasifikasi (`BLOCKED_BY_OUTPUT_GUARD`). | P0 | PROPOSED | US-17 | Ya |
| FR-32 | Niat tulis menghasilkan `REQUIRES_HUMAN_APPROVAL` dan approval request `HERMES_WRITE_ACTION` berstatus PENDING, tanpa eksekusi. | P0 | PROPOSED | US-18 | Ya |
| FR-33 | Setiap query dan umpan balik dicatat sebagai audit `AI_QUERY` dan `AI_FEEDBACK`. | P0 | PROPOSED | US-19 | Ya |
| FR-34 | Provider AI generatif menggantikan `development_extractive` setelah model disetujui. | P1 | OPEN QUESTION (OQ-11) | US-15 | Belum |

## 7. Monitoring Kerja

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-35 | Daftar dan detail work output, tugas, milestone dibatasi team scope. | P0 | PROPOSED | US-20 | Ya |
| FR-36 | Pembaruan tugas memakai kontrol revision; status tugas: NOT_STARTED, IN_PROGRESS, WAITING_INTERNAL, WAITING_EXTERNAL, ON_HOLD, COMPLETED, CANCELLED. | P0 | PROPOSED | US-21 | Ya |
| FR-37 | Daftar pending matters dan follow-up. | P0 | PROPOSED | US-22 | Ya (baca) |
| FR-38 | Status tenggat SAFE, DUE_SOON, DUE_TODAY, OVERDUE, COMPLETED hanya dihitung backend dengan `DEADLINE_DUE_SOON_DAYS` (default 7). | P0 | PROPOSED; ambang OQ-15 | US-23 | Ya |
| FR-39 | Pembuatan work output dan tugas melalui UI dan API. | P0 | PROPOSED | US-20 | Belum |

## 8. Dashboard

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-40 | `GET /dashboard/summary` hanya mengagregasi record yang boleh dibaca. | P0 | PROPOSED | US-24 | Ya |
| FR-41 | Reporting dan ekspor. | P1 | OPEN QUESTION (OQ-10) | US-25 | Belum |

## 9. Audit dan Approval

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-42 | Audit log append-only; UPDATE dan DELETE ditolak trigger PostgreSQL. | P0 | PROPOSED (ADR-010) | US-26 | Ya (skema) |
| FR-43 | `GET /audit-logs` memerlukan `audit:read`. | P0 | PROPOSED | US-26 | Ya |
| FR-44 | Approval request bertipe KNOWLEDGE_PUBLICATION, HERMES_WRITE_ACTION, DOCUMENT_VERSION, ACCESS_EXCEPTION dengan status PENDING, APPROVED, REJECTED, CANCELLED, EXPIRED. | P0 | PROPOSED | US-08, US-18 | Ya |
| FR-45 | Keputusan approval mensyaratkan `approval:decide` dan dicatat sebagai APPROVE atau REJECT. | P0 | PROPOSED | US-08 | Ya |

## 10. Notifikasi, Document Automation, Integrasi

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-46 | Notifikasi dalam aplikasi untuk review dan tenggat; `NOTIFICATION_PROVIDER=disabled` untuk kanal eksternal. | P1 | PROPOSED | US-30 | Belum (tabel ada) |
| FR-47 | Document automation dari template yang disetujui; hasil berstatus draf dan masuk review. | P1 | PROPOSED; template OQ-16 | US-31, US-32 | Belum |
| FR-48 | Integrasi SharePoint, SSO, Power BI, Telegram, WhatsApp, data pasar resmi, Kemenkeu Satu hanya melalui provider dan setelah validasi. | P2 | OUT OF SCOPE MVP | US-33, US-34 | Belum (placeholder nonaktif) |
| FR-49 | `GET /providers` menampilkan status provider dan `GET /data-quality-issues` menampilkan isu kualitas data. | P0 | PROPOSED | US-28, US-29 | Ya |

## Open Questions

OQ-07, OQ-10, OQ-11, OQ-12, OQ-14, OQ-15, OQ-16 di [open-questions.md](../00-project/open-questions.md).

## Related Documents

- [endpoint-catalog.md](../07-api/endpoint-catalog.md)
- [acceptance-criteria.md](acceptance-criteria.md)
- [mvp-scope.md](mvp-scope.md)

## Last Updated

2026-10-01
