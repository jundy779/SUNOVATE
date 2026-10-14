# Decision Log

**Status:** PROPOSED
**Last Updated:** 2026-10-14

## Purpose

Dokumen ini mencatat ringkasan keputusan proyek SUNOVATE beserta status dan dampaknya. Rincian konteks, alternatif, dan konsekuensi teknis ada di [architecture-decisions](../03-architecture/architecture-decisions.md). Jawaban mentor atas open question juga dicatat di sini agar dapat ditelusuri.

## Aturan Pencatatan

- ID tidak dipakai ulang. Keputusan yang diganti tetap tercatat dengan status "Digantikan oleh ...".
- CONFIRMED hanya bila didukung brief pengguna atau jawaban mentor bertanggal. Jawaban knowledge owner dicatat dengan label `CONFIRMED (knowledge owner, <sumber>)` dan dinyatakan belum diakui mentor sampai pengakuan tercatat (OQ-24).
- Setiap keputusan baru diikuti pembaruan dokumen terkait dan, bila material, `CHANGELOG.md` (lihat [change-management](change-management.md)).

## Keputusan

| ID | Tanggal | Keputusan | Alasan | Status | Dampak | Referensi |
|---|---|---|---|---|---|---|
| ADR-001 | 2026-10-01 | Arsitektur modular monolith | Sesuai brief; satu pengembang, enam bulan, tanpa kebutuhan layanan terpisah | CONFIRMED (brief sesi 2026-10-01) | Satu backend API dan satu frontend; modul dipisah di dalam kode | [container-architecture](../03-architecture/container-architecture.md) |
| ADR-002 | 2026-10-01 | FastAPI, SQLAlchemy, Alembic menggantikan NestJS/Prisma pada blueprint lama | Keputusan eksplisit pada brief | CONFIRMED (brief sesi 2026-10-01) | Blueprint v0.1 hanya konteks historis | [technology-stack](../03-architecture/technology-stack.md) |
| ADR-003 | 2026-10-01 | PostgreSQL sebagai penyimpan tunggal (relasional, FTS, pgvector); file tidak disimpan sebagai BLOB | Kesederhanaan; file tetap di sumber resmi | CONFIRMED (brief sesi 2026-10-01) | Hanya referensi, metadata, checksum SHA-256, versi, klasifikasi, lokasi provider | [data-architecture](../04-data/data-architecture.md) |
| ADR-004 | 2026-10-01 | Hermes di belakang HermesGateway; runtime hanya menerima konteks teratorisasi; tanpa kredensial DB | Mencegah kebocoran dan akses langsung | CONFIRMED (brief sesi 2026-10-01) | Semua akses Hermes melalui application service | [hermes-overview](../05-ai-rag/hermes-overview.md) |
| ADR-005 | 2026-10-01 | Token pengembangan bertanda tangan HMAC via `POST /api/v1/auth/dev/login` untuk pengguna SIMULATED; nonaktif di luar development | Mekanisme login resmi belum disetujui (OQ-07) | PROPOSED | Aplikasi menolak start bila `APP_ENV=production` dan dev auth aktif | [authentication](../06-security/authentication.md) |
| ADR-006 | 2026-10-01 | Otorisasi = permission AND lingkup tim AND klasifikasi, deny by default, di API | Kontrol akses tidak boleh bergantung pada frontend | CONFIRMED (prinsip, brief); PROPOSED (matriks) | Penyembunyian menu hanya kosmetik | [authorization-rbac](../06-security/authorization-rbac.md) |
| ADR-007 | 2026-10-01 | `DATA_BACKEND=simulated` untuk runtime scaffold; skema, migrasi, dan seed PostgreSQL sudah divalidasi | Mempercepat pengembangan fitur sebelum repository SQLAlchemy selesai | PROPOSED | Data tidak persisten; repository SQLAlchemy adalah langkah berikut (R-10) | [data-architecture](../04-data/data-architecture.md) |
| ADR-008 | 2026-10-01 | AI provider pengembangan deterministik dan ekstraktif; embedding nonaktif | Model AI dan embedding belum disetujui (OQ-11) | PROPOSED | Tanpa jaringan dan model eksternal; retrieval semantik ditunda | [provider-abstraction](../03-architecture/provider-abstraction.md) |
| ADR-009 | 2026-10-01 | `embedding_references` menyimpan `model_name` dan `dimensions`; kolom vektor tanpa tipe tetap dan tanpa indeks ANN | Dimensi bergantung model yang belum disetujui | PROPOSED | Indeks ANN ditambahkan melalui migrasi setelah model disetujui | [rag-architecture](../05-ai-rag/rag-architecture.md) |
| ADR-010 | 2026-10-01 | Soft delete (`deleted_at`) untuk record bisnis; `audit_logs` append-only dengan trigger penolak UPDATE/DELETE | Jejak audit dan pemulihan | PROPOSED | Retensi tetap OQ-13 | [audit-logging](../06-security/audit-logging.md) |
| ADR-011 | 2026-10-01 | Optimistic concurrency dengan `revision`; pembaruan basi menghasilkan 409 `REVISION_CONFLICT` | Mencegah konflik pembaruan diam-diam | PROPOSED | Klien wajib mengirim revision | [api-conventions](../07-api/api-conventions.md) |
| ADR-012 | 2026-10-01 | `docs/` lama diarsipkan ke `docs/_archive/legacy-docs-v0/`, tidak dihapus | Menjaga jejak historis | PROPOSED | Dokumen baru menggantikan struktur lama | [README](../README.md) |
| ADR-013 | 2026-10-01 | Tabel SUN Business yang belum tervalidasi (instrumen, lelang, transaksi, yield, setelmen) dihapus dari skema | Menghindari model domain tanpa validasi dan data sensitif | PROPOSED | SUN Business tetap OPEN QUESTION untuk fase lanjut | [sun-domain-overview](../02-business/sun-domain-overview.md) |
| ADR-014 | 2026-10-01 | File sumber biner (PDF/PPTX) di root dikecualikan dari Git melalui `.gitignore` | Klasifikasi penyimpanan di repository belum dikonfirmasi (OQ-18) | PROPOSED | File sumber tetap lokal | [simulated-data-policy](../04-data/simulated-data-policy.md) |
| ADR-015 | 2026-10-02 | Backend kedua `DATA_BACKEND=postgres` di belakang interface `Repository` sinkron per request (SQLAlchemy sinkron + `psycopg[binary]==3.3.6`); `simulated` tetap default; revisi `0002_ordering_columns` | Data runtime hilang saat restart (R-10, KL-01); handler tetap `def` sehingga driver sinkron menghindari migrasi async seluruh jalur request | PROPOSED | Data bertahan setelah restart pada mode postgres; satu dependency baru; `pnpm db:test` menjalankan seluruh suite pada PostgreSQL sementara; melanjutkan ADR-007 | [architecture-decisions](../03-architecture/architecture-decisions.md), [data-architecture](../04-data/data-architecture.md) |
| ADR-016 | 2026-10-09 | Baseline demo sekitar 25 pengguna pada satu komputer kantor; Docker Compose + Nginx; Cloudflare Tunnel/Access sebagai opsi akses; Go/Rust/mobile ditunda | Menyediakan demo realistis tanpa menyamakan komputer kantor dengan produksi atau menambah stack sebelum kebutuhan terbukti | PROPOSED (project lead); NEEDS APPROVAL mentor dan TIK/keamanan | Hanya `SIMULATED_DATA`; wajib load/security/backup test; produksi menunggu keputusan instansi | [deployment-architecture](../03-architecture/deployment-architecture.md), [task-tracker](../13-handover/task-tracker.md) |

### DEC-20261009-01

- **Sumber:** Arahan project lead, sesi 2026-10-09.
- **Keputusan kerja:** Siapkan rancangan demo sekitar 25 pengguna pada komputer kantor khusus. Cloudflare Tunnel dan Access dipertimbangkan sebagai jalur akses terbatas.
- **Status:** PROPOSED; belum merupakan persetujuan deployment.
- **Gate:** Persetujuan mentor dan TIK/keamanan, OQ-20/OQ-23/OQ-34, `SIMULATED_DATA`, backup/restore drill, load test, dan security checklist.

### DEC-20261009-02

- **Sumber:** Arahan project lead, sesi 2026-10-09.
- **Keputusan kerja:** Python/FastAPI tetap backend inti. Go, Rust, dan klien mobile masuk roadmap pasca-MVP dan hanya dipilih dari kebutuhan terukur.
- **Status:** PROPOSED.
- **Dampak:** Tidak ada service atau dependency baru pada MVP saat ini.

### DEC-20261014-01

- **Open question:** OQ-37 tata kelola glosarium SAVI.
- **Tanggal jawaban:** 2026-10-14.
- **Sumber:** Jawaban ketua proyek pada sesi 2026-10-14; belum dinyatakan sebagai jawaban mentor.
- **Jawaban:** SUN berarti Surat Utang Negara; admin mengesahkan/memperbaiki dan menjadi tujuan pemeriksaan; sumber berupa peraturan SUN serta playbook transaksi SUN; semua pegawai boleh melihat glosarium; istilah lama tidak disimpan sebagai riwayat aktif; review setiap tiga bulan; singkatan tanpa dokumen resmi tidak boleh digunakan.
- **Keputusan:** Terapkan kebijakan konservatif pada dokumentasi. SUN dapat diperlakukan sebagai kepanjangan resmi. Kandidat lain tetap diblokir. Riwayat tampilan boleh tidak aktif, tetapi audit perubahan tidak dihapus.
- **Status:** PARTIAL, NEEDS MENTOR VALIDATION.
- **Dampak:** OQ-37 menjadi PARTIAL; tidak ada permission admin, ekspansi retrieval, tiket, notifikasi, atau perubahan kandidat runtime.
- **Tindak lanjut:** Tetapkan role admin, sumber per entri, daftar pemetaan yang disahkan, klasifikasi, tanggal review pertama, dan mekanisme pencabutan.

## Jawaban Mentor atas Open Question

Belum ada jawaban mentor yang tercatat per 2026-10-02. Yang tercatat adalah jawaban knowledge owner pada deck proposal versi tetap `v1_` slide 24 (bagian "Jawaban knowledge owner, deck v1_ slide 24" di bawah); pengakuan mentor atas jawaban tersebut masih tertunda (OQ-24). Setiap jawaban dicatat dengan templat berikut, lalu OQ terkait di [open-questions](../00-project/open-questions.md) diperbarui statusnya.

```markdown
### DEC-YYYYMMDD-NN

- **Open question:** OQ-xx <ringkasan pertanyaan>
- **Tanggal jawaban:** YYYY-MM-DD
- **Sumber:** <rapat/catatan/arahan tertulis, tanpa data pribadi>
- **Jawaban:** <ringkasan jawaban mentor>
- **Keputusan:** <apa yang diputuskan untuk SUNOVATE>
- **Status:** CONFIRMED | NEEDS MENTOR VALIDATION (bila jawaban belum final)
- **Dampak:** <dokumen, skema, permission, atau kode yang berubah>
- **ADR/BR terkait:** <ADR-xxx, BR-xx, R-xx>
- **Tindak lanjut:** <tugas dan pemilik>
```

Ketentuan:

- Satu entri per open question; bila jawaban berubah, buat entri baru yang merujuk entri sebelumnya.
- Tidak mencatat nama pribadi, nomor surat tugas, atau data sensitif. Sebut peran secara umum (misalnya "mentor").
- Jawaban yang mengubah arsitektur juga dibuatkan ADR baru.

## Jawaban knowledge owner, deck v1_ slide 24

Entri berikut mencatat jawaban knowledge owner atas delapan pertanyaan slide 24 deck `v1_SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx`, yang dikonfirmasi pengguna sebagai versi tetap deck proposal. Judul slide berubah dari "konfirmasi mentor" menjadi "konfirmasi knowledge owner". Deck tidak mencantumkan tanggal jawaban; tanggal pencatatan adalah 2026-10-02. Kutipan jawaban ditulis dengan ejaan dinormalisasi. Entri ini tidak masuk tabel ADR agar tidak bentrok dengan penambahan ADR pada cabang lain. Bagian yang diturunkan pengembang (tafsiran, pemetaan role, konsekuensi) berlabel PROPOSED.

### DEC-20261002-01

- **Open question:** OQ-03 Tim kerja dan proses mana yang menjadi pilot pertama? (OQ-02 terkait)
- **Tanggal jawaban:** tidak tercantum di deck; dicatat 2026-10-02
- **Sumber:** deck v1_ slide 24 (jawaban knowledge owner)
- **Jawaban:** "6 tim"
- **Keputusan:** CONFIRMED (knowledge owner): pilot mencakup 6 tim. PROPOSED: yang dimaksud adalah enam tim pada brief sesi (PPSUN, AKPSUN, PSUN, PPPSUN, DHTV, SUN Tematik). Bagian "proses" tidak dijawab. Nama resmi tim dan tim tambahan pada Pengayaan 6 Mei 2026 (OQ-02) tetap terbuka.
- **Status:** CONFIRMED (knowledge owner, deck v1_ slide 24) untuk "6 tim"; NEEDS MENTOR VALIDATION untuk sisanya. OQ-03 ANSWERED (knowledge owner); OQ-02 PARTIAL.
- **Dampak:** [team-work-scope](../02-business/team-work-scope.md), [stakeholder-map](../00-project/stakeholder-map.md), [assumptions](../00-project/assumptions.md) (A-02)
- **ADR/BR terkait:** R-12, R-16
- **Tindak lanjut:** Konfirmasi nama resmi dan tim tambahan (OQ-02); proses pilot; pengakuan mentor (OQ-24).

### DEC-20261002-02

- **Open question:** OQ-04 Dokumen apa yang boleh masuk repository dan RAG?
- **Tanggal jawaban:** tidak tercantum di deck; dicatat 2026-10-02
- **Sumber:** deck v1_ slide 24 (jawaban knowledge owner)
- **Jawaban:** "Semua dokumen yang diusulkan tim kerja"
- **Keputusan:** CONFIRMED (knowledge owner): cakupan ditentukan oleh usulan tim kerja. PROPOSED: setiap dokumen asli tetap memerlukan klasifikasi (OQ-05) dan persetujuan eksplisit sebelum masuk, sesuai AGENTS.md; CONFIDENTIAL tetap dikecualikan dari Hermes; semua data pengembangan tetap `SIMULATED_DATA`.
- **Status:** CONFIRMED (knowledge owner, deck v1_ slide 24) untuk cakupan; NEEDS MENTOR VALIDATION untuk syarat masuk. OQ-04 PARTIAL.
- **Dampak:** [ingestion-pipeline](../05-ai-rag/ingestion-pipeline.md), [document-lifecycle](../02-business/document-lifecycle.md), [risk-register](risk-register.md) (R-14)
- **ADR/BR terkait:** ADR-014, R-03, R-14
- **Tindak lanjut:** Tetapkan skema klasifikasi (OQ-05) dan prosedur persetujuan per dokumen; pengakuan mentor (OQ-24).

### DEC-20261002-03

- **Open question:** OQ-05 Bagaimana klasifikasi serta hak akses setiap jenis dokumen?
- **Tanggal jawaban:** tidak tercantum di deck; dicatat 2026-10-02
- **Sumber:** deck v1_ slide 24 (jawaban knowledge owner)
- **Jawaban:** Yang dapat mengubah data atau mengunggah: ketua tim, kasubdit PMP, Kasi MP, dan PIC yang ditunjuk
- **Keputusan:** CONFIRMED (knowledge owner): hak mengubah/mengunggah terbatas pada keempat sebutan tersebut. Jawaban ini tidak mendefinisikan skema klasifikasi maupun hak baca. PROPOSED: `team_lead` = ketua tim; `knowledge_owner` = PIC; `knowledge_coordinator` = peran tingkat PMP; cabut `knowledge:create`, `knowledge:update`, `knowledge:submit`, dan `document:create` dari `staff`.
- **Status:** CONFIRMED (knowledge owner, deck v1_ slide 24) untuk siapa yang boleh mengubah/mengunggah; NEEDS MENTOR VALIDATION untuk pemetaan role. OQ-05 PARTIAL. Perubahan izin belum diimplementasikan.
- **Dampak:** [permission-matrix](../06-security/permission-matrix.md), [authorization-rbac](../06-security/authorization-rbac.md), [document-ownership](document-ownership.md), [future-development](../13-handover/future-development.md) (PD-1)
- **ADR/BR terkait:** ADR-006, R-09, R-17
- **Tindak lanjut:** Konfirmasi role dan kepanjangan PMP (OQ-25); skema klasifikasi dan pemetaan ke skema resmi (OQ-05); perubahan kode pada cabang terpisah.

### DEC-20261002-04

- **Open question:** OQ-06 Apakah SharePoint menjadi sumber utama atau hanya referensi?
- **Tanggal jawaban:** tidak tercantum di deck; dicatat 2026-10-02
- **Sumber:** deck v1_ slide 24 (jawaban knowledge owner)
- **Jawaban:** "Sandbox server"
- **Keputusan:** CONFIRMED (knowledge owner): jawaban tercatat apa adanya. Maknanya ambigu: tampaknya sumber file untuk pilot adalah sandbox server, tetapi tidak jelas apakah SharePoint dipakai sama sekali. Tidak ada keputusan desain yang diambil.
- **Status:** PARTIAL. OQ-06 PARTIAL; klarifikasi di OQ-22.
- **Dampak:** [sharepoint-proposal](../08-integrations/sharepoint-proposal.md), [integration-boundaries](../03-architecture/integration-boundaries.md)
- **ADR/BR terkait:** ADR-003, R-05
- **Tindak lanjut:** Klarifikasi "Sandbox server" (OQ-22).

### DEC-20261002-05

- **Open question:** OQ-07 Mekanisme login dan hosting apa yang disetujui?
- **Tanggal jawaban:** tidak tercantum di deck; dicatat 2026-10-02
- **Sumber:** deck v1_ slide 24 (jawaban knowledge owner)
- **Jawaban:** "Pakai computer tersendiri sebagai server"
- **Keputusan:** CONFIRMED (knowledge owner): hosting pilot memakai satu komputer khusus sebagai server. Mekanisme login tidak dijawab. PROPOSED: satu host untuk web, API, dan PostgreSQL dengan backup di luar host.
- **Status:** CONFIRMED (knowledge owner, deck v1_ slide 24) untuk hosting; login OPEN QUESTION. OQ-07 PARTIAL.
- **Dampak:** [deployment-architecture](../03-architecture/deployment-architecture.md), [deployment-runbook](../11-operations/deployment-runbook.md), [backup-and-restore](../11-operations/backup-and-restore.md), [identity-provider-proposal](../08-integrations/identity-provider-proposal.md)
- **ADR/BR terkait:** ADR-005, R-13
- **Tindak lanjut:** Persyaratan server dan mekanisme login (OQ-23, OQ-07).

### DEC-20261002-06

- **Open question:** OQ-08 Apakah Telegram dan WhatsApp diizinkan untuk penggunaan internal?
- **Tanggal jawaban:** tidak tercantum di deck; dicatat 2026-10-02
- **Sumber:** deck v1_ slide 24 (jawaban knowledge owner)
- **Jawaban:** "bisa"
- **Keputusan:** CONFIRMED (knowledge owner): penggunaan internal dapat. PROPOSED: tetap P2; kajian keamanan dan kebijakan organisasi diperlukan; RESTRICTED dan CONFIDENTIAL tidak dikirim ke kanal eksternal secara default; tidak ada integrasi yang diaktifkan atau diklaim tersedia.
- **Status:** CONFIRMED (knowledge owner, deck v1_ slide 24). OQ-08 ANSWERED (knowledge owner).
- **Dampak:** [telegram-proposal](../08-integrations/telegram-proposal.md), [whatsapp-proposal](../08-integrations/whatsapp-proposal.md), [webhook-policy](../07-api/webhook-policy.md)
- **ADR/BR terkait:** R-02, R-05
- **Tindak lanjut:** Pengakuan mentor (OQ-24); pekerjaan kanal tidak dimulai sebelum P1 notifikasi dalam aplikasi.

### DEC-20261002-07

- **Open question:** OQ-09 Siapa knowledge owner dan reviewer pada masing-masing tim?
- **Tanggal jawaban:** tidak tercantum di deck; dicatat 2026-10-02
- **Sumber:** deck v1_ slide 24 (jawaban knowledge owner)
- **Jawaban:** Masing-masing ketua tim dan PIC yang ditunjuk
- **Keputusan:** CONFIRMED (knowledge owner): knowledge owner dan reviewer per tim adalah ketua tim dan PIC yang ditunjuk. Nama orang tidak dicatat. PROPOSED: ketua tim = `team_lead`, PIC = `knowledge_owner`.
- **Status:** CONFIRMED (knowledge owner, deck v1_ slide 24) untuk peran; penunjukan orang dan pemetaan role OPEN QUESTION. OQ-09 ANSWERED (knowledge owner).
- **Dampak:** [document-ownership](document-ownership.md), [knowledge-governance](knowledge-governance.md), [user-personas](../01-product/user-personas.md), [stakeholder-map](../00-project/stakeholder-map.md)
- **ADR/BR terkait:** R-11, R-16
- **Tindak lanjut:** Pemetaan role (OQ-25); pengakuan mentor (OQ-24). Pemutus publikasi tetap OQ-12.

### DEC-20261002-08

- **Open question:** OQ-10 Format laporan dan indikator dashboard apa yang benar-benar dibutuhkan?
- **Tanggal jawaban:** tidak tercantum di deck; dicatat 2026-10-02
- **Sumber:** deck v1_ slide 24 (jawaban knowledge owner)
- **Jawaban:** "Yield, kepemilikan SBN"
- **Keputusan:** CONFIRMED (knowledge owner): dua indikator diminta. Tidak ada angka, definisi, sumber data, atau format laporan. PROPOSED: tidak ada angka ditampilkan dan tidak ada tabel bisnis SUN (ADR-013) sampai OQ-21 dijawab.
- **Status:** CONFIRMED (knowledge owner, deck v1_ slide 24) untuk indikator yang diminta; sisanya OPEN QUESTION. OQ-10 PARTIAL.
- **Dampak:** [dashboard-requirements](../09-ui-ux/dashboard-requirements.md)
- **ADR/BR terkait:** ADR-013, R-15
- **Tindak lanjut:** Sumber data dan definisi (OQ-21); format laporan.

### DEC-20261002-09

- **Open question:** OQ-24 Pengakuan mentor atas jawaban knowledge owner
- **Tanggal jawaban:** belum ada
- **Sumber:** perubahan judul slide 24 dari "konfirmasi mentor" menjadi "konfirmasi knowledge owner" (deck v1_)
- **Jawaban:** belum ada
- **Keputusan:** Jawaban DEC-20261002-01 sampai DEC-20261002-08 dipakai sebagai dasar kerja berlabel `CONFIRMED (knowledge owner, deck v1_ slide 24)`, bukan keputusan final proyek, sampai mentor mengakuinya.
- **Status:** NEEDS MENTOR VALIDATION. OQ-24 OPEN.
- **Dampak:** [open-questions](../00-project/open-questions.md), [assumptions](../00-project/assumptions.md) (A-18), [risk-register](risk-register.md) (R-16)
- **ADR/BR terkait:** R-16
- **Tindak lanjut:** Minta pengakuan pada sesi mentor berikutnya ([mentor-session-01-agenda](../00-project/mentor-session-01-agenda.md)).
## Related Documents

- [architecture-decisions](../03-architecture/architecture-decisions.md)
- [change-management](change-management.md)
- [risk-register](risk-register.md)
- [open-questions](../00-project/open-questions.md)
