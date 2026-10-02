# Architecture Decisions (ADR)

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose
Rincian konteks, keputusan, alternatif, dan konsekuensi. Ringkasan dan status ada di [decision-log.md](../12-governance/decision-log.md).

### ADR-001 Modular monolith
- Konteks: satu pengembang, enam bulan, kebutuhan belum stabil.
- Keputusan: satu API FastAPI dengan modul internal, satu web Next.js. **CONFIRMED** (brief).
- Alternatif ditolak: microservices (overhead operasional).
- Konsekuensi: batas modul dijaga di kode (`modules/`, `authz/`, `hermes/`).

### ADR-002 FastAPI/SQLAlchemy/Alembic menggantikan NestJS/Prisma
- Keputusan eksplisit brief. **CONFIRMED**. Blueprint v0.1 menjadi konteks historis.
- Konsekuensi: kontrak TypeScript dipelihara manual di `packages/contracts`.

### ADR-003 PostgreSQL tunggal, tanpa BLOB
- Relasional + FTS (`tsvector` GIN) + pgvector. File hanya referensi, metadata, checksum SHA-256, versi, klasifikasi, lokasi provider. **CONFIRMED**.

### ADR-004 Hermes di belakang HermesGateway
- `HermesClient` hanya menerima passage terotorisasi; tanpa kredensial DB. **CONFIRMED**.

### ADR-005 Token pengembangan HMAC
- `POST /api/v1/auth/dev/login` untuk pengguna SIMULATED; TTL default 480 menit; secret kosong menghasilkan secret acak per proses. Config menolak `APP_ENV=production` dengan dev auth aktif. **PROPOSED**.
- Alternatif ditolak: JWT library (dependency tambahan tanpa kebutuhan), login tanpa token (tidak menguji alur otorisasi).

### ADR-006 Otorisasi permission AND team scope AND klasifikasi
- Deny by default, di API. Record yang tidak boleh dibaca dikembalikan 404. **CONFIRMED** (prinsip), **PROPOSED** (matriks).

### ADR-007 Runtime `DATA_BACKEND=simulated`
- Store in-memory memuat dataset yang sama dengan seed DB. Skema dan seed PostgreSQL tervalidasi, repository SQLAlchemy belum. **PROPOSED**.
- Alasan: memvalidasi kontrak API dan otorisasi sebelum persistence; mesin pengembang tanpa Docker.
- Konsekuensi: data hilang saat restart (R-10). Config menolak mode ini di production.

### ADR-008 AI provider pengembangan ekstraktif
- Deterministik, tanpa jaringan; hanya menyalin kalimat dari passage. Embedding nonaktif. **PROPOSED**.

### ADR-009 Embedding tanpa dimensi tetap
- `embedding_references.embedding` bertipe `vector` tanpa dimensi; `model_name` dan `dimensions` disimpan; tanpa indeks ANN sampai model disetujui. **PROPOSED**.

### ADR-010 Soft delete dan audit append-only
- `deleted_at` di record bisnis; trigger `audit_logs_append_only` menolak UPDATE/DELETE. **PROPOSED**.

### ADR-011 Optimistic concurrency
- Kolom `revision`; PATCH wajib menyertakan `revision`; tidak cocok menghasilkan 409 `REVISION_CONFLICT`. **PROPOSED**.

### ADR-012 Arsip dokumentasi lama
- `docs/` sebelumnya dipindah ke `docs/_archive/legacy-docs-v0/`, tidak dihapus. **PROPOSED**.

### ADR-013 Tanpa tabel SUN Business
- Tabel instrumen, lelang, transaksi, yield, setelmen dari scaffold lama dihapus karena belum tervalidasi. **PROPOSED**.

### ADR-014 File sumber biner dikecualikan dari Git
- `/*.pdf`, `/*.pptx` di `.gitignore` sampai OQ-18 dijawab. **PROPOSED**.

## Related Documents
- [decision-log.md](../12-governance/decision-log.md)
- [change-management.md](../12-governance/change-management.md)
