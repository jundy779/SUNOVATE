# Product Requirements Document (PRD) SUNOVATE

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-01

## Purpose

PRD ini merangkum masalah, tujuan, pengguna, scope, fitur per prioritas, non-goals, ukuran keberhasilan, dan ketergantungan SUNOVATE. Rincian kebutuhan ada di [functional-requirements.md](functional-requirements.md) dan [non-functional-requirements.md](non-functional-requirements.md).

## Pernyataan Masalah

**PROPOSED** Rumusan di bawah adalah rumusan pengembang yang selaras dengan arah Proposal v2.4, slide 3, dan tujuan pada brief sesi 2026-10-01. Rumusan ini perlu dicocokkan dengan kondisi nyata oleh mentor.

1. Pengetahuan tim kerja Dit. SUN tersebar di banyak dokumen, folder, dan pengalaman individu, sehingga sulit ditemukan kembali ketika dibutuhkan.
2. Pengetahuan tacit berisiko hilang ketika terjadi rotasi atau pergantian personel, sehingga institutional memory perlu dijaga secara sistematis.
3. Mencari regulasi, kajian, SOP, playbook, lesson learned, bahan rapat, dan arsip yang relevan membutuhkan waktu, terutama lintas tim.
4. Pemantauan pekerjaan, output, dan pending matters antartim belum memiliki tampilan bersama yang mengikuti hak akses.
5. Pemanfaatan AI untuk pencarian pengetahuan membutuhkan pengamanan agar tidak membocorkan dokumen dan tidak memberi jawaban tanpa dasar.

## Tujuan Produk

**CONFIRMED** Delapan tujuan dari brief sesi 2026-10-01; pemetaan ke sasaran terukur ada di [vision-and-objectives.md](../00-project/vision-and-objectives.md).

1. Knowledge Repository web.
2. AI Knowledge Assistant Hermes.
3. Menjaga institutional memory Dit. SUN.
4. Pencarian dokumen, regulasi, kajian, SOP, playbook, lesson learned, bahan rapat, arsip.
5. Monitoring pekerjaan dan output tim kerja.
6. Dashboard sesuai hak akses.
7. Document automation berbasis template yang disetujui.
8. Fondasi integrasi Telegram dan WhatsApp pada fase lanjutan.

## Pengguna

**PROPOSED** Kelompok pengguna dari Proposal v2.4, slide 9. Persona ada di [user-personas.md](user-personas.md).

| Kelompok | Kebutuhan utama |
|---|---|
| Pimpinan | Ringkasan kinerja dan pending matters sesuai hak akses. |
| Enam tim kerja dan SME | Menyimpan, menemukan, meninjau knowledge; memantau pekerjaan tim. |
| Pengelola Knowledge | Kurasi, review, publikasi, kualitas metadata. |
| Auditor / Admin | Jejak audit, pengelolaan pengguna dan konfigurasi. |

## Scope

Ringkasan scope dan batasan ada di [scope-and-boundaries.md](../00-project/scope-and-boundaries.md). Enam tim kerja awal: PPSUN, AKPSUN, PSUN, PPPSUN, DHTV, SUN Tematik (sumber: brief sesi 2026-10-01; fungsi SUN Tematik OQ-01).

## Fitur per Prioritas

**PROPOSED** Prioritas dari Proposal v2.4, slide 11.

### P0 (MVP)

| Fitur | Keterangan |
|---|---|
| Repository dokumen dan metadata | Knowledge entry, referensi dokumen, versi, checksum SHA-256, klasifikasi, tag. File tetap di document provider. |
| Pencarian teks dan semantik | Pencarian teks atas konten PUBLISHED terotorisasi; semantik setelah model embedding disetujui (OQ-11). |
| Hermes dengan sitasi | Jawaban hanya dari chunk terotorisasi, setiap jawaban bersitasi, penolakan di luar scope. |
| RBAC dan klasifikasi | Permission, team scope, dan klasifikasi data ditegakkan di API. |
| Audit log | Append-only untuk aksi penting. |
| Kinerja dan pending matters dasar | Work output, tugas, milestone, pending matter, follow-up dengan status tenggat. |

### P1

| Fitur | Keterangan |
|---|---|
| Relasi antarperaturan | AMENDS, REVOKES, IMPLEMENTS, REFERENCES, SUPERSEDES. |
| Knowledge capture SME | Penangkapan tacit knowledge dari SME. |
| Close Out Note dan playbook | Template dan alur untuk knowledge product. |
| Document automation | Berbasis template yang disetujui (OQ-16). |
| Reporting dan ekspor | Format menunggu OQ-10. |
| Notifikasi dalam aplikasi | Tanpa kanal eksternal. |

### P2 (setelah validasi, bukan janji)

SharePoint production sync, SSO organisasi, Power BI, Telegram dan WhatsApp, data pasar resmi, integrasi Kemenkeu Satu. Semua **OUT OF SCOPE** untuk MVP.

## Non-Goals

- **OUT OF SCOPE** Menggantikan sistem transaksi SUN resmi (sumber: brief sesi 2026-10-01).
- **OUT OF SCOPE** Mengambil atau merekomendasikan keputusan keuangan (sumber: brief sesi 2026-10-01).
- **OUT OF SCOPE** Menjadi sistem korespondensi resmi; Kemenkeu Satu tetap sistem resmi (sumber: `20_NEW_CHAT_MASTER_PROMPT.txt`).
- **OUT OF SCOPE** Fungsi SUN Job Monitor (sumber: `14_NEW_SESSION_HANDOFF_PROMPT.txt`).
- **OUT OF SCOPE** Menyimpan file sebagai BLOB atau menyimpan data instrumen, lelang, transaksi, yield, dan setelmen (ADR-003, ADR-013).
- **OUT OF SCOPE** Hermes menjalankan aksi tulis tanpa persetujuan manusia.

## Ukuran Keberhasilan

**PROPOSED** Retrieval, citation, access control, traceability, adoption, quality (sumber: Proposal v2.4, slide 23). Indikator rinci di [vision-and-objectives.md](../00-project/vision-and-objectives.md). Syarat rilis: nol bug P0 terbuka (sumber: Proposal v2.4, slide 20).

## Ketergantungan

| Ketergantungan | Dampak | Terkait |
|---|---|---|
| Validasi daftar tim dan pilot | Seed data, UAT | OQ-02, OQ-03 |
| Keputusan dokumen yang boleh masuk RAG | Ingestion dan Hermes | OQ-04 |
| Skema klasifikasi resmi | Kontrol akses | OQ-05 |
| Mekanisme login dan hosting | Pengganti dev auth, deployment | OQ-07 |
| Model AI dan embedding yang diizinkan | Pencarian semantik, Hermes generatif | OQ-11 |
| Repository SQLAlchemy | Persistence nyata menggantikan simulated store | ADR-007 |
| Lingkungan UAT | Bulan 6 | OQ-20 |

## Open Questions

OQ-01 sampai OQ-20 di [open-questions.md](../00-project/open-questions.md). Yang paling memengaruhi PRD: OQ-03, OQ-04, OQ-05, OQ-10, OQ-11, OQ-12.

## Risks

R-01, R-02, R-04, R-06, R-07, R-10 di [risk-register.md](../12-governance/risk-register.md).

## Related Documents

- [mvp-scope.md](mvp-scope.md)
- [user-stories.md](user-stories.md)
- [acceptance-criteria.md](acceptance-criteria.md)
- [product-roadmap.md](product-roadmap.md)

## Last Updated

2026-10-01
