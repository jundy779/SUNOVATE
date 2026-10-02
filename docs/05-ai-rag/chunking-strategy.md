# Chunking Strategy

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Menetapkan usulan cara memotong dokumen menjadi chunk agar retrieval akurat dan sitasi dapat menunjuk ke bagian dokumen yang jelas (Pasal, ayat, langkah, atau bagian).

## Status

- **IMPLEMENTED** Chunk pada scaffold berasal dari dataset SIMULATED_DATA yang dimuat ke simulated store; belum ada proses chunking otomatis.
- **PROPOSED** Seluruh strategi di dokumen ini, termasuk ukuran target dalam token. Ukuran dikalibrasi dengan [rag-evaluation.md](./rag-evaluation.md) dan menyesuaikan tokenizer model yang disetujui (OQ-11).

## Prinsip

- **PROPOSED** Potong berdasarkan struktur dokumen terlebih dahulu, lalu berdasarkan ukuran. Batas struktur tidak dipotong di tengah kalimat.
- **PROPOSED** Setiap chunk membawa label bagian yang dapat ditampilkan pada sitasi.
- **PROPOSED** Setiap chunk mewarisi klasifikasi dan tim pemilik dari versi dokumen induknya. Chunk tidak boleh memiliki klasifikasi lebih rendah daripada dokumen induk.
- **PROPOSED** Chunk hanya dibuat dari teks hasil ekstraksi yang sudah dinormalisasi dan lolos review metadata (lihat [ingestion-pipeline.md](./ingestion-pipeline.md)).

## Strategi per jenis knowledge (PROPOSED)

| Jenis knowledge | Unit struktur | Aturan |
|---|---|---|
| REGULATION | Pasal, lalu ayat | Satu Pasal per chunk bila muat. Pasal panjang dipecah per ayat dengan judul Bab dan nomor Pasal diulang di awal setiap chunk. Penjelasan Pasal disimpan sebagai chunk terpisah yang menunjuk Pasal yang sama. Konsiderans dan ketentuan umum (definisi) dijadikan chunk tersendiri. |
| SOP, PLAYBOOK | Langkah atau tahapan | Satu tahapan beserta langkah-langkahnya per chunk. Daftar langkah tidak dipotong di tengah; bila terlalu panjang, dipecah per kelompok langkah dengan judul tahapan diulang. |
| STUDY (kajian), REPORT | Bagian dan subbagian | Potong per heading. Ringkasan eksekutif dan kesimpulan dijadikan chunk tersendiri. |
| MEETING_MATERIAL, DECISION_RECORD, CLOSE_OUT_NOTE, LESSON_LEARNED, TACIT_KNOWLEDGE | Bagian template | Potong per bagian template (mis. konteks, keputusan, tindak lanjut). Template resmi adalah **OPEN QUESTION** OQ-16. |
| Lainnya (POLICY, ARCHIVE, REFERENCE, OTHER) | Paragraf | Gabungkan paragraf berurutan sampai ukuran target. |

Contoh label bagian untuk regulasi: "UU 24/2002, Pasal 1" (dokumen sumber tercantum di `Kompilasi_Peraturan_SUN_formal.pdf`). Contoh ini hanya ilustrasi format label, bukan isi chunk.

Tabel memakai satu chunk per tabel bila muat; bila tidak, dipecah per kelompok baris dengan header tabel diulang.

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
| `page_start`, `page_end` | Rentang halaman sumber |
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

## Risks

- R-11 Kualitas metadata rendah sehingga retrieval buruk.
- R-07 Prompt injection dari dokumen yang ikut ter-chunk.

## Acceptance Criteria

- Tidak ada chunk regulasi yang melintasi batas Pasal.
- Setiap chunk memiliki `section_label` dan rentang halaman yang dapat ditampilkan pada sitasi.
- Klasifikasi chunk selalu sama dengan klasifikasi versi dokumen induk.

## Related Documents

- [ingestion-pipeline.md](./ingestion-pipeline.md)
- [citation-policy.md](./citation-policy.md)
- [metadata-schema.md](../04-data/metadata-schema.md)
- [knowledge-lifecycle.md](../02-business/knowledge-lifecycle.md)
