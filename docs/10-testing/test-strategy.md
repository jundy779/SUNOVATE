# Strategi Pengujian SUNOVATE

**Status:** PROPOSED

**Last Updated:** 2026-10-06

## Purpose

Dokumen ini menetapkan tujuan, lapisan, skenario wajib, kriteria masuk dan keluar, serta aturan data uji untuk SUNOVATE. Detail per lapisan ada pada dokumen turunan di folder ini.

## Status

- **PROPOSED**: Strategi ini adalah usulan pengembang dan belum divalidasi mentor.
- **CONFIRMED**: Hasil eksekusi pengujian tidak dicatat di dokumen ini; lihat laporan validasi terbaru di CHANGELOG.md.

## Tujuan Pengujian

1. **PROPOSED**: Membuktikan otorisasi ditegakkan di API (permission, team scope, klasifikasi data) dan tidak hanya di antarmuka (sumber: brief sesi 2026-10-01, ADR-006).
2. **PROPOSED**: Membuktikan Hermes hanya menjawab dari konteks yang sudah diotorisasi, selalu bersitasi, dan menolak permintaan di luar cakupan (sumber: brief sesi 2026-10-01, ADR-004).
3. **PROPOSED**: Membuktikan integritas data: audit log append-only, optimistic concurrency (`REVISION_CONFLICT`), dan pencegahan duplikasi ingestion (`DUPLICATE_CHECKSUM`) (sumber: ADR-010, ADR-011).
4. **PROPOSED**: Mengukur kualitas retrieval dan sitasi sesuai ukuran keberhasilan retrieval, citation, access control, traceability, adoption, dan quality (sumber: Proposal v2.4, slide 23).
5. **PROPOSED**: Memastikan tidak ada data asli atau data keuangan yang masuk ke repository, fixture, atau log.

## Lapisan Pengujian

| Lapisan | Fokus | Lokasi | Alat |
|---|---|---|---|
| Unit frontend | Komponen, validasi form, utilitas | `apps/web/src/**/*.test.tsx` | Vitest, Testing Library |
| Unit dan API backend | Service, otorisasi, endpoint, Hermes pipeline | `apps/api/tests/` | pytest, FastAPI TestClient |
| Integration | Migration, seed, full-text search pada PostgreSQL | `tests/integration/` | pytest, PostgreSQL |
| End-to-end | Alur pengguna lintas web dan API | `apps/web/e2e/` | Playwright |
| Security | Skenario akses tanpa izin, jailbreak, prompt injection | `tests/security/` | pytest |
| RAG evaluation | Golden set retrieval, sitasi, kebocoran | `tests/rag-evaluation/`, `tests/fixtures/rag_golden_set.json` | pytest |
| UAT | Penerimaan oleh pengguna per persona | Lingkungan UAT (OPEN QUESTION, OQ-20) | Formulir UAT |

- **PROPOSED**: Pembagian lapisan di atas adalah usulan pengembang. Lihat [test-pyramid.md](test-pyramid.md) untuk proporsi.
- **CONFIRMED**: Lokasi folder pengujian di atas adalah struktur scaffold yang dibuat pada sesi ini (sumber: implementasi scaffold sesi 2026-10-01).

## Skenario Wajib

Skenario berikut wajib memiliki pengujian otomatis atau skenario UAT sebelum rilis (sumber: Proposal v2.4, slide 20; status PROPOSED):

| Skenario | Perilaku yang diharapkan | Lapisan utama |
|---|---|---|
| Akses tanpa izin | 401 `UNAUTHENTICATED`, 403 `PERMISSION_DENIED`, atau 404 untuk record yang tidak boleh dibaca | Backend, security |
| Jailbreak | Keputusan Hermes `REFUSED_POLICY` | Security, RAG |
| Prompt injection | Chunk berisi instruksi dikeluarkan dari konteks; output tidak mengikuti instruksi dokumen | Security, RAG |
| Sitasi keliru | Setiap `[n]` harus memetakan ke chunk yang diotorisasi; jika tidak, jawaban diblok | Backend, RAG |
| Duplikasi ingestion | 409 `DUPLICATE_CHECKSUM` untuk checksum SHA-256 yang sama pada dokumen yang sama | Backend, integration |
| Konflik pembaruan | 409 `REVISION_CONFLICT` untuk `revision` yang usang | Backend |

## Tambahan dari Jawaban Knowledge Owner (PLANNED)

- **CONFIRMED**: Slide 20 (P0 sampai P3, lapisan uji, dan enam skenario wajib) tidak berubah pada deck `v1_`; strategi di atas tidak digeser. Dampak jawaban knowledge owner pada slide 24 (pilot "6 tim", "semua dokumen", hak ubah/unggah, hosting server khusus, "bisa" untuk Telegram/WhatsApp, siapa knowledge owner, indikator "yield" dan "kepemilikan SBN") hanya menambah skenario turunan. Pengakuan mentor tertunda (OQ-24).
- **PLANNED**: Skenario turunan dan statusnya ada di [security-testing.md](security-testing.md) (SEC-40 sampai SEC-91), [rag-testing.md](rag-testing.md) (rencana golden set per tim dan prosedur dokumen asli), [backend-testing.md](backend-testing.md), [frontend-testing.md](frontend-testing.md), dan [uat-plan.md](uat-plan.md) (UAT-12 sampai UAT-16). Tidak satu pun yang berstatus PLANNED boleh dilaporkan sebagai ada atau lulus.
- **PROPOSED**: Hasil uji pada `DATA_BACKEND=simulated` tidak membuktikan perilaku server pilot. Pilot pada komputer server khusus memakai `DATA_BACKEND=postgres`, sehingga suite yang relevan dijalankan juga lewat `pnpm db:test` (ADR-015) dan latihan backup-restore dicatat (AC-24).
- **PROPOSED**: Bug yang bersumber dari jawaban ini (mis. `staff` masih dapat mengunggah setelah PD-1 disetujui) diklasifikasikan menurut [bug-severity.md](bug-severity.md) dan dicatat di [bug-register.md](bug-register.md).

## Kriteria Masuk

- **PROPOSED**: Perubahan sudah lolos `pnpm lint`, `pnpm typecheck`, `pnpm api:lint`, dan `pnpm api:typecheck` secara lokal.
- **PROPOSED**: Data uji yang dipakai hanya berlabel `SIMULATED_DATA`.
- **PROPOSED**: Untuk e2e, web (`pnpm dev`) dan API (`pnpm api:dev`) berjalan.
- **PROPOSED**: Untuk integration, tersedia PostgreSQL dengan ekstensi pgvector (lihat [integration-testing.md](integration-testing.md)).

## Kriteria Keluar

- **PROPOSED**: `pnpm validate` dan `pnpm api:test` selesai tanpa kegagalan.
- **PROPOSED**: Tidak ada bug P0 terbuka; bug P1 terbuka hanya dengan keputusan tertulis mentor (lihat [bug-severity.md](bug-severity.md)).
- **PROPOSED**: Gate kebocoran RAG bernilai nol (lihat [rag-testing.md](rag-testing.md)).
- **PROPOSED**: Seluruh skenario wajib memiliki bukti uji.
- **OPEN QUESTION**: Kriteria penerimaan UAT dan pihak yang menandatangani (OQ-20; lihat [uat-plan.md](uat-plan.md)).

## Data Uji

- **CONFIRMED**: Semua record demonstrasi dan fixture menggunakan `SIMULATED_DATA`; data internal atau data keuangan asli tidak boleh ditambahkan (sumber: brief sesi 2026-10-01, AGENTS.md).
- **PROPOSED**: Fixture tidak boleh memuat angka SUN asli (APBN, pembiayaan, yield, hasil lelang), nama pegawai asli, atau nomor surat tugas.
- **PROPOSED**: Pengguna uji adalah pengguna simulasi `@sunovate.local` yang di-seed (lihat [local-development.md](../11-operations/local-development.md)).
- Lihat [simulated-data-policy.md](../04-data/simulated-data-policy.md).

## Open Questions

- OQ-20 Lingkungan UAT dan pengguna uji yang ditunjuk.
- OQ-11 Model AI dan embedding yang diizinkan; menentukan kapan evaluasi semantik dapat dijalankan.

## Risks

- R-02 Kebocoran data melalui pencarian/Hermes; dimitigasi dengan pengujian negatif otorisasi dan gate kebocoran.
- R-07 Prompt injection dari dokumen; dimitigasi dengan skenario wajib di `tests/security/`.
- R-10 Simulated store disangka persistence produksi; hasil uji pada `DATA_BACKEND=simulated` tidak membuktikan perilaku repository SQLAlchemy.

## Related Documents

- [test-pyramid.md](test-pyramid.md)
- [security-testing.md](security-testing.md)
- [rag-testing.md](rag-testing.md)
- [uat-plan.md](uat-plan.md)
- [bug-severity.md](bug-severity.md)
- [security-checklist.md](../06-security/security-checklist.md)
