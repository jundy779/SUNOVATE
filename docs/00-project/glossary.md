# Glosarium

**Status:** DRAFT
**Last Updated:** 2026-10-06

## Purpose

Glosarium menyamakan istilah domain SUN, istilah knowledge management, dan istilah teknis yang dipakai di dokumentasi dan kode SUNOVATE. Definisi domain SUN bersifat ringkasan untuk keperluan pengembangan; rujukan hukum yang berlaku tetap peraturan aslinya.

Sumber singkatan:
- [Pengayaan] = `Pengayaan_Kelas_Magang_6_Mei_2026.pdf`, sesi berbagi Dit. SUN untuk peserta magang, 6 Mei 2026.
- [Kompilasi] = `Kompilasi_Peraturan_SUN_formal.pdf`, kompilasi peraturan publik dari Database Peraturan BPK dan JDIH Kemenkeu.
- [Proposal] = `SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx` (berstatus usulan).
- [Brief] = brief sesi 2026-10-01.

## Istilah Domain SUN

Format sumber kompilasi: `Kompilasi Peraturan SUN, <regulasi>, Pasal X, hal. N` (hal. = halaman PDF 1 sampai 199). Istilah yang hanya ada di deck [Pengayaan] diberi label **NOT VERIFIABLE FROM COMPILATION**: itu bukan berarti salah, hanya tidak dapat diverifikasi dari kompilasi. Status berlaku regulasi tidak dapat diturunkan dari kompilasi.

| Istilah | Definisi ringkas | Sumber |
|---|---|---|
| SUN (Surat Utang Negara) | Surat berharga berupa surat pengakuan utang dalam mata uang rupiah maupun valuta asing yang dijamin pembayaran bunga dan pokoknya oleh Negara Republik Indonesia sesuai masa berlakunya. | **CONFIRMED** (sumber: [Kompilasi], UU 24/2002, Pasal 1 angka 1, hal. 4; [Pengayaan]) |
| SPN (Surat Perbendaharaan Negara) | Jenis SUN berjangka pendek dengan pembayaran bunga secara diskonto; dibedakan dari Obligasi Negara berdasarkan jangka waktu. Batas jangka waktu mengacu UU 24/2002 Pasal 3 ayat (2). Singkatan SPN dipakai pada PMK 51/2019 (Pasal 6 ayat (3) huruf a, hal. 67); UU 24/2002 dan PMK 111/2024 memakai nama lengkap. | **CONFIRMED** (sumber: [Kompilasi], UU 24/2002, Pasal 3 ayat (2), hal. 5; PMK 51/2019, Pasal 6 ayat (3) huruf a, hal. 67) |
| Obligasi Negara | Jenis SUN berjangka lebih panjang daripada SPN, dengan kupon dan/atau pembayaran bunga secara diskonto. Batas jangka waktu mengacu UU 24/2002 Pasal 3 ayat (3). | **CONFIRMED** (sumber: [Kompilasi], UU 24/2002, Pasal 3 ayat (3), hal. 5) |
| SBN (Surat Berharga Negara) | Dipakai dalam percakapan dan deck sebagai istilah payung. Kompilasi memakai "surat berharga negara" tanpa definisi payung dan tanpa singkatan SBN (contoh pemakaian: PMK 165/2022, Pasal 3 huruf c, hal. 52); SBSN didefinisikan sebagai surat berharga negara berdasarkan prinsip syariah (PMK 114/2023, Pasal 1 angka 2, hal. 118). Definisi SBN: **OPEN QUESTION**. Judul PMK 165/2022 pada naskahnya adalah "Transaksi Surat Utang Negara Secara Langsung", bukan transaksi SBN di pasar sekunder (lihat [sun-domain-overview.md](../02-business/sun-domain-overview.md)). | **NOT VERIFIABLE FROM COMPILATION** untuk singkatan dan definisi payung (sumber: [Pengayaan]; [Kompilasi]) |
| SUN ritel | SUN yang dijual Pemerintah kepada investor ritel (individu) di pasar perdana domestik. | **CONFIRMED** (sumber: [Kompilasi], PMK 27/2020, Pasal 1 angka 8 dan 12, hal. 178-179; [Pengayaan]) |
| ORI | Obligasi Negara Ritel, salah satu jenis SUN ritel (klaim deck). Kompilasi hanya menyebut SUN Ritel dalam bentuk dapat atau tidak dapat diperdagangkan (PMK 27/2020, Pasal 2 ayat (2), hal. 181). | **NOT VERIFIABLE FROM COMPILATION** untuk nama produk dan pemetaannya (sumber: [Pengayaan]) |
| SBR | Savings Bond Ritel, salah satu jenis SUN ritel (klaim deck). Lihat catatan ORI. | **NOT VERIFIABLE FROM COMPILATION** untuk nama produk dan pemetaannya (sumber: [Pengayaan]) |
| Dealer Utama | Bank atau perusahaan efek yang ditunjuk Menteri sebagai Dealer Utama. Peraturan Menteri khusus Dealer Utama dirujuk tetapi tidak ada di kompilasi. | **CONFIRMED** (sumber: [Kompilasi], PMK 114/2023, Pasal 1 angka 15, hal. 119; [Pengayaan]) |
| Bank Indonesia | Melaksanakan penatausahaan SUN (pencatatan kepemilikan, kliring dan setelmen, agen pembayar bunga dan pokok) dan dapat ditunjuk Menteri sebagai agen lelang. | **CONFIRMED** (sumber: [Kompilasi], UU 24/2002, Pasal 12 ayat (1) dan Pasal 13 ayat (1)-(2), hal. 7-8; PMK 111/2024, Pasal 19 ayat (4), hal. 43; [Pengayaan]) |
| BEI | Bursa Efek Indonesia, disebut deck sebagai salah satu pihak dalam ekosistem SUN. BEI tidak disebut di kompilasi; kompilasi hanya menyatakan perdagangan SUN dapat melalui bursa dan/atau di luar bursa (PMK 111/2024, Pasal 4 ayat (4), hal. 37). | **NOT VERIFIABLE FROM COMPILATION** (sumber: [Pengayaan]) |
| Mitra Distribusi | Bank, Perusahaan Efek, Perusahaan Financial Technology dan/atau Penyelenggara Perdagangan Melalui Sistem Elektronik yang ditetapkan Pemerintah untuk membantu pemasaran SUN Ritel. | **CONFIRMED** (sumber: [Kompilasi], PMK 27/2020, Pasal 1 angka 13, hal. 179; [Pengayaan]) |
| Lelang | Penjualan SUN di pasar perdana domestik yang diikuti Peserta Lelang SUN. | **CONFIRMED** (sumber: [Kompilasi], PMK 168/2019, Pasal 1 angka 7, hal. 142; PMK 111/2024, Pasal 14 ayat (1)-(2), hal. 40-41; [Pengayaan]) |
| Private placement | Cara penjualan SUN tanpa lelang melalui transaksi bilateral antara Pemerintah dan Pihak, dengan ketentuan sesuai kesepakatan. Dibedakan dari transaksi langsung, yang merupakan metode tanpa lelang lain. | **CONFIRMED** (sumber: [Kompilasi], PMK 111/2024, Pasal 14 ayat (5) huruf a dan c, hal. 41; PMK 51/2019, Pasal 1 angka 7, hal. 62) |
| Bookbuilding | Cara penjualan (atau pembelian kembali) SUN tanpa lelang melalui pengumpulan pemesanan dalam periode yang ditentukan. Pemesanan yang telah disampaikan tidak dapat dibatalkan menurut PMK 114/2023 (Pasal 11 ayat (3), hal. 125), sehingga bukan sekadar pengumpulan minat. | **CONFIRMED** (sumber: [Kompilasi], PMK 111/2024, Pasal 14 ayat (5) huruf b, hal. 41; PMK 114/2023, Pasal 2 ayat (2) huruf b angka 1, hal. 121; PMK 128/PMK.08/2012, Pasal 1 angka 7, hal. 170) |
| Pembelian kembali (buyback) | Pembelian kembali SUN oleh Pemerintah di Pasar Sekunder sebelum jatuh tempo, dengan cara tunai dan/atau penukaran. "Cash buyback" adalah cara tunai; istilah itu tidak dipakai teks regulasi. Diatur antara lain PMK 114/2023 tentang Pembelian Kembali Surat Utang Negara di Pasar Sekunder. | **CONFIRMED** (sumber: [Kompilasi], PMK 114/2023, Pasal 2 ayat (1), (3) dan (4), hal. 121); istilah "cash buyback" dari [Pengayaan], **NOT VERIFIABLE FROM COMPILATION** sebagai istilah |
| Penukaran | Cara pembelian kembali SUN dengan penyerahan SUN atau SBSN sebagai seri penukar; selisih nilai penyelesaian dapat dibayar tunai. | **CONFIRMED** (sumber: [Kompilasi], PMK 114/2023, Pasal 2 ayat (3) huruf b dan ayat (5)-(6), hal. 121) |
| Debt switch | Istilah deck untuk transaksi penukaran SUN dengan SUN lain. Istilah ini tidak ada di kompilasi. **PROPOSED**: dipetakan ke "penukaran" (dasar: PMK 114/2023, Pasal 2 ayat (3) huruf b, hal. 121). Pemetaan ini perlu validasi mentor. | **NOT VERIFIABLE FROM COMPILATION** untuk istilahnya (sumber: [Pengayaan]) |
| Transaksi SUN secara langsung | Transaksi SUN antara Pemerintah dan Bank Indonesia, Lembaga Penjamin Simpanan, BUMN, BLU, dan/atau Dealer Utama secara langsung melalui sarana yang ditentukan. | **CONFIRMED** (sumber: [Kompilasi], PMK 165/2022, Pasal 1 angka 16, hal. 51) |
| Setelmen | Penyelesaian transaksi SUN yang terdiri dari setelmen dana dan/atau setelmen kepemilikan SUN. Data setelmen tidak dimodelkan di SUNOVATE (ADR-013). | **CONFIRMED** (sumber: [Kompilasi], PMK 111/2024, Pasal 1 angka 8, hal. 36) |

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

2026-10-06
