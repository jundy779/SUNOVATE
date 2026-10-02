# Technology Stack

**Status:** CONFIRMED (pilihan stack), PROPOSED (versi dapat diperbarui)
**Last Updated:** 2026-10-01

## Purpose
Mencatat teknologi dan versi yang benar-benar terpasang dan dipakai pada scaffold.

## Frontend
| Teknologi | Versi terpasang | Catatan |
|---|---|---|
| Node.js | 24.19.0 (min. 22) | |
| pnpm | 11.4.0 | workspace `apps/web`, `packages/*` |
| Next.js (App Router, Turbopack) | 16.3.8 | `output: standalone` |
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
| uvicorn | 0.54 |
| pytest / pytest-asyncio / httpx | 8.4.2 / 1.4 / 0.28.1 |
| Ruff / mypy | 0.16.9 / 1.20.2 (strict) |

## Data dan infrastruktur
| Teknologi | Versi |
|---|---|
| PostgreSQL | image `pgvector/pgvector:pg17` (Docker Compose) |
| pgvector extension | 0.6.2 pada server validasi `pgserver` |
| Full-text search | `tsvector` konfigurasi `simple`, indeks GIN |

`pgserver` dan `pypdf` hanya dipakai sementara saat validasi/inspeksi melalui `uv run --with`; keduanya bukan dependency proyek.

## Keputusan
- **CONFIRMED** FastAPI/SQLAlchemy menggantikan NestJS/Prisma (ADR-002).
- **PROPOSED** Resolver Zod ditulis lokal agar tidak menambah dependency `@hookform/resolvers` untuk dua form.
- **OPEN QUESTION** Model LLM dan embedding (OQ-11).

## Related Documents
- [architecture-decisions.md](architecture-decisions.md)
- [environment-configuration.md](../11-operations/environment-configuration.md)
