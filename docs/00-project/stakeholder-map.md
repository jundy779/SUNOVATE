# Peta Pemangku Kepentingan

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-01

## Purpose

Dokumen ini memetakan pemangku kepentingan SUNOVATE berdasarkan peran, bukan nama orang. Tidak ada nama, jabatan, jumlah anggota tim, atau nomor surat tugas yang dicantumkan. Kewenangan nyata setiap peran harus ditetapkan oleh mentor atau pejabat yang berwenang.

## Instansi dan Konteks

**CONFIRMED** SUNOVATE dikembangkan untuk Direktorat Surat Utang Negara (Dit. SUN), DJPPR, Kementerian Keuangan RI, oleh peserta MagangHub (sumber: brief sesi 2026-10-01).

**CONFIRMED** Mentor memberi arahan proyek dan menjadi pihak yang memvalidasi asumsi, prioritas, dan jawaban atas pertanyaan terbuka (sumber: brief sesi 2026-10-01; Proposal v2.4, slide 24). Identitas mentor tidak dicatat di dokumentasi ini.

## Peran Tata Kelola

**PROPOSED** Peran berikut berasal dari Proposal v2.4, slide 18. Penunjukan orang untuk setiap peran adalah OPEN QUESTION.

| Peran | Tanggung jawab (usulan) | Label |
|---|---|---|
| Sponsor | Direktur SUN atau pejabat yang ditetapkan; memberi arah dan dukungan. | **PROPOSED** |
| Pengelola MP / Product Owner | Mengelola prioritas produk dan backlog. | **PROPOSED** |
| Knowledge Coordinator | Mengoordinasikan kurasi, review, dan publikasi knowledge lintas tim. | **PROPOSED** |
| SME / Knowledge Owner | Pemilik substansi knowledge di tim kerja. | **PROPOSED**; penunjukan per tim OQ-09 |
| Administrator sistem | Mengelola pengguna, peran, dan konfigurasi. | **PROPOSED** (peran pendukung) |
| Data steward | Menjaga kualitas metadata dan data. | **PROPOSED** (peran pendukung) |
| Security/compliance reviewer | Meninjau keamanan dan kepatuhan. | **PROPOSED** (peran pendukung) |
| Pengelola integrasi | Mengelola integrasi yang disetujui. | **PROPOSED** (peran pendukung) |
| Pengguna / pemberi feedback | Memakai sistem dan memberi masukan. | **PROPOSED** (peran pendukung) |

Siapa yang berwenang memutuskan publikasi knowledge adalah OQ-12.

## Tim Kerja dalam Scope Awal

**CONFIRMED** Enam tim kerja awal dan enam peran setiap tim dalam platform (sumber: brief sesi 2026-10-01). Deskripsi singkat berstatus NEEDS MENTOR VALIDATION (sumber: Proposal v2.4, slide 10).

| Kode | Nama | Deskripsi singkat (NEEDS MENTOR VALIDATION) |
|---|---|---|
| PPSUN | Pengelolaan Portofolio SUN | Portofolio, transaksi SUN, pelaporan, dokumen transaksi. |
| AKPSUN | Analisis Keuangan dan Pasar SUN | Analisis keuangan, fiskal, pasar SUN, pricing, dukungan analisis. |
| PSUN | Peraturan SUN | Kepatuhan, pemrosesan regulasi, kajian hukum, dukungan penyusunan peraturan. |
| PPPSUN | Pengembangan dan Pendalaman Pasar SUN | Kelembagaan pasar, basis investor, strategi pemasaran, layanan publik, edukasi. |
| DHTV | Dokumen Hukum Transaksi Valas | Dokumen hukum transaksi valas dan engagement letter. |
| SUN Tematik | SUN Tematik | **OPEN QUESTION** (OQ-01); knowledge product dan proses menunggu konfirmasi mentor. |

**OPEN QUESTION** Deck Pengayaan 6 Mei 2026 menampilkan lebih banyak tim kerja dan nama yang sedikit berbeda (OQ-02).

### Peran Setiap Tim dalam Platform

**CONFIRMED** (sumber: brief sesi 2026-10-01)

| Peran tim | Arti di SUNOVATE |
|---|---|
| Knowledge owner | Pemilik knowledge entry dan referensi dokumen tim (`owner_team_id`). |
| Process owner | Pemilik proses kerja yang dipantau di modul monitoring kerja. |
| Repository user | Pengguna yang membaca dan mencari konten sesuai hak akses. |
| Document reviewer | Peninjau konten sebelum publikasi. |
| Sumber data dashboard | Data work output, tugas, dan pending matter tim menjadi bahan dashboard. |
| Konteks otorisasi Hermes | Keanggotaan tim membatasi chunk yang boleh diambil Hermes. |

## Kelompok Pengguna

**PROPOSED** Kelompok pengguna dari Proposal v2.4, slide 9. Persona rinci ada di [user-personas.md](../01-product/user-personas.md).

| Kelompok | Kebutuhan utama (usulan) | Peran pengembangan terkait (PROPOSED) |
|---|---|---|
| Pimpinan | Ringkasan kinerja dan pending matters sesuai hak akses. | Belum dipetakan; OPEN QUESTION |
| Enam tim kerja dan SME | Menyimpan, mencari, dan meninjau knowledge; memantau pekerjaan. | team_lead, knowledge_owner, reviewer, staff, read_only |
| Pengelola Knowledge | Kurasi, review, dan publikasi lintas tim. | knowledge_coordinator |
| Auditor / Admin | Audit jejak aktivitas dan administrasi sistem. | auditor, system_admin |

Pemetaan kelompok Pimpinan ke peran sistem belum ditetapkan karena kewenangan dan kebutuhan datanya belum divalidasi.

## Diagram Hubungan

```mermaid
flowchart TB
    M["Mentor"] -->|"validasi"| PO["Product Owner (PROPOSED)"]
    SP["Sponsor (PROPOSED)"] --> PO
    PO --> KC["Knowledge Coordinator (PROPOSED)"]
    KC --> T["Enam tim kerja dan SME"]
    T --> SYS["SUNOVATE"]
    AU["Auditor / Admin"] --> SYS
    PI["Pimpinan"] --> SYS
```

## Open Questions

- OQ-01, OQ-02 Fungsi SUN Tematik dan daftar tim resmi.
- OQ-09 Knowledge owner dan reviewer di setiap tim.
- OQ-12 Alur dan kewenangan persetujuan publikasi.
- OQ-20 Pengguna uji UAT yang ditunjuk.

## Risks

- R-08 Ketergantungan pada satu pengembang.
- R-12 Perbedaan daftar tim kerja.

## Related Documents

- [team-work-scope.md](../02-business/team-work-scope.md)
- [knowledge-governance.md](../12-governance/knowledge-governance.md)
- [permission-matrix.md](../06-security/permission-matrix.md)

## Last Updated

2026-10-01
