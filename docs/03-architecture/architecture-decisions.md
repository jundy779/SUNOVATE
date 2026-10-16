# Architecture Decisions (ADR)

**Status:** PROPOSED
**Last Updated:** 2026-10-17

## Purpose
Rincian konteks, keputusan, alternatif, dan konsekuensi. Ringkasan dan status ada di [decision-log.md](../12-governance/decision-log.md).

### ADR-001 Modular monolith
- Konteks: satu pengembang, enam bulan, kebutuhan belum stabil.
- Keputusan: satu API FastAPI dengan modul internal, satu web Next.js. **CONFIRMED** (brief).
- Alternatif ditolak: microservices (overhead operasional).
- Konsekuensi: batas modul dijaga di kode (`modules/`, `authz/`, `hermes/`).

### ADR-002 FastAPI/SQLAlchemy/Alembic menggantikan NestJS/Prisma
- Keputusan eksplisit brief. **CONFIRMED**. Blueprint v0.1 menjadi konteks historis.
- Konsekuensi: kontrak TypeScript dipelihara manual di `packages/contracts`.

### ADR-003 PostgreSQL tunggal, tanpa BLOB
- Relasional + FTS (`tsvector` GIN) + pgvector. File hanya referensi, metadata, checksum SHA-256, versi, klasifikasi, lokasi provider. **CONFIRMED**.

### ADR-004 Hermes di belakang HermesGateway
- `HermesClient` hanya menerima passage terotorisasi; tanpa kredensial DB. **CONFIRMED**.

### ADR-005 Token pengembangan HMAC
- `POST /api/v1/auth/dev/login` untuk pengguna SIMULATED; TTL default 480 menit; secret kosong menghasilkan secret acak per proses. Config menolak `APP_ENV=production` dengan dev auth aktif. **PROPOSED**.
- Alternatif ditolak: JWT library (dependency tambahan tanpa kebutuhan), login tanpa token (tidak menguji alur otorisasi).

### ADR-006 Otorisasi permission AND team scope AND klasifikasi
- Deny by default, di API. Record yang tidak boleh dibaca dikembalikan 404. **CONFIRMED** (prinsip), **PROPOSED** (matriks).

### ADR-007 Runtime `DATA_BACKEND=simulated`
- Store in-memory memuat dataset yang sama dengan seed DB. Skema dan seed PostgreSQL tervalidasi, repository SQLAlchemy belum. **PROPOSED**.
- Alasan: memvalidasi kontrak API dan otorisasi sebelum persistence; mesin pengembang tanpa Docker.
- Konsekuensi: data hilang saat restart (R-10). Config menolak mode ini di production.
- Dilanjutkan oleh ADR-015 (backend kedua `DATA_BACKEND=postgres`; `simulated` tetap default).

### ADR-008 AI provider pengembangan ekstraktif
- Deterministik, tanpa jaringan; hanya menyalin kalimat dari passage. Embedding nonaktif. **PROPOSED**.

### ADR-009 Embedding tanpa dimensi tetap
- `embedding_references.embedding` bertipe `vector` tanpa dimensi; `model_name` dan `dimensions` disimpan; tanpa indeks ANN sampai model disetujui. **PROPOSED**.

### ADR-010 Soft delete dan audit append-only
- `deleted_at` di record bisnis; trigger `audit_logs_append_only` menolak UPDATE/DELETE. **PROPOSED**.

### ADR-011 Optimistic concurrency
- Kolom `revision`; PATCH wajib menyertakan `revision`; tidak cocok menghasilkan 409 `REVISION_CONFLICT`. **PROPOSED**.

### ADR-012 Arsip dokumentasi lama
- `docs/` sebelumnya dipindah ke `docs/_archive/legacy-docs-v0/`, tidak dihapus. **PROPOSED**.

### ADR-013 Tanpa tabel SUN Business
- Tabel instrumen, lelang, transaksi, yield, setelmen dari scaffold lama dihapus karena belum tervalidasi. **PROPOSED**.

### ADR-014 File sumber biner dikecualikan dari Git
- `/*.pdf`, `/*.pptx` di `.gitignore` sampai OQ-18 dijawab. **PROPOSED**.

### ADR-015 Persistence PostgreSQL di belakang interface Repository
- Status: **PROPOSED** (diimplementasikan di branch `feat/postgres-persistence`, 2026-10-02; belum disetujui mentor).
- Konteks: ADR-007 menjalankan runtime dari store in-memory, sehingga data hilang saat restart (R-10, KL-01). Skema, migrasi, dan seed PostgreSQL sudah tervalidasi (ADR-003), tetapi belum dipakai runtime. Handler API berupa fungsi sinkron `def` yang berjalan di threadpool FastAPI.
- Keputusan:
  - Satu interface `Repository` (Protocol Python, sinkron) di `store/repository.py`. `SimulatedStore` (`store/simulated.py`) dan `PostgresRepository` (`store/postgres.py`) mengimplementasikannya. Modul API, `AuthorizationService`, `RetrievalService`, dan `HermesGateway` tidak bercabang per backend; satu-satunya titik pemilihan adalah `build_runtime` di `context.py` berdasarkan `DATA_BACKEND` (`simulated` default, `postgres`).
  - Repository dibuat per request lewat `DataBackend.session()` (dependency generator `get_ctx`). Exit dependency tidak melakukan commit; commit hanya terjadi di `repo.transaction()` di dalam handler. `insert`/`update_revisioned` di luar `transaction()` ditolak `RuntimeError` (500) di kedua backend, sehingga kesalahan ini tertangkap di `pnpm test`.
  - Driver runtime: SQLAlchemy 2 sinkron + `psycopg[binary]==3.3.6` (satu-satunya dependency baru, di-pin eksak). `asyncpg` tetap dipakai Alembic, CLI seed, `/health/database`, dan `tests/integration`.
  - Aturan `DATABASE_URL`: hanya skema `postgresql+asyncpg` dan `postgresql+psycopg` yang diterima; `postgresql` polos ditolak. Parsing dan normalisasi hanya di `db/urls.py` (`sync_database_url` untuk runtime, `async_database_url` untuk Alembic, seed, dan health). Kesalahan dilempar sebagai `ValueError` tanpa URL; validasi sengaja tidak di validator pydantic karena `ValidationError` mencetak nilai input.
  - Urutan natural setiap koleksi pada kedua backend adalah `(created_at, id)` naik, sebagai klarifikasi urutan (A-04). Bukti: probe D-C3 (desain) mengurutkan ulang semua koleksi simulated dan seluruh suite tetap lulus (105 passed, 3 skipped), termasuk 16 kasus golden set RAG. Urutan audit memakai urutan insert.
  - Revisi Alembic baru `0002_ordering_columns`: `audit_logs.seq` (BIGINT identity, unik, urutan insert audit) dan `knowledge_tags.position` (INTEGER default 0, `CHECK position >= 0`, urutan tag). `0001_initial_schema` tidak diubah.
  - Tag knowledge didedupe saat validasi (kemunculan pertama dipertahankan, case-sensitive) di kedua backend, karena `knowledge_tags` memiliki UNIQUE `(knowledge_entry_id, tag_id)`.
  - PATCH knowledge dan task memakai `exclude_none`: `null` eksplisit berarti "tidak diubah" di kedua backend (mencegah pelanggaran `NOT NULL` menjadi 500 di postgres).
  - Optimistic concurrency menjadi `UPDATE ... WHERE id AND revision RETURNING` (atomik). Pelanggaran `uq_document_versions_reference_checksum` dipetakan ke 409 `DUPLICATE_CHECKSUM` dan `ck_approval_requests_separation_of_duties` ke 403 `SEPARATION_OF_DUTIES`; pemeriksaan API yang ada tetap berjalan lebih dulu.
  - Otorisasi tetap diputuskan oleh pemeriksaan Python yang sama; SQL hanya mempersempit kandidat (`ReadScope`). Record yang tidak terbaca tetap 404.
  - Pembaruan 2026-10-15: endpoint pencarian umum dan pencarian draf memakai `search_vector` berindeks GIN sebagai prefilter saat backend PostgreSQL aktif. Daftar ID yang sudah lolos otorisasi menjadi klausa wajib dalam query; penilaian akhir tetap memakai `terms()` agar konsisten dengan mode simulated. Retrieval SAVI belum memakai FTS dan tetap mengikuti evidence gate yang ada.
  - `AuditLog`: satu `utcnow()` per audit, sehingga `createdAt == updatedAt == occurredAt` dan stabil antar pembacaan pada kedua backend (sebelumnya tiga nilai berselisih mikrodetik di simulated).
  - Audit penolakan (`audit_denial`) ditulis lewat koneksi terpisah yang langsung di-commit, sehingga tetap tersimpan walau transaksi bisnis di-rollback.
  - Urutan key objek JSON bukan bagian kontrak API; uji paritas lintas backend membandingkan `response.json()` hasil parse (kesetaraan dict).
  - Test postgres berjalan lewat `pnpm db:test` pada pgserver sementara dengan reset `TRUNCATE ... RESTART IDENTITY CASCADE` + seed per test. Reset hanya diizinkan bila `APP_ENV=test` dan `SUNOVATE_DB_RESET_ALLOWED=1` (hanya diset oleh skrip `db:test`).
  - Catatan `/health/database`: tetap memeriksa konektivitas saja dan menyebut backend runtime aktif.
- Alternatif ditolak:
  - asyncpg dengan handler `async`: seluruh jalur request (handler, dependency, `AuthorizationService`, `RetrievalService`, `HermesGateway`, `SimulatedStore`) harus menjadi `async`; risiko regresi tinggi tanpa kebutuhan pada skala SIMULATED_DATA.
  - asyncpg dipanggil dari kode sinkron (`AsyncEngine.sync_engine` atau `asyncio.run` per query): butuh konteks greenlet atau event loop per thread di threadpool; rapuh.
  - `psycopg2`: generasi lama, tidak dikembangkan aktif untuk fitur baru.
  - Kolom `text[]` untuk tag: menduplikasi model `tags`/`knowledge_tags` yang sudah ada.
  - Database template per test: harus memutus koneksi pool setiap test dan lebih lambat dari TRUNCATE + seed.
  - Session global lewat contextvar: dependency sinkron dan handler berjalan di thread berbeda dengan salinan context masing-masing.
- Konsekuensi:
  - Dengan `DATA_BACKEND=postgres`, data bertahan setelah API di-restart. `simulated` tetap default dan tetap ditolak di production; `postgres` diizinkan di production hanya bila dev auth nonaktif (tanpa mekanisme login production, endpoint terlindungi tetap 401; OQ-07).
  - Koneksi dibuka dengan `options=-c timezone=UTC0 -c statement_timeout=15000`. Bentuk POSIX `UTC0` dipakai karena build pgserver Windows tidak memiliki data zona waktu sehingga `UTC` ditolak; offsetnya sama dan setiap timestamp tetap dinormalisasi ke UTC di mapper.
  - Risiko diterima: bila DB mati, permintaan yang seharusnya 403 menjadi 503 `DATABASE_UNAVAILABLE` karena `audit_denial` butuh DB; `audit_denial` memakai koneksi kedua dari pool yang sama (satu request paling banyak dua koneksi); koneksi berstatus idle in transaction selama generasi Hermes (generasi saat ini lokal dan cepat).
  - Reset TRUNCATE hanya pada DB pgserver sementara; trigger `audit_logs_append_only` tidak menghalangi TRUNCATE dan tidak diubah (celah dicatat di known-limitations, penutupannya OUT OF SCOPE).
  - `pnpm db:test` lebih lambat dari `pnpm test` (sekitar 4 sampai 5 menit di mesin Windows pengembang) karena reset per test.

### ADR-016 Baseline demo satu host; ekspansi stack berbasis bukti

- **Status:** PROPOSED; membutuhkan persetujuan mentor dan TIK/keamanan untuk deployment nyata.
- **Keputusan:** Demo terbatas menargetkan sekitar 25 pengguna dengan satu komputer kantor khusus yang menjalankan Next.js, FastAPI/Python, dan PostgreSQL melalui Docker Compose serta Nginx. Cloudflare Tunnel + Access adalah opsi akses yang belum diaktifkan. Semua data tetap `SIMULATED_DATA`.
- **Batas:** Ini bukan target produksi dan bukan klaim kapasitas. Load test, backup/restore, security checklist, daftar akses, logging, serta kill switch tunnel wajib sebelum UAT.
- **Roadmap:** Go dapat dipertimbangkan untuk gateway/webhook/worker konkuren dan Rust untuk pemrosesan file berisiko tinggi hanya setelah metrik dan threat review menunjukkan kebutuhan. PWA/Android/iOS ditunda sampai API dan autentikasi stabil.
- **Alasan:** Menjaga MVP dapat diselesaikan dan diaudit tanpa mengunci jalur skala jangka panjang atau menambah kompleksitas prematur.

### ADR-017 RAG-Anything sebagai adapter pilot terisolasi

- **Status:** PROPOSED; preflight tersedia, parser belum dipasang atau diaktifkan.
- **Konteks:** Ekstraktor Python SUNOVATE telah mendukung TXT/MD/PDF/DOCX/XLSX/XLS, tetapi dokumen kompleks dapat membutuhkan pemahaman layout, tabel, gambar, rumus, dan OCR. RAG-Anything menawarkan pipeline multimodal berbasis LightRAG/MinerU, namun status upstream masih Beta dan dependency serta penggunaan model visual memperluas permukaan serangan dan kebutuhan resource.
- **Keputusan:** Nilai RAG-Anything sebagai adapter parser-only di worker terisolasi. Ia menerima hanya file simulasi yang telah melewati validasi SUNOVATE dan mengembalikan konten/metadata untuk diperiksa manusia. Ia tidak mendapat kredensial database, tidak menentukan izin/klasifikasi, tidak menerbitkan knowledge, dan tidak menggantikan retrieval SAVI.
- **Versi:** `1.4.1` diblokir; kandidat awal minimal `1.4.2` berdasarkan catatan keamanan upstream. Versi final dikunci eksak setelah review supply chain.
- **Jaringan:** Tidak ada egress pada pilot awal. LLM/VLM/OCR eksternal serta telemetry tidak aktif. Penggunaan model/provider harus menunggu OQ-11 dan review klasifikasi data.
- **Fallback:** Ekstraktor Python deterministik tetap baseline. Kegagalan worker tidak boleh menandai dokumen berhasil atau memasukkannya ke indeks.
- **Gate:** threat test, SBOM/dependency scan, benchmark akurasi dan resource, ketertelusuran halaman/sheet, serta persetujuan alat dan lokasi pemrosesan.
- **Rincian:** [rag-anything-pilot](../05-ai-rag/rag-anything-pilot.md).

### ADR-018 Batas data privat deny-by-default

- **Status:** ACTIVE PROJECT SAFETY BASELINE; keputusan deployment tetap membutuhkan persetujuan TIK/keamanan dan pemilik data.
- **Konteks:** Project lead menegaskan pada 2026-10-17 bahwa data SUNOVATE tidak boleh menjadi publik, ditemukan AI Search/SEO/GEO/AIO/crawler, dikirim ke agent/model eksternal, atau diekstraksi melalui jailbreak. Kontrol metadata saja tidak cukup karena crawler jahat dapat mengabaikannya.
- **Keputusan aplikasi:** konfigurasi mode privat dikunci menggunakan tipe literal; public indexing, egress AI, agent eksternal, dan telemetry egress tidak dapat diaktifkan melalui environment. Web dan API mengirim `no-store`, anti-index, anti-archive, no-referrer, frame denial, serta kebijakan resource same-origin. CSP web membatasi `connect-src` ke origin sendiri. `robots.txt` menolak seluruh path. OpenAPI dan dokumentasi interaktif hanya tersedia di development/test.
- **Keputusan SAVI:** pola permintaan pengiriman ke AI/agent/MCP/webhook, publikasi/indexing, encoding data sensitif, pemecahan pesan, dan tool-mediated exfiltration ditolak sebelum retrieval. Pemeriksaan izin, tim, dan klasifikasi tetap menjadi kontrol utama.
- **Batas:** Kode aplikasi tidak dapat menjamin nol kebocoran. Data asli tetap dilarang sampai jaringan privat, firewall egress deny-by-default, SSO/MFA, TLS, enkripsi, audit, pentest, klasifikasi, provider, dan lokasi pemrosesan disetujui serta diverifikasi.
- **Alternatif ditolak:** hanya mengandalkan `robots.txt`, prompt larangan, nama route tersembunyi, atau pernyataan kebijakan. Keempatnya bukan security boundary.
- **Konsekuensi:** Integrasi eksternal, tunnel, analytics, web search, RAG pihak ketiga, dan model AI publik fail-closed. Perubahan lock ini memerlukan ADR pengganti, review keamanan, dan persetujuan resmi.
- **Rincian:** [private-data-boundary](../06-security/private-data-boundary.md).

## Related Documents
- [decision-log.md](../12-governance/decision-log.md)
- [change-management.md](../12-governance/change-management.md)
