# Chunking Strategy

**Status:** IN PROGRESS
**Last Updated:** 2026-10-14

## Purpose

Menetapkan usulan cara memotong dokumen menjadi chunk agar retrieval akurat dan sitasi dapat menunjuk ke bagian dokumen yang jelas (Pasal, ayat, langkah, atau bagian).

## Status

- **IMPLEMENTED** Chunk pada scaffold berasal dari dataset SIMULATED_DATA yang dimuat ke simulated store.
- **IMPLEMENTED (DEVELOPMENT PREVIEW)** Modul Python `hermes/chunking.py` memotong teks yang sudah diekstrak berdasarkan Pasal, tahap/langkah, heading terbatas, atau paragraf; menghasilkan label, jumlah kata, urutan, dan SHA-256 deterministik tanpa menulis database.
- **PROPOSED** Ekstraksi berkas, review metadata, tokenizer model, ukuran produksi dalam token, overlap, penyimpanan chunk, dan pemicu ingestion. Ukuran dikalibrasi dengan [rag-evaluation.md](./rag-evaluation.md) setelah OQ-11 diputuskan.

## Prinsip

- **IMPLEMENTED (DEVELOPMENT PREVIEW)** Potong berdasarkan struktur dokumen terlebih dahulu, lalu pagar jumlah kata. Preview tidak menggabungkan batas Pasal atau tahapan.
- **IMPLEMENTED (DEVELOPMENT PREVIEW)** Setiap preview chunk membawa label bagian yang dapat ditampilkan pada sitasi.
- **PROPOSED** Setiap chunk mewarisi klasifikasi dan tim pemilik dari versi dokumen induknya. Chunk tidak boleh memiliki klasifikasi lebih rendah daripada dokumen induk.
- **PROPOSED** Chunk hanya dibuat dari teks hasil ekstraksi yang sudah dinormalisasi dan lolos review metadata (lihat [ingestion-pipeline.md](./ingestion-pipeline.md)).

## Strategi per jenis knowledge (PROPOSED)

| Jenis knowledge | Unit struktur | Aturan |
|---|---|---|
| REGULATION | Hierarki BAB, Bagian, Pasal, ayat, huruf/angka (tingkat Bagian ada pada sebagian regulasi saja) | Satu Pasal per chunk bila muat. Pasal panjang dipecah per ayat (Pasal definisi per angka) dengan label induk (regulasi, BAB, Bagian bila ada, Pasal) diulang di awal setiap chunk. Lampiran (tabel, format surat, rumus) menjadi unit tersendiri yang menunjuk Pasal yang merujuknya. Penjelasan hanya ada untuk UU 24/2002 dan PP 76/2005; penjelasan berisi uraian menjadi chunk terpisah yang menunjuk Pasal yang sama, sedangkan entri "Cukup jelas" cukup berupa penanda pada chunk Pasal. Konsiderans dan ketentuan umum (definisi) dijadikan chunk tersendiri. |
| SOP, PLAYBOOK | Langkah atau tahapan | Satu tahapan beserta langkah-langkahnya per chunk. Daftar langkah tidak dipotong di tengah; bila terlalu panjang, dipecah per kelompok langkah dengan judul tahapan diulang. |
| STUDY (kajian), REPORT | Bagian dan subbagian | Potong per heading. Ringkasan eksekutif dan kesimpulan dijadikan chunk tersendiri. |
| MEETING_MATERIAL, DECISION_RECORD, CLOSE_OUT_NOTE, LESSON_LEARNED, TACIT_KNOWLEDGE | Bagian template | Potong per bagian template (mis. konteks, keputusan, tindak lanjut). Template resmi adalah **OPEN QUESTION** OQ-16. |
| Lainnya (POLICY, ARCHIVE, REFERENCE, OTHER) | Paragraf | Gabungkan paragraf berurutan sampai ukuran target. |

Contoh label bagian untuk regulasi: "UU 24/2002, Pasal 1" (dokumen sumber tercantum di `Kompilasi_Peraturan_SUN_formal.pdf`). Contoh ini hanya ilustrasi format label, bukan isi chunk.

Tabel memakai satu chunk per tabel bila muat; bila tidak, dipecah per kelompok baris dengan header tabel diulang.
## Struktur regulasi pada Kompilasi Peraturan SUN (PROPOSED)

Pola di bawah teramati pada teks ekstraksi Kompilasi Peraturan SUN (ekstraksi tanpa OCR, tidak dibandingkan dengan gambar PDF). Format sumber: `Kompilasi Peraturan SUN, <regulasi>, <bagian>, hal. N` (hal. = halaman PDF). Usulan strategi tetap **PROPOSED**.

| Elemen | Pola teramati (CONFIRMED) | Contoh |
|---|---|---|
| BAB | Baris "BAB" dan angka Romawi, judul pada baris berikutnya (sering dua baris) | UU 24/2002, hal. 4 |
| Bagian | "Bagian Kesatu/Kedua/Ketiga" diikuti judul, di antara BAB dan Pasal | PMK 114/2023, hal. 125 |
| Pasal, ayat, huruf | Baris "Pasal N"; ayat diawali "(1)"; huruf diawali "a." | UU 24/2002, Pasal 3, hal. 5 |
| Angka definisi | "1.", "2." pada Pasal 1; rujukan "angka" dan "butir" dipakai bergantian | UU 24/2002, Pasal 1, hal. 4 |
| Lampiran | Dirujuk dari Pasal; "bagian tidak terpisahkan dari Peraturan Menteri ini" | PMK 51/2019, Pasal 6 ayat (4), hal. 68 |
| Penjelasan | "Pasal demi Pasal", lalu "Pasal N", "Ayat (1)", "Cukup jelas"; hanya pada UU dan PP | UU 24/2002, hal. 13-20; PP 76/2005, hal. 29-33 |

Kerusakan ekstraksi yang harus ditoleransi pendeteksi penanda (**CONFIRMED** teramati di teks ekstraksi):

- Spasi hilang pada penanda ("Pasal29", "Pasal30" di PMK 168/2019, hal. 155; "Pasal42" di PMK 215/2019, hal. 112).
- Spasi disisipkan atau kata terpecah ("( 1)" di PMK 114/2023, hal. 122).
- Salah baca karakter ("PMK.OS" untuk "PMK.08"; "Basil" untuk "Hasil" di PMK 114/2023, hal. 129).
- Kata penyambung halaman berulang di awal halaman ("(2) Surat..." di UU 24/2002, hal. 5) dan nomor cetak pada baris sendiri ("- 2 -", hal. 4).
- Rujukan ayat yang keliru pada teks sumber; chunk menyimpan teks apa adanya dan tidak mengoreksinya.

Usulan: deteksi penanda Pasal dan ayat toleran terhadap spasi hilang dan galat OCR, kata penyambung halaman dibuang, dan hasil deteksi penanda ditinjau manusia sebelum chunking (lihat [ingestion-pipeline.md](./ingestion-pipeline.md)). Pasal yang melintas halaman tidak dipotong di batas halaman. Ketentuan peralihan dan penutup diberi jenis khusus agar relasi dapat ditinjau manusia, bukan diterapkan otomatis.

## Ukuran target (PROPOSED)

| Parameter | Nilai awal usulan |
|---|---|
| Ukuran target | 300 sampai 500 token |
| Ukuran maksimum | 800 token |
| Ukuran minimum | 50 token; chunk lebih kecil digabung dengan tetangga dalam unit struktur yang sama |
| Overlap | 10 sampai 15 persen, hanya di dalam unit struktur yang sama |

Overlap tidak melintasi batas Pasal atau batas tahapan agar sitasi tidak tercampur.

## Metadata per chunk (PROPOSED)

| Field | Keterangan |
|---|---|
| `document_version_id` | Versi dokumen induk |
| `classification_code` | Diwarisi dari versi dokumen |
| `owner_team_id` | Diwarisi dari referensi dokumen |
| `page_start`, `page_end` | Rentang halaman sumber. Memakai nomor halaman PDF berkas; nomor cetak peraturan disimpan terpisah bila perlu agar sitasi tidak ambigu |
| `section_label` | Label tampilan, mis. Pasal, ayat, langkah, atau judul bagian |
| `chunk_index` | Urutan dalam versi |
| `content_hash` | Hash isi chunk untuk mendeteksi perubahan dan duplikasi |
| `token_count` | Jumlah token menurut tokenizer yang dipakai |

Nama kolom fisik mengikuti [database-schema.md](../04-data/database-schema.md); field yang belum ada di skema `0001_initial_schema` memerlukan migrasi tambahan.

## Versi baru

- **PROPOSED** Registrasi versi baru (`POST /api/v1/documents/{id}/versions`) memicu chunking ulang untuk versi tersebut.
- **PROPOSED** Chunk versi lama tidak dihapus agar sitasi historis tetap dapat ditelusuri, tetapi dikeluarkan dari retrieval default ketika knowledge induk menjadi SUPERSEDED atau ARCHIVED.
- **PROPOSED** `content_hash` dipakai untuk menghindari pembuatan embedding ulang bagi chunk yang isinya tidak berubah, selama `model_name` sama.
- **PROPOSED** Perubahan model embedding mewajibkan embedding ulang seluruh chunk aktif dengan `model_name` baru.

## Open Questions

- OQ-04 Jenis dokumen yang boleh masuk RAG.
- OQ-11 Model dan tokenizer yang disetujui.
- OQ-16 Template knowledge product yang disetujui.
- OQ-32 Validasi teks ekstraksi regulasi terhadap PDF atau sumber resmi.

## Risks

- R-11 Kualitas metadata rendah sehingga retrieval buruk.
- R-07 Prompt injection dari dokumen yang ikut ter-chunk.

## Acceptance Criteria

- Tidak ada chunk regulasi yang melintasi batas Pasal.
- Setiap chunk memiliki `section_label` dan rentang halaman yang dapat ditampilkan pada sitasi.
- Klasifikasi chunk selalu sama dengan klasifikasi versi dokumen induk.

## Related Documents

- [rag-pattern-reference.md](./rag-pattern-reference.md)
- [ingestion-pipeline.md](./ingestion-pipeline.md)
- [citation-policy.md](./citation-policy.md)
- [metadata-schema.md](../04-data/metadata-schema.md)
- [knowledge-lifecycle.md](../02-business/knowledge-lifecycle.md)
