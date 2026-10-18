# Dokumentasi SUNOVATE

**Status:** DRAFT
**Last Updated:** 2026-10-19

## Purpose

Folder `docs/` adalah titik masuk dokumentasi SUNOVATE, SUN Integrated Management and Knowledge Platform, yang dikembangkan untuk Direktorat Surat Utang Negara (Dit. SUN), DJPPR, Kementerian Keuangan RI (sumber: brief sesi 2026-10-01). Dokumen di sini menjelaskan konteks proyek, kebutuhan produk, proses bisnis, arsitektur, data, Hermes, keamanan, API, integrasi, UI/UX, pengujian, operasional, tata kelola, dan serah terima.

Seluruh data contoh di dokumentasi dan kode berlabel `SIMULATED_DATA`. Dokumentasi ini tidak memuat data internal, angka keuangan, atau data pribadi yang nyata.

## Label Bukti

Setiap pernyataan penting diberi salah satu label berikut.

| Label | Arti | Syarat |
|---|---|---|
| **CONFIRMED** | Sudah menjadi arahan atau fakta yang dapat dirujuk. | Wajib mencantumkan sumber, mis. "(sumber: brief sesi 2026-10-01)". |
| **PROPOSED** | Usulan pengembang, belum disetujui mentor. | Boleh dipakai sebagai dasar scaffold, dapat berubah. |
| **OPEN QUESTION** | Belum diketahui dan perlu jawaban mentor. | Dicatat di [open-questions.md](00-project/open-questions.md). |
| **OUT OF SCOPE** | Sengaja tidak dikerjakan pada fase ini. | Alasan dicatat di dokumen terkait. |

## Status Dokumen

| Status | Arti |
|---|---|
| DRAFT | Versi awal, masih disusun. |
| PROPOSED | Isi lengkap dan siap ditinjau, belum disetujui. |
| NEEDS MENTOR VALIDATION | Memuat asumsi proses bisnis atau kebijakan yang wajib divalidasi mentor. |
| CONFIRMED | Sudah ditinjau dan disetujui; perubahan dicatat di [decision-log.md](12-governance/decision-log.md). |

## Urutan Baca yang Disarankan

1. [ai-agent-handoff.md](13-handover/ai-agent-handoff.md) dan [task-tracker.md](13-handover/task-tracker.md) untuk snapshot serta status pekerjaan terbaru.
2. [project-overview.md](00-project/project-overview.md) dan [scope-and-boundaries.md](00-project/scope-and-boundaries.md) untuk memahami apa itu SUNOVATE dan batasannya.
3. [open-questions.md](00-project/open-questions.md) dan [assumptions.md](00-project/assumptions.md) untuk melihat hal yang belum pasti.
4. [prd.md](01-product/prd.md) dan [mvp-scope.md](01-product/mvp-scope.md) untuk kebutuhan produk.
5. [system-context.md](03-architecture/system-context.md) dan [architecture-decisions.md](03-architecture/architecture-decisions.md) untuk arsitektur.
6. [authorization-rbac.md](06-security/authorization-rbac.md) dan [hermes-overview.md](05-ai-rag/hermes-overview.md) untuk kontrol akses dan AI.
7. [local-development.md](11-operations/local-development.md) dan [developer-handover.md](13-handover/developer-handover.md) untuk menjalankan dan melanjutkan pengembangan.

## Indeks Folder

| Folder | Tujuan | Dokumen |
|---|---|---|
| `00-project` | Konteks proyek, rencana induk, batasan, pemangku kepentingan, asumsi, pertanyaan terbuka. | [project-overview](00-project/project-overview.md), [implementation-master-plan](00-project/implementation-master-plan.md), [vision-and-objectives](00-project/vision-and-objectives.md), [scope-and-boundaries](00-project/scope-and-boundaries.md), [stakeholder-map](00-project/stakeholder-map.md), [glossary](00-project/glossary.md), [assumptions](00-project/assumptions.md), [open-questions](00-project/open-questions.md), [mentor-session-01-agenda](00-project/mentor-session-01-agenda.md), [mentor-decision-oq37](00-project/mentor-decision-oq37.md) |
| `01-product` | Kebutuhan produk, persona, user story, kriteria penerimaan, roadmap. | [prd](01-product/prd.md), [user-personas](01-product/user-personas.md), [user-stories](01-product/user-stories.md), [functional-requirements](01-product/functional-requirements.md), [non-functional-requirements](01-product/non-functional-requirements.md), [mvp-scope](01-product/mvp-scope.md), [acceptance-criteria](01-product/acceptance-criteria.md), [product-roadmap](01-product/product-roadmap.md) |
| `02-business` | Latar domain SUN, ruang lingkup tim kerja, siklus knowledge dan dokumen, aturan bisnis. | [sun-domain-overview](02-business/sun-domain-overview.md), [team-work-scope](02-business/team-work-scope.md), [knowledge-lifecycle](02-business/knowledge-lifecycle.md), [document-lifecycle](02-business/document-lifecycle.md), [work-monitoring-flow](02-business/work-monitoring-flow.md), [draft-workspace](02-business/work-file-draft-workspace.md), [business-rules](02-business/business-rules.md) |
| `03-architecture` | Konteks sistem, container, komponen, deployment, stack, batas integrasi, ADR. | [system-context](03-architecture/system-context.md), [container-architecture](03-architecture/container-architecture.md), [component-architecture](03-architecture/component-architecture.md), [deployment-architecture](03-architecture/deployment-architecture.md), [technology-stack](03-architecture/technology-stack.md), [integration-boundaries](03-architecture/integration-boundaries.md), [provider-abstraction](03-architecture/provider-abstraction.md), [architecture-decisions](03-architecture/architecture-decisions.md) |
| `04-data` | Arsitektur data, model konseptual dan logis, skema, metadata, klasifikasi, retensi, kualitas, kebijakan data simulasi. | [data-architecture](04-data/data-architecture.md), [conceptual-data-model](04-data/conceptual-data-model.md), [logical-data-model](04-data/logical-data-model.md), [database-schema](04-data/database-schema.md), [metadata-schema](04-data/metadata-schema.md), [document-classification](04-data/document-classification.md), [data-retention](04-data/data-retention.md), [data-quality](04-data/data-quality.md), [simulated-data-policy](04-data/simulated-data-policy.md) |
| `05-ai-rag` | SAVI AI, RAG, ingestion, retrieval, chunking, sitasi, prompt, guard, evaluasi, persetujuan manusia. | [hermes-overview](05-ai-rag/hermes-overview.md), [rag-architecture](05-ai-rag/rag-architecture.md), [rag-pattern-reference](05-ai-rag/rag-pattern-reference.md), [rag-anything-pilot](05-ai-rag/rag-anything-pilot.md), [ingestion-pipeline](05-ai-rag/ingestion-pipeline.md), [retrieval-strategy](05-ai-rag/retrieval-strategy.md), [chunking-strategy](05-ai-rag/chunking-strategy.md), [citation-policy](05-ai-rag/citation-policy.md), [prompt-policy](05-ai-rag/prompt-policy.md), [scope-guard](05-ai-rag/scope-guard.md), [prompt-injection-defense](05-ai-rag/prompt-injection-defense.md), [rag-evaluation](05-ai-rag/rag-evaluation.md), [human-approval](05-ai-rag/human-approval.md) |
| `06-security` | Autentikasi, otorisasi, batas data privat, matriks izin, klasifikasi, threat model, audit, secret, insiden. | [security-overview](06-security/security-overview.md), [private-data-boundary](06-security/private-data-boundary.md), [authentication](06-security/authentication.md), [authorization-rbac](06-security/authorization-rbac.md), [permission-matrix](06-security/permission-matrix.md), [data-classification](06-security/data-classification.md), [threat-model](06-security/threat-model.md), [audit-logging](06-security/audit-logging.md), [secrets-management](06-security/secrets-management.md), [incident-response](06-security/incident-response.md), [security-checklist](06-security/security-checklist.md) |
| `07-api` | Konvensi API, format error, alur autentikasi, katalog endpoint, kebijakan webhook, OpenAPI. | [api-overview](07-api/api-overview.md), [api-conventions](07-api/api-conventions.md), [error-format](07-api/error-format.md), [authentication-flow](07-api/authentication-flow.md), [endpoint-catalog](07-api/endpoint-catalog.md), [webhook-policy](07-api/webhook-policy.md), [openapi-guidelines](07-api/openapi-guidelines.md) |
| `08-integrations` | Usulan integrasi fase lanjutan dan daftar kesiapan. Semua masih usulan. | [integration-overview](08-integrations/integration-overview.md), [sharepoint-proposal](08-integrations/sharepoint-proposal.md), [identity-provider-proposal](08-integrations/identity-provider-proposal.md), [power-bi-proposal](08-integrations/power-bi-proposal.md), [telegram-proposal](08-integrations/telegram-proposal.md), [whatsapp-proposal](08-integrations/whatsapp-proposal.md), [market-data-proposal](08-integrations/market-data-proposal.md), [integration-readiness-checklist](08-integrations/integration-readiness-checklist.md) |
| `09-ui-ux` | Arsitektur informasi, navigasi, dashboard, design system, aksesibilitas, responsif. | [information-architecture](09-ui-ux/information-architecture.md), [navigation](09-ui-ux/navigation.md), [dashboard-requirements](09-ui-ux/dashboard-requirements.md), [design-system](09-ui-ux/design-system.md), [accessibility](09-ui-ux/accessibility.md), [responsive-design](09-ui-ux/responsive-design.md), [prototype-notes](09-ui-ux/prototype-notes.md) |
| `10-testing` | Strategi dan jenis pengujian, UAT, tingkat keparahan bug, register bug. | [test-strategy](10-testing/test-strategy.md), [test-pyramid](10-testing/test-pyramid.md), [frontend-testing](10-testing/frontend-testing.md), [backend-testing](10-testing/backend-testing.md), [integration-testing](10-testing/integration-testing.md), [security-testing](10-testing/security-testing.md), [load-testing](10-testing/load-testing.md), [rag-testing](10-testing/rag-testing.md), [sme-question-validation](10-testing/sme-question-validation.md), [uat-plan](10-testing/uat-plan.md), [bug-severity](10-testing/bug-severity.md), [bug-register](10-testing/bug-register.md) |
| `11-operations` | Pengembangan lokal, konfigurasi, migrasi, backup, observability, deployment, troubleshooting. | [local-development](11-operations/local-development.md), [environment-configuration](11-operations/environment-configuration.md), [migration-guide](11-operations/migration-guide.md), [backup-and-restore](11-operations/backup-and-restore.md), [observability](11-operations/observability.md), [deployment-runbook](11-operations/deployment-runbook.md), [troubleshooting](11-operations/troubleshooting.md) |
| `12-governance` | Tata kelola knowledge, kepemilikan dokumen, review, perubahan, risiko, log keputusan. | [knowledge-governance](12-governance/knowledge-governance.md), [document-ownership](12-governance/document-ownership.md), [review-and-approval](12-governance/review-and-approval.md), [change-management](12-governance/change-management.md), [risk-register](12-governance/risk-register.md), [decision-log](12-governance/decision-log.md) |
| `13-handover` | Serah terima pengembang dan AI agent, tracker, panduan pengguna, keterbatasan, pengembangan lanjutan. | [ai-agent-handoff](13-handover/ai-agent-handoff.md), [task-tracker](13-handover/task-tracker.md), [developer-handover](13-handover/developer-handover.md), [administrator-guide](13-handover/administrator-guide.md), [user-guide-outline](13-handover/user-guide-outline.md), [known-limitations](13-handover/known-limitations.md), [future-development](13-handover/future-development.md) |

## Batasan Dasar

- **CONFIRMED** SUNOVATE tidak menggantikan sistem transaksi SUN resmi, tidak mengambil keputusan keuangan, dan tidak memberikan akses dokumen tanpa otorisasi (sumber: brief sesi 2026-10-01).
- **CONFIRMED** SUNOVATE bukan SUN Job Monitor; SUN Job Monitor adalah pilot terpisah yang dibekukan (sumber: `14_NEW_SESSION_HANDOFF_PROMPT.txt`, `20_NEW_CHAT_MASTER_PROMPT.txt`).
- **CONFIRMED** Hermes tidak pernah mengakses database secara langsung; semua akses melalui application service yang memeriksa izin pengguna (sumber: brief sesi 2026-10-01).
- **CONFIRMED** File tidak disimpan sebagai BLOB; database hanya menyimpan referensi, metadata, checksum SHA-256, versi, klasifikasi, dan lokasi provider (sumber: brief sesi 2026-10-01, ADR-003).
- **CONFIRMED** Arsitektur modular monolith dengan Next.js dan FastAPI; Turborepo, Kubernetes, microservices, Redis, dan message broker tidak dipakai (sumber: brief sesi 2026-10-01).
- **PROPOSED** Integrasi produksi (identitas, dokumen, notifikasi, AI eksternal, Telegram, WhatsApp, Power BI, data pasar, Kemenkeu Satu) tetap nonaktif sampai divalidasi. Ketersediaannya tidak diklaim di dokumen mana pun.
- **CONFIRMED (project lead, 2026-10-17)** SUNOVATE adalah sistem privat. Data tidak boleh dipublikasikan, diindeks, atau dikirim ke AI, agent, crawler, mesin pencari, maupun layanan eksternal tanpa persetujuan resmi dan kontrol teknis yang diverifikasi. Data asli tetap dilarang pada lingkungan pengembangan/demo saat ini.
- **OPEN QUESTION** Fungsi SUN Tematik belum diketahui (OQ-01). Tidak ada perilaku yang dikarang untuk tim ini.

## Arsip

Folder `docs/_archive/legacy-docs-v0/` berisi draf dokumentasi dari sesi sebelumnya. Isinya bersifat historis dan tidak otoritatif (ADR-012). Jika ada perbedaan, dokumen di luar `_archive` yang berlaku. Stack NestJS/Prisma dalam blueprint lama sudah digantikan oleh FastAPI/SQLAlchemy (ADR-002).

## Cara Memperbarui Dokumentasi

- Perbarui baris `Last Updated` setiap kali isi berubah.
- Ubah status menjadi CONFIRMED hanya setelah ada keputusan yang tercatat di [decision-log.md](12-governance/decision-log.md).
- Jawaban mentor atas pertanyaan terbuka dicatat di [open-questions.md](00-project/open-questions.md) lalu dirujuk dari dokumen terdampak.
- Jawaban knowledge owner pada deck proposal versi tetap `v1_` (slide 24) diberi label `CONFIRMED (knowledge owner, deck v1_ slide 24)`; pengakuan mentor masih tertunda (OQ-24). Rinciannya ada di [open-questions.md](00-project/open-questions.md) dan [decision-log.md](12-governance/decision-log.md) (DEC-20261002-01 sampai DEC-20261002-09).
- Gunakan hanya data berlabel `SIMULATED_DATA` untuk contoh.
- Setiap perubahan material wajib memperbarui [task-tracker.md](13-handover/task-tracker.md) dan root `CHANGELOG.md`; status `DONE` membutuhkan bukti implementasi dan validasi.

## Last Updated

2026-10-19
