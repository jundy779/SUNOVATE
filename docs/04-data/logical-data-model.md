# Logical Data Model

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose
Atribut kunci, kardinalitas, dan aturan integritas per entitas. Kolom lengkap ada di [database-schema.md](database-schema.md).

## Kolom bersama
- **Semua tabel kecuali `audit_logs`:** `id`, `created_at`, `updated_at`, `data_origin`.
- **Record bisnis ber-governance** (`knowledge_entries`, `document_references`, `work_outputs`, `tasks`, `milestones`, `pending_matters`, `follow_ups`, `approval_requests`, `data_quality_issues`): tambahan `owner_team_id` (wajib), `owner_user_id`, `classification_code` (wajib, FK), `created_by`, `updated_by`, `revision`, `deleted_at`.

## Aturan integritas
| Entitas | Aturan | Ditegakkan oleh |
|---|---|---|
| `team_memberships` | unik (`user_id`, `team_id`) | constraint |
| `user_roles` | unik (`user_id`, `role_id`, `team_id`) | constraint |
| `role_permissions` | unik (`role_id`, `permission_id`) | constraint |
| `knowledge_entries.lifecycle_status` | DRAFT, IN_REVIEW, PUBLISHED, SUPERSEDED, ARCHIVED | CHECK + API |
| `knowledge_entries.sharing_scope` | TEAM, DIRECTORATE | CHECK + API |
| `document_versions` | unik (`document_reference_id`, `checksum_sha256`); checksum 64 hex | constraint + API 409 `DUPLICATE_CHECKSUM` |
| `document_versions.extraction_status` | PENDING, EXTRACTED, FAILED, QUARANTINED, NOT_APPLICABLE | CHECK |
| `document_chunks` | unik (`document_version_id`, `chunk_index`) | constraint |
| `embedding_references` | unik (`document_chunk_id`, `model_name`) | constraint |
| `regulation_relations` | tipe AMENDS, REVOKES, IMPLEMENTS, REFERENCES, SUPERSEDES; tidak boleh ke diri sendiri | CHECK |
| `work_outputs`, `tasks` | status 7 nilai task; `progress` 0 sampai 100 | CHECK |
| `milestones.status` | PLANNED, ACHIEVED, MISSED, CANCELLED | CHECK |
| `pending_matters.status` | OPEN, IN_PROGRESS, RESOLVED, CANCELLED | CHECK |
| `follow_ups.status` | OPEN, DONE, CANCELLED | CHECK |
| `approval_requests` | tipe 4 nilai, status 5 nilai, `decided_by <> requested_by` | CHECK + API 403 `SEPARATION_OF_DUTIES` |
| `ai_messages.role` | USER, ASSISTANT | CHECK |
| `ai_feedback.rating` | HELPFUL, NOT_HELPFUL | CHECK |
| `audit_logs` | tidak boleh UPDATE/DELETE | trigger |

Status work output, milestone, dan pending matter adalah usulan dan menunggu konfirmasi (OQ-15).

## Kardinalitas penting
- Satu pengguna dapat masuk ke beberapa tim; role dapat diberikan per tim (`user_roles.team_id`) atau global (`NULL`).
- Satu knowledge entry memiliki nol atau lebih document reference; satu reference memiliki banyak versi; `current_version_id` menunjuk versi aktif.
- Chunk mewarisi kepemilikan dan klasifikasi dari knowledge entry induk melalui `knowledge_entry_id`.

## Related Documents
- [conceptual-data-model.md](conceptual-data-model.md)
- [metadata-schema.md](metadata-schema.md)
- [business-rules.md](../02-business/business-rules.md)
