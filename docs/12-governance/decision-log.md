# Decision Log

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Dokumen ini mencatat ringkasan keputusan proyek SUNOVATE beserta status dan dampaknya. Rincian konteks, alternatif, dan konsekuensi teknis ada di [architecture-decisions](../03-architecture/architecture-decisions.md). Jawaban mentor atas open question juga dicatat di sini agar dapat ditelusuri.

## Aturan Pencatatan

- ID tidak dipakai ulang. Keputusan yang diganti tetap tercatat dengan status "Digantikan oleh ...".
- CONFIRMED hanya bila didukung brief pengguna atau jawaban mentor bertanggal.
- Setiap keputusan baru diikuti pembaruan dokumen terkait dan, bila material, `CHANGELOG.md` (lihat [change-management](change-management.md)).

## Keputusan

| ID | Tanggal | Keputusan | Alasan | Status | Dampak | Referensi |
|---|---|---|---|---|---|---|
| ADR-001 | 2026-10-01 | Arsitektur modular monolith | Sesuai brief; satu pengembang, enam bulan, tanpa kebutuhan layanan terpisah | CONFIRMED (brief sesi 2026-10-01) | Satu backend API dan satu frontend; modul dipisah di dalam kode | [container-architecture](../03-architecture/container-architecture.md) |
| ADR-002 | 2026-10-01 | FastAPI, SQLAlchemy, Alembic menggantikan NestJS/Prisma pada blueprint lama | Keputusan eksplisit pada brief | CONFIRMED (brief sesi 2026-10-01) | Blueprint v0.1 hanya konteks historis | [technology-stack](../03-architecture/technology-stack.md) |
| ADR-003 | 2026-10-01 | PostgreSQL sebagai penyimpan tunggal (relasional, FTS, pgvector); file tidak disimpan sebagai BLOB | Kesederhanaan; file tetap di sumber resmi | CONFIRMED (brief sesi 2026-10-01) | Hanya referensi, metadata, checksum SHA-256, versi, klasifikasi, lokasi provider | [data-architecture](../04-data/data-architecture.md) |
| ADR-004 | 2026-10-01 | Hermes di belakang HermesGateway; runtime hanya menerima konteks teratorisasi; tanpa kredensial DB | Mencegah kebocoran dan akses langsung | CONFIRMED (brief sesi 2026-10-01) | Semua akses Hermes melalui application service | [hermes-overview](../05-ai-rag/hermes-overview.md) |
| ADR-005 | 2026-10-01 | Token pengembangan bertanda tangan HMAC via `POST /api/v1/auth/dev/login` untuk pengguna SIMULATED; nonaktif di luar development | Mekanisme login resmi belum disetujui (OQ-07) | PROPOSED | Aplikasi menolak start bila `APP_ENV=production` dan dev auth aktif | [authentication](../06-security/authentication.md) |
| ADR-006 | 2026-10-01 | Otorisasi = permission AND lingkup tim AND klasifikasi, deny by default, di API | Kontrol akses tidak boleh bergantung pada frontend | CONFIRMED (prinsip, brief); PROPOSED (matriks) | Penyembunyian menu hanya kosmetik | [authorization-rbac](../06-security/authorization-rbac.md) |
| ADR-007 | 2026-10-01 | `DATA_BACKEND=simulated` untuk runtime scaffold; skema, migrasi, dan seed PostgreSQL sudah divalidasi | Mempercepat pengembangan fitur sebelum repository SQLAlchemy selesai | PROPOSED | Data tidak persisten; repository SQLAlchemy adalah langkah berikut (R-10) | [data-architecture](../04-data/data-architecture.md) |
| ADR-008 | 2026-10-01 | AI provider pengembangan deterministik dan ekstraktif; embedding nonaktif | Model AI dan embedding belum disetujui (OQ-11) | PROPOSED | Tanpa jaringan dan model eksternal; retrieval semantik ditunda | [provider-abstraction](../03-architecture/provider-abstraction.md) |
| ADR-009 | 2026-10-01 | `embedding_references` menyimpan `model_name` dan `dimensions`; kolom vektor tanpa tipe tetap dan tanpa indeks ANN | Dimensi bergantung model yang belum disetujui | PROPOSED | Indeks ANN ditambahkan melalui migrasi setelah model disetujui | [rag-architecture](../05-ai-rag/rag-architecture.md) |
| ADR-010 | 2026-10-01 | Soft delete (`deleted_at`) untuk record bisnis; `audit_logs` append-only dengan trigger penolak UPDATE/DELETE | Jejak audit dan pemulihan | PROPOSED | Retensi tetap OQ-13 | [audit-logging](../06-security/audit-logging.md) |
| ADR-011 | 2026-10-01 | Optimistic concurrency dengan `revision`; pembaruan basi menghasilkan 409 `REVISION_CONFLICT` | Mencegah konflik pembaruan diam-diam | PROPOSED | Klien wajib mengirim revision | [api-conventions](../07-api/api-conventions.md) |
| ADR-012 | 2026-10-01 | `docs/` lama diarsipkan ke `docs/_archive/legacy-docs-v0/`, tidak dihapus | Menjaga jejak historis | PROPOSED | Dokumen baru menggantikan struktur lama | [README](../README.md) |
| ADR-013 | 2026-10-01 | Tabel SUN Business yang belum tervalidasi (instrumen, lelang, transaksi, yield, setelmen) dihapus dari skema | Menghindari model domain tanpa validasi dan data sensitif | PROPOSED | SUN Business tetap OPEN QUESTION untuk fase lanjut | [sun-domain-overview](../02-business/sun-domain-overview.md) |
| ADR-014 | 2026-10-01 | File sumber biner (PDF/PPTX) di root dikecualikan dari Git melalui `.gitignore` | Klasifikasi penyimpanan di repository belum dikonfirmasi (OQ-18) | PROPOSED | File sumber tetap lokal | [simulated-data-policy](../04-data/simulated-data-policy.md) |

## Jawaban Mentor atas Open Question

Belum ada jawaban mentor yang tercatat per 2026-10-01. Setiap jawaban dicatat dengan templat berikut, lalu OQ terkait di [open-questions](../00-project/open-questions.md) diperbarui statusnya.

```markdown
### DEC-YYYYMMDD-NN

- **Open question:** OQ-xx <ringkasan pertanyaan>
- **Tanggal jawaban:** YYYY-MM-DD
- **Sumber:** <rapat/catatan/arahan tertulis, tanpa data pribadi>
- **Jawaban:** <ringkasan jawaban mentor>
- **Keputusan:** <apa yang diputuskan untuk SUNOVATE>
- **Status:** CONFIRMED | NEEDS MENTOR VALIDATION (bila jawaban belum final)
- **Dampak:** <dokumen, skema, permission, atau kode yang berubah>
- **ADR/BR terkait:** <ADR-xxx, BR-xx, R-xx>
- **Tindak lanjut:** <tugas dan pemilik>
```

Ketentuan:

- Satu entri per open question; bila jawaban berubah, buat entri baru yang merujuk entri sebelumnya.
- Tidak mencatat nama pribadi, nomor surat tugas, atau data sensitif. Sebut peran secara umum (misalnya "mentor").
- Jawaban yang mengubah arsitektur juga dibuatkan ADR baru.

## Related Documents

- [architecture-decisions](../03-architecture/architecture-decisions.md)
- [change-management](change-management.md)
- [risk-register](risk-register.md)
- [open-questions](../00-project/open-questions.md)
