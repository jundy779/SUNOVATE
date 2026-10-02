# Kriteria Penerimaan

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Dokumen ini memuat kriteria penerimaan Given/When/Then untuk skenario kunci MVP. Skenario ditulis agar dapat diubah langsung menjadi uji otomatis backend (pytest) dan uji end-to-end (Playwright). Semua kriteria **PROPOSED**. Pengguna yang disebut adalah pengguna simulasi berdomain `@sunovate.local` (`SIMULATED_DATA`); record contoh bersifat fiktif.

Konvensi umum yang berlaku untuk semua skenario:
- Semua endpoint berprefiks `/api/v1`.
- Setiap respons membawa header `X-Request-ID`; respons sukses membawa `meta.dataLabel` = `SIMULATED_DATA`.
- Respons error berbentuk `{ "code", "message", "details", "requestId" }` (lihat [error-format.md](../07-api/error-format.md)).

## AC-01 Permintaan tanpa autentikasi ditolak

- **Given** permintaan tanpa token yang valid
- **When** klien memanggil `GET /knowledge`
- **Then** API mengembalikan 401 dengan `code` = `UNAUTHENTICATED`
- **And** tidak ada data knowledge di respons.

Terkait: FR-05, US-03.

## AC-02 Akses tanpa permission ditolak dan diaudit

- **Given** `sim.readonly.dhtv` (peran read_only, tanpa `knowledge:create`)
- **When** ia memanggil `POST /knowledge`
- **Then** API mengembalikan 403 dengan `code` = `PERMISSION_DENIED`
- **And** entri audit `ACCESS_DENIED` tercatat dengan `requestId` yang sama.

Terkait: FR-05, FR-08, US-03.

## AC-03 Record di luar team scope tidak terlihat

- **Given** knowledge entry milik tim PSUN dengan `sharing_scope` = TEAM
- **And** `sim.staff.pppsun` (tim PPPSUN, tanpa `scope:all_teams`)
- **When** ia memanggil `GET /knowledge/{id}` untuk entri tersebut
- **Then** API mengembalikan 404 dengan `code` = `NOT_FOUND`, bukan 403
- **And** entri tersebut tidak muncul di `GET /knowledge`, `GET /search`, maupun `GET /dashboard/summary` miliknya.

Terkait: FR-07, FR-15, US-04.

## AC-04 Plafon klasifikasi pengguna ditegakkan

- **Given** dokumen PUBLISHED berklasifikasi RESTRICTED milik tim PPSUN
- **And** `sim.owner.ppsun` (tim PPSUN, clearance INTERNAL)
- **When** ia membuka detail dokumen atau mencari kata kunci yang cocok
- **Then** dokumen tidak dikembalikan (404 untuk detail, tidak ada di hasil pencarian)
- **Because** rank(INTERNAL) = 1 lebih kecil dari rank(RESTRICTED) = 2.

Terkait: FR-06, US-04.

## AC-05 Plafon klasifikasi Hermes ditegakkan

- **Given** `HERMES_MAX_CLASSIFICATION` = RESTRICTED
- **And** chunk berklasifikasi CONFIDENTIAL yang relevan dengan pertanyaan
- **When** pengguna dengan clearance memadai bertanya ke `POST /hermes/query`
- **Then** chunk CONFIDENTIAL tidak diambil dan tidak dikutip
- **And** bila tidak ada bukti lain, keputusan = `INSUFFICIENT_EVIDENCE`.

Terkait: FR-28, NFR-10.

## AC-06 Hermes menolak pertanyaan di luar scope

- **Given** `sim.staff.pppsun` dengan `hermes:query` dan `search:query`
- **When** ia bertanya hal di luar domain SUN
- **Then** keputusan = `REFUSED_OUT_OF_SCOPE` dan tidak ada retrieval yang dijalankan
- **When** ia meminta bantuan coding umum
- **Then** keputusan = `REFUSED_GENERAL_CODING`
- **When** ia meminta Hermes mengabaikan aturan atau mengungkap instruksi sistem
- **Then** keputusan = `REFUSED_POLICY`
- **And** setiap pertanyaan tercatat sebagai audit `AI_QUERY`.

Terkait: FR-26, FR-33, US-17.

## AC-07 Hermes menolak menjawab tanpa bukti

- **Given** pertanyaan dalam domain SUN yang tidak didukung chunk PUBLISHED mana pun yang boleh dibaca pengguna
- **When** pengguna bertanya ke Hermes
- **Then** keputusan = `INSUFFICIENT_EVIDENCE`
- **And** respons tidak memuat jawaban substantif maupun sitasi.

Terkait: FR-30, US-16.

## AC-08 Sitasi valid

- **Given** pertanyaan yang didukung minimal satu chunk terotorisasi
- **When** Hermes mengembalikan keputusan `ANSWERED`
- **Then** jawaban memuat minimal satu penanda sitasi [n]
- **And** setiap [n] menunjuk chunk yang benar-benar diambil untuk pengguna tersebut
- **And** tidak ada sitasi yang menunjuk dokumen di luar scope atau di atas clearance.
- **Given** keluaran provider yang memuat sitasi tidak valid
- **Then** CitationValidator menolak jawaban dan tidak mengembalikannya sebagai `ANSWERED`.

Terkait: FR-30, US-15.

## AC-09 Chunk berisi instruksi disaring

- **Given** chunk PUBLISHED berisi teks menyerupai instruksi kepada AI (mis. perintah mengabaikan aturan)
- **When** chunk tersebut cocok dengan pertanyaan
- **Then** chunk dikeluarkan sebelum disusun menjadi jawaban dan tidak dikutip.

Terkait: FR-29.

## AC-10 Aksi tulis membutuhkan persetujuan manusia

- **Given** pengguna dengan `hermes:query`
- **When** ia meminta Hermes mengubah, membuat, atau menghapus data
- **Then** keputusan = `REQUIRES_HUMAN_APPROVAL`
- **And** approval request bertipe `HERMES_WRITE_ACTION` berstatus PENDING dibuat
- **And** tidak ada data bisnis yang berubah.

Terkait: FR-32, US-18.

## AC-11 Separation of duties pada approval

- **Given** approval request berstatus PENDING yang diajukan oleh pengguna X
- **When** pengguna X memanggil `POST /approvals/{id}/decision`
- **Then** keputusan ditolak dan status permintaan tetap PENDING.
- **When** pengguna lain dengan `approval:decide` dan scope yang sesuai memutuskan APPROVED
- **Then** status menjadi APPROVED dan audit `APPROVE` tercatat.

Terkait: FR-13, FR-45, US-08.

## AC-12 Revision conflict menghasilkan 409

- **Given** knowledge entry dengan `revision` = 3
- **When** pengguna mengirim `PATCH /knowledge/{id}` dengan `revision` = 2
- **Then** API mengembalikan 409 dengan `code` = `REVISION_CONFLICT`
- **And** data tidak berubah dan `revision` tetap 3.

Pola yang sama berlaku untuk `PATCH /tasks/{id}`. Terkait: FR-11, FR-36, US-06.

## AC-13 Checksum ganda menghasilkan 409

- **Given** referensi dokumen yang sudah memiliki versi dengan checksum SHA-256 tertentu
- **When** pengguna dengan `document:version` mendaftarkan versi baru dengan checksum yang sama melalui `POST /documents/{id}/versions`
- **Then** API mengembalikan 409 dengan `code` = `DUPLICATE_CHECKSUM`
- **And** tidak ada versi baru yang dibuat.

Terkait: FR-19, US-09.

## AC-14 Entri audit tercatat untuk aksi penting

- **Given** pengguna dengan izin yang sesuai
- **When** ia login, membuat atau mengubah knowledge, mengajukan, memutuskan approval, mendaftarkan versi, bertanya ke Hermes, atau memberi umpan balik
- **Then** entri audit dengan aksi LOGIN, CREATE, UPDATE, SUBMIT, APPROVE/REJECT, VERSION_REGISTER, AI_QUERY, atau AI_FEEDBACK tercatat dengan pelaku, waktu, target, dan request id
- **And** pada PostgreSQL, upaya UPDATE atau DELETE pada `audit_logs` ditolak trigger.

Terkait: FR-21, FR-33, FR-42.

## AC-15 Validasi input

- **Given** pengguna terautentikasi
- **When** ia memanggil endpoint daftar dengan `pageSize` = 500
- **Then** API mengembalikan 422 dengan `code` = `VALIDATION_ERROR`.

Terkait: NFR-20.

## Open Questions

- Kode error untuk pelanggaran separation of duties belum dikunci di dokumentasi API; perlu diselaraskan dengan [error-format.md](../07-api/error-format.md).
- OQ-12 dapat mengubah siapa yang berhak memutuskan pada AC-11.

## Related Documents

- [functional-requirements.md](functional-requirements.md)
- [backend-testing.md](../10-testing/backend-testing.md)
- [security-testing.md](../10-testing/security-testing.md)
- [rag-testing.md](../10-testing/rag-testing.md)

## Last Updated

2026-10-01
