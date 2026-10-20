const CLASSIFICATION_LABELS: Record<string, string> = {
  PUBLIC: "Terbuka",
  INTERNAL: "Internal",
  RESTRICTED: "Terbatas",
  CONFIDENTIAL: "Rahasia",
};

const KNOWLEDGE_STATUS_LABELS: Record<string, string> = {
  DRAFT: "Draf",
  IN_REVIEW: "Dalam pemeriksaan",
  PUBLISHED: "Diterbitkan",
  SUPERSEDED: "Digantikan",
  ARCHIVED: "Diarsipkan",
};

const KNOWLEDGE_TYPE_LABELS: Record<string, string> = {
  SOP: "SOP",
  PLAYBOOK: "Panduan kerja",
  LESSON_LEARNED: "Catatan pembelajaran",
  STUDY: "Kajian",
  REFERENCE: "Bahan rujukan",
  DECISION_RECORD: "Catatan keputusan",
};

const ROLE_LABELS: Record<string, string> = {
  system_admin: "Pengelola sistem",
  knowledge_coordinator: "Koordinator pengetahuan",
  team_lead: "Ketua tim",
  knowledge_owner: "Pemilik pengetahuan",
  reviewer: "Pemeriksa",
  staff: "Pelaksana",
  auditor: "Pemeriksa kepatuhan",
  read_only: "Pembaca",
};

const PERMISSION_LABELS: Record<string, string> = {
  "user:read": "Melihat pengguna",
  "user:manage": "Mengelola pengguna",
  "team:read": "Melihat tim kerja",
  "team:manage": "Mengelola tim kerja",
  "role:read": "Melihat peran dan kewenangan",
  "role:manage": "Mengelola peran dan kewenangan",
  "knowledge:read": "Membaca pengetahuan",
  "knowledge:create": "Membuat draf pengetahuan",
  "knowledge:update": "Mengubah draf pengetahuan",
  "knowledge:submit": "Mengajukan pemeriksaan pengetahuan",
  "knowledge:review": "Memeriksa pengetahuan",
  "knowledge:publish": "Menyetujui penerbitan pengetahuan",
  "knowledge:archive": "Mengarsipkan pengetahuan",
  "document:read": "Melihat informasi dokumen",
  "document:create": "Mendaftarkan dokumen",
  "document:update": "Mengubah informasi dokumen",
  "document:version": "Mendaftarkan versi dokumen",
  "search:query": "Melakukan pencarian",
  "work:read": "Melihat pekerjaan",
  "work:create": "Membuat pekerjaan",
  "work:update": "Memperbarui pekerjaan",
  "pending:read": "Melihat hal yang perlu ditindaklanjuti",
  "pending:manage": "Mengelola hal yang perlu ditindaklanjuti",
  "audit:read": "Melihat catatan aktivitas",
  "approval:request": "Mengajukan persetujuan",
  "approval:decide": "Memberikan keputusan",
  "hermes:query": "Bertanya kepada SAVI AI",
  "hermes:feedback": "Memberikan penilaian jawaban SAVI",
  "provider:read": "Melihat status layanan pendukung",
  "data_quality:read": "Melihat masalah kualitas data",
  "data_quality:manage": "Mengelola masalah kualitas data",
  "scope:all_teams": "Mengakses seluruh tim sesuai klasifikasi",
};

const AUDIT_ACTION_LABELS: Record<string, string> = {
  LOGIN: "Masuk",
  ACCESS_DENIED: "Akses ditolak",
  CREATE: "Membuat",
  UPDATE: "Memperbarui",
  DELETE: "Mengarsipkan",
  SUBMIT: "Mengajukan",
  APPROVE: "Menyetujui",
  REJECT: "Menolak",
  SEARCH: "Mencari",
  VERSION_REGISTER: "Mendaftarkan versi",
  AI_QUERY: "Bertanya kepada SAVI",
  AI_FEEDBACK: "Menilai jawaban SAVI",
};

const AUDIT_ENTITY_LABELS: Record<string, string> = {
  user: "Pengguna",
  knowledge_entry: "Pengetahuan",
  document_version: "Versi dokumen",
  work_output: "Output kerja",
  task: "Tugas",
  milestone: "Tahapan penting",
  pending_matter: "Hal yang perlu ditindaklanjuti",
  follow_up: "Tindak lanjut",
  approval_request: "Permintaan persetujuan",
  ai_message: "Jawaban SAVI",
};

const OUTCOME_LABELS: Record<string, string> = {
  SUCCESS: "Berhasil",
  DENIED: "Ditolak",
  FAILED: "Gagal",
};

const PROVIDER_LABELS: Record<string, string> = {
  AIProvider: "Penyusunan jawaban SAVI AI",
  EmbeddingProvider: "Pencarian berdasarkan kemiripan makna",
  DocumentProvider: "Penyimpanan dokumen",
  IdentityProvider: "Pengelolaan akun dan akses",
  NotificationProvider: "Pemberitahuan",
  HermesClient: "Percakapan SAVI AI",
  MarketDataProvider: "Sumber data pasar resmi",
};

const PROVIDER_DESCRIPTIONS: Record<string, string> = {
  AIProvider: "Menyusun jawaban hanya dari bahan yang telah lolos pemeriksaan.",
  EmbeddingProvider: "Membantu menemukan bahan dengan makna yang serupa.",
  DocumentProvider: "Menunjuk lokasi berkas tanpa menyimpan berkas di basis data.",
  IdentityProvider: "Memastikan pengguna masuk dengan akun yang berwenang.",
  NotificationProvider: "Menyampaikan pemberitahuan melalui kanal yang disetujui.",
  HermesClient: "Mengatur percakapan SAVI AI dengan sumber yang boleh diakses.",
  MarketDataProvider: "Mengambil data pasar dari sumber resmi yang disetujui.",
};

const PROVIDER_MODE_LABELS: Record<string, string> = {
  DISABLED: "Belum diaktifkan",
  DEVELOPMENT: "Simulasi pengembangan",
};

export const classificationLabel = (code: string) => CLASSIFICATION_LABELS[code] ?? "Belum ditetapkan";
export const knowledgeStatusLabel = (code: string) => KNOWLEDGE_STATUS_LABELS[code] ?? "Belum diketahui";
export const knowledgeTypeLabel = (code: string) => KNOWLEDGE_TYPE_LABELS[code] ?? "Pengetahuan lainnya";
export const roleLabel = (code: string) => ROLE_LABELS[code] ?? "Peran lainnya";
export const permissionLabel = (code: string) => PERMISSION_LABELS[code] ?? "Kewenangan lainnya";
export const auditActionLabel = (code: string) => AUDIT_ACTION_LABELS[code] ?? "Aktivitas sistem";
export const auditEntityLabel = (code: string) => AUDIT_ENTITY_LABELS[code] ?? "Data SUNOVATE";
export const outcomeLabel = (code: string) => OUTCOME_LABELS[code] ?? "Belum diketahui";
export const providerLabel = (code: string) => PROVIDER_LABELS[code] ?? "Layanan pendukung lainnya";
export const providerDescription = (code: string) =>
  PROVIDER_DESCRIPTIONS[code] ?? "Status layanan ini belum memiliki keterangan tambahan.";
export const providerModeLabel = (code: string) =>
  PROVIDER_MODE_LABELS[code] ?? "Status belum diketahui";

