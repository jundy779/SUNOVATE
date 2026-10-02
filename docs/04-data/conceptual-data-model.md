# Conceptual Data Model

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose
Gambaran entitas utama dan hubungannya tanpa detail kolom. Dibagi per area agar diagram tetap kecil.

## Identitas dan akses

```mermaid
erDiagram
    USER ||--o{ TEAM_MEMBERSHIP : "anggota"
    TEAM ||--o{ TEAM_MEMBERSHIP : "memiliki"
    USER ||--o{ USER_ROLE : "diberi"
    ROLE ||--o{ USER_ROLE : "dipakai"
    ROLE ||--o{ ROLE_PERMISSION : "berisi"
    PERMISSION ||--o{ ROLE_PERMISSION : "termasuk"
    DATA_CLASSIFICATION ||--o{ USER : "clearance"
```

## Knowledge dan dokumen

```mermaid
erDiagram
    TEAM ||--o{ KNOWLEDGE_ENTRY : "memiliki"
    KNOWLEDGE_ENTRY ||--o{ DOCUMENT_REFERENCE : "merujuk"
    DOCUMENT_REFERENCE ||--o{ DOCUMENT_VERSION : "berversi"
    DOCUMENT_VERSION ||--o{ DOCUMENT_CHUNK : "diekstrak"
    DOCUMENT_CHUNK ||--o{ EMBEDDING_REFERENCE : "divektorkan"
    KNOWLEDGE_ENTRY ||--o{ KNOWLEDGE_TAG : "ditandai"
    TAG ||--o{ KNOWLEDGE_TAG : "dipakai"
    KNOWLEDGE_ENTRY ||--o{ REGULATION_RELATION : "sumber relasi"
```

## Kerja

```mermaid
erDiagram
    TEAM ||--o{ WORK_OUTPUT : "memiliki"
    WORK_OUTPUT ||--o{ TASK : "dipecah"
    WORK_OUTPUT ||--o{ MILESTONE : "ditandai"
    TEAM ||--o{ PENDING_MATTER : "memiliki"
    PENDING_MATTER ||--o{ FOLLOW_UP : "ditindaklanjuti"
```

## Hermes dan tata kelola

```mermaid
erDiagram
    USER ||--o{ AI_CONVERSATION : "memulai"
    AI_CONVERSATION ||--o{ AI_MESSAGE : "berisi"
    AI_MESSAGE ||--o{ AI_CITATION : "mengutip"
    AI_MESSAGE ||--o{ AI_FEEDBACK : "dinilai"
    USER ||--o{ APPROVAL_REQUEST : "mengajukan"
    USER ||--o{ AUDIT_LOG : "bertindak"
```

Entitas pendukung: `notifications`, `integration_sync_logs`, `data_quality_issues`.

## Catatan
- **OUT OF SCOPE (ADR-013)** Entitas SUN Business (instrumen, lelang, transaksi, yield, setelmen) belum dimodelkan.
- **OPEN QUESTION** Entitas rapat dan pemeriksaan (BPK/BPKP/Itjen) dari blueprint lama belum masuk skema; perlu validasi kebutuhan.

## Related Documents
- [logical-data-model.md](logical-data-model.md)
- [database-schema.md](database-schema.md)
