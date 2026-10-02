# Database Schema

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose
Katalog fisik 30 tabel pada revisi Alembic `0001_initial_schema` (sumber: `apps/api/sunovate_api/db/models.py`).

## Ekstensi dan objek khusus
- `CREATE EXTENSION vector` (pgvector).
- Fungsi `audit_logs_reject_mutation()` dan trigger `audit_logs_append_only` (BEFORE UPDATE OR DELETE).
- Kolom `search_vector` (`tsvector` GENERATED STORED, konfigurasi `simple`) pada `knowledge_entries` (title + summary) dan `document_chunks` (content), masing-masing dengan indeks GIN.
- Penamaan constraint konsisten (`pk_`, `fk_`, `uq_`, `ck_`, `ix_`).

## Tabel
`G` = memiliki kolom governance (lihat [logical-data-model.md](logical-data-model.md)).

| # | Tabel | Kolom khusus | G |
|---|---|---|---|
| 1 | `data_classifications` | `code` (unik), `rank` (unik), `label`, `description` | |
| 2 | `teams` | `code` (unik), `name`, `description`, `validation_status`, `status` | |
| 3 | `users` | `email` (unik), `display_name`, `clearance_code` FK, `status` | |
| 4 | `team_memberships` | `user_id`, `team_id` | |
| 5 | `roles` | `code` (unik), `name`, `description` | |
| 6 | `permissions` | `code` (unik), `description` | |
| 7 | `role_permissions` | `role_id`, `permission_id` | |
| 8 | `user_roles` | `user_id`, `role_id`, `team_id` (nullable) | |
| 9 | `knowledge_entries` | `title`, `knowledge_type`, `summary`, `lifecycle_status`, `sharing_scope`, `version_label`, `effective_date`, `expires_at`, `source_note`, `superseded_by_id`, `published_at`, `search_vector` | G |
| 10 | `document_references` | `knowledge_entry_id`, `title`, `provider`, `provider_location`, `external_id`, `mime_type`, `current_version_id`, `status` | G |
| 11 | `document_versions` | `document_reference_id`, `version_label`, `checksum_sha256`, `size_bytes`, `provider_location`, `extraction_status`, `failure_reason`, `created_by` | |
| 12 | `document_chunks` | `document_version_id`, `knowledge_entry_id`, `chunk_index`, `section_label`, `content`, `search_vector` | |
| 13 | `embedding_references` | `document_chunk_id`, `model_name`, `dimensions`, `embedding vector` | |
| 14 | `tags` | `slug` (unik), `label` | |
| 15 | `knowledge_tags` | `knowledge_entry_id`, `tag_id` | |
| 16 | `regulation_relations` | `source_entry_id`, `target_entry_id`, `relation_type`, `note`, `created_by` | |
| 17 | `work_outputs` | `title`, `description`, `status`, `priority`, `progress`, `start_date`, `target_date` | G |
| 18 | `tasks` | `work_output_id`, `title`, `description`, `status`, `priority`, `progress`, `start_date`, `due_date`, `assignee_user_id` | G |
| 19 | `milestones` | `work_output_id`, `title`, `status`, `due_date` | G |
| 20 | `pending_matters` | `title`, `description`, `status`, `due_date` | G |
| 21 | `follow_ups` | `pending_matter_id`, `title`, `status`, `due_date` | G |
| 22 | `ai_conversations` | `user_id`, `title`, `channel` | |
| 23 | `ai_messages` | `conversation_id`, `role`, `content`, `decision`, `classification_code`, `prompt_version` | |
| 24 | `ai_citations` | `message_id`, `citation_index`, `knowledge_entry_id`, `document_chunk_id`, `score` | |
| 25 | `ai_feedback` | `message_id`, `user_id`, `rating`, `comment` | |
| 26 | `audit_logs` | `occurred_at`, `actor_user_id`, `action`, `entity_type`, `entity_id`, `outcome`, `request_id`, `detail jsonb`, `data_origin` (tanpa `updated_at`) | |
| 27 | `approval_requests` | `request_type`, `target_entity_type`, `target_entity_id`, `status`, `requested_by`, `decided_by`, `decided_at`, `decision_reason`, `expires_at`, `payload jsonb` | G |
| 28 | `notifications` | `recipient_user_id`, `notification_type`, `title`, `body`, `entity_type`, `entity_id`, `channel`, `dedupe_key` (unik), `read_at`, `classification_code` | |
| 29 | `integration_sync_logs` | `provider_kind`, `provider_name`, `operation`, `status`, `started_at`, `finished_at`, `records_processed`, `error_summary`, `is_production` | |
| 30 | `data_quality_issues` | `entity_type`, `entity_id`, `issue_type`, `severity`, `description`, `status` | G |

Tidak ada kolom yang menyimpan isi file biner.

## Validasi yang dijalankan (2026-10-01)
`pnpm db:check` pada PostgreSQL sementara + pgvector 0.6.2: upgrade head, `alembic check` (tidak ada drift model vs migrasi), seed (run kedua menyisipkan 0 baris), 30 tabel, FTS `metadata` menemukan 2 chunk, `data_origin` non-simulasi = 0, UPDATE pada `audit_logs` ditolak, downgrade base berhasil.

## Related Documents
- [migration-guide.md](../11-operations/migration-guide.md)
- [metadata-schema.md](metadata-schema.md)
