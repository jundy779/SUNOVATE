# AI Agent Handoff

**Status:** ACTIVE
**Last Updated:** 2026-10-20

## Baca Sebelum Bertindak

Urutan wajib: root `AGENTS.md`, [task-tracker.md](task-tracker.md), [developer-handover.md](developer-handover.md), [open-questions.md](../00-project/open-questions.md), lalu dokumen domain/arsitektur yang berkaitan dengan task.

## Snapshot Saat Ini

- SUNOVATE adalah modular monolith Next.js/TypeScript + FastAPI/Python + PostgreSQL/pgvector. Nama asisten pada frontend adalah **SAVI AI**; beberapa nama internal lama masih dapat memakai `HermesGateway` dan tidak boleh diganti massal tanpa migration plan.
- Build produksi frontend memakai `next build --webpack` karena cache persisten Turbopack dua kali
  rusak pada build berulang (BUG-021). Pengembangan tetap memakai `next dev`. Jangan mengembalikan
  build produksi ke Turbopack sebelum reproduksi cache dan stabilitas build berulang terverifikasi.
- **Aturan yang tidak boleh dinegosiasikan:** SUNOVATE privat. Jangan memublikasikan, mengindeks, atau mengirim data ke AI Search, SEO/GEO/AIO, crawler, scraper, model/agent eksternal, MCP, plugin, webhook, telemetry, atau kanal umum. Data asli tetap dilarang. Jangan melonggarkan lock konfigurasi, header anti-index/no-store, CSP, RBAC, batas klasifikasi, dan penolakan exfiltration/jailbreak. Lihat `private-data-boundary.md` dan ADR-018.
- Kontrol API ADR-019 menggunakan limiter memori satu proses, batas body 3 MiB, timeout penerimaan body, counter privat, serta trusted proxy CIDR fail-closed. Paket `deploy/demo/` memuat Nginx/Compose localhost-only, tetapi belum dibangun di Docker atau di host kantor. Jangan mengklaim distributed/production-ready atau kapasitas 25 pengguna dari baseline API-only lokal.
- BUG-022 sudah memperbaiki pembacaan lima pengaman boolean dari `.env` pada Pydantic 2.13. Field memakai `bool` agar teks environment dapat diparsing, lalu model validator menolak setiap nilai yang melonggarkan pengaman. Jangan mengembalikannya ke `Literal[True]`/`Literal[False]` tanpa uji `.env` aktual.
- `pnpm demo:preflight` wajib tetap fail-closed. Tanpa argumen alat memeriksa scaffold; dengan
  `--env-file` alat memeriksa secret, izin file, origin, dan URL database tanpa mencetak nilainya.
  Status `environmentFile: NOT_CHECKED` bukan persetujuan deploy. Access log Nginx dilarang
  memakai `$request`, `$request_uri`, `$args`, atau `$query_string` karena dapat merekam istilah
  pencarian. Preflight tidak menjalankan container dan tidak mengaktifkan tunnel.
- Semua demo memakai `SIMULATED_DATA`. Tidak ada integrasi produksi yang aktif atau boleh diklaim tersedia.
- Target demo yang sedang diusulkan adalah sekitar 25 pengguna pada satu komputer kantor khusus, menggunakan Docker Compose dan reverse proxy. Cloudflare Tunnel + Cloudflare Access adalah **PROPOSED** dan belum boleh diaktifkan tanpa persetujuan mentor serta TIK/keamanan.
- Probe `pnpm demo:load` hanya menerima loopback secara default dan IP privat literal dengan opt-in. Baseline 2026-10-19 (25 pengguna/100 health request, p95 41,26 ms, error 0%) tidak melalui web/Nginx/PostgreSQL dan bukan hasil host aktual.
- `pnpm demo:smoke` menjalankan sembilan langkah perjalanan API pada backend baru `SIMULATED_DATA` di memori. Output hanya nama langkah dan agregat, tanpa pertanyaan, jawaban, sitasi, token, ID, atau isi dokumen. Ini bukan bukti browser, PostgreSQL, Nginx, jaringan, maupun host kantor. Naskahnya berada di `docs/00-project/demo-scenario-month-one.md` dan masih perlu review mentor (TASK-024).
- Komputer kantor adalah target demo/UAT sementara, bukan arsitektur produksi. Produksi menunggu keputusan private cloud/Azure/internal data center/hybrid.
- Go, Rust, PWA, Android, dan iOS adalah roadmap pasca-MVP. Jangan menambah service atau dependency hanya agar stack tampak lebih banyak.
- Monitoring kerja memiliki CRUD terotorisasi untuk output, tugas, milestone, pending matter, dan follow-up. Approval khusus monitoring belum boleh dikarang; TASK-005 tetap IN PROGRESS sampai OQ-12/OQ-25 diputuskan.
- Dashboard menyebut Yield SUN dan Kepemilikan SBN tanpa angka, masing-masing "Sumber data belum tersedia". Jangan menambahkan angka, grafik, atau tabel bisnis sebelum OQ-21 diputuskan.
- ScopeGuard SAVI memiliki 24 golden cases sejak 2026-10-11. Pertanyaan tertolak harus berhenti sebelum retrieval; karakter zero-width sederhana dinormalisasi; permintaan kredensial/jailbreak/keputusan investasi ditolak; penyebutan Python dalam konteks SUNOVATE dan kata "menghapus" yang informasional tidak boleh menjadi false refusal.
- Arahan mentor yang diteruskan project lead pada 2026-10-14 menyatakan mekanisme tindak lanjut bukti tidak cukup dapat dilanjutkan. Implementasi menampilkan panduan memperjelas konteks atau meminta pemeriksaan pegawai berwenang. Retry maksimal satu kali hanya mengenali lima kelompok variasi ejaan di `hermes/text.py`; semua filter dan ambang tetap berlaku. Jangan menambahkan sinonim domain, penunjukan PIC, tiket, notifikasi, SLA, atau publikasi otomatis tanpa validasi dan keputusan yang sesuai.
- Register glosarium terstruktur ada di `savi_glossary_intake.json` dan ditampilkan read-only pada `/savi-validation`. Lima variasi ejaan harus selalu sama dengan allowlist kode; tujuh kandidat pemetaan domain tetap `BLOCKED`. Jangan mempromosikan debt switch, cash buyback, SBN, ORI, SBR, T&C, atau nama institusi lama sebelum OQ-37 ditutup dan golden set diperbarui.
- Referensi visual Agentic AI dan lima lapisan RAG sudah dipetakan di `rag-pattern-reference.md`. Layar `/knowledge/ingestion-preview` dapat membaca TXT/MD/PDF/DOCX/XLSX/XLS simulasi secara terbatas di memori dan menjalankan chunking Python deterministik. DOCX mempertahankan urutan paragraf/tabel dan gaya judul sebagai penanda bagian. Excel hanya membaca nilai tersimpan tanpa menjalankan rumus; semua lembar termasuk yang tersembunyi dipindai agar pemeriksaan injection tidak dapat dilewati. Makro dan tautan luar ditolak. Uji sintetis representatif untuk keenam format dasar tersedia. Berkas sumber tidak disimpan; teks hasil pembacaan wajib ditinjau manusia. Hasil yang disahkan akun dengan gabungan permission terkait hanya dapat disimpan sebagai draf `SIMULATED_DATA`; draf tidak masuk pencarian umum atau SAVI dan bukan persetujuan publikasi. Jangan menganggap jalur ini sebagai unggah produksi atau mengaktifkan dokumen resmi, OCR, embedding, web search, multi-agent, memory jangka panjang, maupun tool eksternal tanpa keputusan tata kelola.
- RAG-Anything adalah kandidat adapter parser-only melalui ADR-017/TASK-022, bukan dependency atau fitur aktif. Preflight di `scripts/experiments/rag_anything/` bersifat fail-closed, tidak membaca isi, dan sengaja gagal bila paket belum dipasang. Versi 1.4.1 diblokir; kandidat minimal 1.4.2. Jangan memberi worker akses DB/egress, memakai data asli, mengikuti path/URL eksternal, atau menggantikan ekstraktor Python/SAVI sebelum OQ-11, sandbox, SBOM, security test, dan benchmark lulus.
- Preview ekstraksi memakai status resmi `PENDING`, `EXTRACTED`, `FAILED`, dan `QUARANTINED`. Jangan menambahkan `REVIEWED` ke `extraction_status`; pemeriksaan manusia menggunakan lifecycle knowledge `DRAFT/IN_REVIEW/PUBLISHED`. Penolakan preview tidak memiliki record persisten dan hanya dicatat melalui audit aman.
- Indikasi prompt injection diperiksa pada hasil ekstraksi dan sebelum simpan draf dengan `is_instruction_like` yang menormalisasi karakter format tersembunyi. Temuan memakai `QUARANTINED`/`PROMPT_INJECTION_SUSPECTED`, tidak dipersistenkan, dan bukan vonis final. Jangan membuat tombol bypass; perluasan pola harus disertai kasus uji false-positive dan false-negative.
- Evaluasi ekstraksi dapat dijalankan dengan `pnpm extraction:eval`. Corpus tujuh kasus berada di
  `tests/fixtures/document_extraction_set.json`, seluruhnya `SIMULATED_DATA`. Baseline 2026-10-19
  lulus pada seluruh gate dengan forbidden hits 0. Output tidak boleh diperluas agar mencetak
  nama, checksum, teks sumber, atau hasil ekstraksi.
- Pencarian draf terpisah tersedia pada `/knowledge/drafts` dan `/api/v1/knowledge/drafts/search`. `knowledge_owner` hanya memperoleh draf miliknya; pemeriksa memperoleh draf dalam scope tim dan klasifikasi. Filter akses berjalan sebelum pencocokan isi, audit tidak menyimpan kata kunci, dan jalur ini tidak boleh digabungkan ke pencarian umum atau SAVI.
- Mode PostgreSQL memakai indeks GIN `search_vector` untuk `/search` dan `/knowledge/drafts/search`; query selalu dibatasi ID yang sudah lolos otorisasi dan scoring akhir tetap memakai normalisasi Python. Mode simulated mempertahankan fallback leksikal. Retrieval SAVI belum memakai FTS, jadi jangan mengklaim pencarian semantik atau hybrid RAG sudah aktif.
- Evaluasi pencarian terpisah tersedia melalui `pnpm search:eval` dan `search_relevance_set.json`. Baseline simulated 10 kasus lulus pada hit@5 1,00, MRR 1,00, leakage 0. Runner `pnpm search:eval:postgres` hanya menerima database uji lokal/private yang dikonfirmasi berisi `SIMULATED_DATA`; hasil PostgreSQL aktual belum ada. Jangan memperluas FTS ke retrieval SAVI sebelum evaluator berjalan pada PostgreSQL dan golden set SAVI tetap lulus.
- `pnpm db:restore-drill` adalah alat latihan fail-closed, bukan backup produksi. Alat hanya berjalan pada `APP_ENV=test`, membutuhkan konfirmasi `SIMULATED_DATA_ONLY`, menolak target tidak kosong/sama/publik, tidak menghapus objek, tidak mencetak URL, dan menghapus dump sementara. Sebelas uji guard lulus, tetapi restore PostgreSQL aktual dan backup off-host belum dilakukan pada lingkungan ini. Jangan menulis "backup tervalidasi" sebelum SEC-75 dijalankan dan buktinya dicatat.
- Halaman detail `/knowledge/[id]` sudah memiliki alur kontekstual ubah draf, ajukan pemeriksaan, kembalikan dengan alasan, serta setujui dan terbitkan. Pengaju tidak mendapat tombol keputusan; pemeriksa tanpa `knowledge:publish` hanya dapat mengembalikan. Jangan melonggarkan aturan backend atau menjadikan pemeriksaan UI sebagai pengganti otorisasi API.
- Antrean `/approvals` merangkum permintaan publikasi yang boleh dilihat pengguna, dengan filter status dan tim. API memperkaya respons dengan nama pengaju serta judul/status bahan hanya setelah otorisasi. Keputusan tetap dilakukan di detail knowledge; jangan memindahkan keputusan ke tabel tanpa memastikan konteks bahan tetap wajib dibaca.
- `docs/00-project/implementation-master-plan.md` adalah urutan implementasi utama. Ide atau teknologi baru harus dimasukkan ke fase dan gate dokumen tersebut sebelum kode dibuat; jangan mengubah roadmap hanya berdasarkan referensi visual.
- `EvidenceGate` adalah baseline abstention SAVI: passage hanya diteruskan bila coverage, dukungan istilah, skor rerank, dan ambang relatif terpenuhi. Jangan menggantinya dengan model reranker eksternal atau menurunkan ambang tanpa OQ-11 dan evaluasi golden set.
- Antarmuka percakapan SAVI menyediakan dua contoh pertanyaan yang sudah diuji, daftar sumber
  terstruktur, jumlah rujukan, penghitung karakter, serta tombol percakapan baru. Tindak lanjut
  membedakan sumber yang tidak ditemukan dari sumber yang belum cukup mendukung. Pesan pengguna
  wajib memakai nama SAVI AI; `Hermes` tetap hanya nama internal kode. Perubahan ini tidak
  mengaktifkan model atau koneksi AI eksternal.
- Audit bahasa antarmuka 2026-10-20 menutup BUG-025. Hasil pencarian menerjemahkan jenis
  pengetahuan, halaman administrasi membedakan tujuh layanan dengan nama dan penjelasan awam,
  katalog kewenangan memakai SAVI AI, serta pesan layanan tidak lagi menampilkan `knowledge`,
  `clearance`, `approval`, atau nama Hermes kepada pengguna. Kode permission, route, dan nama
  kelas internal tidak diubah.
- OQ-37 dijawab sebagian oleh mentor pada 2026-10-14. `SUN = Surat Utang Negara`, sumber glosarium berupa peraturan SUN/playbook transaksi, review setiap tiga bulan, dan singkatan tanpa sumber resmi dilarang. Kata `admin` belum menjadi role runtime; tujuh kandidat domain tetap BLOCKED sampai pemetaan dan validator final disahkan.
- Delapan pertanyaan operasional dari arahan mentor 2026-10-13 berada di `apps/api/sunovate_api/resources/sme_question_intake.json`, bukan golden set aktif. Halaman read-only `/savi-validation` tersedia bagi role simulasi dengan `knowledge:review` dan `scope:all_teams`, dilengkapi ringkasan status, pencarian, filter, format cetak, serta lembar persiapan keputusan mentor yang hanya hidup pada state browser. Pertanyaan tetap diblokir dari retrieval dan jawaban SAVI (OQ-36). Jangan menyimpan keputusan, menambahkan aksi approval, atau mempromosikan kasus sebelum keputusan mentor diterima melalui mekanisme resmi.
- Draft Workspace untuk file hasil pekerjaan adalah proposal tertunda (FR-56/TASK-019), bukan fitur aktif. DRAFT boleh diubah/dihapus lunak oleh pemilik berizin; versi PUBLISHED harus immutable; koreksi menjadi versi baru; penarikan mempertahankan audit. Jangan implementasikan atau menganggap akun utama sebagai super-admin konten sebelum OQ-35 diputuskan.
- Specification-ready package Draft Workspace ada di `docs/02-business/work-file-draft-workspace.md`, termasuk model dan endpoint kandidat serta AC-26 sampai AC-31. Jangan membuat migration atau route dari rancangan ini sebelum OQ-35, provider file, dan approval chain dikonfirmasi.
- Ketua tim proyek mengarahkan implementasi; mentor mengawasi dan memvalidasi kebutuhan. Keputusan jaringan, domain, identitas, data, keamanan, dan produksi tetap memerlukan pihak instansi yang berwenang.

## Batas yang Tidak Boleh Dilanggar

- Jangan mengarang fungsi SUN Tematik, proses kerja Dit. SUN, angka yield/kepemilikan SBN, struktur persetujuan, atau format dokumen resmi.
- Jangan mengubah label `NEEDS APPROVAL`/`OPEN QUESTION` menjadi selesai tanpa sumber keputusan.
- Jangan menyimpan file sebagai BLOB, memberi SAVI AI akses DB langsung, atau mengeksekusi aksi tulis AI tanpa human approval.
- Teks yang terlihat pengguna wajib memakai bahasa Indonesia nonteknis sesuai `docs/09-ui-ux/content-language.md`. Jangan tampilkan nama internal Hermes, API/endpoint, permission/scope, runtime, enum mentah, atau label mesin seperti `SIMULATED_DATA`, `PROPOSED`, dan `BLOCKED` pada antarmuka. Istilah tersebut tetap boleh berada pada kode dan dokumentasi pengembang.
- Jangan mengaktifkan Cloudflare Tunnel, SSO, SharePoint, Telegram, WhatsApp, Power BI, model AI eksternal, atau data pasar hanya berdasarkan roadmap.
- Jangan mengedit dokumen sumber root atau `docs/_archive/`.

## Definition of Handoff Selesai

1. Task tracker dan changelog diperbarui.
2. ADR/decision log/risk register diperbarui bila ada perubahan arsitektur atau kebijakan.
3. Test relevan benar-benar dijalankan dan hasil aktual dicatat.
4. Tidak ada klaim yang melampaui implementasi atau persetujuan.
5. Commit kecil, dapat ditinjau, dan tidak mencampur file pengguna yang tidak terkait.

## Related Documents

- [task-tracker.md](task-tracker.md)
- [architecture-decisions.md](../03-architecture/architecture-decisions.md)
- [decision-log.md](../12-governance/decision-log.md)
- [risk-register.md](../12-governance/risk-register.md)

