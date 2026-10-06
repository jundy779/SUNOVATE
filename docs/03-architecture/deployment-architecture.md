# Deployment Architecture

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-02

## Purpose
Menjelaskan deployment lokal yang sudah ada dan usulan deployment yang menunggu keputusan hosting.

## Confirmed Information
- **CONFIRMED** Hosting, SSO, storage, dan model AI menunggu persetujuan instansi (sumber: Proposal v2.4, slide 14; OQ-07).
- **CONFIRMED (knowledge owner, deck v1_ slide 24)** Hosting dijawab: "pakai computer tersendiri sebagai server" (OQ-07, DEC-20261002-05). Jawaban ini tidak menyebut lokasi, jaringan, sistem operasi, backup, administrator, siapa yang boleh mengakses, atau TLS, dan tidak menjawab mekanisme login. Pengakuan mentor masih tertunda (OQ-24).
- **CONFIRMED (implementasi)** Lingkungan lokal: web `:3000`, API `:8000`, PostgreSQL via `docker-compose.yml` di `127.0.0.1:5432`.
- **CONFIRMED (fakta mesin)** Docker tidak terpasang di mesin pengembang saat sesi ini; migrasi divalidasi dengan PostgreSQL sementara (`pnpm db:check`).

## Lokal (implemented)

```mermaid
flowchart LR
    Dev["Laptop pengembang"]
    subgraph Local["localhost"]
      W["next dev / next start :3000"]
      A["uvicorn :8000"]
      P[("postgres pgvector :5432<br/>opsional")]
    end
    Dev --> W --> A
    A -.-> P
```

## Varian server khusus (PROPOSED, sesuai jawaban hosting)

Jawaban knowledge owner diterjemahkan menjadi satu komputer khusus di jaringan instansi. Semua detail di bawah adalah usulan pengembang dan belum ada persetujuan atau lingkungan nyata.

```mermaid
flowchart LR
    U["Pengguna jaringan internal"] --> H
    subgraph H["Satu komputer khusus (server)"]
      RP["TLS / reverse proxy"] --> W["Web (Next.js standalone)"]
      W --> A["API (FastAPI)"]
      A --> P[("PostgreSQL + pgvector")]
    end
    H -.-> B["Backup di luar host<br/>belum ditetapkan"]
```

- **PROPOSED** Web, API, dan PostgreSQL berjalan pada satu host; file dokumen tetap berupa referensi (ADR-003) dan bukan BLOB.
- **PROPOSED** Satu host adalah titik kegagalan tunggal (R-13): ketersediaan, backup di luar host, patching, serta akses fisik dan jaringan harus dirancang sebelum data asli masuk.
- **OPEN QUESTION (OQ-23)** Lokasi dan akses jaringan, sistem operasi, apakah Docker boleh dipasang, backup, siapa yang mengadministrasi, siapa yang boleh mengakses, dan TLS.
- **OPEN QUESTION (OQ-07)** Mekanisme login di server ini. Sampai dijawab, `POST /auth/dev/login` tetap hanya untuk development dan aplikasi menolak start bila `APP_ENV=production` dengan dev auth aktif.
- **PROPOSED** Tidak ada data asli, data pribadi, atau data keuangan di server sampai klasifikasi (OQ-05) dan persetujuan eksplisit ada.

## Usulan target (PROPOSED)

```mermaid
flowchart LR
    U["Pengguna jaringan internal"] --> RP["Reverse proxy / TLS<br/>disediakan instansi"]
    RP --> W["Web (Next.js standalone)"]
    W --> A["API (FastAPI, uvicorn workers)"]
    A --> P[("PostgreSQL terkelola + pgvector")]
    A -.-> IDP["SSO yang disetujui"]
    A -.-> DOC["Document provider yang disetujui"]
```

- **PROPOSED** Web dan API dideploy terpisah tetapi tetap satu boundary aplikasi; `next.config.ts` sudah memakai `output: "standalone"`.
- **PROPOSED** Prasyarat sebelum deploy apa pun: repository SQLAlchemy, identity provider produksi, secret store, backup, logging terpusat, security review.
- **OUT OF SCOPE** Kubernetes, multi-region, atau autoscaling pada fase magang.

## Open Questions
OQ-07 login (hosting dijawab sebagian: komputer tersendiri sebagai server); OQ-23 persyaratan server; OQ-11 lokasi pemrosesan AI; OQ-20 lingkungan UAT; OQ-24 pengakuan mentor.

## Related Documents
- [deployment-runbook.md](../11-operations/deployment-runbook.md)
- [local-development.md](../11-operations/local-development.md)
- [technology-stack.md](technology-stack.md)
