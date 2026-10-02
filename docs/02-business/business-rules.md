# Aturan Bisnis

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Dokumen ini menghimpun aturan bisnis SUNOVATE dalam bentuk bernomor agar dapat dirujuk dari kode, pengujian, dan review. Setiap aturan diberi label bukti dan sumber. Aturan PROPOSED berlaku untuk scaffold pengembangan sampai divalidasi mentor.

## Cara Membaca

- ID aturan bersifat tetap. Aturan yang dicabut ditandai "Dicabut", tidak dihapus dan tidak dipakai ulang.
- Setiap aturan yang ditegakkan kode sebaiknya memiliki pengujian yang menyebut ID aturan.
- Perubahan aturan mengikuti [change-management](../12-governance/change-management.md).

## Batas Sistem

| ID | Aturan | Label | Sumber |
|---|---|---|---|
| BR-01 | SUNOVATE tidak menggantikan sistem transaksi SUN resmi dan tidak mengambil keputusan keuangan. | CONFIRMED | Brief sesi 2026-10-01 |
| BR-02 | SUNOVATE bukan SUN Job Monitor; keduanya terpisah. | CONFIRMED | 14_NEW_SESSION_HANDOFF_PROMPT.txt |
| BR-03 | Integrasi produksi (identitas, dokumen, notifikasi, AI, dan lainnya) tetap nonaktif sampai divalidasi. | CONFIRMED | Brief sesi 2026-10-01; AGENTS.md |

## Knowledge dan Publikasi

| ID | Aturan | Label | Sumber |
|---|---|---|---|
| BR-04 | Hanya knowledge berstatus `PUBLISHED` yang masuk pencarian default dan retrieval Hermes. | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-05 | Knowledge menjadi `PUBLISHED` hanya melalui `approval_requests` bertipe `KNOWLEDGE_PUBLICATION` yang berstatus `APPROVED`. | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-06 | Pemutus approval tidak boleh sama dengan pengaju (separation of duties). | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-07 | Knowledge `TEAM` hanya dapat dibaca tim pemilik; `DIRECTORATE` dapat dibaca semua tim hanya bila `PUBLISHED`. Kebijakan lintas tim tetap OQ-14. | PROPOSED | Keputusan desain sesi 2026-10-01 |

## Dokumen

| ID | Aturan | Label | Sumber |
|---|---|---|---|
| BR-08 | File tidak disimpan sebagai BLOB; hanya referensi, metadata, checksum SHA-256, versi, klasifikasi, dan lokasi provider. | CONFIRMED | Brief sesi 2026-10-01; ADR-003 |
| BR-09 | Versi dengan pasangan (`document_reference_id`, `checksum_sha256`) yang sudah ada ditolak dengan 409 `DUPLICATE_CHECKSUM`. | PROPOSED | ADR-003; Proposal v2.4, slide 20 |
| BR-10 | Chunk dari versi berstatus selain `EXTRACTED` tidak diindeks dan tidak diambil Hermes. | PROPOSED | Keputusan desain sesi 2026-10-01 |

## Data dan Integritas

| ID | Aturan | Label | Sumber |
|---|---|---|---|
| BR-11 | Pembaruan wajib menyertakan `revision`; revision lama ditolak 409 `REVISION_CONFLICT`. | PROPOSED | ADR-011; blueprint v0.1 |
| BR-12 | Status tenggat (`SAFE`, `DUE_SOON`, `DUE_TODAY`, `OVERDUE`, `COMPLETED`) dihitung hanya oleh backend. | PROPOSED | Blueprint v0.1 |
| BR-13 | Ambang `DUE_SOON` diatur `DEADLINE_DUE_SOON_DAYS` (default 7); nilai final OQ-15. | PROPOSED | .env.example |
| BR-14 | Record bisnis dihapus secara soft delete (`deleted_at`). | PROPOSED | ADR-010 |
| BR-15 | `audit_logs` bersifat append-only; trigger PostgreSQL menolak UPDATE dan DELETE. | PROPOSED | ADR-010 |
| BR-16 | Seluruh data seed dan demonstrasi berlabel `SIMULATED_DATA`; tidak ada data internal atau keuangan riil. | CONFIRMED | AGENTS.md |
| BR-17 | Respons API membawa `meta.dataLabel = SIMULATED_DATA` selama memakai dataset simulasi. | PROPOSED | ADR-007 |

## Akses dan Keamanan

| ID | Aturan | Label | Sumber |
|---|---|---|---|
| BR-18 | Akses memerlukan permission AND lingkup tim AND klasifikasi; deny by default; ditegakkan di API pada setiap endpoint terlindungi. | CONFIRMED (prinsip), PROPOSED (matriks) | Brief sesi 2026-10-01; ADR-006 |
| BR-19 | Penyembunyian menu di frontend hanya kosmetik dan bukan kontrol akses. | PROPOSED | ADR-006 |
| BR-20 | Record yang tidak boleh dibaca pemanggil dikembalikan sebagai 404, bukan 403, agar keberadaannya tidak bocor. | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-21 | Akses hanya bila peringkat `clearance_code` pengguna lebih besar atau sama dengan peringkat klasifikasi record. | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-22 | Hermes tidak memproses record di atas `HERMES_MAX_CLASSIFICATION` (pengembangan: `RESTRICTED`); `CONFIDENTIAL` tidak diproses Hermes. | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-23 | Autentikasi pengembangan nonaktif di luar development; aplikasi menolak start bila `APP_ENV=production` dan dev auth aktif. | PROPOSED | ADR-005 |
| BR-24 | Penolakan akses dicatat sebagai audit `ACCESS_DENIED`. | PROPOSED | Keputusan desain sesi 2026-10-01 |

## Hermes

| ID | Aturan | Label | Sumber |
|---|---|---|---|
| BR-25 | Hermes tidak pernah mengakses database secara langsung; semua akses melalui application service yang memeriksa izin pengguna. | CONFIRMED | Brief sesi 2026-10-01; ADR-004 |
| BR-26 | Filter otorisasi diterapkan sebelum scoring retrieval. | PROPOSED | ADR-004 |
| BR-27 | Setiap jawaban `ANSWERED` wajib memiliki minimal satu sitasi, dan setiap sitasi harus menunjuk chunk teratorisasi yang diambil. | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-28 | Bukti tidak cukup menghasilkan `INSUFFICIENT_EVIDENCE`, bukan jawaban karangan. | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-29 | Permintaan aksi tulis via Hermes tidak pernah dieksekusi otomatis; menghasilkan `REQUIRES_HUMAN_APPROVAL` dan approval `HERMES_WRITE_ACTION` berstatus `PENDING`. | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-30 | Pertanyaan di luar domain, coding umum, dan upaya jailbreak/prompt injection ditolak (`REFUSED_OUT_OF_SCOPE`, `REFUSED_GENERAL_CODING`, `REFUSED_POLICY`). | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-31 | Setiap query Hermes dan feedback dicatat di audit (`AI_QUERY`, `AI_FEEDBACK`). | PROPOSED | Keputusan desain sesi 2026-10-01 |
| BR-32 | Jawaban Hermes adalah bantuan penelusuran, bukan keputusan atau fakta resmi. | PROPOSED | Risiko R-04 |

## Open Questions Terkait

- OQ-05 Pemetaan klasifikasi ke skema resmi Kemenkeu (BR-21, BR-22).
- OQ-12 Pemutus publikasi (BR-05, BR-06).
- OQ-13 Retensi (BR-14, BR-15).
- OQ-14 Berbagi lintas tim (BR-07).
- OQ-15 Ambang tenggat (BR-13).

## Related Documents

- [knowledge-lifecycle](knowledge-lifecycle.md)
- [document-lifecycle](document-lifecycle.md)
- [work-monitoring-flow](work-monitoring-flow.md)
- [authorization-rbac](../06-security/authorization-rbac.md)
- [citation-policy](../05-ai-rag/citation-policy.md)
- [decision-log](../12-governance/decision-log.md)
