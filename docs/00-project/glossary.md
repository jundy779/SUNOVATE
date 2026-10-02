# Glosarium

**Status:** DRAFT
**Last Updated:** 2026-10-01

## Purpose

Glosarium menyamakan istilah domain SUN, istilah knowledge management, dan istilah teknis yang dipakai di dokumentasi dan kode SUNOVATE. Definisi domain SUN bersifat ringkasan untuk keperluan pengembangan; rujukan hukum yang berlaku tetap peraturan aslinya.

Sumber singkatan:
- [Pengayaan] = `Pengayaan_Kelas_Magang_6_Mei_2026.pdf`, sesi berbagi Dit. SUN untuk peserta magang, 6 Mei 2026.
- [Kompilasi] = `Kompilasi_Peraturan_SUN_formal.pdf`, kompilasi peraturan publik dari Database Peraturan BPK dan JDIH Kemenkeu.
- [Proposal] = `SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx` (berstatus usulan).
- [Brief] = brief sesi 2026-10-01.

## Istilah Domain SUN

| Istilah | Definisi ringkas | Sumber |
|---|---|---|
| SUN (Surat Utang Negara) | Surat berharga berupa surat pengakuan utang dalam mata uang rupiah maupun valuta asing yang dijamin pembayaran bunga dan pokoknya oleh Negara Republik Indonesia sesuai masa berlakunya. | **CONFIRMED** (sumber: [Pengayaan], mengutip Pasal 1 UU 24/2002) |
| SPN (Surat Perbendaharaan Negara) | Jenis SUN berjangka pendek, dibedakan dari Obligasi Negara berdasarkan jangka waktu. Ketentuan rinci mengacu UU 24/2002. | **CONFIRMED** (sumber: [Pengayaan]) |
| Obligasi Negara | Jenis SUN berjangka waktu lebih panjang dari SPN. Ketentuan rinci mengacu UU 24/2002. | **CONFIRMED** (sumber: [Pengayaan]) |
| SBN (Surat Berharga Negara) | Istilah payung untuk surat berharga yang diterbitkan negara; dipakai antara lain pada PMK 165/2022 tentang Transaksi SBN di Pasar Sekunder. Cakupan persisnya mengacu regulasi terkait. | **CONFIRMED** sebagai istilah (sumber: [Kompilasi]) |
| SUN ritel | SUN yang ditawarkan kepada investor individu. | **CONFIRMED** (sumber: [Pengayaan]) |
| ORI | Obligasi Negara Ritel, salah satu jenis SUN ritel. | **CONFIRMED** (sumber: [Pengayaan]) |
| SBR | Savings Bond Ritel, salah satu jenis SUN ritel. | **CONFIRMED** (sumber: [Pengayaan]) |
| Dealer Utama | Pihak yang terlibat dalam penerbitan dan perdagangan SUN sesuai ketentuan. Hak dan kewajiban rinci mengacu regulasi. | **CONFIRMED** sebagai pihak (sumber: [Pengayaan]) |
| Bank Indonesia | Berperan sebagai agen penatausaha dan agen lelang SUN. | **CONFIRMED** (sumber: [Pengayaan]) |
| BEI | Bursa Efek Indonesia, salah satu pihak dalam ekosistem SUN. | **CONFIRMED** sebagai pihak (sumber: [Pengayaan]) |
| Mitra Distribusi | Pihak yang terlibat dalam distribusi SUN ritel. | **CONFIRMED** sebagai pihak (sumber: [Pengayaan]) |
| Lelang | Cara penerbitan SUN melalui lelang. | **CONFIRMED** (sumber: [Pengayaan]) |
| Private placement | Cara penerbitan SUN melalui penempatan langsung kepada pihak tertentu. | **CONFIRMED** (sumber: [Pengayaan]) |
| Bookbuilding | Cara penerbitan SUN melalui pengumpulan minat pemesanan. | **CONFIRMED** (sumber: [Pengayaan]) |
| Buyback (cash buyback) | Pembelian kembali SUN oleh pemerintah dengan pembayaran tunai; diatur antara lain PMK 114/2023 tentang Pembelian Kembali SUN di Pasar Sekunder. | **CONFIRMED** (sumber: [Pengayaan]; [Kompilasi]) |
| Debt switch | Transaksi penukaran SUN dengan SUN lain. | **CONFIRMED** sebagai jenis transaksi (sumber: [Pengayaan]) |
| Setelmen | Penyelesaian transaksi, yaitu penyerahan surat berharga dan pembayaran. Data setelmen tidak dimodelkan di SUNOVATE (ADR-013). | **PROPOSED** definisi kerja |

**OUT OF SCOPE** SUNOVATE tidak menyimpan data instrumen, lelang, transaksi, yield, atau setelmen (ADR-013).

## Istilah Knowledge Management

| Istilah | Definisi kerja | Sumber |
|---|---|---|
| Institutional memory | Pengetahuan kolektif institusi yang harus tetap tersedia walau terjadi pergantian personel. | **CONFIRMED** sebagai tujuan ([Brief]) |
| Tacit knowledge | Pengetahuan berbasis pengalaman yang belum terdokumentasi; tipe knowledge `TACIT_KNOWLEDGE`. | **NEEDS MENTOR VALIDATION** ([Proposal], slide 7) |
| Close Out Note | Catatan penutup pekerjaan yang merangkum hasil, keputusan, dan pelajaran; tipe `CLOSE_OUT_NOTE`. | **NEEDS MENTOR VALIDATION** ([Proposal], slide 7) |
| Playbook | Panduan langkah proses bisnis; tipe `PLAYBOOK`. | **NEEDS MENTOR VALIDATION** ([Proposal], slide 7) |
| SOP | Standard Operating Procedure; tipe `SOP`. | **CONFIRMED** sebagai jenis konten ([Brief]) |
| Lesson learned | Pelajaran dari pekerjaan sebelumnya; tipe `LESSON_LEARNED`. | **CONFIRMED** sebagai jenis konten ([Brief]) |
| Decision & Meeting Record | Catatan keputusan dan rapat; tipe `DECISION_RECORD` dan `MEETING_MATERIAL`. | **PROPOSED** ([Proposal], slide 7) |
| Knowledge entry | Unit knowledge di SUNOVATE dengan tipe, status lifecycle, pemilik, dan klasifikasi. | **PROPOSED** |
| Knowledge lifecycle | Tangkap, Validasi, Organisasikan, Temukan, Gunakan, Pelajari. | **PROPOSED** ([Proposal]) |
| Knowledge Hub | Domain area untuk repository knowledge dan pencarian. | **CONFIRMED** sebagai domain area (sumber: `20_NEW_CHAT_MASTER_PROMPT.txt`) |

## Istilah Teknis

| Istilah | Definisi | Label |
|---|---|---|
| Hermes | AI Knowledge Assistant SUNOVATE. Hanya menerima konteks terotorisasi melalui HermesGateway, tidak mengakses database. | **CONFIRMED** ([Brief], ADR-004) |
| HermesGateway | Application service yang menjadi satu-satunya pintu Hermes ke data. | **CONFIRMED** (ADR-004) |
| RAG | Retrieval-Augmented Generation; jawaban disusun dari potongan dokumen yang diambil terlebih dahulu. | **PROPOSED** pendekatan |
| Chunk | Potongan teks dokumen (`document_chunks`) yang menjadi unit retrieval dan sitasi. | **PROPOSED** |
| Embedding | Representasi vektor teks untuk pencarian semantik; disimpan di `embedding_references`. Provider nonaktif sampai model disetujui. | **PROPOSED** (ADR-008, ADR-009) |
| pgvector | Ekstensi PostgreSQL untuk menyimpan dan mencari vektor. | **CONFIRMED** sebagai stack ([Brief]) |
| FTS | Full-text search PostgreSQL berbasis `tsvector` dan indeks GIN. | **CONFIRMED** sebagai stack ([Brief], ADR-003) |
| RBAC | Role-Based Access Control. Di SUNOVATE dikombinasikan dengan team scope dan klasifikasi data. | **CONFIRMED** prinsip; matriks **PROPOSED** (ADR-006) |
| Data classification | Tingkat sensitivitas record: PUBLIC, INTERNAL, RESTRICTED, CONFIDENTIAL. | **PROPOSED**, NEEDS MENTOR VALIDATION |
| Clearance | Tingkat klasifikasi tertinggi yang boleh diakses pengguna (`clearance_code`). | **PROPOSED** |
| Team scope | Batas akses berdasarkan tim pemilik record; `scope:all_teams` membuka semua tim, tetap tunduk pada klasifikasi. | **PROPOSED** |
| sharing_scope | `TEAM` (hanya tim pemilik) atau `DIRECTORATE` (semua tim, hanya bila PUBLISHED). | **PROPOSED**; kebijakan OQ-14 |
| SIMULATED_DATA | Label wajib untuk seluruh data demonstrasi; muncul di `meta.dataLabel` dan kolom `data_origin`. | **CONFIRMED** aturan proyek |
| Revision | Bilangan versi record untuk optimistic concurrency; pembaruan basi menghasilkan HTTP 409 `REVISION_CONFLICT`. | **PROPOSED** (ADR-011) |
| Soft delete | Penandaan `deleted_at` tanpa menghapus baris. | **PROPOSED** (ADR-010) |
| Provider | Abstraksi integrasi eksternal (AI, embedding, dokumen, identitas, notifikasi, Hermes). | **PROPOSED** |
| Modular monolith | Satu aplikasi yang dipisah per modul domain, tanpa microservices. | **CONFIRMED** (ADR-001) |

## Kode Tim Kerja

| Kode | Nama | Sumber |
|---|---|---|
| PPSUN | Pengelolaan Portofolio SUN | **CONFIRMED** ([Brief]) |
| AKPSUN | Analisis Keuangan dan Pasar SUN | **CONFIRMED** ([Brief]); variasi nama di [Pengayaan] OQ-02 |
| PSUN | Peraturan SUN | **CONFIRMED** ([Brief]) |
| PPPSUN | Pengembangan dan Pendalaman Pasar SUN | **CONFIRMED** ([Brief]) |
| DHTV | Dokumen Hukum Transaksi Valas | **CONFIRMED** ([Brief]) |
| SUN Tematik | Fungsi belum diketahui | **OPEN QUESTION** (OQ-01) |

## Related Documents

- [sun-domain-overview.md](../02-business/sun-domain-overview.md)
- [document-classification.md](../04-data/document-classification.md)
- [hermes-overview.md](../05-ai-rag/hermes-overview.md)

## Last Updated

2026-10-01
