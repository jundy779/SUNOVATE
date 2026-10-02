# Hermes Overview

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Dokumen ini menjelaskan apa itu Hermes, batasannya, komponen yang membentuknya, alur pemrosesan pertanyaan, serta keputusan (decision) yang dapat dihasilkan. Dokumen ini membedakan secara tegas antara yang sudah diimplementasikan pada scaffold dan yang masih berupa usulan.

## Confirmed Information

- **CONFIRMED** Hermes adalah AI Knowledge Assistant SUNOVATE dan merupakan salah satu tujuan proyek (sumber: brief sesi 2026-10-01).
- **CONFIRMED** Hermes tidak boleh mengakses database secara langsung. Seluruh akses melalui application service atau tool API yang memeriksa izin pengguna (sumber: brief sesi 2026-10-01).
- **CONFIRMED** Hermes berada di belakang application service `HermesGateway`; runtime Hermes hanya menerima konteks yang sudah diotorisasi dan tidak memegang kredensial database (sumber: ADR-004, brief sesi 2026-10-01).
- **CONFIRMED** SUNOVATE tidak mengambil keputusan keuangan dan tidak memberikan akses dokumen tanpa otorisasi; batasan ini berlaku penuh untuk Hermes (sumber: brief sesi 2026-10-01).
- **CONFIRMED** Tim kerja menjadi konteks otorisasi Hermes (sumber: brief sesi 2026-10-01).

## Apa itu Hermes dan apa yang bukan

Hermes adalah:

- Asisten tanya jawab berbasis knowledge repository SUNOVATE yang menjawab hanya dari konteks yang boleh dibaca pengguna, disertai sitasi.
- Antarmuka pencarian percakapan atas dokumen, regulasi, kajian, SOP, playbook, lesson learned, bahan rapat, dan arsip yang berstatus PUBLISHED.

Hermes bukan:

- **OUT OF SCOPE** Pengambil keputusan keuangan atau pemberi rekomendasi transaksi SUN.
- **OUT OF SCOPE** Pengganti sistem transaksi SUN resmi.
- **OUT OF SCOPE** Asisten pemrograman umum atau chatbot serba guna.
- **OUT OF SCOPE** Jalur untuk membuka dokumen yang tidak boleh diakses pengguna.
- **OUT OF SCOPE** Pelaksana aksi tulis secara otomatis; aksi tulis selalu membutuhkan persetujuan manusia (lihat [human-approval.md](./human-approval.md)).

## Komponen

| Komponen | Peran | Status di scaffold |
|---|---|---|
| `AIProvider` | Antarmuka penyusun jawaban. Implementasi pengembangan `development_extractive` bersifat deterministik dan ekstraktif, tanpa model eksternal dan tanpa jaringan. | IMPLEMENTED (pengembangan); provider produksi disabled |
| `EmbeddingProvider` | Antarmuka pembuat embedding. | Disabled (`EMBEDDING_PROVIDER=disabled`); semantic retrieval PROPOSED |
| `DocumentProvider` | Antarmuka akses referensi dokumen; file tetap referensi eksternal. | `DOCUMENT_PROVIDER=local` untuk pengembangan |
| `IdentityProvider` | Antarmuka identitas pengguna. | `IDENTITY_PROVIDER=development` (token pengembangan) |
| `NotificationProvider` | Antarmuka notifikasi. | `NOTIFICATION_PROVIDER=disabled` |
| `HermesClient` | Antarmuka ke runtime Hermes; menerima konteks yang sudah diotorisasi. | Implementasi pengembangan ekstraktif |
| `RetrievalService` | Mengambil chunk PUBLISHED yang boleh dibaca pengguna; filter sebelum scoring. | IMPLEMENTED (leksikal, simulated store) |
| `AuthorizationService` | Memeriksa permission, team scope, dan klasifikasi data. | IMPLEMENTED |
| `CitationValidator` | Memastikan setiap penanda `[n]` merujuk ke chunk yang diambil dan diotorisasi; minimal satu sitasi. | IMPLEMENTED |
| `OutputGuard` | Memblokir pola rahasia/sensitif dan pelanggaran batas klasifikasi pada keluaran. | IMPLEMENTED |
| `ScopeGuard` | Mengklasifikasikan pertanyaan: domain SUN, general coding, jailbreak/policy override, write intent. | IMPLEMENTED (berbasis aturan) |
| `HermesGateway` | Orkestrator seluruh alur; satu-satunya pintu masuk Hermes di API. | IMPLEMENTED |

Sumber tabel: fact sheet bagian 3 dan 9 (ADR-004, ADR-008). Selain itu terdapat Reranker leksikal dan filter injeksi dokumen di modul Hermes.

## Alur 10 langkah (IMPLEMENTED pada scaffold)

1. Pengguna mengirim pertanyaan melalui web (`/hermes`), diteruskan oleh route handler `/api/hermes` ke `POST /api/v1/hermes/query`.
2. `ScopeGuard` menilai cakupan: domain SUN, general coding, jailbreak/policy override, atau write intent.
3. `AuthorizationService` memeriksa permission `hermes:query` dan `search:query`.
4. `RetrievalService` mengambil chunk PUBLISHED yang boleh dibaca pengguna; filter otorisasi dijalankan sebelum scoring.
5. Reranker leksikal mengurutkan ulang kandidat.
6. Filter injeksi dokumen mengeluarkan chunk yang berisi teks menyerupai instruksi.
7. `HermesClient` (development extractive) menyusun jawaban hanya dari chunk yang tersisa.
8. `CitationValidator` memeriksa bahwa setiap `[n]` merujuk ke chunk yang diambil dan diotorisasi, dengan minimal satu sitasi.
9. `OutputGuard` memeriksa pola rahasia/sensitif dan batas klasifikasi.
10. Audit log dicatat (aksi `AI_QUERY`), lalu respons dikembalikan.

Jika `ScopeGuard` mendeteksi write intent, Hermes tidak mengeksekusi apa pun; sistem membuat approval request berstatus PENDING dan mengembalikan `REQUIRES_HUMAN_APPROVAL`. Rincian alur ada di [rag-architecture.md](./rag-architecture.md).

## Decisions

| Decision | Arti |
|---|---|
| `ANSWERED` | Jawaban disusun dari konteks terotorisasi dengan sitasi valid. |
| `INSUFFICIENT_EVIDENCE` | Tidak ada konteks terotorisasi yang memadai atau sitasi tidak dapat divalidasi. |
| `REFUSED_OUT_OF_SCOPE` | Pertanyaan di luar domain SUN. |
| `REFUSED_GENERAL_CODING` | Permintaan pemrograman umum. |
| `REFUSED_POLICY` | Jailbreak, policy override, atau prompt injection. |
| `REQUIRES_HUMAN_APPROVAL` | Permintaan aksi tulis; approval request PENDING dibuat, tidak dieksekusi. |
| `BLOCKED_BY_OUTPUT_GUARD` | Keluaran diblokir `OutputGuard`. |

Sumber: fact sheet bagian 6.

## Kanal

- **CONFIRMED** Web SUNOVATE (`/hermes`) adalah kanal yang tersedia pada scaffold (sumber: fact sheet bagian 9).
- **PROPOSED** Telegram dan WhatsApp merupakan prioritas P2, hanya setelah validasi dan bukan janji (sumber: Proposal v2.4, slide 11). Izin penggunaannya adalah **OPEN QUESTION** OQ-08. Lihat [telegram-proposal.md](../08-integrations/telegram-proposal.md) dan [whatsapp-proposal.md](../08-integrations/whatsapp-proposal.md).

## Proposed Design (belum diimplementasikan)

- **PROPOSED** Semantic retrieval dengan embedding dan pgvector, hybrid retrieval FTS + vektor dengan reciprocal rank fusion, cross-encoder rerank, LLM yang disetujui, dan OCR.
- **OPEN QUESTION** Pilihan model AI/LLM dan embedding, lokasi pemrosesan, dan apakah data boleh keluar dari jaringan instansi (OQ-11). Tidak ada model berbayar yang digunakan pada scaffold.

## Risks

- R-02 Kebocoran data melalui pencarian/Hermes.
- R-04 Jawaban AI dianggap fakta/keputusan.
- R-07 Prompt injection dari dokumen.
- R-10 Simulated store disangka persistence produksi.

Lihat [risk-register.md](../12-governance/risk-register.md).

## Acceptance Criteria

- Setiap jawaban `ANSWERED` memiliki minimal satu sitasi valid ke chunk terotorisasi.
- Tidak ada konteks di luar hak akses pengguna yang mencapai `HermesClient`.
- Setiap query menghasilkan entri audit `AI_QUERY`.
- Write intent tidak pernah dieksekusi tanpa keputusan manusia.

## Related Documents

- [rag-architecture.md](./rag-architecture.md)
- [scope-guard.md](./scope-guard.md)
- [citation-policy.md](./citation-policy.md)
- [prompt-injection-defense.md](./prompt-injection-defense.md)
- [provider-abstraction.md](../03-architecture/provider-abstraction.md)
- [authorization-rbac.md](../06-security/authorization-rbac.md)
- [open-questions.md](../00-project/open-questions.md)
