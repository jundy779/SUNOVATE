# Retrieval Strategy

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Menjelaskan cara Hermes dan pencarian memilih chunk: filter otorisasi, scoring yang berjalan saat ini, desain hybrid yang diusulkan, serta ambang untuk menyatakan bukti tidak cukup.

## Confirmed Information

- **CONFIRMED** Authorization = permission AND team scope AND data classification, deny by default (sumber: ADR-006, brief sesi 2026-10-01).
- **CONFIRMED** Hanya knowledge PUBLISHED yang masuk pencarian default dan retrieval Hermes (sumber: fact sheet bagian 6).
- **CONFIRMED** Filter otorisasi dijalankan sebelum scoring (sumber: fact sheet bagian 9).
- **CONFIRMED** `HERMES_MAX_CLASSIFICATION=RESTRICTED` pada pengembangan; CONFIDENTIAL tidak diproses Hermes pada pengembangan (sumber: fact sheet bagian 4).
- **CONFIRMED** Semantic retrieval masih PROPOSED sampai model embedding disetujui (sumber: ADR-008).

## Filter otorisasi (IMPLEMENTED)

Filter dijalankan sebelum scoring. Chunk yang tidak lolos tidak dihitung skornya, tidak memengaruhi peringkat, dan tidak dikirim ke `HermesClient`. Sebuah chunk menjadi kandidat hanya jika semua syarat berikut terpenuhi:

| Syarat | Aturan |
|---|---|
| Permission | Principal memiliki `hermes:query` dan `search:query` (untuk Hermes) atau `search:query` (untuk `GET /search`). |
| Status | Knowledge induk berstatus `PUBLISHED`. |
| Soft delete | `deleted_at` bernilai null pada knowledge, referensi dokumen, dan versi terkait. |
| Klasifikasi | rank(`clearance_code` pengguna) >= rank(`classification_code` record). |
| Batas Hermes | rank(`classification_code` record) <= rank(`HERMES_MAX_CLASSIFICATION`). |
| Team scope | `owner_team_id` termasuk tim pengguna, atau pengguna memiliki `scope:all_teams`, atau `sharing_scope = DIRECTORATE` dan record PUBLISHED. |

Rank klasifikasi: PUBLIC 0, INTERNAL 1, RESTRICTED 2, CONFIDENTIAL 3 (PROPOSED, NEEDS MENTOR VALIDATION; lihat [document-classification.md](../04-data/document-classification.md)). Kebijakan berbagi lintas tim untuk konten INTERNAL adalah **OPEN QUESTION** OQ-14.

Konsekuensi: pengguna dengan clearance INTERNAL tidak pernah menerima chunk RESTRICTED, meskipun pertanyaannya sangat relevan. Record yang tidak boleh dibaca dikembalikan sebagai 404 pada endpoint detail untuk mencegah kebocoran keberadaan.

## Scoring saat ini (IMPLEMENTED)

- Retrieval leksikal atas chunk PUBLISHED terotorisasi di simulated store (`DATA_BACKEND=simulated`).
- Rerank leksikal terhadap kandidat.
- Filter injeksi dokumen mengeluarkan chunk yang berisi teks menyerupai instruksi, setelah rerank dan sebelum penyusunan jawaban.
- Tidak ada embedding, tidak ada model eksternal, tidak ada panggilan jaringan.

Nilai yang dipakai kode scaffold saat ini (`hermes/retrieval.py`, `hermes/gateway.py`, semua **PROPOSED** dan dikalibrasi terhadap golden set simulasi):

| Parameter | Nilai | Arti |
|---|---|---|
| Kandidat | 20 | chunk terotorisasi teratas berdasarkan coverage term |
| Coverage | term query yang cocok di judul + label bagian + isi, dibagi jumlah term query | |
| Skor rerank | 0,6 x coverage + 0,4 x coverage isi saja | mencegah kecocokan judul saja dianggap bukti |
| `MIN_COVERAGE` | 0,4 | minimum coverage chunk teratas |
| Term cocok minimum | 2 (atau 1 bila query hanya satu term) | |
| `MIN_SCORE` | 0,45 | minimum skor rerank chunk teratas dan chunk lain yang dipilih |
| `RELATIVE_CUTOFF` | 0,6 | chunk lain harus >= 60 persen skor teratas |
| `MAX_PASSAGES` | 3 | passage maksimum yang diberikan ke HermesClient |

Kasus golden set RAG-16 (query yang hanya cocok dengan judul dan label "Langkah" dari SOP lain) memicu penambahan `MIN_SCORE`.

## Desain hybrid (PROPOSED)

Berlaku setelah repository SQLAlchemy diimplementasikan dan model embedding disetujui (OQ-11).

```mermaid
flowchart LR
    Q["Pertanyaan"] --> F["Filter otorisasi SQL"]
    F --> T["FTS: search_vector GIN"]
    F --> V["Vektor: embedding_references"]
    T --> R["Reciprocal rank fusion"]
    V --> R
    R --> X["Rerank (cross-encoder, usulan)"]
    X --> I["Filter injeksi"]
    I --> C["Konteks top-k ke HermesClient"]
```

- **PROPOSED** Filter otorisasi diterapkan sebagai klausa WHERE pada kedua kanal, bukan pasca-filter.
- **PROPOSED** Kanal FTS memakai `document_chunks.search_vector` dengan konfigurasi teks yang sesuai Bahasa Indonesia; konfigurasi kamus adalah keputusan teknis yang perlu diuji dengan golden set.
- **PROPOSED** Kanal vektor memakai `embedding_references` dengan `model_name` yang sama dengan embedding pertanyaan. Indeks ANN baru dibuat setelah model dan dimensi disetujui (ADR-009).
- **PROPOSED** Fusi dengan reciprocal rank fusion: skor = jumlah 1 / (k + rank) dari setiap kanal, dengan k = 60 sebagai nilai awal.
- **PROPOSED** Cross-encoder rerank hanya jika modelnya disetujui dan diproses di lokasi yang diizinkan (OQ-11). Tanpa itu, rerank leksikal tetap dipakai.
- **PROPOSED** Boost untuk metadata: kecocokan judul, jenis knowledge, dan relasi regulasi yang masih berlaku.

## Top-k (PROPOSED)

| Parameter | Nilai awal usulan | Catatan |
|---|---|---|
| Kandidat per kanal | 20 | Sebelum fusi |
| Kandidat setelah fusi untuk rerank | 20 | |
| Chunk konteks ke HermesClient | 5 | Dibatasi juga oleh anggaran token model yang disetujui |
| Chunk per dokumen dalam konteks | maksimal 3 | Menjaga keragaman sumber |

Nilai dikalibrasi dengan metrik retrieval hit@k pada [rag-evaluation.md](./rag-evaluation.md).

## Ambang bukti tidak cukup

Hermes mengembalikan `INSUFFICIENT_EVIDENCE` bila:

- **IMPLEMENTED** Tidak ada chunk terotorisasi yang tersisa setelah filter dan filter injeksi.
- **IMPLEMENTED** Jawaban tidak memiliki minimal satu sitasi valid (lihat [citation-policy.md](./citation-policy.md)).
- **IMPLEMENTED** Chunk teratas di bawah `MIN_COVERAGE`, `MIN_SCORE`, atau jumlah term cocok minimum (nilai di tabel di atas, PROPOSED untuk kalibrasi ulang).

Pesan kepada pengguna tidak boleh mengisyaratkan adanya dokumen yang tidak boleh dibaca pengguna. Pesan yang diusulkan: "Hermes belum menemukan sumber yang cukup pada dokumen yang dapat Anda akses untuk menjawab pertanyaan ini."

## Open Questions

- OQ-05 Klasifikasi dan hak akses tiap jenis dokumen.
- OQ-11 Model embedding dan rerank, lokasi pemrosesan.
- OQ-14 Kebijakan `sharing_scope` lintas tim.

## Risks

- R-02 Kebocoran data melalui pencarian/Hermes.
- R-09 Klasifikasi tidak sesuai skema resmi.
- R-11 Kualitas metadata rendah sehingga retrieval buruk.

## Acceptance Criteria

- Kebocoran tanpa otorisasi pada golden set = 0.
- Record dengan klasifikasi di atas clearance pengguna, atau di atas `HERMES_MAX_CLASSIFICATION` untuk Hermes, tidak pernah muncul sebagai kandidat, konteks, maupun sitasi.
- Record dengan `deleted_at` terisi atau status selain PUBLISHED tidak pernah muncul.

## Related Documents

- [rag-architecture.md](./rag-architecture.md)
- [authorization-rbac.md](../06-security/authorization-rbac.md)
- [permission-matrix.md](../06-security/permission-matrix.md)
- [data-classification.md](../06-security/data-classification.md)
- [rag-evaluation.md](./rag-evaluation.md)
