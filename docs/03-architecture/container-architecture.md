# Container Architecture

**Status:** PROPOSED
**Last Updated:** 2026-10-02

## Purpose
Menjelaskan unit yang dapat dijalankan (container) dan cara keduanya berkomunikasi.

## Confirmed Information
- **CONFIRMED** Modular monolith; frontend Next.js App Router, backend FastAPI, PostgreSQL + pgvector + FTS (sumber: brief sesi 2026-10-01, ADR-001, ADR-002, ADR-003).
- **CONFIRMED** Tidak memakai Turborepo, Kubernetes, microservices, Redis, atau message broker (sumber: brief sesi 2026-10-01).

## Diagram

```mermaid
flowchart TB
    B["Browser"]
    W["apps/web<br/>Next.js 16, server components<br/>cookie httpOnly berisi token dev"]
    A["apps/api<br/>FastAPI modular monolith<br/>/api/v1"]
    ST["Simulated store<br/>in-memory, SIMULATED_DATA"]
    PG[("PostgreSQL 17 + pgvector<br/>skema 31 tabel")]
    B -->|HTTPS| W
    W -->|"REST + Bearer token, server-side"| A
    A -->|"runtime DATA_BACKEND=simulated (default)"| ST
    A -->|"runtime DATA_BACKEND=postgres (psycopg)"| PG
    A -.->|"migrasi, seed, /health/database (asyncpg)"| PG
```

## Container
| Container | Tanggung jawab | Status |
|---|---|---|
| `apps/web` | UI, login dev (server action), memanggil API dari server; proxy `/api/hermes` | Implemented (scaffold) |
| `apps/api` | Validasi, otorisasi, use case, audit, Hermes pipeline, OpenAPI | Implemented (scaffold) |
| Simulated store | Data runtime in-memory yang dimuat ulang tiap restart; default `DATA_BACKEND=simulated` | Implemented (ADR-007) |
| PostgreSQL | Skema, migrasi, seed, FTS, pgvector; dipakai runtime bila `DATA_BACKEND=postgres` | Implemented (ADR-015, PROPOSED); FTS dan pgvector belum dipakai runtime |

- **PROPOSED (ADR-015)** Kedua backend berada di belakang interface `Repository` yang sama; kontrak API tidak berubah. Lihat [component-architecture.md](component-architecture.md).
- **CONFIRMED (implementasi)** Browser tidak memanggil API langsung dan tidak membaca token; seluruh panggilan berasal dari server Next.js.

## Risks
R-10 simulated store disangka persistence produksi. Mitigasi: label `dataBackend` di `/health` (`simulated` atau `postgres`), `meta.dataLabel` di setiap respons, config menolak `DATA_BACKEND=simulated` di production. Mode postgres tetap hanya berisi `SIMULATED_DATA` dan bukan deployment production.

## Related Documents
- [component-architecture.md](component-architecture.md)
- [deployment-architecture.md](deployment-architecture.md)
- [data-architecture.md](../04-data/data-architecture.md)
