# Aturan Bisnis

**Status:** PROPOSED
**Last Updated:** 2026-10-06

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
| BR-13 | Ambang `DUE_SOON` diatur `DEADLINE_DUE_SOON_DAYS` (default 7); nilai final OQ-15. Ini pengaturan aplikasi, bukan tenggat hukum; tenggat yang tertulis dalam regulasi tidak dipakai sebagai nilai default. | PROPOSED | .env.example |
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

## Jawaban Knowledge Owner (deck v1_ slide 24)

Aturan BR-33 sampai BR-39 berasal dari jawaban knowledge owner (**CONFIRMED (knowledge owner, deck v1_ slide 24)**; pengakuan mentor tertunda, OQ-24). Kolom Label memisahkan isi jawaban dari penegakannya. Kolom Konflik menandai pertentangan dengan matriks atau kode saat ini.

| ID | Aturan | Label | Sumber | Konflik |
|---|---|---|---|---|
| BR-33 | Yang dapat mengubah data atau mengunggah (membuat, mengubah, dan mengajukan knowledge; mendaftarkan dokumen dan versi) hanyalah ketua tim, kasubdit PMP, Kasi MP, dan PIC yang ditunjuk. Berlaku bersama BR-18 (permission AND lingkup tim AND klasifikasi). | CONFIRMED (knowledge owner) untuk siapa yang berwenang; PROPOSED untuk pemetaan role (`team_lead`, `knowledge_owner`, `knowledge_coordinator`) dan penegakan di API | Deck v1_ slide 24, pertanyaan 3 (OQ-05); DEC-20261002-03 | Konflik: `staff` memiliki `knowledge:create`, `knowledge:update`, `knowledge:submit`, dan `document:create` pada matriks saat ini. Belum diterapkan (PD-1, FR-50, R-17). Cakupan "data" untuk data kerja: OPEN QUESTION (OQ-25) |
| BR-34 | Knowledge owner dan reviewer pada setiap tim adalah ketua tim dan PIC yang ditunjuk untuk tim itu. Penunjukan berlaku per tim; penunjukan untuk satu tim tidak memberi hak atas tim lain. | CONFIRMED (knowledge owner) untuk peran; PROPOSED untuk sifat per tim dan pencatatannya | Deck v1_ slide 24, pertanyaan 7 (OQ-09); DEC-20261002-07 | Konflik: belum ada pencatatan penunjukan; role berlaku global karena `user_roles.team_id` tidak diperiksa saat resolusi permission (FR-51). `knowledge_owner` belum memiliki `knowledge:review` atau `approval:decide` |
| BR-35 | Cakupan dokumen yang boleh masuk repository dan RAG adalah yang diusulkan tim kerja, tetapi dokumen asli hanya boleh masuk setelah klasifikasi ditetapkan (OQ-05) dan persetujuan eksplisit ada. Konten `CONFIDENTIAL` tidak diproses Hermes. Sampai itu, hanya `SIMULATED_DATA` yang dimuat. | CONFIRMED (knowledge owner) untuk cakupan; CONFIRMED (aturan proyek) untuk larangan data asli tanpa persetujuan; PROPOSED untuk gerbang intake | Deck v1_ slide 24, pertanyaan 2 (OQ-04); AGENTS.md; BR-16, BR-22; DEC-20261002-02 | Belum ada gerbang intake; tidak ada pipeline ingestion (KL-07, FR-53) |
| BR-36 | Indikator tanpa sumber data otoritatif (saat ini "yield" dan "kepemilikan SBN") tidak menampilkan angka; dashboard menyatakan sumber data belum tersedia. SUNOVATE tidak menyimpan data transaksi, yield, atau lelang dan tidak membuat tabel bisnis SUN. | CONFIRMED (knowledge owner) untuk indikator yang diminta; PROPOSED untuk perilaku blokir; OUT OF SCOPE untuk data bisnis SUN (ADR-013) | Deck v1_ slide 24, pertanyaan 8 (OQ-10); ADR-013; DEC-20261002-08 | Tidak ada konflik kode (tidak ada angka); teks "sumber data belum tersedia" belum ada di UI (FR-54). Sumber dan definisi: OPEN QUESTION (OQ-21) |
| BR-37 | Pilot berjalan pada satu komputer khusus sebagai server. Sebelum data non-simulasi masuk: `DATA_BACKEND=postgres`, dev auth tidak terbuka ke jaringan, secret di luar repository, backup di luar host dengan uji restore, dan administrator serta akses server ditetapkan. | CONFIRMED (knowledge owner) untuk hosting; PROPOSED untuk syarat yang menyertainya | Deck v1_ slide 24, pertanyaan 5 (OQ-07); NFR-39 sampai NFR-44; DEC-20261002-05 | Mekanisme login belum dijawab dan `APP_ENV=production` menolak dev auth, sehingga server pada mode production belum dapat dipakai login (OQ-07, OQ-23, PD-3) |
| BR-38 | Telegram dan WhatsApp tidak diaktifkan dan tidak diklaim tersedia (P2). Bila dilanjutkan: otorisasi tetap lewat HermesGateway seperti web, dan konten `RESTRICTED` ke atas tidak dikirim ke kanal eksternal secara default (lihat BR-03 dan BR-25). | CONFIRMED (knowledge owner) untuk "bisa" penggunaan internal; PROPOSED untuk batasan | Deck v1_ slide 24, pertanyaan 6 (OQ-08); DEC-20261002-06; PD-6 | Tidak ada konflik kode: tidak ada kode kanal (FR-55) |
| BR-39 | Pilot mencakup enam tim. Tim di luar enam tim tidak dibuat sampai nama resmi dan tim tambahan dikonfirmasi; isolasi antar tim mengikuti BR-07 dan BR-18. | CONFIRMED (knowledge owner) untuk "6 tim"; PROPOSED untuk identitas keenam tim | Deck v1_ slide 24, pertanyaan 1 (OQ-03); DEC-20261002-01 | Tidak ada konflik: enam tim seed; nama resmi dan tim tambahan OPEN QUESTION (OQ-02) |

Konflik dengan aturan yang sudah ada:

- BR-33 bertentangan dengan matriks role `staff` (bukan dengan BR-18); hingga PD-1 diterapkan, perilaku API lebih longgar daripada BR-33.
- BR-05 dan BR-06 tidak berubah; siapa yang memutuskan publikasi tetap OQ-12.
- BR-23 tetap: `APP_ENV=production` dengan dev auth aktif ditolak. BR-37 menambahkan konsekuensi untuk server pilot.

## Regulasi dan Sitasi

Aturan BR-40 sampai BR-45 berasal dari telaah Kompilasi Peraturan SUN terhadap dokumentasi (lihat bagian "Asal Temuan Kompilasi Peraturan" di [open-questions](../00-project/open-questions.md)). Seluruhnya **PROPOSED**; belum ada penegakan di kode.

| ID | Aturan | Label | Sumber |
|---|---|---|---|
| BR-40 | Status hukum regulasi (berlaku, diubah, dicabut sebagian, dicabut) tidak pernah diturunkan otomatis dari teks regulasi atau dari ketiadaan relasi di repository. Nilainya diisi pemilik konten setelah validasi; sebelum itu ditampilkan sebagai belum diverifikasi. | PROPOSED | Telaah Kompilasi Peraturan SUN (kompilasi tidak menyatakan status berlaku saat ini); OQ-09, OQ-26; R-18 |
| BR-41 | Setiap entri REGULATION dan setiap sitasi regulasi membawa rujukan Pasal (bila ada) dan nomor halaman PDF berkas, dengan format `<regulasi>, Pasal X, hal. N`. | PROPOSED | [citation-policy](../05-ai-rag/citation-policy.md); telaah Kompilasi Peraturan SUN |
| BR-42 | Pencabutan sebagian dicatat sebagai relasi `REVOKES` dengan cakupan Pasal/ayat dan tidak menjadikan seluruh regulasi target `SUPERSEDED` atau dicabut. Ketentuan peralihan yang mempertahankan regulasi lama bukan pencabutan. Status akhir tetap OPEN QUESTION. | PROPOSED | Kompilasi Peraturan SUN, PMK 111/2024, Pasal 30 angka 2 sampai 4, hal. 47; PMK 168/2019, Pasal 28, hal. 154-155; OQ-29 |
| BR-43 | Judul dan nomor regulasi diambil dari kepala naskah. Bila berbeda dari indeks sumber, kedua nilai disimpan dan ditandai NEEDS LEGAL CONFIRMATION; nilai yang rusak oleh ekstraksi tidak diperbaiki diam-diam. | PROPOSED | Kompilasi Peraturan SUN, PMK 165/2022, judul, hal. 49 (berbeda dari indeks, hal. 2); OQ-27 |
| BR-44 | Rujukan tak bernomor dalam regulasi (mis. "peraturan menteri mengenai dealer utama SUN") tidak dipetakan otomatis ke regulasi bernomor. Pemetaan bersifat PROPOSED sampai divalidasi. | PROPOSED | Telaah relasi Kompilasi Peraturan SUN; OQ-30 |
| BR-45 | `effectiveDate` regulasi diturunkan dari tanggal pengundangan dengan tinjauan manusia. Tanggal yang tidak terbaca pada sumber dibiarkan kosong dengan penanda, bukan diisi dari dugaan. | PROPOSED | Kompilasi Peraturan SUN, UU 24/2002, Pasal 22, hal. 10; PMK 111/2024, hal. 48 (tanggal pengundangan tidak terbaca); OQ-28 |

## Open Questions Terkait

- OQ-05 Pemetaan klasifikasi ke skema resmi Kemenkeu (BR-21, BR-22).
- OQ-25 Pemetaan "ketua tim", "kasubdit PMP", "Kasi MP", dan "PIC" ke role sistem (BR-33, BR-34).
- OQ-21 Sumber data otoritatif "yield" dan "kepemilikan SBN" (BR-36).
- OQ-23 Persyaratan server khusus (BR-37).
- OQ-24 Pengakuan mentor atas jawaban knowledge owner (BR-33 sampai BR-39).
- OQ-12 Pemutus publikasi (BR-05, BR-06).
- OQ-13 Retensi (BR-14, BR-15).
- OQ-14 Berbagi lintas tim (BR-07).
- OQ-15 Ambang tenggat (BR-13).
- OQ-26 Status berlaku terkini regulasi (BR-40).
- OQ-27 Sumber acuan judul dan nomor regulasi (BR-43).
- OQ-28 Tanggal pengundangan PMK 111/2024 (BR-45).
- OQ-29 Tampilan pencabutan sebagian dan ketentuan peralihan (BR-42).
- OQ-30 Pemetaan rujukan tak bernomor (BR-44).

## Related Documents

- [knowledge-lifecycle](knowledge-lifecycle.md)
- [document-lifecycle](document-lifecycle.md)
- [work-monitoring-flow](work-monitoring-flow.md)
- [authorization-rbac](../06-security/authorization-rbac.md)
- [citation-policy](../05-ai-rag/citation-policy.md)
- [decision-log](../12-governance/decision-log.md)
