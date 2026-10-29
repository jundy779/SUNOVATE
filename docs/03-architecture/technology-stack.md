# Technology Stack

**Status:** CONFIRMED (pilihan stack), PROPOSED (versi dapat diperbarui)
**Last Updated:** 2026-10-19

## Purpose
Mencatat teknologi dan versi yang benar-benar terpasang dan dipakai pada scaffold.

## Frontend
| Teknologi | Versi terpasang | Catatan |
|---|---|---|
| Node.js | 24.19.0 (min. 22) | |
| pnpm | 11.4.0 | workspace `apps/web`, `packages/*` |
| Next.js App Router | 16.3.8 | `output: standalone`; `next dev` untuk pengembangan, Webpack untuk build produksi yang deterministik |
| React | 19.3 | server components default |
| TypeScript | 5.9.3 | strict, `noUncheckedIndexedAccess` |
| Tailwind CSS | 4.3.3 | token SUNOVATE di `globals.css` |
| TanStack Query | 5.104 | mutasi chat Hermes |
| React Hook Form | 7.89 | login, form Hermes; resolver Zod lokal (`lib/zod-resolver.ts`) |
| Zod | 4.6.5 | skema request di `@sunovate/contracts` |
| Recharts | 3.10.1 | grafik tugas per status |
| Vitest / Testing Library | 5.0.3 / 16.3 | unit dan komponen |
| Playwright | 1.63 | e2e smoke |
| ESLint | 9.39 | `eslint-config-next` |
| shadcn/ui | tidak terpasang | belum ada kebutuhan konkret |

## Backend
| Teknologi | Versi terpasang |
|---|---|
| Python | 3.14.4 (didukung 3.12 sampai 3.14) |
| uv | 0.11.6 |
| FastAPI / Starlette | 0.142.2 / 1.7.0 |
| Pydantic / pydantic-settings | 2.13.5 / 2.15 |
| SQLAlchemy | 2.1.1 |
| Alembic | 1.20.0 |
| asyncpg | 0.31 |
| pgvector (Python) | 0.5.0 |
| cryptography | 50.0.2 | AES-256-GCM envelope untuk dokumen RAHASIA (ADR-020) |
| Pillow | 13.0.0 | render halaman PNG bertanda air untuk penampil RAHASIA (ADR-020) |
| uvicorn | 0.54 |
| pytest / pytest-asyncio / httpx | 8.4.2 / 1.4 / 0.28.1 |
| Ruff / mypy | 0.16.9 / 1.20.2 (strict) |

## Data dan infrastruktur
| Teknologi | Versi |
|---|---|
| PostgreSQL | image `pgvector/pgvector:pg17` (Docker Compose) |
| pgvector extension | 0.6.2 pada server validasi `pgserver` |
| Full-text search | `tsvector` konfigurasi `simple`, indeks GIN |

## Profil Stack per Fase

| Fase | Stack | Status dan alasan |
|---|---|---|
| MVP dan demo 25 pengguna | Next.js/React/TypeScript, FastAPI/Python, PostgreSQL/pgvector, Alembic, Docker Compose, Nginx | **CURRENT / PROPOSED DEPLOYMENT**. Python tetap inti untuk API, RAG, data engineering, dan document automation. |
| Akses demo | Cloudflare Tunnel + Cloudflare Access | **PROPOSED; NEEDS APPROVAL** mentor dan TIK/keamanan. Bukan pengganti autentikasi aplikasi dan belum diaktifkan. |
| Skala lanjut | Go untuk gateway, webhook, notifikasi, worker atau workload konkuren | **DEFERRED**. Ditambahkan hanya bila observability/load test membuktikan bottleneck; tidak dibutuhkan hanya untuk 25 pengguna. |
| Keamanan file lanjut | Rust untuk parsing/validasi file, checksum, redaction, atau komponen berisiko tinggi | **DEFERRED**. Bukan alasan membuat microservice sebelum kebutuhan terbukti. |
| Klien masa depan | PWA dan aplikasi Android/iOS (opsi Flutter atau native wrapper) | **DEFERRED**. Menggunakan API yang sama setelah auth, kontrak API, dan kebijakan perangkat stabil. |

`pgserver` dan `pypdf` hanya dipakai sementara saat validasi/inspeksi melalui `uv run --with`; keduanya bukan dependency proyek.

## Keputusan
- **CONFIRMED** FastAPI/SQLAlchemy menggantikan NestJS/Prisma (ADR-002).
- **PROPOSED** Resolver Zod ditulis lokal agar tidak menambah dependency `@hookform/resolvers` untuk dua form.
- **OPEN QUESTION** Model LLM dan embedding (OQ-11).
- **PROPOSED** Penambahan bahasa/framework ditentukan kebutuhan operasional, bukan jumlah teknologi. Modular monolith tetap baseline sampai data beban menunjukkan boundary layanan yang layak dipisah.

## Related Documents
- [architecture-decisions.md](architecture-decisions.md)
- [environment-configuration.md](../11-operations/environment-configuration.md)
