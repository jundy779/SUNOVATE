# SUNOVATE

**SUN Integrated Management and Knowledge Platform** untuk Direktorat Surat Utang Negara, DJPPR,
Kementerian Keuangan. Repository ini adalah **fondasi pengembangan** (modular monolith) untuk
program MagangHub periode 21 September 2026 sampai 20 Maret 2027. **Bukan sistem siap produksi.**

## Batas penting
- Seluruh data adalah `SIMULATED_DATA` fiktif. Tidak ada data internal, keuangan, atau pribadi.
- Integrasi produksi (SSO, SharePoint, Power BI, Telegram, WhatsApp, Kemenkeu Satu, Bank Indonesia, data pasar) **tidak tersedia** dan dinonaktifkan.
- Hermes tidak mengakses database secara langsung, tidak memberi keputusan keuangan, dan tidak menjalankan aksi tulis tanpa persetujuan manusia.
- SUNOVATE bukan SUN Job Monitor dan tidak menggantikan sistem transaksi SUN resmi.
- Fungsi SUN Tematik adalah **OPEN QUESTION**.

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
Docker opsional, hanya untuk PostgreSQL lokal. API berjalan tanpa database (store simulasi in-memory).

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

## Validasi

```bash
pnpm lint         # ESLint + Ruff
pnpm typecheck    # tsc + mypy strict
pnpm test         # Vitest + pytest (apps/api/tests dan tests/)
pnpm build        # next build
pnpm e2e          # Playwright; butuh pnpm api:dev berjalan
pnpm db:sql       # render SQL migrasi tanpa database
```

Hasil validasi terakhir dicatat di `CHANGELOG.md`. Mulai membaca dokumentasi dari `docs/README.md`.
Aturan untuk AI coding agent ada di `AGENTS.md`.
