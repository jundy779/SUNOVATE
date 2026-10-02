# Scope MVP

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-02

## Purpose

Dokumen ini menetapkan apa yang termasuk dan tidak termasuk dalam MVP SUNOVATE, status implementasi scaffold saat ini secara jujur, dan definisi selesai MVP.

## Sumber

**PROPOSED** Daftar inklusi mengikuti prioritas P0 pada Proposal v2.4, slide 11, dan daftar MVP pada Proposal v2.4, slide 19. Keduanya berstatus usulan. Bila ada perbedaan rincian antara kedua slide, dokumen ini mengikuti daftar P0 dan perbedaannya dicatat sebagai pertanyaan untuk mentor.

## Termasuk MVP

| No | Kemampuan | Label |
|---|---|---|
| M-01 | Repository dokumen dan metadata (knowledge entry, referensi dokumen, versi, checksum, klasifikasi, tag) | PROPOSED |
| M-02 | Pencarian teks dan semantik atas konten terotorisasi | PROPOSED; semantik bergantung OQ-11 |
| M-03 | Hermes dengan sitasi, scope guard, dan persetujuan manusia untuk aksi tulis | PROPOSED |
| M-04 | RBAC dan klasifikasi data ditegakkan di API | CONFIRMED prinsip (sumber: brief sesi 2026-10-01); matriks PROPOSED |
| M-05 | Audit log append-only | PROPOSED |
| M-06 | Kinerja dan pending matters dasar (work output, tugas, milestone, pending matter, follow-up, status tenggat) | PROPOSED |
| M-07 | Dashboard ringkas sesuai hak akses | CONFIRMED sebagai tujuan (sumber: brief sesi 2026-10-01) |

## Tidak Termasuk MVP

| Kemampuan | Prioritas | Label |
|---|---|---|
| Relasi antarperaturan (antarmuka dan endpoint) | P1 | PROPOSED |
| Knowledge capture SME, Close Out Note, playbook | P1 | NEEDS MENTOR VALIDATION |
| Document automation | P1 | PROPOSED; OQ-16 |
| Reporting dan ekspor | P1 | PROPOSED; OQ-10 |
| Notifikasi dalam aplikasi | P1 | PROPOSED |
| SharePoint production sync, SSO organisasi, Power BI, Telegram, WhatsApp, data pasar resmi, integrasi Kemenkeu Satu | P2 | OUT OF SCOPE MVP |
| Data instrumen, lelang, transaksi, yield, setelmen | Tidak dijadwalkan | OUT OF SCOPE (ADR-013) |
| Perilaku khusus SUN Tematik | Tidak dijadwalkan | OPEN QUESTION (OQ-01) |

## Status Saat Ini di Scaffold (2026-10-01)

Kolom "Scaffold" berarti ada implementasi awal yang berjalan dengan `DATA_BACKEND=simulated` dan `SIMULATED_DATA`. Ini bukan kesiapan produksi.

| Kemampuan | Sudah ada di scaffold | Belum ada |
|---|---|---|
| M-01 Repository | Endpoint knowledge (daftar, detail, buat, ubah, ajukan) dan dokumen (daftar, detail, versi, registrasi versi); checksum ganda ditolak; revision conflict 409. Skema 30 tabel dan migrasi `0001_initial_schema` tervalidasi. | Repository SQLAlchemy (persistence nyata); unggah file ke document provider produksi; endpoint relasi antarperaturan. |
| M-02 Pencarian | `GET /search?q=` atas simulated store dengan filter otorisasi sebelum penilaian. | Pencarian FTS PostgreSQL di runtime; pencarian semantik (embedding provider nonaktif, tanpa indeks ANN). |
| M-03 Hermes | Pipeline lengkap: ScopeGuard, otorisasi, retrieval, rerank leksikal, filter injection, provider ekstraktif deterministik, CitationValidator, OutputGuard, audit; niat tulis menjadi approval PENDING; umpan balik. | Model generatif yang disetujui; evaluasi RAG dengan set uji tervalidasi; ingestion dokumen nyata. |
| M-04 RBAC dan klasifikasi | AuthorizationService dengan permission, team scope, clearance; 404 untuk record tak terbaca; delapan pengguna simulasi. | Identitas produksi (OQ-07); skema klasifikasi resmi (OQ-05). |
| M-05 Audit | Aksi LOGIN, CREATE, UPDATE, SUBMIT, APPROVE, REJECT, ACCESS_DENIED, AI_QUERY, AI_FEEDBACK, VERSION_REGISTER, SEARCH; trigger append-only di skema PostgreSQL. | Audit permanen pada default runtime (`DATA_BACKEND=simulated` masih in-memory; `DATA_BACKEND=postgres` menyimpan ke `audit_logs`, ADR-015, PROPOSED); kebijakan retensi (OQ-13). |
| M-06 Monitoring kerja | Daftar work output, tugas, milestone, pending matter, follow-up; pembaruan tugas; status tenggat dihitung backend. | Pembuatan work output dan tugas; pengelolaan pending matter dari UI. |
| M-07 Dashboard | `GET /dashboard/summary` dan halaman dashboard dengan grafik status. | Indikator tervalidasi (OQ-10). |
| Frontend | Rute `/login`, `/dashboard`, `/knowledge`, `/knowledge/[id]`, `/search`, `/work-monitoring`, `/hermes`, `/admin`, `/unauthorized`, serta state not-found, error, loading. | Formulir lengkap untuk membuat dan mengubah seluruh entitas; uji aksesibilitas manual. |

## Definition of Done MVP

**PROPOSED** MVP dinyatakan selesai bila seluruh syarat berikut terpenuhi:

1. Seluruh kemampuan M-01 sampai M-07 berjalan di atas PostgreSQL (repository SQLAlchemy), bukan simulated store.
2. Seluruh skenario di [acceptance-criteria.md](acceptance-criteria.md) lulus pada uji otomatis backend dan, untuk alur utama, pada uji end-to-end.
3. Skenario keamanan wajib lulus: akses tanpa izin, jailbreak, prompt injection, sitasi keliru, duplikasi ingestion, konflik pembaruan (sumber: Proposal v2.4, slide 20).
4. Nol bug P0 terbuka; bug P1 memiliki rencana perbaikan (lihat [bug-severity.md](../10-testing/bug-severity.md)).
5. `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, `pnpm api:lint`, `pnpm api:typecheck`, dan `pnpm api:test` lulus.
6. Seluruh data masih `SIMULATED_DATA`, kecuali mentor menyetujui penggunaan data lain secara tertulis dan kontrolnya sudah tersedia.
7. Provider produksi tetap nonaktif kecuali yang sudah divalidasi.
8. Dokumentasi terkait diperbarui, termasuk [known-limitations.md](../13-handover/known-limitations.md).
9. Pertanyaan prioritas Tinggi di [open-questions.md](../00-project/open-questions.md) sudah dijawab atau memiliki asumsi yang disetujui mentor.

## Open Questions

- OQ-03 Pilot pertama menentukan skenario MVP yang diprioritaskan.
- OQ-04, OQ-05 Dokumen dan klasifikasi yang boleh masuk.
- OQ-11 Model embedding untuk pencarian semantik.

## Risks

- R-06 Scope melebihi periode enam bulan.
- R-10 Simulated store disangka persistence produksi.

## Related Documents

- [prd.md](prd.md)
- [functional-requirements.md](functional-requirements.md)
- [product-roadmap.md](product-roadmap.md)
- [known-limitations.md](../13-handover/known-limitations.md)

## Last Updated

2026-10-02
