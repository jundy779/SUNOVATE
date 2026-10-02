# Threat Model

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Mengidentifikasi ancaman utama terhadap aset SUNOVATE menggunakan kategori STRIDE dan mencatat mitigasi beserta statusnya (Implemented pada scaffold atau Proposed). Model ini mencakup scaffold dengan `SIMULATED_DATA`; ancaman terhadap integrasi produksi dinilai ulang saat integrasi divalidasi.

## Ruang lingkup

- **CONFIRMED** Komponen dalam lingkup: aplikasi web Next.js, API FastAPI, simulated store dan skema PostgreSQL, modul Hermes dengan provider `development_extractive` (sumber: fact sheet bagian 9).
- **OUT OF SCOPE** Integrasi produksi (SSO, SharePoint, Power BI, Telegram, WhatsApp, Kemenkeu Satu, market data) karena belum tersedia (sumber: Proposal v2.4, slide 11).

## Aset

| ID | Aset | Alasan penting |
|---|---|---|
| A1 | Konten knowledge dan metadata dokumen | Institutional memory; dapat bersifat INTERNAL atau RESTRICTED |
| A2 | Permission, role, team membership, clearance | Menentukan siapa membaca apa |
| A3 | Audit log | Bukti jejak akses dan perubahan |
| A4 | Development token dan `DEV_AUTH_SECRET` | Kunci identitas pada development |
| A5 | Konteks Hermes (chunk terotorisasi, prompt, jawaban, sitasi) | Jalur paling mudah untuk kebocoran lintas tim |

## STRIDE

| ID | Kategori | Aset | Ancaman | Mitigasi | Status |
|---|---|---|---|---|---|
| T-01 | Spoofing | A4 | Pemalsuan token pengembangan | Tanda tangan HMAC-SHA256, expiry dalam token, TTL terbatas | Implemented |
| T-02 | Spoofing | A4 | Dev auth aktif di produksi | API menolak start jika `APP_ENV=production` dan `DEV_AUTH_ENABLED=true` | Implemented |
| T-03 | Spoofing | A4 | Pencurian token melalui skrip di browser | Cookie httpOnly SameSite=Lax; panggilan API dari server Next.js | Implemented |
| T-04 | Tampering | A1 | Konflik atau penimpaan pembaruan bersamaan | `revision`; pembaruan basi menghasilkan 409 `REVISION_CONFLICT` | Implemented |
| T-05 | Tampering | A3 | Pengubahan atau penghapusan audit log | Trigger PostgreSQL menolak UPDATE/DELETE pada `audit_logs` | Implemented (skema); runtime memakai simulated store |
| T-06 | Tampering | A1 | Duplikasi ingestion dokumen | Unique (`document_reference_id`, `checksum_sha256`); 409 `DUPLICATE_CHECKSUM` | Implemented |
| T-07 | Repudiation | A3 | Pengguna menyangkal aksi | Audit action LOGIN, CREATE, UPDATE, SUBMIT, APPROVE, REJECT, ACCESS_DENIED, AI_QUERY, AI_FEEDBACK, VERSION_REGISTER, SEARCH; `X-Request-ID` | Implemented |
| T-08 | Information disclosure | A1 | IDOR: menebak id rekaman tim lain | Pemeriksaan team scope dan klasifikasi per rekaman; rekaman tak terbaca menghasilkan 404 | Implemented |
| T-09 | Information disclosure | A1, A5 | Kebocoran lintas tim melalui pencarian atau Hermes | Filter otorisasi sebelum scoring; hanya `PUBLISHED`; `HERMES_MAX_CLASSIFICATION` | Implemented |
| T-10 | Information disclosure | A5 | Prompt injection dari isi dokumen | Filter chunk berisi teks bernada instruksi; `CitationValidator`; `OutputGuard` | Implemented (heuristik) |
| T-11 | Information disclosure | A5 | Jailbreak atau policy override oleh pengguna | `ScopeGuard` menghasilkan `REFUSED_POLICY` | Implemented (heuristik) |
| T-12 | Information disclosure | A3, A4 | Kebocoran secret atau konten melalui log | Log JSON hanya berisi metadata; secret, token, dan isi dokumen tidak dicatat; `OutputGuard` memeriksa pola secret | Implemented (sebagian); review log Proposed |
| T-13 | Information disclosure | A1 | Pesan error membocorkan detail internal | Error envelope tanpa stack trace; `INTERNAL_ERROR` generik dengan `requestId` | Implemented |
| T-14 | Denial of service | API | Request berlebihan ke pencarian atau Hermes | `pageSize` maksimal 100; rate limiting | Proposed |
| T-15 | Elevation of privilege | A2 | Eskalasi hak melalui manipulasi frontend | Otorisasi hanya di API; menu frontend kosmetik | Implemented |
| T-16 | Elevation of privilege | A2 | Approver menyetujui request sendiri | Separation of duties pada keputusan approval (API 403 `SEPARATION_OF_DUTIES` + CHECK constraint) | Implemented |
| T-17 | Elevation of privilege | A1 | Hermes mengeksekusi aksi tulis | Write intent menjadi `REQUIRES_HUMAN_APPROVAL`; tidak pernah dieksekusi | Implemented |
| T-18 | Tampering | Supply chain | Dependency berbahaya atau typosquatting | Lockfile (`uv.lock`, pnpm lockfile); versi terkunci; dependency baru harus punya kebutuhan konkret | Implemented (lockfile); audit dependency otomatis Proposed |
| T-19 | Information disclosure | A1 | Data asli masuk repository | Hanya `SIMULATED_DATA`; file sumber PDF/PPTX dikecualikan via `.gitignore` | Implemented |

Status Implemented berarti kontrol ada pada scaffold (sumber: fact sheet bagian 3 dan 9; implementasi scaffold sesi 2026-10-01). Seluruh kontrol berjalan pada simulated store (`DATA_BACKEND=simulated`); kontrol yang sama wajib diterapkan ulang saat repository SQLAlchemy dibuat (ADR-007).

## Alur prompt injection

```mermaid
flowchart LR
    Q["Pertanyaan"] --> SG["ScopeGuard"]
    SG --> R["Retrieval terotorisasi"]
    R --> F["Filter injection pada chunk"]
    F --> HC["HermesClient"]
    HC --> CV["CitationValidator"]
    CV --> OG["OutputGuard"]
    OG --> AU["Audit log"]
```

Detail pertahanan ada di [prompt-injection-defense](../05-ai-rag/prompt-injection-defense.md).

## Proposed Design

- **PROPOSED** Rate limiting per pengguna untuk `/search` dan `/hermes/query`.
- **PROPOSED** Pemindaian dependency dan secret pada CI.
- **PROPOSED** Uji regresi keamanan untuk T-08 sampai T-11 menjadi bagian [security-testing](../10-testing/security-testing.md).
- **PROPOSED** Penilaian ulang threat model sebelum setiap integrasi dari [integration-readiness-checklist](../08-integrations/integration-readiness-checklist.md).

## Open Questions

- **OPEN QUESTION** OQ-07 Hosting yang disetujui; menentukan ancaman jaringan dan TLS.
- **OPEN QUESTION** OQ-11 Model AI dan lokasi pemrosesan; menentukan ancaman exfiltration melalui provider AI.

## Risks

R-02, R-03, R-07, R-10 pada [risk-register](../12-governance/risk-register.md).

## Related Documents

- [security-overview](security-overview.md)
- [authorization-rbac](authorization-rbac.md)
- [audit-logging](audit-logging.md)
- [scope-guard](../05-ai-rag/scope-guard.md)
