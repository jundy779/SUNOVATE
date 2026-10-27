# SUNOVATE

**SUN Organizational Values and Transformation through Experience** untuk Direktorat Surat Utang Negara, DJPPR,
Kementerian Keuangan.

*Menjaga pengetahuan, belajar dari pengalaman, berinovasi untuk meningkatkan kinerja.*

Repository ini adalah **fondasi pengembangan** (modular monolith) untuk
program MagangHub periode 21 September 2026 sampai 20 Maret 2027. **Bukan sistem siap produksi.**

## Batas penting
- Seluruh data adalah `SIMULATED_DATA` fiktif. Tidak ada data internal, keuangan, atau pribadi.
- Integrasi produksi (SSO, SharePoint, Power BI, Telegram, WhatsApp, Kemenkeu Satu, Bank Indonesia, data pasar) **tidak tersedia** dan dinonaktifkan.
- Asisten AI tampil ke pengguna sebagai **SAVI AI**. Nama Hermes hanya dipakai pada identifier kode internal (mesin yang direncanakan: Hermes Agent, Nous Research). SAVI saat ini berjalan pada mode `development_extractive`, embedding nonaktif, dan bukan RAG produksi.
- SAVI tidak mengakses database secara langsung, tidak memberi keputusan keuangan, dan tidak menjalankan aksi tulis tanpa persetujuan manusia.
- File berklasifikasi `RAHASIA` (file tertentu saja) hanya boleh dibaca lewat Secure Viewer tanpa download, edit, hapus, copy, atau cetak. Status: penampil, daftar pembaca, pernyataan kerahasiaan, tanda air, batas laju, dan enkripsi envelope sudah berjalan untuk `SIMULATED_DATA` (ADR-020, TASK-027 sampai TASK-032). Saat ini isi dienkripsi dengan kunci sementara per proses yang hilang saat API dimulai ulang. Kunci berbasis TPM (HSM menyusul) belum terpasang, sehingga dokumen asli tetap dilarang (OQ-40 sampai OQ-42).
- SUNOVATE bukan SUN Job Monitor dan tidak menggantikan sistem transaksi SUN resmi.
- Scope pilot: tujuh tim kerja (PPSUN, AKPSUN, PSUN, PPPSUN, DHTV, SUN Tematik, MONEV). MONEV ditambahkan setelah rapat 6 Oktober 2026. Fungsi SUN Tematik masih **OPEN QUESTION**.
- Target MVP (P1 repository + P2 asisten AI) sekitar 3 bulan, kira-kira akhir Desember 2026.

## Isi repository

```text
apps/web        Next.js 16 App Router, TypeScript strict, Tailwind CSS 4
apps/api        FastAPI, Pydantic v2, SQLAlchemy 2, Alembic (env Python terpisah, uv)
packages/       contracts (tipe + Zod), shared-types (enum), config (tsconfig), ui (placeholder)
database/       penunjuk ke model, migrasi, dan seed di apps/api
infrastructure/ konfigurasi lokal; docker-compose.yml di root (PostgreSQL 17 + pgvector)
scripts/        setup, development, validation (termasuk cek DB tanpa Docker)
tests/          security, rag-evaluation, integration, fixtures (Python)
references/     catatan dokumen sumber
docs/           dokumentasi 00-project sampai 13-handover
```

## Prasyarat
Node.js 22+ (diuji 24.19), pnpm 11.4, Python 3.12 sampai 3.14 (diuji 3.14.4), uv 0.11+.
Docker opsional, hanya untuk PostgreSQL lokal. Secara default API berjalan tanpa database (store simulasi in-memory).

## Menjalankan

```bash
pnpm install
pnpm api:setup              # uv sync di apps/api
cp .env.example .env        # opsional; Windows: Copy-Item .env.example .env
pnpm api:dev                # API http://localhost:8000, OpenAPI di /docs
pnpm dev                    # Web http://localhost:3000
```

Masuk di `/login` dengan salah satu akun simulasi, misalnya `sim.staff.pppsun@sunovate.local` atau
`sim.coordinator@sunovate.local` (daftar lengkap di `docs/11-operations/local-development.md`).

PostgreSQL (opsional): `pnpm db:up`, `pnpm db:migrate`, `pnpm db:seed`. Tanpa Docker: `pnpm db:check`.

Mode PostgreSQL (PROPOSED, ADR-015): set `DATA_BACKEND=postgres` dan `DATABASE_URL`
(skema `postgresql+asyncpg://` atau `postgresql+psycopg://`) di `.env`, jalankan `pnpm db:migrate` dan
`pnpm db:seed`, lalu `pnpm api:dev`. Data yang dibuat lewat API tetap ada setelah restart, dan
`GET /api/v1/health` melaporkan `dataBackend: "postgres"`. Default tetap `DATA_BACKEND=simulated`.
Rincian di `docs/11-operations/local-development.md`.

## Validasi

```bash
pnpm lint         # ESLint + Ruff
pnpm typecheck    # tsc + mypy strict
pnpm test         # Vitest + pytest (apps/api/tests dan tests/)
pnpm build        # next build
pnpm e2e          # Playwright; butuh pnpm api:dev berjalan
pnpm db:sql       # render SQL migrasi tanpa database
pnpm db:check     # migrasi + seed pada PostgreSQL sementara (pgserver, tanpa Docker)
pnpm db:test      # seluruh pytest pada backend postgres (pgserver sementara, beberapa menit)
```

Hasil validasi terakhir dicatat di `CHANGELOG.md`. Mulai membaca dokumentasi dari `docs/README.md`.
AI agent wajib membaca `docs/13-handover/ai-agent-handoff.md` dan memperbarui
`docs/13-handover/task-tracker.md` untuk setiap perubahan material. Aturan coding agent ada di `AGENTS.md`.

## Deployment demo dan roadmap

- **PROPOSED / NEEDS APPROVAL:** demo sekitar 25 pengguna pada satu komputer kantor khusus dengan Docker Compose dan Nginx; Cloudflare Tunnel + Access hanya boleh diaktifkan setelah persetujuan mentor dan TIK/keamanan.
- Komputer kantor bukan target produksi. Opsi produksi private cloud/Azure/internal data center/hybrid menunggu keputusan instansi.
- Python/FastAPI tetap inti. Go, Rust, PWA, Android, dan iOS adalah roadmap pasca-MVP berbasis kebutuhan terukur, bukan fitur aktif.
