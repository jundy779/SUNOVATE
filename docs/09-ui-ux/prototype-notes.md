# Prototype Notes

**Status:** DRAFT | NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-01

## Purpose

Mencatat posisi prototype SUNOVATE: konsep pada proposal, layar yang ada di scaffold, bagian yang masih placeholder, dan umpan balik yang perlu dikumpulkan dari mentor.

## Status

- **CONFIRMED:** Proposal v2.4 slide 17 memuat konsep dashboard dengan data simulasi (sumber: arahan pengguna sesi 2026-10-01; `SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx`). Konsep tersebut berstatus usulan, bukan desain yang disetujui.
- **CONFIRMED:** Scaffold `apps/web` adalah prototype pengembangan dengan data SIMULATED_DATA; tidak ada koneksi produksi (sumber: fact sheet bagian 9).

## Layar pada scaffold

| Layar | Route | Catatan |
|---|---|---|
| Login pengembangan | `/login` | Login untuk pengguna SIMULATED hasil seed; bukan mekanisme login produksi (OQ-07) |
| Dashboard | `/dashboard` | Metrik ringkas dan tabel "Perlu perhatian" |
| Knowledge Hub | `/knowledge`, `/knowledge/[id]` | Daftar dan detail knowledge |
| Pencarian | `/search` | Pencarian teks |
| Monitoring Kerja | `/work-monitoring` | Output, tugas, milestone, pending matters |
| Hermes | `/hermes` | Pertanyaan dengan sitasi dari provider pengembangan |
| Administrasi | `/admin` | Informasi pengguna, role, provider, audit |
| Akses ditolak, not found, error, loading | `/unauthorized` dan halaman sistem | Keadaan sistem |

Daftar ini mengikuti fact sheet sesi; verifikasi terhadap kode terbaru sebelum demo kepada mentor.

## Bagian yang masih placeholder

- **CONFIRMED:** Seluruh data berasal dari dataset SIMULATED_DATA dengan `DATA_BACKEND=simulated` (in-memory); repository berbasis SQLAlchemy belum diimplementasikan (sumber: ADR-007).
- **CONFIRMED:** Jawaban Hermes disusun secara ekstraktif dan deterministik dari chunk yang diizinkan; tidak ada model AI eksternal (sumber: ADR-008).
- **CONFIRMED:** Pencarian semantik belum aktif karena provider embedding dinonaktifkan (sumber: ADR-008).
- **CONFIRMED:** Login memakai token pengembangan; SSO organisasi belum tersedia (sumber: ADR-005; [Identity Provider Proposal](../08-integrations/identity-provider-proposal.md)).
- **CONFIRMED:** Integrasi SharePoint, Power BI, Telegram, WhatsApp, market data, dan Kemenkeu Satu tidak tersedia (lihat [Integration Overview](../08-integrations/integration-overview.md)).
- **PROPOSED:** Indikator dashboard adalah kandidat dan belum tervalidasi (OQ-10).
- **PROPOSED:** Nama tim dan isi knowledge pada data demo bersifat fiktif dan tidak mewakili pekerjaan nyata tim.
- **OUT OF SCOPE:** Layar SUN Business (instrumen, lelang, transaksi, yield) tidak dibuat (sumber: ADR-013).

## Umpan balik yang perlu dikumpulkan dari mentor

| Topik | Pertanyaan | Terkait |
|---|---|---|
| Pilot | Tim dan proses mana yang dipakai untuk demo berikutnya | OQ-03 |
| Nama tim | Nama resmi tim yang ditampilkan di antarmuka | OQ-02 |
| Dashboard | Indikator mana yang berguna, mana yang perlu dihapus | OQ-10 |
| Status kerja | Apakah istilah status dan ambang jatuh tempo sesuai praktik tim | OQ-15 |
| Knowledge Hub | Metadata minimum yang wajib diisi | OQ-04, OQ-09 |
| Klasifikasi | Apakah label klasifikasi mudah dipahami dan sesuai skema resmi | OQ-05 |
| Hermes | Apakah format jawaban bersitasi dan pesan penolakan dapat diterima | OQ-11 |
| Bahasa | Istilah Indonesia atau Inggris untuk menu dan status | Glossary |
| Kepadatan | Apakah tampilan tabel cukup padat untuk kerja harian | Design System |

## Cara mencatat umpan balik

- **PROPOSED:** Umpan balik dicatat per sesi pada [Decision Log](../12-governance/decision-log.md) bila menghasilkan keputusan, atau pada [Open Questions](../00-project/open-questions.md) bila masih terbuka.
- **PROPOSED:** Umpan balik tidak memuat data pribadi atau data internal asli.

## Related Documents

- [Information Architecture](information-architecture.md)
- [Dashboard Requirements](dashboard-requirements.md)
- [Design System](design-system.md)
- [MVP Scope](../01-product/mvp-scope.md)
- [Known Limitations](../13-handover/known-limitations.md)
