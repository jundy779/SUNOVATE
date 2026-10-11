# Kriteria Penerimaan

**Status:** PROPOSED
**Last Updated:** 2026-10-11

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

## Skenario dari Jawaban Knowledge Owner (deck v1_ slide 24)

AC-16 sampai AC-25 diturunkan dari jawaban knowledge owner (**CONFIRMED (knowledge owner, deck v1_ slide 24)**; pengakuan mentor tertunda, OQ-24). Skenarionya **PROPOSED**. Setiap skenario diberi "Status terhadap kode saat ini" berdasarkan pembacaan `apps/api/sunovate_api` dan uji yang ada serta satu pengecekan manual pada 2026-10-06 dengan pengguna simulasi. Status "GAGAL" berarti skenario akan gagal bila dijalankan terhadap kode hari ini sampai PD-1 diterapkan; itu bukan klaim bahwa ada uji otomatis yang gagal. Belum ada uji otomatis untuk skenario yang ditandai "belum ada uji".

## AC-16 Pihak berwenang dapat membuat dan mengubah knowledge timnya

- **Given** `sim.owner.ppsun` (role `knowledge_owner`, representasi PIC, tim PPSUN), `sim.lead.psun` (role `team_lead`, representasi ketua tim, tim PSUN), atau `sim.coordinator` (role `knowledge_coordinator`, representasi tingkat PMP)
- **When** ia memanggil `POST /knowledge` untuk tim dalam scope-nya dengan klasifikasi tidak melebihi clearance, lalu `PATCH /knowledge/{id}` dengan `revision` benar
- **Then** API mengembalikan 201 dan 200, dan audit `CREATE` serta `UPDATE` tercatat.

Status terhadap kode saat ini: lulus (diuji di `apps/api/tests/test_knowledge_workflow.py`, mis. `test_create_update_and_revision_conflict`). Pemetaan role ke sebutan jabatan adalah PROPOSED (OQ-25). Terkait: FR-50, US-35.

## AC-17 Staff tidak dapat membuat, mengubah, atau mengajukan knowledge

- **Given** `sim.staff.pppsun` (role `staff`, tim PPPSUN, clearance INTERNAL) dan PD-1 sudah disetujui serta diterapkan
- **When** ia memanggil `POST /knowledge` (tim PPPSUN, klasifikasi INTERNAL), `PATCH /knowledge/{id}`, atau `POST /knowledge/{id}/submit`
- **Then** API mengembalikan 403 dengan `code` = `PERMISSION_DENIED`
- **And** entri audit `ACCESS_DENIED` tercatat dengan `requestId` yang sama
- **And** `GET /auth/me` untuk `staff` tidak memuat `knowledge:create`, `knowledge:update`, maupun `knowledge:submit`.

Status terhadap kode saat ini: **GAGAL**. Pengecekan manual 2026-10-06 menunjukkan `POST /knowledge` oleh `sim.staff.pppsun` mengembalikan 201, `PATCH` 200, dan `submit` 200, karena `staff` memiliki ketiga permission tersebut. Belum ada uji otomatis. Terkait: FR-50, US-35, PD-1, R-17.

## AC-18 Staff tidak dapat mendaftarkan dokumen atau versi

- **Given** `sim.staff.pppsun`
- **When** ia memanggil `POST /documents/{id}/versions` untuk dokumen timnya
- **Then** API mengembalikan 403 dengan `code` = `PERMISSION_DENIED` dan audit `ACCESS_DENIED` tercatat.

Status terhadap kode saat ini: lulus untuk `POST /documents/{id}/versions` (pengecekan manual 2026-10-06: 403; `staff` tidak memiliki `document:version`), belum ada uji otomatis. Pembuatan referensi dokumen (`document:create`, yang dimiliki `staff` pada matriks) tidak memiliki endpoint, sehingga bagian itu belum dapat diuji sampai endpoint dibuat; karena itu `document:create` untuk `staff` adalah celah matriks, bukan celah perilaku API saat ini. Terkait: FR-50, US-35.

## AC-19 Penunjukan ketua tim dan PIC berlaku hanya untuk timnya

- **Given** PIC yang ditunjuk untuk tim PPSUN (`sim.owner.ppsun`)
- **When** ia memanggil `POST /knowledge` dengan `ownerTeamId` tim PSUN
- **Then** API mengembalikan 403 dengan pesan di luar cakupan tim.
- **Given** penunjukan PIC untuk sebuah tim dicabut atau melewati masa berlaku (PROPOSED, memerlukan entitas penunjukan)
- **When** ia membuat atau mengubah knowledge tim tersebut
- **Then** API mengembalikan 403.

Status terhadap kode saat ini: bagian pertama lulus (`test_cannot_create_for_other_team_or_above_clearance` di `apps/api/tests/test_knowledge_workflow.py`). Bagian kedua belum dapat diuji: tidak ada entitas penunjukan, dan role diterapkan global karena `user_roles.team_id` tidak diperiksa saat resolusi permission (lihat [logical-data-model.md](../04-data/logical-data-model.md)). Terkait: FR-51, US-36.

## AC-20 Visibilitas pilot enam tim

- **Given** data pilot `SIMULATED_DATA` untuk enam tim
- **When** `sim.staff.pppsun` memanggil `GET /teams`
- **Then** respons berisi tepat enam kode: AKPSUN, DHTV, PPPSUN, PPSUN, PSUN, SUN_TEMATIK
- **And** `GET /knowledge`, `GET /search`, dan `GET /dashboard/summary` miliknya hanya memuat record PPPSUN dan konten `DIRECTORATE` yang `PUBLISHED`
- **And** tidak ada record kerja atau knowledge untuk SUN_TEMATIK (OQ-01).

Status terhadap kode saat ini: lulus untuk daftar tim dan isolasi tim (`test_teams_are_the_six_confirmed_codes`, `test_listing_respects_team_scope_and_sharing`, `test_cross_team_detail_returns_404_not_403`). Belum ada uji khusus bahwa SUN_TEMATIK tidak memiliki record. Nama resmi dan tim tambahan tetap OPEN QUESTION (OQ-02). Terkait: FR-52, US-37, AC-03.

## AC-21 Intake dokumen dibatasi klasifikasi dan persetujuan

- **Given** dokumen yang diusulkan tim kerja dan belum memiliki klasifikasi atau persetujuan eksplisit
- **When** dokumen itu diajukan masuk ke repository dan RAG
- **Then** dokumen ditahan dan tidak diindeks, tidak muncul di `GET /search`, dan tidak diambil Hermes
- **And** konten `CONFIDENTIAL` tidak pernah diambil Hermes, apa pun persetujuannya (lihat AC-05)
- **And** sebelum klasifikasi (OQ-05) dan persetujuan ada, hanya record `SIMULATED_DATA` yang ada di lingkungan.

Status terhadap kode saat ini: bagian `CONFIDENTIAL` lulus (AC-05; kasus golden set RAG-07). Gerbang intake belum ada: tidak ada pipeline ingestion atau unggah file (KL-07), sehingga bagian pertama belum ada uji. Terkait: FR-53, US-38, R-14.

## AC-22 Indikator yield dan kepemilikan SBN tanpa sumber data

- **Given** sumber data otoritatif belum ditetapkan (OQ-21)
- **When** pengguna membuka `/dashboard` dan memanggil `GET /dashboard/summary`
- **Then** respons tidak memuat angka atau field untuk yield atau kepemilikan SBN
- **And** halaman menampilkan "sumber data belum tersedia" untuk kedua indikator
- **And** tidak ada tabel bisnis SUN di skema (ADR-013).

Status terhadap kode saat ini: bagian respons API dan skema lulus secara struktural (pengecekan manual 2026-10-06: field respons hanya `attention`, `metrics`, `recentKnowledge`, `referenceDate`, `scope`, `tasksByStatus`; skema 30 tabel tanpa tabel yield), belum ada uji otomatis. Teks "sumber data belum tersedia" belum ada di UI, sehingga bagian itu belum sesuai. Terkait: FR-54, US-39, R-15.

## AC-23 Telegram dan WhatsApp tidak aktif

- **Given** konfigurasi default dan `NOTIFICATION_PROVIDER=disabled`
- **When** `sim.admin` memanggil `GET /providers`
- **Then** `meta.productionIntegrations` = `DISABLED` dan tidak ada provider kanal pesan berstatus aktif
- **And** tidak ada route webhook kanal (mis. `POST /webhooks/telegram` mengembalikan 404).

Status terhadap kode saat ini: lulus (`test_providers_report_no_production_integration`; route webhook dicek manual 2026-10-06: 404, belum ada uji otomatis). Jawaban "bisa" (OQ-08) tidak mengaktifkan apa pun. Terkait: FR-55, FR-48, US-33.

## AC-24 Latihan backup dan restore di server pilot

- **Given** server pilot dengan `DATA_BACKEND=postgres` dan hanya `SIMULATED_DATA`
- **When** administrator membuat backup ke lokasi di luar host, lalu memulihkannya ke database terpisah
- **Then** revision Alembic hasil restore sama dengan sumber (saat ini `0002_ordering_columns`), trigger append-only `audit_logs` masih menolak UPDATE, jumlah baris tabel utama sama, dan `GET /api/v1/health/database` sukses saat `DATABASE_URL` diarahkan ke database hasil restore
- **And** tanggal, ukuran, durasi, dan hasil latihan dicatat.

Status terhadap kode saat ini: prosedur ada sebagai usulan di [backup-and-restore.md](../11-operations/backup-and-restore.md); belum pernah dijalankan dan belum ada skrip. Server dan lokasi backup belum ditetapkan (OQ-23). Terkait: NFR-39, NFR-41, US-40, R-13.

## AC-25 Paparan server pilot diperiksa

- **Given** konfigurasi server pilot
- **When** pemeriksaan paparan dijalankan
- **Then** aplikasi menolak start bila `APP_ENV=production` dengan dev auth aktif atau `DATA_BACKEND=simulated`
- **And** `POST /auth/dev/login` mengembalikan 404 `DEV_AUTH_DISABLED` dari jaringan pengguna
- **And** hanya port web atau reverse proxy yang dapat dijangkau dari jaringan pengguna; port API dan PostgreSQL tidak
- **And** `CORS_ORIGINS` hanya berisi origin yang diperlukan dan secret berada di luar repository.

Status terhadap kode saat ini: dua bagian pertama lulus terhadap kode (`test_production_refuses_dev_auth_and_simulated_backend`, `test_production_refuses_simulated_backend`, `test_dev_auth_disabled_blocks_login_and_access`). Bagian jaringan, CORS, dan secret adalah pemeriksaan manual pada server yang belum ada. Catatan: `APP_ENV=production` mewajibkan dev auth nonaktif, sedangkan belum ada mekanisme login lain (OQ-07, PD-3), sehingga server pada mode production belum dapat dipakai login. Terkait: NFR-42, NFR-43, US-40.

## AC-26 Draft milik sendiri dapat diperbarui

- **Given** staf memiliki grant aktif untuk membuat dan memperbarui draft pada timnya
- **And** lampiran miliknya berstatus DRAFT dengan `revision` yang cocok
- **When** ia mengganti file dengan file valid
- **Then** versi draft baru tercatat, checksum dihitung server-side, dan audit `WORK_FILE_DRAFT_UPDATE` dibuat.

## AC-27 Draft lintas pemilik atau tim ditolak

- **Given** pengguna tidak memiliki kepemilikan atau team scope atas draft
- **When** ia membaca, mengganti, atau menghapus draft tersebut
- **Then** API mengembalikan 404 dan audit akses ditolak tercatat tanpa membocorkan keberadaan record.

## AC-28 Submit membekukan file

- **Given** DRAFT lolos validasi file, scan, klasifikasi, dan checksum
- **When** pemilik mengajukan
- **Then** status menjadi SUBMITTED dan approval dibuat
- **And** PATCH, DELETE, atau unggah versi pada record tersebut ditolak sampai dikembalikan ke DRAFT.

## AC-29 Versi terbit immutable

- **Given** lampiran berstatus PUBLISHED
- **When** pemilik, reviewer, atau system administrator mencoba menimpa file, mengubah metadata inti, atau hard delete
- **Then** API menolak operasi dan versi, checksum, provider locator, serta audit historis tidak berubah.

## AC-30 Koreksi menghasilkan versi baru

- **Given** lampiran PUBLISHED memerlukan koreksi
- **When** pengguna berizin memulai revisi
- **Then** sistem membuat DRAFT baru yang merujuk versi terbit sebelumnya
- **And** versi lama tetap PUBLISHED sampai versi pengganti disetujui
- **And** setelah pengganti terbit, versi lama menjadi SUPERSEDED tanpa dihapus.

## AC-31 Grant akses dibatasi dan diaudit

- **Given** pengelola akses yang disetujui mentor
- **When** ia memberi permission file kepada staf
- **Then** grant mencatat tim, classification ceiling, masa berlaku, pemberi, dan alasan
- **And** grant kedaluwarsa atau dicabut tidak lagi memberi akses
- **And** pengelola akses tidak otomatis mendapat hak mengubah file PUBLISHED.

Status AC-26 sampai AC-31: **PROPOSED, belum dapat diuji**. Model, endpoint, permission, storage provider, dan approval chain belum diimplementasikan; OQ-35 masih OPEN.

## Open Questions

- Kode error untuk pelanggaran separation of duties belum dikunci di dokumentasi API; perlu diselaraskan dengan [error-format.md](../07-api/error-format.md).
- OQ-12 dapat mengubah siapa yang berhak memutuskan pada AC-11.
- OQ-25 menentukan role yang menjadi pelaku pada AC-16 sampai AC-19 dan apakah staf biasa boleh menyusun draf; AC-17 berlaku hanya setelah PD-1 disetujui.
- OQ-21 menentukan kapan AC-22 dapat diganti dengan skenario angka.
- OQ-23 menentukan lingkungan untuk AC-24 dan AC-25.
- OQ-35 menentukan pelaku dan kebijakan final AC-26 sampai AC-31.

## Related Documents

- [functional-requirements.md](functional-requirements.md)
- [backend-testing.md](../10-testing/backend-testing.md)
- [security-testing.md](../10-testing/security-testing.md)
- [rag-testing.md](../10-testing/rag-testing.md)

## Last Updated

2026-10-11
