# Endpoint Catalog

**Status:** PROPOSED
**Last Updated:** 2026-10-13

## Purpose
Daftar seluruh endpoint `/api/v1` yang diimplementasikan (scaffold, data dari backend `DATA_BACKEND`: `simulated` default atau `postgres`; kontrak identik pada keduanya, ADR-015). Sumber: `apps/api/sunovate_api/modules/`. OpenAPI hidup: `http://localhost:8000/docs`.

- **PROPOSED (ADR-015)** Pada mode `postgres`, database yang tidak terjangkau menghasilkan 503 `DATABASE_UNAVAILABLE` pada endpoint data, sedangkan timeout, deadlock, atau serialization failure menghasilkan 503 `DATABASE_BUSY` dengan header `Retry-After`; `/health` tetap 200. Urutan key objek JSON bukan bagian kontrak.

"Auth" = cukup login. Endpoint yang mengembalikan satu record mengembalikan 404 bila record di luar scope.

| Method | Path | Permission | Keterangan |
|---|---|---|---|
| GET | `/health` | publik | status, versi, environment, `dataBackend` |
| GET | `/health/database` | publik | uji koneksi PostgreSQL; 503 bila tidak tersedia |
| POST | `/auth/dev/login` | publik (dev) | body `{email}`; token pengembangan |
| GET | `/auth/me` | Auth | principal: role, permission, tim, clearance |
| GET | `/users` | `user:read` | paginasi |
| GET | `/teams` | `team:read` | enam tim |
| GET | `/roles` | `role:read` | role + permission |
| GET | `/permissions` | `role:read` | katalog permission |
| GET | `/classifications` | Auth | empat tingkat |
| GET | `/knowledge` | `knowledge:read` | filter `q`, `status`, `type`, `teamCode`; paginasi |
| GET | `/knowledge/{id}` | `knowledge:read` | detail + dokumen + bagian teks |
| POST | `/knowledge` | `knowledge:create` | draf baru untuk tim dalam scope; `tags` duplikat dibuang (kemunculan pertama dipertahankan) |
| PATCH | `/knowledge/{id}` | `knowledge:update` | hanya DRAFT; wajib `revision`; `null` berarti field tidak diubah; `tags` didedupe seperti POST |
| POST | `/knowledge/{id}/submit` | `knowledge:submit` + `approval:request` | DRAFT ke IN_REVIEW, membuat approval `KNOWLEDGE_PUBLICATION` |
| GET | `/documents` | `document:read` | referensi yang terbaca |
| GET | `/documents/{id}` | `document:read` | detail + status provider |
| GET | `/documents/{id}/versions` | `document:read` | daftar versi |
| POST | `/documents/{id}/versions` | `document:version` | hanya `local://`; checksum duplikat 409 |
| GET | `/search?q=` | `search:query` + `knowledge:read` | leksikal atas knowledge PUBLISHED terbaca |
| GET | `/dashboard/summary` | `work:read` | metrik, perlu perhatian, tugas per status, knowledge terbaru |
| GET | `/work-outputs` | `work:read` | filter `teamCode`; `deadlineState` |
| GET | `/work-outputs/{id}` | `work:read` | + tugas + milestone |
| POST | `/work-outputs` | `work:create` | team scope + clearance; 201 |
| PATCH / DELETE | `/work-outputs/{id}` | `work:update` | revision wajib; delete soft delete |
| GET | `/tasks` | `work:read` | filter `status`, `deadlineState`, `teamCode` |
| POST | `/tasks` | `work:create` | output terkait opsional; harus satu tim |
| PATCH / DELETE | `/tasks/{id}` | `work:update` | wajib `revision`; delete soft delete |
| GET | `/milestones` | `work:read` | |
| POST / PATCH / DELETE | `/milestones[/{id}]` | `work:create` / `work:update` | output terkait wajib dan satu tim |
| GET | `/pending-matters` | `pending:read` | |
| GET | `/follow-ups` | `pending:read` | |
| POST / PATCH / DELETE | `/pending-matters[/{id}]` | `pending:manage` | team scope + clearance |
| POST / PATCH / DELETE | `/follow-ups[/{id}]` | `pending:manage` | induk opsional dan satu tim |
| GET | `/audit-logs` | `audit:read` | filter `action`; terbaru dulu |
| GET | `/approvals` | `approval:request` atau `approval:decide` | milik sendiri + yang boleh diputuskan dalam scope |
| POST | `/approvals/{id}/decision` | `approval:decide` (+ `knowledge:publish` untuk APPROVE publikasi) | body `{decision, revision, reason}` |
| POST | `/hermes/query` | `hermes:query` + `search:query` | body `{question, conversationId?}` |
| POST | `/hermes/messages/{id}/feedback` | `hermes:feedback` | hanya pesan milik sendiri |
| GET | `/hermes/sme-question-intake` | `knowledge:review` + `scope:all_teams` | register mentor/SME read-only; `MENTOR_PROVIDED_DRAFT`; diblokir dari retrieval/jawaban SAVI |
| GET | `/providers` | `provider:read` | status provider; semua non-produksi |
| GET | `/data-quality-issues` | `data_quality:read` | |

## Contoh: `GET /knowledge?pageSize=2`

```json
{
  "data": [
    {
      "id": "<uuid>",
      "title": "SIMULASI - SOP Registrasi Metadata Dokumen Knowledge",
      "knowledgeType": "SOP",
      "lifecycleStatus": "PUBLISHED",
      "sharingScope": "DIRECTORATE",
      "classificationCode": "INTERNAL",
      "ownerTeamCode": "PSUN",
      "revision": 1,
      "dataOrigin": "SIMULATED_DATA"
    }
  ],
  "meta": { "dataLabel": "SIMULATED_DATA", "page": 1, "pageSize": 2, "total": 4, "totalPages": 2 }
}
```

## Contoh: `POST /hermes/query`

Request: `{ "question": "Apa saja metadata wajib saat mendaftarkan dokumen knowledge?" }`

```json
{
  "data": {
    "conversationId": "<uuid>",
    "messageId": "<uuid>",
    "decision": "ANSWERED",
    "reason": "ok",
    "answer": "Berdasarkan sumber yang dapat Anda akses:\n\n1. Setiap dokumen ... [1]\n\n...",
    "citations": [
      { "index": 1, "knowledgeEntryId": "<uuid>", "documentChunkId": "<uuid>",
        "title": "SIMULASI - SOP Registrasi Metadata Dokumen Knowledge",
        "sectionLabel": "Langkah 1", "versionLabel": "v1.0", "knowledgeType": "SOP",
        "classificationCode": "INTERNAL" }
    ],
    "excludedPassages": 0,
    "approvalRequestId": null
  },
  "meta": { "dataLabel": "SIMULATED_DATA", "provider": "development" }
}
```

Nilai `decision` lain: `INSUFFICIENT_EVIDENCE`, `REFUSED_OUT_OF_SCOPE`, `REFUSED_GENERAL_CODING`, `REFUSED_POLICY`, `REQUIRES_HUMAN_APPROVAL` (dengan `approvalRequestId`), `BLOCKED_BY_OUTPUT_GUARD`.

## Belum diimplementasikan (PROPOSED)

CRUD pengguna/tim/role, approval khusus monitoring kerja, arsip knowledge, upload/ekstraksi dokumen, notifikasi, eksekusi aksi setelah approval, regulation relations, document automation.

Draft Workspace FR-56 juga belum diimplementasikan. Kontrak kandidat mencakup `/work-attachments`, versi draft, submit, return, publish, revisions, withdraw, dan `/access-grants`. Endpoint tersebut tidak boleh ditambahkan ke OpenAPI aktif sebelum OQ-35 disetujui. Spesifikasi lengkap: [work-file-draft-workspace.md](../02-business/work-file-draft-workspace.md).

## Related Documents
- [permission-matrix.md](../06-security/permission-matrix.md)
- [error-format.md](error-format.md)
- [openapi-guidelines.md](openapi-guidelines.md)
