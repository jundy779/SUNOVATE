# Kebutuhan Fungsional

**Status:** PROPOSED
**Last Updated:** 2026-10-06

## Purpose

Dokumen ini mendefinisikan kebutuhan fungsional SUNOVATE dengan ID `FR-xx`. Setiap kebutuhan memiliki prioritas (P0/P1/P2 menurut Proposal v2.4, slide 11), label bukti, dan user story terkait dari [user-stories.md](user-stories.md). Kolom "Scaffold" menyatakan apakah kebutuhan sudah memiliki implementasi awal (Ya, Sebagian, Belum, atau Belum sesuai bila implementasi ada tetapi berbeda dari kebutuhan). Nilai kolom ini diperiksa ulang terhadap `apps/api/sunovate_api` dan `apps/api/tests` pada 2026-10-06, termasuk backend `DATA_BACKEND=postgres` (ADR-015).

Kata "harus" berarti wajib untuk prioritas tersebut. Semua endpoint berprefiks `/api/v1`.

## 1. Autentikasi Pengembangan

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-01 | Sistem harus menerbitkan token pengembangan bertanda tangan HMAC melalui `POST /auth/dev/login` hanya untuk pengguna simulasi yang di-seed. | P0 | PROPOSED (ADR-005) | US-01 | Ya |
| FR-02 | Endpoint dev login harus mengembalikan 404 `DEV_AUTH_DISABLED` bila dev auth nonaktif, dan aplikasi harus menolak start bila `APP_ENV=production` dengan dev auth aktif. | P0 | PROPOSED (ADR-005) | US-01 | Ya |
| FR-03 | `GET /auth/me` harus mengembalikan principal: pengguna, tim, peran, izin, dan clearance. | P0 | PROPOSED | US-02 | Ya |
| FR-04 | Mekanisme login produksi menggantikan dev auth melalui `IdentityProvider`. | P2 | OPEN QUESTION (OQ-07) | US-01 | Belum |

## 2. Otorisasi (RBAC, Team Scope, Klasifikasi)

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-05 | Setiap endpoint terproteksi harus memeriksa permission, team scope, dan klasifikasi data; deny by default. | P0 | CONFIRMED prinsip (sumber: brief sesi 2026-10-01, ADR-006) | US-03 | Ya |
| FR-06 | Akses record mensyaratkan rank(clearance) >= rank(klasifikasi record). | P0 | PROPOSED | US-04 | Ya |
| FR-07 | Record yang tidak boleh dibaca harus menghasilkan 404, bukan 403. | P0 | PROPOSED | US-04 | Ya |
| FR-08 | Penolakan akses harus dicatat sebagai audit `ACCESS_DENIED`. | P0 | PROPOSED | US-26 | Ya |
| FR-09 | Matriks izin delapan peran pengembangan mengikuti [permission-matrix.md](../06-security/permission-matrix.md). Isi matriks untuk hak ubah/unggah belum selaras dengan jawaban knowledge owner (lihat FR-50). | P0 | PROPOSED | US-27 | Ya (matriks saat ini); Belum sesuai untuk hak ubah/unggah `staff` |

## 3. Knowledge dan Lifecycle

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-10 | Pengguna dengan `knowledge:create` harus dapat membuat knowledge entry berstatus DRAFT dengan tipe dari daftar 14 tipe knowledge. Himpunan pemegang `knowledge:create` tunduk pada FR-50. | P0 | PROPOSED | US-05, US-35 | Ya |
| FR-11 | Pembaruan knowledge harus menyertakan `revision`; revision basi menghasilkan 409 `REVISION_CONFLICT`. | P0 | PROPOSED (ADR-011) | US-06 | Ya |
| FR-12 | Lifecycle: DRAFT ke IN_REVIEW ke PUBLISHED ke SUPERSEDED/ARCHIVED; IN_REVIEW kembali ke DRAFT bila perubahan diminta. | P0 | PROPOSED | US-07 | **Sebagian**: DRAFT, pengajuan, pemeriksaan, pengembalian ke DRAFT, dan PUBLISHED tersedia pada API serta halaman detail; SUPERSEDED/ARCHIVED belum memiliki alur pengguna |
| FR-13 | Publikasi hanya melalui approval request `KNOWLEDGE_PUBLICATION` yang disetujui; pengaju tidak boleh memutuskan permintaannya sendiri. | P0 | PROPOSED | US-08 | **Ya**: backend menegakkan pemisahan kewenangan; halaman detail hanya menampilkan keputusan kepada pemeriksa lain dan tombol terbit kepada pemilik `knowledge:publish` |
| FR-14 | Hanya knowledge PUBLISHED yang masuk pencarian default dan retrieval Hermes. | P0 | PROPOSED | US-12, US-15 | Ya |
| FR-15 | `sharing_scope` TEAM membatasi ke tim pemilik; DIRECTORATE membuka ke semua tim hanya bila PUBLISHED. | P0 | PROPOSED; kebijakan OQ-14 | US-04 | Ya |
| FR-16 | Relasi antarperaturan AMENDS, REVOKES, IMPLEMENTS, REFERENCES, SUPERSEDES dapat dicatat dan ditampilkan. | P1 | PROPOSED | US-10 | Sebagian (tabel ada, endpoint belum) |
| FR-17 | Template knowledge capture SME, Close Out Note, dan playbook. | P1 | NEEDS MENTOR VALIDATION | US-11 | Belum |

## 4. Referensi Dokumen dan Versi

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-18 | Sistem harus menyimpan referensi dokumen beserta metadata, klasifikasi, lokasi provider, dan versi; file tidak disimpan sebagai BLOB. | P0 | CONFIRMED (sumber: brief sesi 2026-10-01, ADR-003) | US-09 | Ya |
| FR-19 | Registrasi versi harus menyimpan checksum SHA-256; pasangan (document_reference_id, checksum_sha256) ganda ditolak dengan 409 `DUPLICATE_CHECKSUM`. | P0 | PROPOSED | US-09 | Ya |
| FR-20 | Status ekstraksi: PENDING, EXTRACTED, FAILED, QUARANTINED, NOT_APPLICABLE. | P0 | PROPOSED | US-09 | Sebagian |
| FR-21 | Registrasi versi dicatat sebagai audit `VERSION_REGISTER`. | P0 | PROPOSED | US-26 | Ya |

## 5. Pencarian

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-22 | `GET /search?q=` harus mengembalikan hanya konten yang boleh dibaca pengguna, dengan filter otorisasi diterapkan sebelum penilaian relevansi. | P0 | PROPOSED | US-12 | Ya; ID terotorisasi membatasi query FTS PostgreSQL dan pemeriksaan Python tetap final |
| FR-23 | Pencarian teks berbasis PostgreSQL FTS memakai `search_vector` dan indeks GIN untuk pengetahuan terbit serta draf terotorisasi. | P0 | PROPOSED (ADR-003, ADR-015) | US-12 | Ya untuk endpoint pencarian; retrieval SAVI belum memakai FTS |
| FR-24 | Pencarian semantik berbasis pgvector setelah model embedding disetujui. | P0 | OPEN QUESTION (OQ-11) | US-14 | Belum |

## 6. Hermes

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-25 | Hermes hanya diakses melalui HermesGateway; runtime Hermes tidak memiliki kredensial database. | P0 | CONFIRMED (sumber: brief sesi 2026-10-01, ADR-004) | US-15 | Ya |
| FR-26 | ScopeGuard harus mengklasifikasi pertanyaan: domain SUN, coding umum, jailbreak/policy override, dan niat tulis. | P0 | PROPOSED | US-17 | Ya |
| FR-27 | Query mensyaratkan `hermes:query` dan `search:query`. | P0 | PROPOSED | US-15 | Ya |
| FR-28 | Retrieval hanya chunk dari konten PUBLISHED yang boleh dibaca, tidak melebihi `HERMES_MAX_CLASSIFICATION`. | P0 | PROPOSED | US-15 | Ya |
| FR-29 | Chunk berisi teks menyerupai instruksi harus dikeluarkan oleh filter prompt injection. | P0 | PROPOSED | US-17 | Ya |
| FR-30 | CitationValidator: setiap penanda [n] harus menunjuk chunk terotorisasi yang diambil, minimal satu sitasi untuk `ANSWERED`. | P0 | PROPOSED | US-15 | Ya |
| FR-31 | OutputGuard harus memblokir pola rahasia/sensitif dan pelanggaran plafon klasifikasi (`BLOCKED_BY_OUTPUT_GUARD`). | P0 | PROPOSED | US-17 | Ya |
| FR-32 | Niat tulis menghasilkan `REQUIRES_HUMAN_APPROVAL` dan approval request `HERMES_WRITE_ACTION` berstatus PENDING, tanpa eksekusi. | P0 | PROPOSED | US-18 | Ya |
| FR-33 | Setiap query dan umpan balik dicatat sebagai audit `AI_QUERY` dan `AI_FEEDBACK`. | P0 | PROPOSED | US-19 | Ya |
| FR-34 | Provider AI generatif menggantikan `development_extractive` setelah model disetujui. | P1 | OPEN QUESTION (OQ-11) | US-15 | Belum |

## 7. Monitoring Kerja

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-35 | Daftar dan detail work output, tugas, milestone dibatasi team scope. | P0 | PROPOSED | US-20 | Ya |
| FR-36 | Pembaruan tugas memakai kontrol revision; status tugas: NOT_STARTED, IN_PROGRESS, WAITING_INTERNAL, WAITING_EXTERNAL, ON_HOLD, COMPLETED, CANCELLED. | P0 | PROPOSED | US-21 | Ya |
| FR-37 | Daftar pending matters dan follow-up. | P0 | PROPOSED | US-22 | Ya (baca) |
| FR-38 | Status tenggat SAFE, DUE_SOON, DUE_TODAY, OVERDUE, COMPLETED hanya dihitung backend dengan `DEADLINE_DUE_SOON_DAYS` (default 7). | P0 | PROPOSED; ambang OQ-15 | US-23 | Ya |
| FR-39 | Pembuatan work output dan tugas melalui UI dan API. Apakah "mengubah data" pada jawaban knowledge owner (OQ-05) mencakup data kerja ini adalah OPEN QUESTION (OQ-25); role `staff` saat ini memiliki `work:create` dan `work:update`. | P0 | PROPOSED | US-20 | Belum |

## 8. Dashboard

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-40 | `GET /dashboard/summary` hanya mengagregasi record yang boleh dibaca. | P0 | PROPOSED | US-24 | Ya |
| FR-41 | Reporting dan ekspor. | P1 | OPEN QUESTION (OQ-10 PARTIAL: dua indikator diminta, format laporan belum; lihat FR-54) | US-25 | Belum |

## 9. Audit dan Approval

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-42 | Audit log append-only; UPDATE dan DELETE ditolak trigger PostgreSQL. | P0 | PROPOSED (ADR-010) | US-26 | Ya (skema dan backend `postgres`); `TRUNCATE` tidak dicegah (KL-21) |
| FR-43 | `GET /audit-logs` memerlukan `audit:read`. | P0 | PROPOSED | US-26 | Ya |
| FR-44 | Approval request bertipe KNOWLEDGE_PUBLICATION, HERMES_WRITE_ACTION, DOCUMENT_VERSION, ACCESS_EXCEPTION dengan status PENDING, APPROVED, REJECTED, CANCELLED, EXPIRED. | P0 | PROPOSED | US-08, US-18 | Ya |
| FR-45 | Keputusan approval mensyaratkan `approval:decide` dan dicatat sebagai APPROVE atau REJECT. | P0 | PROPOSED | US-08 | Ya |

## 10. Notifikasi, Document Automation, Integrasi

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-46 | Notifikasi dalam aplikasi untuk review dan tenggat; `NOTIFICATION_PROVIDER=disabled` untuk kanal eksternal. | P1 | PROPOSED | US-30 | Belum (tabel ada) |
| FR-47 | Document automation dari template yang disetujui; hasil berstatus draf dan masuk review. | P1 | PROPOSED; template OQ-16 | US-31, US-32 | Belum |
| FR-48 | Integrasi SharePoint, SSO, Power BI, Telegram, WhatsApp, data pasar resmi, Kemenkeu Satu hanya melalui provider dan setelah validasi. Jawaban knowledge owner "bisa" untuk Telegram/WhatsApp (OQ-08) dan "Sandbox server" untuk peran SharePoint (OQ-06, OQ-22) tidak mengubah prioritas; lihat FR-55. | P2 | OUT OF SCOPE MVP | US-33, US-34 | Belum (placeholder nonaktif) |
| FR-49 | `GET /providers` menampilkan status provider dan `GET /data-quality-issues` menampilkan isu kualitas data. | P0 | PROPOSED | US-28, US-29 | Ya |

## 11. Kebutuhan dari Jawaban Knowledge Owner (deck v1_ slide 24)

Bagian ini menambahkan FR-50 sampai FR-55 dari jawaban knowledge owner pada deck `v1_SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx`. Pemisahan label:

- **CONFIRMED (knowledge owner, deck v1_ slide 24)**: isi jawaban. Pengakuan mentor masih tertunda (OQ-24).
- **PROPOSED**: kebutuhan yang diturunkan pengembang dari jawaban, termasuk pemetaan ke role sistem (OQ-25).
- **OPEN QUESTION**: bagian yang tidak dijawab.

Slide 11 (prioritas P0/P1/P2), 12 (alur dokumen), 15 (model data), dan 20 (bug dan pengujian) tidak berubah pada deck `v1_` (lihat [references/README.md](../../references/README.md)). Karena itu prioritas P0/P1/P2 tidak digeser oleh jawaban ini; dampaknya hanya pada siapa yang bertindak, batas data, dan indikator dashboard.

| ID | Kebutuhan | Prioritas | Label | Story | Scaffold |
|---|---|---|---|---|---|
| FR-50 | Hak mengubah dan mengunggah data (membuat, mengubah, dan mengajukan knowledge; mendaftarkan referensi dan versi dokumen) hanya dimiliki ketua tim, kasubdit PMP, Kasi MP, dan PIC yang ditunjuk. Role lain, termasuk `staff`, ditolak dengan 403 `PERMISSION_DENIED` dan tercatat sebagai `ACCESS_DENIED`. Tetap berlaku bersama team scope dan klasifikasi. | P0 | Siapa yang berwenang: CONFIRMED (knowledge owner, deck v1_ slide 24, OQ-05). Pemetaan ke role (`team_lead` = ketua tim, `knowledge_owner` = PIC, `knowledge_coordinator` = tingkat PMP) dan penegakannya: PROPOSED (OQ-25, PD-1). Apakah staf biasa boleh menyusun draf tanpa hak unggah: OPEN QUESTION (OQ-25) | US-35 | **Belum sesuai**: `staff` masih memiliki `knowledge:create`, `knowledge:update`, `knowledge:submit`, dan `document:create` (`authz/catalog.py`, himpunan `_AUTHOR`). Belum ada endpoint yang memakai `document:create`, dan `staff` tidak memiliki `document:version`, sehingga tidak ada jalur registrasi versi dokumen bagi `staff`; jalur knowledge terbuka (lihat AC-17 di [acceptance-criteria.md](acceptance-criteria.md)) |
| FR-51 | Setiap tim memiliki ketua tim dan PIC yang ditunjuk sebagai knowledge owner dan reviewer. Penunjukan dicatat (siapa, untuk tim mana, sejak kapan, ditetapkan oleh siapa) dan berlaku hanya untuk tim tersebut. | P0 | Peran knowledge owner dan reviewer: CONFIRMED (knowledge owner, deck v1_ slide 24, OQ-09). Penunjukan orang tidak dicatat (OPEN QUESTION). Mekanisme pencatatan: PROPOSED (opsi di [logical-data-model.md](../04-data/logical-data-model.md)) | US-36 | **Sebagian**: setiap record governed memiliki `owner_user_id` dan `owner_team_id`, dan kolom `user_roles.team_id` ada, tetapi resolusi permission menggabungkan semua `user_roles` pengguna tanpa memeriksa `team_id` (role berlaku global). Tidak ada entitas penunjukan ketua tim atau PIC per tim |
| FR-52 | Pilot mencakup enam tim. Data pilot terisolasi per tim melalui team scope; tim di luar enam tim tidak dibuat sampai nama resmi dan tim tambahan dikonfirmasi. | P0 | "6 tim": CONFIRMED (knowledge owner, deck v1_ slide 24, OQ-03). Bahwa yang dimaksud adalah PPSUN, AKPSUN, PSUN, PPPSUN, DHTV, SUN Tematik: PROPOSED (OQ-02). Proses pilot dan perilaku SUN Tematik: OPEN QUESTION (OQ-03, OQ-01) | US-37 | **Ya** untuk enam tim `SIMULATED_DATA` (`GET /teams` mengembalikan enam kode dan isolasi tim diuji); SUN Tematik tanpa data atau perilaku |
| FR-53 | Dokumen yang boleh masuk repository dan RAG adalah "semua dokumen yang diusulkan tim kerja". Dokumen asli hanya boleh masuk setelah klasifikasi ditetapkan (OQ-05) dan persetujuan eksplisit ada; konten `CONFIDENTIAL` tidak diproses Hermes. Sampai itu, hanya `SIMULATED_DATA` yang dimuat. | P0 | Cakupan: CONFIRMED (knowledge owner, deck v1_ slide 24, OQ-04). Syarat klasifikasi dan persetujuan: PROPOSED (AGENTS.md, DEC-20261002-02). Skema klasifikasi resmi: OPEN QUESTION (OQ-05) | US-38 | **Sebagian**: plafon clearance dan `HERMES_MAX_CLASSIFICATION` berjalan. Preview terstruktur dan penyimpanan draf hanya menerima judul `SIMULASI -`, membutuhkan gabungan permission, dan draf tidak masuk retrieval. Belum ada unggah, ekstraksi berkas, atau gerbang intake dokumen asli (KL-07); endpoint knowledge umum tetap dapat membuat `USER_ENTERED` |
| FR-54 | Indikator dashboard "yield" dan "kepemilikan SBN" ditampilkan sebagai "sumber data belum tersedia", tanpa angka, sampai sumber data otoritatif, definisi, dan hak lihat diketahui (OQ-21). Tidak ada tabel bisnis SUN (ADR-013). | P1 | Indikator diminta: CONFIRMED (knowledge owner, deck v1_ slide 24, OQ-10). Perilaku diblokir dan placeholder: PROPOSED (ADR-013, R-15). Sumber data dan definisi: OPEN QUESTION (OQ-21) | US-39 | **Belum**: `GET /dashboard/summary` dan UI tidak memuat kedua indikator (tidak ada angka); teks "sumber data belum tersedia" juga belum ada di UI |
| FR-55 | Kanal Telegram dan WhatsApp tetap P2: tidak diaktifkan dan tidak diklaim tersedia. Bila kelak dilanjutkan, otorisasi lewat HermesGateway yang sama dengan web dan konten `RESTRICTED` ke atas tidak dikirim ke kanal eksternal secara default. | P2 | "bisa" untuk penggunaan internal: CONFIRMED (knowledge owner, deck v1_ slide 24, OQ-08). Status P2, kajian keamanan, dan larangan default RESTRICTED ke atas: PROPOSED (PD-6, DEC-20261002-06) | US-33, US-34 | **Belum** (sesuai dengan P2): `NOTIFICATION_PROVIDER` hanya `disabled`; tidak ada kode kanal, token, atau webhook; `/providers` melaporkan integrasi produksi `DISABLED` |
| FR-56 | File hasil pekerjaan staf memiliki ruang DRAFT yang dapat diubah, diganti, atau dihapus secara lunak oleh pemilik yang berizin. Setelah diajukan dan diterbitkan, versi file dikunci: tidak dapat ditimpa atau dihapus permanen; koreksi dibuat sebagai versi baru, sedangkan penarikan/arsip memerlukan izin dan alasan yang diaudit. Pemberian izin per akun harus berbasis role, team scope, klasifikasi, masa berlaku, dan jejak audit. | P1 | PROPOSED oleh project lead 2026-10-10; kebijakan penerbit, penarik, retensi, dan delegasi izin adalah OPEN QUESTION (OQ-35) | US-41 (belum ditulis) | **Belum**: belum ada model file lampiran pekerjaan, penyimpanan objek, endpoint unggah, permission khusus, atau UI Draft Workspace |
| FR-57 | Draf knowledge dicari melalui ruang kerja terpisah dari pencarian umum. `knowledge_owner` hanya melihat draf yang dimilikinya; pemeriksa hanya melihat draf dalam lingkup tim dan klasifikasinya. Draf tidak pernah menjadi sumber SAVI sebelum diterbitkan. | P0 | PROPOSED sebagai penguatan BR-04 dan arahan project lead 2026-10-15 | US-12, US-38 | **Ya**: `/knowledge/drafts/search` memfilter otorisasi sebelum pencocokan judul, ringkasan, dan bagian; halaman `/knowledge/drafts` memakai bahasa kerja nonteknis; audit tidak menyimpan kata kunci |

Hosting pilot pada satu komputer khusus sebagai server (OQ-07, OQ-23) menghasilkan NFR-39 sampai NFR-44 di [non-functional-requirements.md](non-functional-requirements.md), bukan FR.

## Open Questions

OQ-04, OQ-05, OQ-07, OQ-10, OQ-11, OQ-12, OQ-14, OQ-15, OQ-16, OQ-21, OQ-23, OQ-24, OQ-25 di [open-questions.md](../00-project/open-questions.md).

## Related Documents

- [endpoint-catalog.md](../07-api/endpoint-catalog.md)
- [acceptance-criteria.md](acceptance-criteria.md)
- [mvp-scope.md](mvp-scope.md)

## Last Updated

2026-10-15
